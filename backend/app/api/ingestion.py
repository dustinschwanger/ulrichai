import json
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

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
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