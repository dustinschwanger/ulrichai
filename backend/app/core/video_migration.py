# backend/app/core/video_migration.py

from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class VideoMigration:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def add_video_support_to_documents_table(self):
        """Add video-specific columns to admin_documents table"""
        try:
            logger.info("Adding video support columns to admin_documents table...")
            
            # Check if columns already exist
            columns_to_add = [
                ('content_type', 'VARCHAR(50) DEFAULT \'document\''),
                ('duration', 'FLOAT DEFAULT NULL'),
                ('video_width', 'INTEGER DEFAULT NULL'),
                ('video_height', 'INTEGER DEFAULT NULL'),
                ('transcript_language', 'VARCHAR(10) DEFAULT NULL'),
                ('has_audio', 'BOOLEAN DEFAULT NULL'),
                ('video_format', 'VARCHAR(50) DEFAULT NULL'),
                ('thumbnail_url', 'TEXT DEFAULT NULL')
            ]
            
            with self.db.connect() as conn:
                # Check which columns already exist
                existing_columns = self._get_existing_columns(conn, 'admin_documents')
                
                for column_name, column_def in columns_to_add:
                    if column_name not in existing_columns:
                        logger.info(f"Adding column: {column_name}")
                        alter_query = f"ALTER TABLE admin_documents ADD COLUMN {column_name} {column_def}"
                        conn.execute(text(alter_query))
                    else:
                        logger.info(f"Column {column_name} already exists, skipping")
                
                conn.commit()
                logger.info("Successfully added video support columns")
                
        except Exception as e:
            logger.error(f"Error adding video support columns: {e}")
            raise
    
    def create_video_chunks_table(self):
        """Create table for storing video transcript chunks with timing info"""
        try:
            logger.info("Creating video_chunks table...")
            
            create_table_query = """
            CREATE TABLE IF NOT EXISTS video_chunks (
                id SERIAL PRIMARY KEY,
                document_id UUID REFERENCES admin_documents(id) ON DELETE CASCADE,
                chunk_id VARCHAR(255) UNIQUE NOT NULL,
                content TEXT NOT NULL,
                start_time FLOAT NOT NULL,
                end_time FLOAT NOT NULL,
                segment_ids INTEGER[] DEFAULT '{}',
                timestamp_display VARCHAR(20),
                duration_display VARCHAR(20),
                avg_confidence FLOAT DEFAULT 0.5,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            create_indexes_queries = [
                "CREATE INDEX IF NOT EXISTS idx_video_chunks_time ON video_chunks (document_id, start_time, end_time)",
                "CREATE INDEX IF NOT EXISTS idx_video_chunks_document ON video_chunks (document_id)"
            ]
            
            with self.db.connect() as conn:
                conn.execute(text(create_table_query))
                for index_query in create_indexes_queries:
                    conn.execute(text(index_query))
                conn.commit()
                logger.info("Successfully created video_chunks table with indexes")
                
        except Exception as e:
            logger.error(f"Error creating video_chunks table: {e}")
            raise
    
    def create_video_segments_table(self):
        """Create table for storing individual transcript segments"""
        try:
            logger.info("Creating video_segments table...")
            
            create_table_query = """
            CREATE TABLE IF NOT EXISTS video_segments (
                id SERIAL PRIMARY KEY,
                document_id UUID REFERENCES admin_documents(id) ON DELETE CASCADE,
                segment_id INTEGER NOT NULL,
                start_time FLOAT NOT NULL,
                end_time FLOAT NOT NULL,
                text TEXT NOT NULL,
                tokens TEXT[] DEFAULT '{}',
                temperature FLOAT DEFAULT 0.0,
                avg_logprob FLOAT DEFAULT 0.0,
                compression_ratio FLOAT DEFAULT 0.0,
                no_speech_prob FLOAT DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            create_indexes_queries = [
                "CREATE INDEX IF NOT EXISTS idx_video_segments_doc_time ON video_segments (document_id, start_time)",
                "CREATE INDEX IF NOT EXISTS idx_video_segments_segment ON video_segments (document_id, segment_id)"
            ]
            
            with self.db.connect() as conn:
                conn.execute(text(create_table_query))
                for index_query in create_indexes_queries:
                    conn.execute(text(index_query))
                conn.commit()
                logger.info("Successfully created video_segments table with indexes")
                
        except Exception as e:
            logger.error(f"Error creating video_segments table: {e}")
            raise
    
    def run_all_migrations(self):
        """Run all video-related database migrations"""
        try:
            logger.info("Running all video database migrations...")
            
            self.add_video_support_to_documents_table()
            self.create_video_chunks_table()
            self.create_video_segments_table()
            
            logger.info("All video migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Error running video migrations: {e}")
            raise
    
    def _get_existing_columns(self, conn, table_name):
        """Get list of existing columns in a table"""
        try:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = :table_name
            """), {'table_name': table_name})
            
            return [row[0] for row in result.fetchall()]
            
        except Exception as e:
            logger.error(f"Error getting existing columns: {e}")
            return []

def migrate_database_for_video_support():
    """Convenience function to run video migrations"""
    try:
        from .database import db
        
        if not db.engine:
            logger.error("Database engine not available")
            return False
            
        migration = VideoMigration(db.engine)
        migration.run_all_migrations()
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        return False