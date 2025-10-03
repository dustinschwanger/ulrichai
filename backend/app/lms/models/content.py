"""
Content models for courses (modules, lessons, content items)
"""

from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Section(Base):
    """
    Sections are the top-level organization within a course version (e.g., Week 1, Week 2).
    They contain modules and help organize the course into major segments.
    """
    __tablename__ = "lms_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent course version
    course_version_id = Column(UUID(as_uuid=True), ForeignKey("lms_course_versions.id"), nullable=False, index=True)

    # Section Information
    title = Column(String(500), nullable=False)  # e.g., "Week 1 | Developing an Outside-In Mindset"
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)

    # Section Settings
    is_optional = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    course_version = relationship("CourseVersion", back_populates="sections")
    modules = relationship("Module", back_populates="section", order_by="Module.sequence_order")

    def __repr__(self):
        return f"<Section {self.title} (order: {self.sequence_order})>"


class Module(Base):
    """
    Modules are the main sections of a course version.
    They contain lessons and define the learning structure.
    """
    __tablename__ = "lms_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent section
    section_id = Column(UUID(as_uuid=True), ForeignKey("lms_sections.id"), nullable=False, index=True)

    # Keep course_version_id for backward compatibility and direct queries
    course_version_id = Column(UUID(as_uuid=True), ForeignKey("lms_course_versions.id"), nullable=False, index=True)

    # Module Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)

    # Learning Details
    learning_objectives = Column(ARRAY(Text), default=[], nullable=False)
    estimated_duration_minutes = Column(Integer, nullable=True)

    # Module Settings
    is_optional = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    unlock_requirements = Column(JSON, default={}, nullable=True)  # e.g., {"previous_module_complete": true}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    section = relationship("Section", back_populates="modules")
    course_version = relationship("CourseVersion", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", order_by="Lesson.sequence_order")

    def __repr__(self):
        return f"<Module {self.title} (order: {self.sequence_order})>"


class Lesson(Base):
    """
    Lessons are the individual learning units within a module.
    They contain the actual content items.
    """
    __tablename__ = "lms_lessons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent module
    module_id = Column(UUID(as_uuid=True), ForeignKey("lms_modules.id"), nullable=False, index=True)

    # Lesson Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)

    # Lesson Type
    lesson_type = Column(String(50), default="standard")  # standard, video, reading, interactive, assessment

    # Duration and Requirements
    estimated_duration_minutes = Column(Integer, nullable=True)
    is_required = Column(Boolean, default=True)
    passing_criteria = Column(JSON, default={}, nullable=True)  # e.g., {"min_score": 80, "min_time_spent": 300}

    # AI Enhancement
    ai_enhanced_content = Column(JSON, default={}, nullable=True)  # AI-generated summaries, key points, etc.

    # Content Data (for media files, quiz questions, etc.)
    content_data = Column(JSON, default={}, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    module = relationship("Module", back_populates="lessons")
    content_items = relationship("ContentItem", back_populates="lesson", order_by="ContentItem.sequence_order")
    media_files = relationship("LessonMedia", back_populates="lesson", order_by="LessonMedia.sequence_order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lesson {self.title} (type: {self.lesson_type})>"


class ContentItem(Base):
    """
    Content items are the actual learning materials within a lesson.
    They can be videos, documents, quizzes, discussions, reflections, polls, etc.
    """
    __tablename__ = "lms_content_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent lesson
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lms_lessons.id"), nullable=False, index=True)

    # Content Information
    content_type = Column(String(50), nullable=False)  # video, document, quiz, discussion, reflection, poll, activity
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    sequence_order = Column(Integer, nullable=False)

    # Content Data
    content_data = Column(JSON, nullable=False, default={})
    # For different content types:
    # - video: {"url": "...", "duration": 300, "transcript": "..."}
    # - document: {"url": "...", "pages": 10, "file_type": "pdf"}
    # - quiz: {"quiz_id": "uuid"}
    # - discussion: {"discussion_id": "uuid"}
    # - reflection: {"reflection_id": "uuid"}
    # - poll: {"poll_id": "uuid"}

    # Requirements
    is_required = Column(Boolean, default=True)
    points_possible = Column(Numeric(5, 2), nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Completion Criteria
    completion_criteria = Column(JSON, default={}, nullable=True)
    # e.g., {"min_view_percentage": 80, "require_submission": true}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    lesson = relationship("Lesson", back_populates="content_items")

    def __repr__(self):
        return f"<ContentItem {self.content_type} ({self.title})>"


class Cohort(Base):
    """
    Cohorts group students together for a specific course version.
    They define pacing, start/end dates, and group settings.
    """
    __tablename__ = "lms_cohorts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Course association
    course_version_id = Column(UUID(as_uuid=True), ForeignKey("lms_course_versions.id"), nullable=False, index=True)

    # Cohort Information
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False)  # For student enrollment

    # Schedule
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    enrollment_deadline = Column(DateTime(timezone=True), nullable=True)

    # Pacing
    pacing_type = Column(String(50), default="self_paced")  # self_paced, instructor_paced, cohort_paced

    # Capacity
    max_students = Column(Integer, nullable=True)
    is_waitlist_enabled = Column(Boolean, default=False)

    # Settings
    settings = Column(JSON, default={}, nullable=False)
    discussion_visibility = Column(String(50), default="cohort")  # cohort, course, private

    # Status
    is_active = Column(Boolean, default=True)
    is_enrollable = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    course_version = relationship("CourseVersion", backref="cohorts")
    enrollments = relationship("Enrollment", back_populates="cohort")

    def __repr__(self):
        return f"<Cohort {self.name} ({self.code})>"


class Enrollment(Base):
    """
    Enrollments link users to cohorts and track their progress.
    """
    __tablename__ = "lms_enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User and Cohort
    user_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)
    cohort_id = Column(UUID(as_uuid=True), ForeignKey("lms_cohorts.id"), nullable=False, index=True)

    # Enrollment Status
    enrollment_status = Column(String(50), default="active")  # active, completed, dropped, paused
    enrollment_type = Column(String(50), default="student")  # student, auditor, teaching_assistant

    # Progress
    progress_percentage = Column(Numeric(5, 2), default=0.0)
    completed_modules = Column(Integer, default=0)
    completed_lessons = Column(Integer, default=0)

    # Dates
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)

    # Grade
    current_grade = Column(Numeric(5, 2), nullable=True)
    final_grade = Column(Numeric(5, 2), nullable=True)

    # Certificate
    certificate_issued = Column(Boolean, default=False)
    certificate_issued_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user = relationship("LMSUser", backref="enrollments")
    cohort = relationship("Cohort", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment {self.user_id} in {self.cohort_id}>"