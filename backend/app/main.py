# backend/app/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .api import admin_ingestion
import os
import logging
from starlette.middleware.base import BaseHTTPMiddleware

# Import routers
from .api import ingestion, chat, documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Create FastAPI app with increased file upload limits
app = FastAPI(
    title=os.getenv("APP_NAME", "Ulrich AI"),
    version=os.getenv("APP_VERSION", "0.1.0"),
    description="AI-powered knowledge platform for HR and business leaders"
)

# Configure maximum request body size for large video uploads (1.5 GB)
MAX_UPLOAD_SIZE = 1610612736  # 1.5 GB in bytes

# Custom middleware to handle large file uploads
class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length:
                content_length = int(content_length)
                if content_length > MAX_UPLOAD_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size allowed is {MAX_UPLOAD_SIZE // (1024*1024*1024)} GB"
                    )
        response = await call_next(request)
        return response

# Add the middleware
app.add_middleware(LimitUploadSizeMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["ingestion"])
app.include_router(chat.router)
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(admin_ingestion.router, prefix="/api/ingestion", tags=["admin"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logging.info("Starting Ulrich AI...")
    
    # Initialize vector store indexes
    from .core.vector_store import vector_store
    
    try:
        vector_store.create_indexes()
        logging.info("Vector store indexes ready")
    except Exception as e:
        logging.error(f"Error initializing vector store: {e}")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Ulrich AI",
        "version": os.getenv("APP_VERSION", "0.1.0"),
        "status": "online",
        "endpoints": {
            "documentation": "/docs",
            "upload": "/api/ingestion/upload",
            "chat": "/api/chat/query",
            "documents": "/api/documents/{filename}"
        }
    }

@app.get("/health")
async def health_check():
    from .core.vector_store import vector_store
    
    try:
        stats = vector_store.index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        return {
            "status": "healthy",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "vectors_indexed": total_vectors
        }
    except Exception as e:
        logging.warning(f"Could not get vector stats: {e}")
        return {
            "status": "healthy",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "vectors_indexed": "unknown"
        }