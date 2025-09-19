"""
API endpoints for organization management in the LMS.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from app.core.database import get_db
from app.lms.services.organization_service import OrganizationService


router = APIRouter(
    prefix="/api/lms/organizations",
    tags=["LMS Organizations"]
)


# Pydantic models for request/response
class OrganizationCreate(BaseModel):
    """Request model for creating an organization."""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern="^[a-z0-9-]+$")
    owner_email: EmailStr
    settings: Optional[dict] = {}
    features: Optional[dict] = None


class OrganizationUpdate(BaseModel):
    """Request model for updating an organization."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    settings: Optional[dict] = None
    features: Optional[dict] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    secondary_color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    custom_domain: Optional[str] = None


class SubscriptionUpdate(BaseModel):
    """Request model for updating subscription."""
    tier: str = Field(..., pattern="^(basic|pro|enterprise)$")
    max_users: Optional[int] = Field(None, ge=1)
    max_courses: Optional[int] = Field(None, ge=1)
    storage_limit_gb: Optional[int] = Field(None, ge=1)


class OrganizationResponse(BaseModel):
    """Response model for organization data."""
    id: UUID
    name: str
    slug: str
    logo_url: Optional[str]
    primary_color: str
    secondary_color: str
    custom_domain: Optional[str]
    settings: dict
    features: dict
    subscription_tier: str
    max_users: Optional[int]
    max_courses: Optional[int]
    storage_limit_gb: Optional[int]
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True


# API Endpoints
@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new organization.

    This endpoint creates a new organization with the specified settings.
    The slug must be unique across all organizations.
    """
    service = OrganizationService(db)
    organization = service.create_organization(
        name=org_data.name,
        slug=org_data.slug,
        owner_email=org_data.owner_email,
        settings=org_data.settings,
        features=org_data.features
    )
    return organization


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(
    org_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get organization by ID.

    Returns the organization details if found and active.
    """
    service = OrganizationService(db)
    return service.get_organization(org_id=org_id)


@router.get("/slug/{slug}", response_model=OrganizationResponse)
def get_organization_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    Get organization by slug.

    Returns the organization details if found and active.
    """
    service = OrganizationService(db)
    return service.get_organization(slug=slug)


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    skip: int = 0,
    limit: int = 100,
    only_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    List all organizations with pagination.

    Returns a list of organizations, optionally filtered by active status.
    """
    service = OrganizationService(db)
    return service.list_organizations(
        skip=skip,
        limit=limit,
        only_active=only_active
    )


@router.put("/{org_id}", response_model=OrganizationResponse)
def update_organization(
    org_id: UUID,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update organization details.

    Updates the specified fields for an organization.
    All fields are optional.
    """
    service = OrganizationService(db)
    return service.update_organization(
        org_id=org_id,
        name=org_data.name,
        settings=org_data.settings,
        features=org_data.features,
        logo_url=org_data.logo_url,
        primary_color=org_data.primary_color,
        secondary_color=org_data.secondary_color,
        custom_domain=org_data.custom_domain
    )


@router.put("/{org_id}/subscription", response_model=OrganizationResponse)
def update_subscription(
    org_id: UUID,
    subscription_data: SubscriptionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update organization subscription and limits.

    Updates the subscription tier and resource limits for an organization.
    """
    service = OrganizationService(db)
    return service.update_subscription(
        org_id=org_id,
        tier=subscription_data.tier,
        max_users=subscription_data.max_users,
        max_courses=subscription_data.max_courses,
        storage_limit_gb=subscription_data.storage_limit_gb
    )


@router.get("/{org_id}/check-limits/{resource_type}")
def check_resource_limits(
    org_id: UUID,
    resource_type: str,
    db: Session = Depends(get_db)
):
    """
    Check if organization has reached resource limits.

    Resource types: users, courses, storage
    Returns whether the organization is within its limits.
    """
    if resource_type not in ["users", "courses", "storage"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resource type. Must be one of: users, courses, storage"
        )

    service = OrganizationService(db)
    within_limits = service.check_limits(org_id, resource_type)

    return {
        "organization_id": org_id,
        "resource_type": resource_type,
        "within_limits": within_limits
    }


@router.delete("/{org_id}")
def delete_organization(
    org_id: UUID,
    permanent: bool = False,
    db: Session = Depends(get_db)
):
    """
    Delete or deactivate an organization.

    By default, performs a soft delete (deactivation).
    Set permanent=true for hard delete.
    """
    service = OrganizationService(db)
    success = service.delete_organization(
        org_id=org_id,
        soft_delete=not permanent
    )

    return {
        "success": success,
        "message": "Organization deleted successfully" if permanent else "Organization deactivated successfully"
    }