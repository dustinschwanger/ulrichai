"""
Create a super admin user for the LMS
"""
from app.core.database import db as database, get_db
from app.lms.models import LMSUser, UserRole, Organization
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_superadmin():
    """Create a super admin user"""
    session = database.get_session()
    if not session:
        print("Error: Database not configured")
        return

    try:
        # Check if organization exists, create if not
        org = session.query(Organization).first()
        if not org:
            org = Organization(
                id=uuid.uuid4(),
                name="Ulrich AI",
                domain="ulrichai.com"
            )
            session.add(org)
            session.commit()
            session.refresh(org)
            print(f"Created organization: {org.name}")

        # Check if user already exists
        email = "admin@ulrichai.com"
        existing_user = session.query(LMSUser).filter(LMSUser.email == email).first()

        if existing_user:
            print(f"User {email} already exists. Updating password and role...")
            existing_user.hashed_password = pwd_context.hash("admin123")
            existing_user.role = UserRole.SUPER_ADMIN
            existing_user.is_active = True
            session.commit()
            print(f"Updated user: {email}")
        else:
            # Create new super admin user
            user = LMSUser(
                id=uuid.uuid4(),
                organization_id=org.id,
                email=email,
                hashed_password=pwd_context.hash("admin123"),
                first_name="Super",
                last_name="Admin",
                role=UserRole.SUPER_ADMIN,
                is_active=True
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Created super admin user: {email}")

        print("\nLogin credentials:")
        print(f"Email: {email}")
        print(f"Password: admin123")
        print("\nPlease change the password after first login!")

    except Exception as e:
        print(f"Error creating super admin: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    create_superadmin()
