from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Create Base for SQLAlchemy models
Base = declarative_base()

class Database:
    def __init__(self):
        try:
            # Use the PostgreSQL connection string from Supabase
            database_url = os.getenv("DATABASE_URL")
            
            if not database_url:
                logger.warning("DATABASE_URL not found, skipping database connection")
                self.engine = None
                self.SessionLocal = None
            else:
                # Fix for SQLAlchemy compatibility with Supabase
                if database_url.startswith("postgresql://"):
                    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
                
                self.engine = create_engine(
                    database_url,
                    pool_pre_ping=True,  # Test connections before using them
                    pool_recycle=300,    # Recycle connections after 5 minutes
                    pool_size=10,        # Connection pool size
                    max_overflow=20      # Max overflow connections
                )
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                logger.info("Successfully connected to database")
                
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            self.engine = None
            self.SessionLocal = None
    
    def get_session(self):
        if self.SessionLocal:
            return self.SessionLocal()
        return None

# Create global database instance
db = Database()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    logger.error(f"SUPABASE_URL found: {bool(SUPABASE_URL)}")
    logger.error(f"SUPABASE_KEY found: {bool(SUPABASE_KEY)}")
else:
    try:
        from supabase import create_client, Client
        
        # Initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized successfully")
        
        # Test the connection by listing buckets
        try:
            buckets = supabase.storage.list_buckets()
            logger.info(f"Connected to Supabase Storage. Available buckets: {[b.name for b in buckets]}")
            
            # Check if 'documents' bucket exists
            bucket_names = [b.name for b in buckets]
            if 'documents' not in bucket_names:
                logger.warning("'documents' bucket not found in Supabase Storage. Please create it in the Supabase dashboard.")
        except Exception as storage_error:
            logger.warning(f"Could not list storage buckets: {storage_error}")
            
    except ImportError as e:
        logger.error(f"Supabase package not installed: {e}")
        logger.error("Run: pip install supabase==1.2.0")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        logger.error("Check your SUPABASE_URL and SUPABASE_KEY in .env file")

# FastAPI dependency for database sessions
def get_db():
    """
    Dependency for FastAPI endpoints to get database session.
    Yields a session and ensures it's closed after the request.
    """
    session = db.get_session()
    if session:
        try:
            yield session
        finally:
            session.close()
    else:
        raise Exception("Database not configured")

# Export db, supabase, Base, and get_db
__all__ = ['db', 'supabase', 'Base', 'get_db']