"""
Course models for the LMS
"""

from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Course(Base):
    """
    Main course model. Courses belong to organizations and can have multiple versions.
    """
    __tablename__ = "lms_courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Organization association
    organization_id = Column(UUID(as_uuid=True), ForeignKey("lms_organizations.id"), nullable=False, index=True)

    # Basic Information
    title = Column(String(500), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)

    # Instructor
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False)

    # Course Details
    duration_hours = Column(Numeric(5, 2), nullable=True)
    difficulty_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)

    # Prerequisites and Tags
    prerequisites = Column(ARRAY(UUID(as_uuid=True)), default=[], nullable=False)  # Array of course IDs
    tags = Column(ARRAY(Text), default=[], nullable=False)

    # AI Enhancement
    is_ai_enhanced = Column(Boolean, default=False)
    ai_features = Column(JSON, default={
        "ai_chat": True,
        "ai_summaries": False,
        "ai_quiz_generation": False,
        "ai_personalization": False
    }, nullable=False)

    # Publishing
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Settings
    settings = Column(JSON, default={}, nullable=False)
    enrollment_type = Column(String(50), default="open")  # open, approval_required, invitation_only

    # Pricing (for future use)
    price = Column(Numeric(10, 2), default=0.00)
    currency = Column(String(3), default="USD")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    organization = relationship("Organization", backref="courses")
    instructor = relationship("LMSUser", backref="courses_taught", foreign_keys=[instructor_id])
    versions = relationship("CourseVersion", back_populates="course", order_by="CourseVersion.version_number.desc()")

    def __repr__(self):
        return f"<Course {self.title} ({self.slug})>"


class CourseVersion(Base):
    """
    Course versions allow tracking changes and A/B testing.
    Each version contains the actual course content structure.
    """
    __tablename__ = "lms_course_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent course
    course_id = Column(UUID(as_uuid=True), ForeignKey("lms_courses.id"), nullable=False, index=True)

    # Version Information
    version_number = Column(String(20), nullable=False)  # e.g., "1.0", "2.1", "draft"
    version_name = Column(String(255), nullable=True)  # e.g., "Summer 2025 Edition"

    # Content (can override course-level fields)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Version Details
    change_notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)  # Currently active version
    is_draft = Column(Boolean, default=True)    # Draft vs. published version

    # AI Generation Tracking
    is_ai_generated = Column(Boolean, default=False)
    ai_generation_data = Column(JSON, default={}, nullable=True)

    # Creator
    created_by = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="versions")
    creator = relationship("LMSUser", backref="course_versions_created")
    modules = relationship("Module", back_populates="course_version", order_by="Module.sequence_order")

    def __repr__(self):
        return f"<CourseVersion {self.course_id} v{self.version_number}>"