"""
Authentication service for the LMS.
Handles user registration, login, and role-based access control.
"""

from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import os
from dotenv import load_dotenv

from app.lms.models.user import LMSUser, UserRole
from app.lms.models.organization import Organization
from app.core.database import get_db

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/lms/auth/login")


class AuthService:
    """Service for managing LMS user authentication and authorization."""

    def __init__(self, db: Session):
        self.db = db

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def register_user(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        organization_id: UUID,
        role: UserRole = UserRole.STUDENT,
        department: Optional[str] = None,
        job_title: Optional[str] = None
    ) -> LMSUser:
        """
        Register a new user in the LMS.

        Args:
            email: User email address
            password: Plain text password
            first_name: User's first name
            last_name: User's last name
            organization_id: Organization UUID
            role: User role (default: STUDENT)
            department: Optional department
            job_title: Optional job title

        Returns:
            Created user object

        Raises:
            HTTPException: If email already exists or organization not found
        """
        # Check if organization exists
        org = self.db.query(Organization).filter(Organization.id == organization_id).first()
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found"
            )

        # Check if email already exists
        existing_user = self.db.query(LMSUser).filter(LMSUser.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )

        # Check organization user limits
        user_count = self.db.query(LMSUser).filter(
            LMSUser.organization_id == organization_id
        ).count()

        if org.max_users and user_count >= org.max_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization has reached maximum user limit"
            )

        # Create new user
        try:
            user = LMSUser(
                email=email,
                password_hash=self.hash_password(password),
                first_name=first_name,
                last_name=last_name,
                organization_id=organization_id,
                role=role,
                department=department,
                job_title=job_title,
                is_active=True,
                email_verified=False  # Require email verification
            )

            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            return user

        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user and return tokens.

        Args:
            email: User email
            password: Plain text password

        Returns:
            Dictionary with access token, refresh token, and user info

        Raises:
            HTTPException: If credentials are invalid
        """
        # Find user by email
        user = self.db.query(LMSUser).filter(LMSUser.email == email).first()

        if not user or not self.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()

        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "org_id": str(user.organization_id),
            "role": user.role.value
        }

        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "organization_id": str(user.organization_id)
            }
        }

    def get_current_user(self, token: str, db: Session) -> LMSUser:
        """
        Get current user from JWT token.

        Args:
            token: JWT token
            db: Database session

        Returns:
            Current user object

        Raises:
            HTTPException: If token is invalid or user not found
        """
        payload = self.decode_token(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        user = db.query(LMSUser).filter(LMSUser.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user

    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """
        Create a new access token from a refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            New access token

        Raises:
            HTTPException: If refresh token is invalid
        """
        payload = self.decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Create new access token
        token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "org_id": payload.get("org_id"),
            "role": payload.get("role")
        }

        new_access_token = self.create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    def check_permission(
        self,
        user: LMSUser,
        required_role: UserRole,
        organization_id: Optional[UUID] = None
    ) -> bool:
        """
        Check if user has required role and belongs to organization.

        Args:
            user: User object
            required_role: Minimum required role
            organization_id: Optional organization to check

        Returns:
            True if user has permission, False otherwise
        """
        # Check organization membership if specified
        if organization_id and user.organization_id != organization_id:
            return False

        # Check role hierarchy
        role_hierarchy = {
            UserRole.STUDENT: 1,
            UserRole.INSTRUCTOR: 2,
            UserRole.ADMIN: 3,
            UserRole.SUPER_ADMIN: 4
        }

        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 999)

        return user_level >= required_level

    def update_password(self, user_id: UUID, old_password: str, new_password: str) -> bool:
        """
        Update user password.

        Args:
            user_id: User UUID
            old_password: Current password
            new_password: New password

        Returns:
            True if password updated successfully

        Raises:
            HTTPException: If old password is incorrect or user not found
        """
        user = self.db.query(LMSUser).filter(LMSUser.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not self.verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

        user.password_hash = self.hash_password(new_password)
        self.db.commit()

        return True


# Dependency to get current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> LMSUser:
    """FastAPI dependency to get current authenticated user."""
    auth_service = AuthService(db)
    return auth_service.get_current_user(token, db)


# Dependency to require specific role
def require_role(roles: list[str]):
    """Factory function to create role-checking dependencies."""

    async def role_checker(
        current_user: LMSUser = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> LMSUser:
        # Normalize user role to uppercase for comparison
        user_role = current_user.role.upper() if isinstance(current_user.role, str) else current_user.role.value

        # Check if user's role is in the allowed roles
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {', '.join(roles)}"
            )

        return current_user

    return role_checker


# Pre-defined role dependencies
require_instructor = require_role(UserRole.INSTRUCTOR)
require_admin = require_role(UserRole.ADMIN)
require_super_admin = require_role(UserRole.SUPER_ADMIN)