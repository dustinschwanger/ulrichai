# backend/app/api/documents.py

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, RedirectResponse
from pathlib import Path
import logging
from typing import Optional
from urllib.parse import unquote
import os
import re

logger = logging.getLogger(__name__)

router = APIRouter()

# Path to uploads folder - use absolute path to the root uploads directory
UPLOADS_DIR = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "uploads"

# Import Supabase client for document storage
from ..core.database import supabase

@router.get("/documents/{filename:path}")
async def get_document(filename: str, page: Optional[int] = None, bucket: Optional[str] = None):
    """
    Serve a PDF document from the uploads folder or Supabase storage.

    Args:
        filename: Name of the PDF file (can contain spaces)
        page: Optional page number to highlight (for future use)
        bucket: Optional Supabase bucket name (documents)
    """
    try:
        # URL decode the filename to handle spaces and special characters
        filename = unquote(filename)
        logger.info(f"Requested file: {filename} from bucket: {bucket}")

        # Sanitize filename to prevent directory traversal
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Ensure it's a PDF
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        # Extract base filename without timestamp prefix for fuzzy matching
        # Pattern: YYYYMMDD_HHMMSS_filename.pdf -> filename.pdf
        base_filename = filename
        timestamp_match = re.match(r'^\d{8}_\d{6}_(.+)$', filename)
        if timestamp_match:
            base_filename = timestamp_match.group(1)
            logger.info(f"Extracted base filename: {base_filename}")

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
                # Try Supabase storage as fallback
                logger.info(f"Document not found locally, checking Supabase storage: {filename}")
                if supabase:
                    # List of buckets to check
                    buckets_to_check = [bucket] if bucket else ['documents']

                    for bucket_name in buckets_to_check:
                        try:
                            logger.info(f"Checking bucket '{bucket_name}' for exact filename: {filename}")
                            # First try exact filename match
                            signed_url = supabase.storage.from_(bucket_name).create_signed_url(
                                filename,
                                3600  # 1 hour
                            )

                            if signed_url and 'signedURL' in signed_url:
                                logger.info(f"Found exact match in bucket '{bucket_name}'")
                                return RedirectResponse(url=signed_url['signedURL'])
                        except Exception as e:
                            logger.debug(f"Exact match not found in bucket '{bucket_name}': {e}")

                        # If exact match fails, try fuzzy matching by listing files
                        try:
                            logger.info(f"Trying fuzzy match in bucket '{bucket_name}' for base: {base_filename}")
                            # List all files in the bucket
                            files_response = supabase.storage.from_(bucket_name).list()

                            if files_response:
                                logger.info(f"Found {len(files_response)} files in bucket '{bucket_name}'")
                                # Look for files that end with the base filename
                                for file_obj in files_response:
                                    file_name = file_obj.get('name', '')
                                    logger.debug(f"Checking file: {file_name}")

                                    # Check if this file ends with our base filename (fuzzy timestamp match)
                                    if file_name.endswith(base_filename) or (base_filename in file_name):
                                        logger.info(f"Found fuzzy match: {file_name} matches base {base_filename}")
                                        # Generate signed URL for the matched file
                                        signed_url = supabase.storage.from_(bucket_name).create_signed_url(
                                            file_name,
                                            3600
                                        )
                                        if signed_url and 'signedURL' in signed_url:
                                            logger.info(f"Successfully generated signed URL for fuzzy match")
                                            return RedirectResponse(url=signed_url['signedURL'])
                        except Exception as e:
                            logger.debug(f"Fuzzy match failed in bucket '{bucket_name}': {e}")
                            continue

                logger.error(f"Document not found: {filename}")
                logger.error(f"Available local files: {[f.name for f in pdf_files]}")
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
