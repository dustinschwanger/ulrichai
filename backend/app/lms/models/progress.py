"""
Progress tracking models for student learning journey.
Simple and clear progress indicators for better UX.
"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class LessonProgress(Base):
    """
    Tracks student progress through individual lessons.
    One record per user per lesson.
    """
    __tablename__ = "lms_lesson_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lms_lessons.id"), nullable=False, index=True)

    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("lms_enrollments.id"), nullable=False, index=True)

    status = Column(String(50), default="not_started", nullable=False)

    progress_percentage = Column(Integer, default=0)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    time_spent_seconds = Column(Integer, default=0)

    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("LMSUser", backref="lesson_progress")
    lesson = relationship("Lesson", backref="student_progress")
    enrollment = relationship("Enrollment", backref="lesson_progress_records")

    def __repr__(self):
        return f"<LessonProgress user={self.user_id} lesson={self.lesson_id} status={self.status}>"


class ContentProgress(Base):
    """
    Tracks progress on individual content items within lessons.
    For videos: watch percentage, last position
    For documents: pages viewed
    For quizzes: completion status
    """
    __tablename__ = "lms_content_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("lms_content_items.id"), nullable=False, index=True)
    lesson_progress_id = Column(UUID(as_uuid=True), ForeignKey("lms_lesson_progress.id"), nullable=False)

    progress_percentage = Column(Integer, default=0)

    status = Column(String(50), default="not_started")

    last_position = Column(JSON, nullable=True)

    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("LMSUser", backref="content_progress")
    content_item = relationship("ContentItem", backref="user_progress")
    lesson_progress = relationship("LessonProgress", backref="content_items_progress")

    def __repr__(self):
        return f"<ContentProgress content={self.content_item_id} progress={self.progress_percentage}%>"


class ModuleProgress(Base):
    """
    Tracks completion of entire modules.
    Automatically calculated based on lesson completion.
    """
    __tablename__ = "lms_module_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("lms_modules.id"), nullable=False, index=True)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("lms_enrollments.id"), nullable=False, index=True)

    completed_lessons = Column(Integer, default=0)
    total_lessons = Column(Integer, nullable=False)

    progress_percentage = Column(Integer, default=0)

    is_complete = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    user = relationship("LMSUser", backref="module_progress")
    module = relationship("Module", backref="student_progress")
    enrollment = relationship("Enrollment", backref="module_progress_records")

    def __repr__(self):
        return f"<ModuleProgress module={self.module_id} {self.completed_lessons}/{self.total_lessons}>"