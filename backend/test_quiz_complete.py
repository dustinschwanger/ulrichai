#!/usr/bin/env python3
"""Complete test for Quiz functionality using direct database setup"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import uuid4
import requests

# Load environment variables
load_dotenv()

# Import models
from app.lms.models import (
    Organization, LMSUser, Course, CourseVersion,
    Module, Lesson, ContentItem,
    Quiz, QuizQuestion, QuizAttempt, QuizResponse,
    QuestionType, QuizStatus
)
from app.lms.services.auth_service import AuthService

# API base URL
BASE_URL = "http://localhost:8000"


def setup_test_environment():
    """Setup complete test environment with all necessary data"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    test_id = uuid4().hex[:8]
    test_data = {}

    try:
        print("🏗️ Setting up test environment...")

        # Create organization
        org = Organization(
            name=f"Quiz Test Org {test_id}",
            slug=f"quiz-test-{test_id}"
        )
        session.add(org)
        session.flush()
        test_data["org_id"] = str(org.id)
        print(f"✅ Created organization: {org.name}")

        # Create instructor user
        auth_service = AuthService(session)
        instructor = auth_service.register_user(
            email=f"quiz_instructor_{test_id}@test.com",
            password="TestPassword123!",
            first_name="Quiz",
            last_name="Instructor",
            organization_id=org.id,
            role="INSTRUCTOR"
        )
        test_data["instructor_email"] = instructor.email
        test_data["instructor_id"] = str(instructor.id)
        print(f"✅ Created instructor: {instructor.email}")

        # Create course
        course = Course(
            organization_id=org.id,
            title=f"Quiz Test Course {test_id}",
            slug=f"quiz-course-{test_id}",
            instructor_id=instructor.id,
            is_published=True
        )
        session.add(course)
        session.flush()
        test_data["course_id"] = str(course.id)
        print(f"✅ Created course: {course.title}")

        # Create course version
        version = CourseVersion(
            course_id=course.id,
            version_number="1.0",
            title=course.title,
            is_active=True,
            created_by=instructor.id
        )
        session.add(version)
        session.flush()
        test_data["version_id"] = str(version.id)
        print(f"✅ Created course version: {version.version_number}")

        # Create module
        module = Module(
            course_version_id=version.id,
            title="Module 1: Assessments",
            sequence_order=1
        )
        session.add(module)
        session.flush()
        test_data["module_id"] = str(module.id)
        print(f"✅ Created module: {module.title}")

        # Create lesson
        lesson = Lesson(
            module_id=module.id,
            title="Lesson 1: Python Quiz",
            sequence_order=1,
            lesson_type="assessment"
        )
        session.add(lesson)
        session.flush()
        test_data["lesson_id"] = str(lesson.id)
        print(f"✅ Created lesson: {lesson.title}")

        # Create content item for quiz
        content_item = ContentItem(
            lesson_id=lesson.id,
            content_type="quiz",
            title="Python Fundamentals Assessment",
            sequence_order=1,
            is_required=True,
            points_possible=10.0,
            content_data={}
        )
        session.add(content_item)
        session.flush()
        test_data["content_item_id"] = str(content_item.id)
        print(f"✅ Created content item for quiz")

        session.commit()
        print("\n✅ Test environment setup complete!")

        test_data["password"] = "TestPassword123!"
        return test_data

    except Exception as e:
        print(f"❌ Setup failed: {e}")
        session.rollback()
        raise
    finally:
        session.close()


