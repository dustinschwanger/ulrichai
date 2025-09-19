"""
Service layer for organization management in the LMS.
Handles multi-tenant operations and organization-level settings.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.lms.models.organization import Organization
from app.core.database import get_db


class OrganizationService:
    """Service for managing LMS organizations with multi-tenant support."""

    def __init__(self, db: Session):
        self.db = db

    def create_organization(
        self,
        name: str,
        slug: str,
        owner_email: str,
        settings: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, bool]] = None
    ) -> Organization:
        """
        Create a new organization.

        Args:
            name: Organization display name
            slug: Unique URL-safe identifier
            owner_email: Email of the organization owner
            settings: Optional organization settings
            features: Optional feature flags

        Returns:
            Created organization

        Raises:
            HTTPException: If slug already exists
        """
        try:
            # Create organization
            organization = Organization(
                name=name,
                slug=slug.lower(),
                settings=settings or {},
                features=features or {
                    "ai_chat": True,
                    "ai_course_builder": True,
                    "discussions": True,
                    "reflections": True,
                    "white_labeling": False
                }
            )

            self.db.add(organization)
            self.db.commit()
            self.db.refresh(organization)

            return organization

        except IntegrityError as e:
            self.db.rollback()
            if "slug" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Organization with slug '{slug}' already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create organization"
            )

    def get_organization(self, org_id: Optional[UUID] = None, slug: Optional[str] = None) -> Organization:
        """
        Get organization by ID or slug.

        Args:
            org_id: Organization UUID
            slug: Organization slug

        Returns:
            Organization if found

        Raises:
            HTTPException: If organization not found
        """
        query = self.db.query(Organization)

        if org_id:
            org = query.filter(Organization.id == org_id).first()
        elif slug:
            org = query.filter(Organization.slug == slug.lower()).first()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either org_id or slug must be provided"
            )

        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        if not org.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization is inactive"
            )

        return org

    def list_organizations(
        self,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = True
    ) -> List[Organization]:
        """
        List all organizations with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            only_active: Filter only active organizations

        Returns:
            List of organizations
        """
        query = self.db.query(Organization)

        if only_active:
            query = query.filter(Organization.is_active == True)

        return query.offset(skip).limit(limit).all()

    def update_organization(
        self,
        org_id: UUID,
        name: Optional[str] = None,
        settings: Optional[Dict[str, Any]] = None,
        features: Optional[Dict[str, bool]] = None,
        logo_url: Optional[str] = None,
        primary_color: Optional[str] = None,
        secondary_color: Optional[str] = None,
        custom_domain: Optional[str] = None
    ) -> Organization:
        """
        Update organization details.

        Args:
            org_id: Organization UUID
            name: New organization name
            settings: Updated settings
            features: Updated features
            logo_url: Logo URL for branding
            primary_color: Primary brand color
            secondary_color: Secondary brand color
            custom_domain: Custom domain for white-labeling

        Returns:
            Updated organization

        Raises:
            HTTPException: If organization not found
        """
        org = self.get_organization(org_id=org_id)

        if name:
            org.name = name
        if settings is not None:
            org.settings = {**org.settings, **settings}
        if features is not None:
            org.features = {**org.features, **features}
        if logo_url is not None:
            org.logo_url = logo_url
        if primary_color:
            org.primary_color = primary_color
        if secondary_color:
            org.secondary_color = secondary_color
        if custom_domain is not None:
            org.custom_domain = custom_domain

        try:
            self.db.commit()
            self.db.refresh(org)
            return org
        except IntegrityError as e:
            self.db.rollback()
            if "custom_domain" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Custom domain '{custom_domain}' already in use"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update organization"
            )

    def update_subscription(
        self,
        org_id: UUID,
        tier: str,
        max_users: Optional[int] = None,
        max_courses: Optional[int] = None,
        storage_limit_gb: Optional[int] = None
    ) -> Organization:
        """
        Update organization subscription and limits.

        Args:
            org_id: Organization UUID
            tier: Subscription tier (basic, pro, enterprise)
            max_users: Maximum allowed users
            max_courses: Maximum allowed courses
            storage_limit_gb: Storage limit in GB

        Returns:
            Updated organization
        """
        org = self.get_organization(org_id=org_id)

        org.subscription_tier = tier

        # Set default limits based on tier if not provided
        if tier == "basic" and not max_users:
            max_users = 100
            max_courses = 10
            storage_limit_gb = 10
        elif tier == "pro" and not max_users:
            max_users = 1000
            max_courses = 100
            storage_limit_gb = 100
        elif tier == "enterprise" and not max_users:
            max_users = None  # Unlimited
            max_courses = None
            storage_limit_gb = 1000

        if max_users is not None:
            org.max_users = max_users
        if max_courses is not None:
            org.max_courses = max_courses
        if storage_limit_gb is not None:
            org.storage_limit_gb = storage_limit_gb

        self.db.commit()
        self.db.refresh(org)
        return org

    def check_limits(self, org_id: UUID, resource_type: str) -> bool:
        """
        Check if organization has reached its resource limits.

        Args:
            org_id: Organization UUID
            resource_type: Type of resource (users, courses, storage)

        Returns:
            True if within limits, False otherwise
        """
        org = self.get_organization(org_id=org_id)

        if resource_type == "users":
            if org.max_users is None:
                return True
            # Count users in organization
            from app.lms.models.user import LMSUser
            user_count = self.db.query(LMSUser).filter(
                LMSUser.organization_id == org_id
            ).count()
            return user_count < org.max_users

        elif resource_type == "courses":
            if org.max_courses is None:
                return True
            # Count courses in organization
            from app.lms.models.course import Course
            course_count = self.db.query(Course).filter(
                Course.organization_id == org_id
            ).count()
            return course_count < org.max_courses

        elif resource_type == "storage":
            # This would need integration with file storage service
            # For now, always return True
            return True

        return False

    def delete_organization(self, org_id: UUID, soft_delete: bool = True) -> bool:
        """
        Delete or deactivate an organization.

        Args:
            org_id: Organization UUID
            soft_delete: If True, only deactivate; if False, permanently delete

        Returns:
            True if successful
        """
        org = self.get_organization(org_id=org_id)

        if soft_delete:
            # Soft delete - just deactivate
            org.is_active = False
            self.db.commit()
        else:
            # Hard delete - remove from database
            # This would cascade to all related data
            self.db.delete(org)
            self.db.commit()

        return True