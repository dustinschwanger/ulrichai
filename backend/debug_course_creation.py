#!/usr/bin/env python3
"""Debug course creation directly"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import uuid4

# Load environment variables
load_dotenv()

# Import models
from app.lms.models import Organization, LMSUser, Course, CourseVersion

def debug_course_creation():
    """Debug course creation"""

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        print("=" * 60)
        print("🔍 DEBUG: Course Creation")
        print("=" * 60)

        # Get instructor
        instructor = db.query(LMSUser).filter(
            LMSUser.email == "instructor@test.com"
        ).first()

        if not instructor:
            print("❌ Instructor not found")
            return

        print(f"✅ Found instructor: {instructor.email}")
        print(f"   ID: {instructor.id}")
        print(f"   Org ID: {instructor.organization_id}")

        # Check course table fields
        test_slug = f"test-course-{uuid4().hex[:6]}"

        # Create minimal course
        print("\n📚 Creating minimal course...")
        course = Course(
            organization_id=instructor.organization_id,
            title="Test Course",
            slug=test_slug,
            instructor_id=instructor.id,
            is_published=False
        )

        # Check default values
        print(f"   Prerequisites (default): {course.prerequisites}")
        print(f"   Tags (default): {course.tags}")

        db.add(course)
        db.flush()  # Get ID without committing

        print(f"✅ Course created with ID: {course.id}")

        # Create version
        print("\n📦 Creating course version...")
        version = CourseVersion(
            course_id=course.id,
            version_number="1.0",
            title=course.title,
            is_active=True,
            created_by=instructor.id
        )
        db.add(version)

        # Commit everything
        db.commit()
        print("✅ Successfully committed to database")

        # Try to fetch it back
        fetched = db.query(Course).filter(Course.id == course.id).first()
        if fetched:
            print(f"\n✅ Course fetched back successfully")
            print(f"   Title: {fetched.title}")
            print(f"   Slug: {fetched.slug}")
            print(f"   Prerequisites type: {type(fetched.prerequisites)}")
            print(f"   Prerequisites value: {fetched.prerequisites}")
            print(f"   Tags type: {type(fetched.tags)}")
            print(f"   Tags value: {fetched.tags}")

        # Clean up
        db.delete(version)
        db.delete(course)
        db.commit()
        print("\n🧹 Test data cleaned up")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    debug_course_creation()