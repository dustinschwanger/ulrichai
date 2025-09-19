"""
User model for LMS with role-based access control
"""

from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles for the LMS"""
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class LMSUser(Base):
    """
    Extended user model for LMS functionality.
    Includes organization association, roles, and learning profile.
    """
    __tablename__ = "lms_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Organization association (multi-tenancy)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("lms_organizations.id"), nullable=False, index=True)

    # Basic Information
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)  # Store hashed password
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    avatar_url = Column(Text, nullable=True)

    # Role and Permissions
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    permissions = Column(ARRAY(String), default=[], nullable=False)

    # Professional Profile (for personalization)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    industry = Column(String(255), nullable=True)
    company_size = Column(String(50), nullable=True)  # "1-50", "51-200", "201-500", etc.
    years_experience = Column(Integer, nullable=True)

    # Learning Profile
    learning_goals = Column(ARRAY(Text), default=[], nullable=False)
    preferred_learning_style = Column(String(50), nullable=True)  # "visual", "auditory", "reading", "kinesthetic"
    time_zone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")

    # Profile Data (flexible storage for additional info)
    profile_data = Column(JSON, default={}, nullable=False)
    onboarding_completed = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False)

    # Timestamps
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships (to be defined as we create other models)
    organization = relationship("Organization", backref="users", foreign_keys=[organization_id])

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission"""
        return permission in self.permissions or self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    def is_instructor_or_above(self) -> bool:
        """Check if user is instructor, admin, or super admin"""
        return self.role in [UserRole.INSTRUCTOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]

    def is_admin_or_above(self) -> bool:
        """Check if user is admin or super admin"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    def __repr__(self):
        return f"<LMSUser {self.email} ({self.role.value})>"