def test_quiz_api(test_data):
    """Test the Quiz API endpoints"""
    session = requests.Session()

    print("\n" + "="*50)
    print("🧪 TESTING QUIZ API")
    print("="*50)

    # Login
    print("\n🔑 Logging in...")
    login_response = session.post(
        f"{BASE_URL}/api/lms/auth/login",
        data={
            "username": test_data["instructor_email"],
            "password": test_data["password"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False

    token_data = login_response.json()
    token = token_data["access_token"]
    user_info = token_data.get("user", {})
    session.headers.update({"Authorization": f"Bearer {token}"})
    print(f"✅ Logged in as: {test_data['instructor_email']}")
    print(f"   User role: {user_info.get('role', 'unknown')}")

    # Create quiz
    print("\n📝 Creating quiz...")
    quiz_data = {
        "content_item_id": test_data["content_item_id"],
        "title": "Python Fundamentals Quiz",
        "instructions": "Test your Python knowledge",
        "time_limit_minutes": 30,
        "attempts_allowed": 2,
        "passing_score": 70.0,
        "shuffle_questions": False,
        "show_correct_answers": True,
        "questions": [
            {
                "question_type": "multiple_choice",
                "question_text": "What is Python?",
                "options": [
                    {"id": "a", "text": "A snake"},
                    {"id": "b", "text": "A programming language"},
                    {"id": "c", "text": "A framework"},
                    {"id": "d", "text": "A database"}
                ],
                "correct_answers": ["b"],
                "explanation": "Python is a high-level programming language",
                "points": 2.0,
                "sequence_order": 1
            },
            {
                "question_type": "true_false",
                "question_text": "Python is compiled language.",
                "options": [
                    {"id": "true", "text": "True"},
                    {"id": "false", "text": "False"}
                ],
                "correct_answers": ["false"],
                "explanation": "Python is an interpreted language",
                "points": 1.0,
                "sequence_order": 2
            },
            {
                "question_type": "short_answer",
                "question_text": "What keyword is used to define a function?",
                "correct_answers": ["def", "DEF"],
                "points": 2.0,
                "sequence_order": 3
            }
        ]
    }

    create_response = session.post(
        f"{BASE_URL}/api/lms/quiz/",
        json=quiz_data
    )

    if create_response.status_code != 201:
        print(f"❌ Failed to create quiz: {create_response.text}")
        return False

    quiz = create_response.json()
    quiz_id = quiz["id"]
    print(f"✅ Quiz created with ID: {quiz_id}")
    print(f"   - Questions: {quiz['question_count']}")
    print(f"   - Total points: {quiz['total_points']}")

    # Get quiz details
    print("\n📖 Getting quiz details...")
    get_response = session.get(f"{BASE_URL}/api/lms/quiz/{quiz_id}")

    if get_response.status_code != 200:
        print(f"❌ Failed to get quiz: {get_response.text}")
        return False

    quiz_details = get_response.json()
    print(f"✅ Quiz retrieved: {quiz_details['title']}")
    print(f"   - Passing score: {quiz_details['passing_score']}%")
    print(f"   - Time limit: {quiz_details['time_limit_minutes']} minutes")

    # Start quiz attempt
    print("\n🚀 Starting quiz attempt...")
    attempt_response = session.post(
        f"{BASE_URL}/api/lms/quiz/attempt/start",
        json={"quiz_id": quiz_id}
    )

    if attempt_response.status_code != 200:
        print(f"❌ Failed to start attempt: {attempt_response.text}")
        return False

    attempt = attempt_response.json()
    attempt_id = attempt["id"]
    print(f"✅ Quiz attempt started")
    print(f"   - Attempt ID: {attempt_id}")
    print(f"   - Status: {attempt['status']}")

    # Get questions
    print("\n❓ Getting questions...")
    questions_response = session.get(f"{BASE_URL}/api/lms/quiz/{quiz_id}/questions")

    if questions_response.status_code != 200:
        print(f"❌ Failed to get questions: {questions_response.text}")
        return False

    questions = questions_response.json()
    print(f"✅ Retrieved {len(questions)} questions")

    # Submit answers
    print("\n✍️ Submitting answers...")
    responses = []
    for q in questions:
        if q["question_type"] == "multiple_choice":
            answer = ["b"]  # Correct
        elif q["question_type"] == "true_false":
            answer = ["false"]  # Correct
        elif q["question_type"] == "short_answer":
            answer = ["def"]  # Correct
        else:
            answer = [""]

        responses.append({
            "question_id": q["id"],
            "answer": answer
        })

    submit_response = session.post(
        f"{BASE_URL}/api/lms/quiz/attempt/submit",
        json={
            "attempt_id": attempt_id,
            "responses": responses
        }
    )

    if submit_response.status_code != 200:
        print(f"❌ Failed to submit: {submit_response.text}")
        return False

    result = submit_response.json()
    attempt_result = result["attempt"]
    print(f"✅ Quiz submitted successfully!")
    print(f"   - Score: {attempt_result['score']:.1f}%")
    print(f"   - Points: {attempt_result['points_earned']}/{attempt_result['points_possible']}")
    print(f"   - Passed: {'✅ Yes' if attempt_result['passed'] else '❌ No'}")

    # Review attempt
    print("\n🔍 Reviewing attempt...")
    review_response = session.get(f"{BASE_URL}/api/lms/quiz/attempt/{attempt_id}/review")

    if review_response.status_code != 200:
        print(f"❌ Failed to get review: {review_response.text}")
        return False

    review = review_response.json()
    print(f"✅ Review retrieved for: {review['quiz_title']}")

    return True


def cleanup_test_data(test_data):
    """Clean up test data from database"""
    print("\n🧹 Cleaning up test data...")

    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Clean up in reverse order of creation
        session.query(ContentItem).filter_by(id=test_data.get("content_item_id")).delete()
        session.query(Lesson).filter_by(id=test_data.get("lesson_id")).delete()
        session.query(Module).filter_by(id=test_data.get("module_id")).delete()
        session.query(CourseVersion).filter_by(id=test_data.get("version_id")).delete()
        session.query(Course).filter_by(id=test_data.get("course_id")).delete()
        session.query(LMSUser).filter_by(id=test_data.get("instructor_id")).delete()
        session.query(Organization).filter_by(id=test_data.get("org_id")).delete()

        session.commit()
        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    try:
        # Setup
        test_data = setup_test_environment()

        # Test
        success = test_quiz_api(test_data)

        # Results
        print("\n" + "="*50)
        if success:
            print("🎉 ALL QUIZ API TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED")
        print("="*50)

        # Cleanup
        cleanup_test_data(test_data)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")