# backend/app/api/documents.py

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from typing import Optional
from urllib.parse import unquote

logger = logging.getLogger(__name__)

router = APIRouter()

# Path to uploads folder
UPLOADS_DIR = Path("uploads")

@router.get("/documents/{filename:path}")
async def get_document(filename: str, page: Optional[int] = None):
    """
    Serve a PDF document from the uploads folder.
    
    Args:
        filename: Name of the PDF file (can contain spaces)
        page: Optional page number to highlight (for future use)
    """
    try:
        # URL decode the filename to handle spaces and special characters
        filename = unquote(filename)
        logger.info(f"Requested file: {filename}")
        
        # Sanitize filename to prevent directory traversal
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Ensure it's a PDF
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        # Build file path
        file_path = UPLOADS_DIR / filename
        
        # Log for debugging
        logger.info(f"Looking for file at: {file_path}")
        logger.info(f"File exists: {file_path.exists()}")
        
        # List all PDF files for debugging
        pdf_files = list(UPLOADS_DIR.glob('*.pdf'))
        logger.info(f"Available PDF files: {[f.name for f in pdf_files]}")
        
        # Check if file exists
        if not file_path.exists():
            # Try to find the file with timestamp prefix
            found = False
            for pdf_file in pdf_files:
                # Check if the file ends with the requested filename
                # This handles the timestamp prefix pattern: 1756395268.482499_filename.pdf
                if pdf_file.name.endswith(f"_{filename}") or pdf_file.name.endswith(filename):
                    file_path = pdf_file
                    logger.info(f"Found file with timestamp: {file_path}")
                    found = True
                    break
                # Also try case-insensitive match
                elif pdf_file.name.lower().endswith(f"_{filename.lower()}") or pdf_file.name.lower() == filename.lower():
                    file_path = pdf_file
                    logger.info(f"Found case-insensitive match: {file_path}")
                    found = True
                    break
            
            if not found:
                logger.error(f"Document not found: {filename}")
                logger.error(f"Available files: {[f.name for f in pdf_files]}")
                raise HTTPException(
                    status_code=404, 
                    detail=f"Document not found: {filename}"
                )
        
        # Return the PDF file
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={file_path.name}",
                # Add page hint for frontend (can be used by PDF viewer)
                "X-Page-Number": str(page) if page else "1"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving document {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{filename:path}/info")
async def get_document_info(filename: str):
    """
    Get metadata about a document.
    """
    try:
        # URL decode the filename
        filename = unquote(filename)
        
        # Sanitize filename
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        file_path = UPLOADS_DIR / filename
        
        if not file_path.exists():
            # Try case-insensitive search
            pdf_files = list(UPLOADS_DIR.glob('*.pdf'))
            for pdf_file in pdf_files:
                if pdf_file.name.lower() == filename.lower():
                    file_path = pdf_file
                    break
            else:
                raise HTTPException(status_code=404, detail="Document not found")
        
        # Get file size and other metadata
        file_stats = file_path.stat()
        
        return {
            "filename": file_path.name,
            "size": file_stats.st_size,
            "modified": file_stats.st_mtime,
            "exists": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document info for {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")