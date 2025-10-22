import json
import re
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import os
import shutil
from pathlib import Path
import logging
from datetime import datetime

from ..processing.document_processor import processor
from ..processing.graph_builder import graph_builder
from ..core.database import db
from ..core.vector_store import vector_store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingestion"])

# Create uploads directory if it doesn't exist
# Use absolute path to root uploads directory (two levels up from app/api to get to backend, then one more to root)
UPLOAD_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload and process a single document"""
    
    # Validate file type
    allowed_types = ['pdf', 'docx', 'doc', 'pptx', 'ppt']
    file_ext = file.filename.split('.')[-1].lower()
    
    if file_ext not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{file_ext} not supported. Allowed types: {allowed_types}"
        )
    
    # Save uploaded file
    file_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving uploaded file")
    
    # Process document in background
    background_tasks.add_task(process_document_task, str(file_path), file_ext, file.filename)
    
    return {
        "message": "Document uploaded successfully",
        "filename": file.filename,
        "status": "processing"
    }

async def process_document_task(file_path: str, file_type: str, original_filename: str):
    """Background task to process document"""
    try:
        logger.info(f"Starting to process document: {original_filename}")
        
        # Process document
        doc_data = await processor.process_document(file_path, file_type)
        doc_data['title'] = original_filename
        
        # Generate embeddings for all levels
        logger.info("Generating embeddings...")
        
        # Document-level embedding
        doc_embedding = vector_store.get_embedding(doc_data['summary'])
        
        # Section-level embeddings
        section_embeddings = []
        for section in doc_data['sections']:
            section_summary = section['text'][:500]  # First 500 chars as summary
            section_embedding = vector_store.get_embedding(section_summary)
            section_embeddings.append({
                'title': section['title'],
                'embedding': section_embedding
            })
        
        # Chunk-level embeddings
        chunk_texts = [chunk['text'] for chunk in doc_data['chunks']]
        chunk_embeddings = vector_store.get_embeddings_batch(chunk_texts)
        
        # Store in vector database
        logger.info("Storing in vector database...")
        await store_in_vector_db(doc_data, doc_embedding, section_embeddings, chunk_embeddings)
        
        # Store metadata in database
        logger.info("Storing metadata in database...")
        await store_metadata_in_db(doc_data)
        
        # Update document graph
        logger.info("Updating document graph...")
        await update_document_graph(doc_data, doc_embedding)
        
        logger.info(f"Successfully processed document: {original_filename}")
        
    except Exception as e:
        logger.error(f"Error processing document {original_filename}: {e}")
        # Could update a status table here to mark as failed

async def store_in_vector_db(doc_data: Dict, doc_embedding: List[float], 
                            section_embeddings: List[Dict], chunk_embeddings: List[List[float]]):
    """Store embeddings in Pinecone using namespaces"""
    
    try:
        # Get the single index
        index = vector_store.index
        
        # Store document embedding in 'documents' namespace
        index.upsert(
            vectors=[{
                'id': doc_data['doc_id'],
                'values': doc_embedding,
                'metadata': {
                    'title': doc_data['title'],
                    'summary': doc_data['summary'],
                    'concepts': ','.join(doc_data['concepts'][:10]),
                    'file_type': doc_data['file_type']
                }
            }],
            namespace='documents'
        )
        
        # Store section embeddings in 'sections' namespace
        section_vectors = []
        for i, section in enumerate(doc_data['sections']):
            section_vectors.append({
                'id': f"{doc_data['doc_id']}_section_{i}",
                'values': section_embeddings[i]['embedding'],
                'metadata': {
                    'doc_id': doc_data['doc_id'],
                    'doc_title': doc_data['title'],
                    'section_title': section['title'],
                    'section_text': section['text'][:1000]
                }
            })
        
        if section_vectors:
            index.upsert(vectors=section_vectors, namespace='sections')
        
        # Store chunk embeddings in 'chunks' namespace
        chunk_vectors = []
        for i, chunk in enumerate(doc_data['chunks']):
            chunk_vectors.append({
                'id': f"{doc_data['doc_id']}_chunk_{i}",
                'values': chunk_embeddings[i],
                'metadata': {
                    'doc_id': doc_data['doc_id'],
                    'doc_title': doc_data['title'],
                    'section_title': chunk['section_title'],
                    'chunk_text': chunk['text'],
                    'chunk_id': chunk['chunk_id']
                }
            })
        
        if chunk_vectors:
            # Batch upsert in groups of 100
            batch_size = 100
            for i in range(0, len(chunk_vectors), batch_size):
                batch = chunk_vectors[i:i+batch_size]
                index.upsert(vectors=batch, namespace='chunks')
        
        logger.info(f"Stored {len(chunk_vectors)} chunks in vector database")
        
    except Exception as e:
        logger.error(f"Error storing in vector database: {e}")
        raise

async def store_metadata_in_db(doc_data: Dict):
    """Store document metadata in database"""
    
    try:
        if db.engine:
            # Store document metadata using SQLAlchemy
            from sqlalchemy import text
            
            with db.engine.connect() as conn:
                query = text("""
                    INSERT INTO documents (id, title, summary, concepts, file_type, file_path, 
                                         processed_at, num_sections, num_chunks)
                    VALUES (:id, :title, :summary, :concepts, :file_type, :file_path, 
                           :processed_at, :num_sections, :num_chunks)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        summary = EXCLUDED.summary,
                        updated_at = NOW()
                """)
                
                conn.execute(query, {
                    'id': doc_data['doc_id'],
                    'title': doc_data['title'],
                    'summary': doc_data['summary'],
                    'concepts': json.dumps(doc_data['concepts']),
                    'file_type': doc_data['file_type'],
                    'file_path': doc_data['file_path'],
                    'processed_at': datetime.now(),
                    'num_sections': len(doc_data['sections']),
                    'num_chunks': len(doc_data['chunks'])
                })
                conn.commit()
                
            logger.info(f"Stored document metadata for: {doc_data['title']}")
        else:
            logger.warning("Database not connected, skipping metadata storage")
            
    except Exception as e:
        logger.error(f"Error storing metadata in database: {e}")
        # Continue processing even if metadata storage fails

async def update_document_graph(doc_data: Dict, doc_embedding: List[float]):
    """Update the document relationship graph"""
    
    try:
        if db.engine:
            # Get existing documents from database
            from sqlalchemy import text
            
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM documents"))
                existing_docs = [dict(row._mapping) for row in result]
            
            if existing_docs:
                # Get embeddings for existing documents
                embeddings = {doc_data['doc_id']: doc_embedding}
                
                # Fetch embeddings for other documents
                index = vector_store.index
                for doc in existing_docs:
                    if doc['id'] != doc_data['doc_id']:
                        try:
                            result = index.fetch(ids=[doc['id']], namespace='documents')
                            if doc['id'] in result['vectors']:
                                embeddings[doc['id']] = result['vectors'][doc['id']]['values']
                        except:
                            continue
                
                # Build updated graph
                all_docs = existing_docs + [doc_data]
                graph_builder.build_document_graph(all_docs, embeddings)
                
                logger.info("Document graph updated successfully")
        else:
            logger.warning("Database not connected, skipping graph update")
            
    except Exception as e:
        logger.error(f"Error updating document graph: {e}")

@router.get("/status/{doc_id}")
async def get_processing_status(doc_id: str):
    """Get processing status for a document"""
    
    try:
        if db.engine:
            from sqlalchemy import text
            
            with db.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT * FROM documents WHERE id = :id"),
                    {'id': doc_id}
                )
                row = result.first()
                
                if row:
                    return {
                        "status": "completed",
                        "document": dict(row._mapping)
                    }
        
        return {
            "status": "processing",
            "message": "Document is still being processed"
        }
            
    except Exception as e:
        logger.error(f"Error checking document status: {e}")
        raise HTTPException(status_code=500, detail="Error checking document status")

@router.get("/documents")
async def list_documents(page: int = 1, limit: int = 50):
    """List all uploaded documents from Supabase storage"""

    try:
        from ..core.database import supabase

        all_files = []

        # Check if Supabase storage is available
        if supabase:
            # List of buckets to check
            buckets = ['documents']

            for bucket_name in buckets:
                try:
                    logger.info(f"Fetching files from bucket: {bucket_name}")
                    files = supabase.storage.from_(bucket_name).list()

                    if files:
                        for file_obj in files:
                            # Add bucket info to each file object
                            file_obj['bucket'] = bucket_name
                            all_files.append(file_obj)
                        logger.info(f"Found {len(files)} files in {bucket_name}")
                    else:
                        logger.info(f"No files found in {bucket_name}")

                except Exception as e:
                    logger.error(f"Error listing files from bucket {bucket_name}: {e}")
                    continue

            if all_files:
                # Sort all files by created_at timestamp (newest first), handling None values
                sorted_files = sorted(all_files, key=lambda x: x.get('created_at') or '1970-01-01', reverse=True)
                total_count = len(sorted_files)

                # Paginate results
                start_idx = (page - 1) * limit
                end_idx = start_idx + limit
                paginated_files = sorted_files[start_idx:end_idx]

                documents = []
                for file_obj in paginated_files:
                    file_name = file_obj['name']
                    bucket_name = file_obj.get('bucket', 'documents')

                    # Clean up the display name by removing timestamp prefixes and adding spaces
                    clean_name = file_name.rsplit('.', 1)[0] if '.' in file_name else file_name

                    # Remove timestamp patterns: YYYYMMDD_HHMMSS_ or TIMESTAMP_
                    if '_' in clean_name:
                        parts = clean_name.split('_')
                        # Remove leading numeric parts (timestamps)
                        while parts and parts[0].replace('.', '').replace('-', '').isdigit():
                            parts.pop(0)
                        clean_name = '_'.join(parts) if parts else clean_name

                    # Add spaces before capital letters (camelCase to Title Case)
                    clean_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', clean_name)
                    # Replace underscores and hyphens with spaces
                    clean_name = clean_name.replace('_', ' ').replace('-', ' ')
                    # Clean up multiple spaces
                    clean_name = re.sub(r'\s+', ' ', clean_name).strip()

                    # If name is empty or just "lessons", try to get a better name
                    if not clean_name or clean_name.lower() == 'lessons':
                        # Try to extract from metadata or use filename
                        clean_name = file_obj.get('metadata', {}).get('name', file_name) if isinstance(file_obj.get('metadata'), dict) else file_name

                    # Determine file type
                    file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
                    doc_type = 'video' if file_ext in ['mp4', 'webm', 'mov', 'avi'] else 'article'

                    # All documents come from the documents bucket
                    source = 'upload'

                    # Get author from metadata if available
                    author = 'Unknown'
                    if isinstance(file_obj.get('metadata'), dict):
                        file_metadata = file_obj.get('metadata', {})
                        author = file_metadata.get('author', file_metadata.get('uploader', 'Unknown'))

                    documents.append({
                        'id': f"{bucket_name}_{file_name.rsplit('.', 1)[0]}",
                        'displayName': clean_name,
                        'filename': file_name,
                        'documentSource': source,
                        'documentType': doc_type,
                        'humanCapabilityDomain': 'hr',
                        'author': author,
                        'publicationDate': (file_obj.get('created_at') or datetime.now().isoformat())[:10],
                        'uploadDate': file_obj.get('updated_at') or file_obj.get('created_at') or datetime.now().isoformat(),
                        'description': '',
                        'allowDownload': True,
                        'showInViewer': True,
                        'size': (file_obj.get('metadata') or {}).get('size', 0),
                        'permissions': 'read',
                        'fileUrl': f'/api/documents/{file_name}?bucket={bucket_name}',
                        'bucket': bucket_name
                    })
            else:
                total_count = 0
                documents = []
        else:
            logger.warning("Supabase storage not available")
            total_count = 0
            documents = []

        return {
            'documents': documents,
            'total': total_count,
            'page': page,
            'limit': limit,
            'pages': (total_count + limit - 1) // limit if total_count > 0 else 0
        }

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@router.post("/bulk-upload")
async def bulk_upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload multiple documents at once"""

    results = []
    
    for file in files:
        # Validate file type
        file_ext = file.filename.split('.')[-1].lower()
        allowed_types = ['pdf', 'docx', 'doc', 'pptx', 'ppt']
        
        if file_ext not in allowed_types:
            results.append({
                "filename": file.filename,
                "status": "rejected",
                "reason": f"Unsupported file type: .{file_ext}"
            })
            continue
        
        # Save file
        file_path = UPLOAD_DIR / f"{datetime.now().timestamp()}_{file.filename}"
        
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Add to background processing
            background_tasks.add_task(process_document_task, str(file_path), file_ext, file.filename)
            
            results.append({
                "filename": file.filename,
                "status": "queued"
            })
            
        except Exception as e:
            logger.error(f"Error processing {file.filename}: {e}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "reason": str(e)
            })
    
    return {
        "message": f"Processing {len(files)} documents",
        "results": results
    }

