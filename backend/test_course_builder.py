#!/usr/bin/env python3
"""Test script for Course Builder API endpoints"""

import requests
import json
from uuid import uuid4
import sys

BASE_URL = "http://localhost:8000"

def login_as_instructor():
    """Login and get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/lms/auth/login",
        data={
            "username": "instructor@test.com",
            "password": "TestPassword123!"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Logged in as instructor")
        return {"Authorization": f"Bearer {token}"}
    else:
        print(f"❌ Login failed: {response.text}")
        sys.exit(1)

def test_course_builder_api():
    """Test Course Builder API endpoints"""

    print("=" * 60)
    print("🧪 COURSE BUILDER API TEST")
    print("=" * 60)

    # Login
    headers = login_as_instructor()

    # 1. Create a course
    print("\n📚 Creating a new course...")
    course_data = {
        "title": "Introduction to Python Programming",
        "slug": f"python-intro-{uuid4().hex[:6]}",
        "description": "Learn Python from scratch with hands-on projects",
        "category": "Programming",
        "subcategory": "Python",
        "difficulty_level": "beginner",
        "duration_hours": 20,
        "prerequisites": [],  # Array of course IDs, empty for this test
        "tags": ["python", "programming", "beginner"],
        "is_published": False,
        "is_featured": False
    }

    response = requests.post(
        f"{BASE_URL}/api/lms/course-builder/courses",
        json=course_data,
        headers=headers
    )

    if response.status_code == 201:
        course = response.json()
        course_id = course["id"]
        print(f"✅ Course created: {course['title']} (ID: {course_id})")
    else:
        print(f"❌ Failed to create course: Status {response.status_code}")
        print(f"   Error details: {response.text}")
        return False

    # 2. Get instructor's courses
    print("\n📋 Getting instructor's courses...")
    response = requests.get(
        f"{BASE_URL}/api/lms/course-builder/courses",
        headers=headers
    )

    if response.status_code == 200:
        courses = response.json()
        print(f"✅ Found {len(courses)} course(s)")
        for c in courses[:3]:  # Show first 3
            print(f"   - {c['title']} (Modules: {c.get('module_count', 0)}, Lessons: {c.get('lesson_count', 0)})")
    else:
        print(f"❌ Failed to get courses: {response.text}")

    # 3. Create modules
    print(f"\n📦 Creating modules for course...")
    modules = []

    module_data = [
        {
            "title": "Getting Started with Python",
            "description": "Install Python and set up your environment",
            "sequence_order": 1,
            "is_optional": False,  # Required module
            "estimated_duration_minutes": 120,  # 2 hours
            "learning_objectives": [
                "Install Python on your system",
                "Set up development environment",
                "Run your first Python script"
            ]
        },
        {
            "title": "Python Basics",
            "description": "Variables, data types, and basic operations",
            "sequence_order": 2,
            "is_optional": False,  # Required module
            "estimated_duration_minutes": 300,  # 5 hours
            "learning_objectives": [
                "Understand Python data types",
                "Work with variables",
                "Perform basic operations"
            ]
        },
        {
            "title": "Control Flow",
            "description": "If statements, loops, and functions",
            "sequence_order": 3,
            "is_optional": False,  # Required module
            "estimated_duration_minutes": 240,  # 4 hours
            "learning_objectives": [
                "Write conditional statements",
                "Create and use loops",
                "Define and call functions"
            ]
        }
    ]

    for mod_data in module_data:
        response = requests.post(
            f"{BASE_URL}/api/lms/course-builder/courses/{course_id}/modules",
            json=mod_data,
            headers=headers
        )

        if response.status_code == 201:
            module = response.json()
            modules.append(module)
            print(f"✅ Module created: {module['title']}")
        else:
            print(f"❌ Failed to create module: {response.text}")

    if not modules:
        print("❌ No modules created, stopping test")
        return False

    # 4. Create lessons in first module
    print(f"\n📝 Creating lessons in first module...")
    module_id = modules[0]["id"]

    lesson_data = [
        {
            "title": "Installing Python",
            "description": "How to install Python on different operating systems",
            "sequence_order": 1,
            "lesson_type": "video",
            "estimated_duration_minutes": 15,
            "is_required": True
        },
        {
            "title": "Setting Up Your IDE",
            "description": "Configure VS Code for Python development",
            "sequence_order": 2,
            "lesson_type": "video",
            "estimated_duration_minutes": 20,
            "is_required": True
        },
        {
            "title": "Your First Python Program",
            "description": "Write and run Hello World",
            "sequence_order": 3,
            "lesson_type": "interactive",
            "estimated_duration_minutes": 10,
            "is_required": True
        }
    ]

    lessons = []
    for les_data in lesson_data:
        response = requests.post(
            f"{BASE_URL}/api/lms/course-builder/modules/{module_id}/lessons",
            json=les_data,
            headers=headers
        )

        if response.status_code == 201:
            lesson = response.json()
            lessons.append(lesson)
            print(f"✅ Lesson created: {lesson['title']}")
        else:
            print(f"❌ Failed to create lesson: {response.text}")

    if not lessons:
        print("❌ No lessons created, stopping test")
        return False

    # 5. Create content items in first lesson
    print(f"\n📄 Creating content items in first lesson...")
    lesson_id = lessons[0]["id"]

    content_data = [
        {
            "content_type": "video",
            "title": "Installation Video Tutorial",
            "description": "Step-by-step installation guide",
            "sequence_order": 1,
            "is_required": True,
            "content_data": {
                "video_url": "https://example.com/video.mp4",
                "duration_seconds": 900
            }
        },
        {
            "content_type": "document",
            "title": "Installation Guide PDF",
            "description": "Detailed written instructions",
            "sequence_order": 2,
            "is_required": False,
            "content_data": {
                "document_url": "https://example.com/guide.pdf"
            }
        },
        {
            "content_type": "quiz",
            "title": "Installation Check Quiz",
            "description": "Verify your installation was successful",
            "sequence_order": 3,
            "is_required": True,
            "points_possible": 10,
            "content_data": {}
        }
    ]

    for cont_data in content_data:
        response = requests.post(
            f"{BASE_URL}/api/lms/course-builder/lessons/{lesson_id}/content",
            json=cont_data,
            headers=headers
        )

        if response.status_code == 201:
            content = response.json()
            print(f"✅ Content item created: {content['title']} ({content['content_type']})")
        else:
            print(f"❌ Failed to create content: {response.text}")

    # 6. Get course structure
    print(f"\n🏗️ Getting full course structure...")
    response = requests.get(
        f"{BASE_URL}/api/lms/course-builder/courses/{course_id}/structure",
        headers=headers
    )

    if response.status_code == 200:
        structure = response.json()
        print(f"✅ Course structure retrieved:")
        print(f"   Course: {structure['course']['title']}")
        print(f"   Modules: {len(structure['modules'])}")

        for module in structure['modules']:
            print(f"\n   📦 Module {module['sequence_order']}: {module['title']}")
            print(f"      Lessons: {len(module['lessons'])}")

            for lesson in module['lessons']:
                print(f"      📝 Lesson {lesson['sequence_order']}: {lesson['title']}")
                print(f"         Content items: {len(lesson['content_items'])}")

                for content in lesson['content_items']:
                    req = "✓" if content['is_required'] else "○"
                    print(f"         {req} {content['title']} ({content['content_type']})")
    else:
        print(f"❌ Failed to get structure: {response.text}")

    # 7. Update course to published
    print(f"\n🚀 Publishing course...")
    response = requests.put(
        f"{BASE_URL}/api/lms/course-builder/courses/{course_id}",
        json={"is_published": True},
        headers=headers
    )

    if response.status_code == 200:
        updated_course = response.json()
        print(f"✅ Course published: {updated_course['is_published']}")
    else:
        print(f"❌ Failed to publish course: {response.text}")

    # 8. Test update operations
    print(f"\n✏️ Testing update operations...")

    # Update module
    if modules:
        module_id = modules[0]["id"]
        response = requests.put(
            f"{BASE_URL}/api/lms/course-builder/modules/{module_id}",
            json={"title": "Getting Started with Python (Updated)"},
            headers=headers
        )

        if response.status_code == 200:
            print(f"✅ Module updated successfully")
        else:
            print(f"❌ Failed to update module: {response.text}")

    # Update lesson
    if lessons:
        lesson_id = lessons[0]["id"]
        response = requests.put(
            f"{BASE_URL}/api/lms/course-builder/lessons/{lesson_id}",
            json={"estimated_duration_minutes": 25},
            headers=headers
        )

        if response.status_code == 200:
            print(f"✅ Lesson updated successfully")
        else:
            print(f"❌ Failed to update lesson: {response.text}")

    print("\n" + "=" * 60)
    print("🎉 COURSE BUILDER API TEST COMPLETED!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    try:
        success = test_course_builder_api()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)