#!/usr/bin/env python3
"""Create test instructor for Course Builder testing"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables
load_dotenv()

# Import models
from app.lms.models import Organization, LMSUser
from app.lms.services.auth_service import AuthService

def setup_test_instructor():
    """Create test organization and instructor"""

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    try:
        # Check if instructor already exists
        existing = db_session.query(LMSUser).filter(
            LMSUser.email == "instructor@test.com"
        ).first()

        if existing:
            print(f"✅ Instructor already exists: {existing.email}")
            return

        # Create organization
        org = db_session.query(Organization).filter(
            Organization.slug == "test-org"
        ).first()

        if not org:
            org = Organization(
                name="Test Organization",
                slug="test-org"
            )
            db_session.add(org)
            db_session.flush()
            print(f"✅ Created organization: {org.name}")
        else:
            print(f"✅ Using existing organization: {org.name}")

        # Create instructor
        auth_service = AuthService(db_session)
        instructor = auth_service.register_user(
            email="instructor@test.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Instructor",
            organization_id=org.id,
            role="INSTRUCTOR"
        )

        db_session.commit()
        print(f"✅ Created instructor: {instructor.email}")
        print(f"   Password: TestPassword123!")
        print(f"   Role: {instructor.role}")

    except Exception as e:
        print(f"❌ Error: {e}")
        db_session.rollback()
        raise
    finally:
        db_session.close()

if __name__ == "__main__":
    setup_test_instructor()