@router.delete("/documents/{filename}")
async def delete_document(filename: str, bucket: str = "documents"):
    """Delete a document from Supabase storage and Pinecone vector database"""

    try:
        from ..core.database import supabase

        if not supabase:
            raise HTTPException(status_code=503, detail="Storage service is not available")

        # Delete from Supabase storage
        try:
            supabase.storage.from_(bucket).remove([filename])
            logger.info(f"Deleted {filename} from Supabase storage")
        except Exception as e:
            logger.error(f"Error deleting file from storage: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting file from storage: {str(e)}")

        # Delete from Pinecone vector database
        try:
            vector_store.delete_by_filename(filename)
            logger.info(f"Deleted vectors for {filename} from Pinecone")
        except Exception as e:
            logger.warning(f"Could not delete from Pinecone (continuing anyway): {e}")

        return {
            "message": f"Successfully deleted {filename} from all locations",
            "filename": filename,
            "bucket": bucket
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@router.get("/documents/{filename}/download")
async def download_document(filename: str, bucket: str = "documents"):
    """Generate a signed URL for downloading a document from Supabase storage"""

    try:
        from ..core.database import supabase

        if not supabase:
            raise HTTPException(status_code=503, detail="Storage service is not available")

        # Generate a signed URL (valid for 1 hour)
        signed_url = supabase.storage.from_(bucket).create_signed_url(
            filename,
            3600  # 1 hour expiry
        )

        if not signed_url or 'signedURL' not in signed_url:
            raise HTTPException(status_code=404, detail=f"Could not generate download URL for {filename}")

        return {
            "url": signed_url['signedURL'],
            "filename": filename,
            "bucket": bucket,
            "expires_in": 3600
        }

    except Exception as e:
        logger.error(f"Error generating download URL for {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating download URL: {str(e)}")