# backend/app/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
# from .api import admin_ingestion  # Commented out due to moviepy dependency issues
import os
import logging
from starlette.middleware.base import BaseHTTPMiddleware
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
# import sentry_sdk  # Commented out due to venv issues
# from sentry_sdk.integrations.fastapi import FastApiIntegration  # Commented out due to venv issues
# from sentry_sdk.integrations.starlette import StarletteIntegration  # Commented out due to venv issues

# Import routers
from .api import ingestion, chat, documents
# from .api import admin_ingestion  # Commented out due to moviepy dependency issues

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
load_dotenv()

# Initialize Sentry for error tracking
# Commented out due to venv issues
# sentry_dsn = os.getenv("SENTRY_DSN")
# if sentry_dsn:
#     sentry_sdk.init(
#         dsn=sentry_dsn,
#         environment=os.getenv("ENVIRONMENT", "development"),
#         integrations=[
#             StarletteIntegration(transaction_style="endpoint"),
#             FastApiIntegration(transaction_style="endpoint"),
#         ],
#         # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
#         # Reduce in production to save on costs
#         traces_sample_rate=1.0 if os.getenv("ENVIRONMENT") != "production" else 0.1,
#         # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
#         # Reduce in production to save on costs
#         profiles_sample_rate=1.0 if os.getenv("ENVIRONMENT") != "production" else 0.1,
#     )
#     logging.info("✅ Sentry error tracking initialized")
# else:
#     logging.info("ℹ️  Sentry not configured (SENTRY_DSN not set)")
logging.info("ℹ️  Sentry disabled (venv rebuild in progress)")

# Initialize rate limiter
# limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app with increased file upload limits
app = FastAPI(
    title=os.getenv("APP_NAME", "Ulrich AI"),
    version=os.getenv("APP_VERSION", "0.1.0"),
    description="AI-powered knowledge platform for HR and business leaders"
)

# Add rate limit handler
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
# Get allowed origins from environment variable
cors_origins_env = os.getenv("CORS_ORIGINS", "")
allowed_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()] if cors_origins_env else []

# Development origins (only used if CORS_ORIGINS not set)
default_dev_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:8000",
]

# Determine origins based on environment
if os.getenv("ENVIRONMENT") == "production":
    # Production MUST specify exact origins in CORS_ORIGINS env var
    if not allowed_origins:
        logging.warning("⚠️  PRODUCTION: No CORS_ORIGINS set! Using restrictive defaults.")
        # Fallback to Railway patterns (user must still configure exact domains)
        all_origins = []
    else:
        all_origins = allowed_origins
        logging.info(f"✅ Production CORS origins configured: {all_origins}")
else:
    # Development: use specified origins or defaults
    all_origins = allowed_origins if allowed_origins else default_dev_origins
    logging.info(f"🔧 Development CORS origins: {all_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers with proper prefixes
app.include_router(ingestion.router, prefix="/api/ingestion", tags=["ingestion"])
app.include_router(chat.router)
app.include_router(documents.router, prefix="/api", tags=["documents"])
# app.include_router(admin_ingestion.router, prefix="/api/ingestion", tags=["admin"])  # Commented out due to moviepy dependency issues

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