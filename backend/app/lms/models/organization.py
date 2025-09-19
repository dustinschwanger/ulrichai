"""
Organization model for multi-tenant LMS
"""

from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Organization(Base):
    """
    Organization model for multi-tenant architecture.
    Each organization represents a separate tenant with their own courses, users, and settings.
    """
    __tablename__ = "lms_organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Branding
    logo_url = Column(Text, nullable=True)
    primary_color = Column(String(7), default="#0066CC")
    secondary_color = Column(String(7), default="#FF6600")
    custom_domain = Column(String(255), nullable=True, unique=True)

    # Settings
    settings = Column(JSON, default={}, nullable=False)
    features = Column(JSON, default={
        "ai_chat": True,
        "ai_course_builder": True,
        "discussions": True,
        "reflections": True,
        "white_labeling": False
    }, nullable=False)

    # Subscription
    subscription_tier = Column(String(50), default="basic")  # basic, professional, enterprise
    max_users = Column(Integer, default=100)
    max_courses = Column(Integer, default=10)
    storage_limit_gb = Column(Integer, default=10)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    def __repr__(self):
        return f"<Organization {self.name} ({self.slug})>"