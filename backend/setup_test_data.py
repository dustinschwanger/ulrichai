#!/usr/bin/env python3
"""Setup test data for Quiz API testing"""

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

def setup_test_data():
    """Create test organization and users"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create test organization
        test_id = uuid4().hex[:8]
        org = Organization(
            name=f"Test Organization {test_id}",
            slug=f"test-org-{test_id}"
        )
        session.add(org)
        session.flush()

        print(f"✅ Created organization: {org.name}")
        print(f"   Organization ID: {org.id}")

        # Create instructor user
        auth_service = AuthService(session)
        instructor = auth_service.register_user(
            email=f"instructor_{test_id}@test.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Instructor",
            organization_id=org.id,
            role="INSTRUCTOR"
        )

        print(f"✅ Created instructor: {instructor.email}")
        print(f"   User ID: {instructor.id}")

        # Create student user
        student = auth_service.register_user(
            email=f"student_{test_id}@test.com",
            password="TestPassword123!",
            first_name="Test",
            last_name="Student",
            organization_id=org.id,
            role="STUDENT"
        )

        print(f"✅ Created student: {student.email}")
        print(f"   User ID: {student.id}")

        session.commit()

        print("\n" + "="*50)
        print("TEST CREDENTIALS")
        print("="*50)
        print(f"Organization ID: {org.id}")
        print(f"Instructor Email: instructor_{test_id}@test.com")
        print(f"Student Email: student_{test_id}@test.com")
        print(f"Password: TestPassword123!")
        print("="*50)

        return {
            "org_id": str(org.id),
            "instructor_email": f"instructor_{test_id}@test.com",
            "student_email": f"student_{test_id}@test.com",
            "password": "TestPassword123!"
        }

    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    test_data = setup_test_data()

    # Save to file for the test script to use
    with open("test_credentials.txt", "w") as f:
        f.write(f"ORG_ID={test_data['org_id']}\n")
        f.write(f"INSTRUCTOR_EMAIL={test_data['instructor_email']}\n")
        f.write(f"STUDENT_EMAIL={test_data['student_email']}\n")
        f.write(f"PASSWORD={test_data['password']}\n")