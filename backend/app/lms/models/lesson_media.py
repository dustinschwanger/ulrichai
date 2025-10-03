"""
Lesson Media model - separate table for media files
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class LessonMedia(Base):
    """
    Media files associated with lessons (videos, documents, resources).
    Stored in a separate table to avoid JSON mutation tracking issues.
    """
    __tablename__ = "lms_lesson_media"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lms_lessons.id", ondelete="CASCADE"), nullable=False, index=True)

    # Media information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    media_type = Column(String(50), nullable=False)  # video, document, resource, audio, image
    filename = Column(String(500), nullable=False)

    # RAG metadata fields (for AI indexing and search)
    display_name = Column(String(500), nullable=True)  # User-friendly display name
    document_source = Column(String(200), nullable=True)  # Institute, Dave Ulrich HR Academy, etc.
    document_type = Column(String(100), nullable=True)  # Article, Case Study, Video, etc.
    capability_domain = Column(String(100), nullable=True)  # HR, Talent, Leadership, Organization
    author = Column(String(300), nullable=True)
    publication_date = Column(DateTime(timezone=True), nullable=True)

    # AI/RAG flags
    is_indexed = Column(String(10), default='no')  # no, pending, yes, error
    indexed_at = Column(DateTime(timezone=True), nullable=True)
    transcription_status = Column(String(20), default='pending')  # pending, processing, completed, error
    transcription_data = Column(Text, nullable=True)  # Store transcript JSON

    # Storage information
    storage = Column(String(50), nullable=False)  # supabase, local
    bucket = Column(String(200), nullable=True)  # For Supabase
    path = Column(String(1000), nullable=False)
    url = Column(String(2000), nullable=True)  # For local storage or direct URLs

    # File metadata
    size = Column(Integer, nullable=True)
    content_type = Column(String(100), nullable=True)

    # Sequence
    sequence_order = Column(Integer, default=1)

    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    lesson = relationship("Lesson", back_populates="media_files")

    def __repr__(self):
        return f"<LessonMedia {self.title} ({self.media_type})>"
