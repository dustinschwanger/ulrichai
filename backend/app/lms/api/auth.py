"""
API endpoints for authentication in the LMS.
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, EmailStr

from app.core.database import get_db
from app.lms.services.auth_service import AuthService, get_current_user
from app.lms.models.user import LMSUser, UserRole


router = APIRouter(
    prefix="/api/lms/auth",
    tags=["LMS Authentication"]
)


# Pydantic models for request/response
class UserRegister(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    organization_id: UUID
    role: Optional[UserRole] = UserRole.STUDENT
    department: Optional[str] = Field(None, max_length=100)
    job_title: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Request model for password change."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(BaseModel):
    """Response model for user data."""
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: UserRole
    organization_id: UUID
    department: Optional[str]
    job_title: Optional[str]
    is_active: bool
    email_verified: bool

    class Config:
        from_attributes = True


# API Endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Creates a new user account in the specified organization.
    Default role is STUDENT unless specified otherwise.
    """
    service = AuthService(db)
    user = service.register_user(
        email=user_data.email,
        password=user_data.password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        organization_id=user_data.organization_id,
        role=user_data.role,
        department=user_data.department,
        job_title=user_data.job_title
    )
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login a user.

    Authenticates a user and returns access and refresh tokens.
    Username field accepts email address.
    """
    service = AuthService(db)
    result = service.login(
        email=form_data.username,  # OAuth2 form uses 'username' field for email
        password=form_data.password
    )
    return result


@router.post("/login-json", response_model=TokenResponse)
def login_json(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login a user (JSON endpoint).

    Alternative login endpoint that accepts JSON instead of form data.
    """
    service = AuthService(db)
    result = service.login(
        email=login_data.email,
        password=login_data.password
    )
    return result


@router.post("/refresh", response_model=dict)
def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token.

    Creates a new access token using a valid refresh token.
    """
    service = AuthService(db)
    result = service.refresh_access_token(token_data.refresh_token)
    return result


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: LMSUser = Depends(get_current_user)
):
    """
    Get current user profile.

    Returns the profile of the authenticated user.
    """
    return current_user


@router.put("/me/password")
def change_password(
    password_data: PasswordChange,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.

    Updates the password for the current authenticated user.
    """
    service = AuthService(db)
    success = service.update_password(
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )

    return {
        "success": success,
        "message": "Password updated successfully"
    }


@router.get("/verify")
def verify_token(
    current_user: LMSUser = Depends(get_current_user)
):
    """
    Verify authentication token.

    Validates the current token and returns user information.
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value,
        "organization_id": str(current_user.organization_id)
    }


@router.post("/logout")
def logout():
    """
    Logout user.

    This is primarily for client-side token removal.
    The server doesn't maintain session state for JWT auth.
    """
    return {
        "success": True,
        "message": "Logged out successfully. Please remove tokens from client storage."
    }