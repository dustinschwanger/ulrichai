#!/usr/bin/env python3
"""End-to-end test for Quiz functionality"""

import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from uuid import uuid4
import requests
import json

# Load environment variables
load_dotenv()

# Import models
from app.lms.models import (
    Organization, LMSUser, Course, CourseVersion,
    Module, Lesson, ContentItem,
    Quiz, QuizQuestion, QuizAttempt, QuizResponse as DBQuizResponse,
)
from app.lms.services.auth_service import AuthService

# API base URL
BASE_URL = "http://localhost:8000"

def test_quiz_end_to_end():
    """Complete end-to-end test of quiz functionality"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    test_id = uuid4().hex[:8]
    test_data = {}

    try:
        print("=" * 60)
        print("🧪 QUIZ END-TO-END TEST")
        print("=" * 60)

        # 1. Setup test environment
        print("\n📦 SETUP: Creating test organization and users...")

        # Create organization
        org = Organization(
            name=f"E2E Test Org {test_id}",
            slug=f"e2e-test-{test_id}"
        )
        db_session.add(org)
        db_session.flush()
        test_data["org_id"] = org.id
        print(f"✅ Created organization: {org.name}")

        # Create instructor and student
        auth_service = AuthService(db_session)
        instructor = auth_service.register_user(
            email=f"instructor_e2e_{test_id}@test.com",
            password="TestPassword123!",
            first_name="E2E",
            last_name="Instructor",
            organization_id=org.id,
            role="INSTRUCTOR"
        )
        test_data["instructor"] = instructor
        print(f"✅ Created instructor: {instructor.email}")

        student = auth_service.register_user(
            email=f"student_e2e_{test_id}@test.com",
            password="TestPassword123!",
            first_name="E2E",
            last_name="Student",
            organization_id=org.id,
            role="STUDENT"
        )
        test_data["student"] = student
        print(f"✅ Created student: {student.email}")

        # Create course structure
        print("\n📚 Creating course structure...")
        course = Course(
            organization_id=org.id,
            title=f"E2E Test Course {test_id}",
            slug=f"e2e-course-{test_id}",
            instructor_id=instructor.id,
            is_published=True
        )
        db_session.add(course)
        db_session.flush()
        test_data["course_id"] = course.id

        version = CourseVersion(
            course_id=course.id,
            version_number="1.0",
            title=course.title,
            is_active=True,
            created_by=instructor.id
        )
        db_session.add(version)
        db_session.flush()

        module = Module(
            course_version_id=version.id,
            title="E2E Test Module",
            sequence_order=1
        )
        db_session.add(module)
        db_session.flush()

        lesson = Lesson(
            module_id=module.id,
            title="E2E Quiz Lesson",
            sequence_order=1,
            lesson_type="assessment"
        )
        db_session.add(lesson)
        db_session.flush()

        content_item = ContentItem(
            lesson_id=lesson.id,
            content_type="quiz",
            title="E2E Quiz Content",
            sequence_order=1,
            is_required=True,
            points_possible=10.0,
            content_data={}
        )
        db_session.add(content_item)
        db_session.flush()
        test_data["content_item_id"] = content_item.id

        db_session.commit()
        print("✅ Course structure created")

        # 2. Test as Instructor - Create Quiz
        print("\n👨‍🏫 INSTRUCTOR FLOW: Creating quiz...")
        instructor_session = requests.Session()

        # Login as instructor
        login_response = instructor_session.post(
            f"{BASE_URL}/api/lms/auth/login",
            data={
                "username": f"instructor_e2e_{test_id}@test.com",
                "password": "TestPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        instructor_token = login_response.json()["access_token"]
        instructor_session.headers.update({"Authorization": f"Bearer {instructor_token}"})
        print("✅ Instructor logged in")

        # Create quiz
        quiz_data = {
            "content_item_id": str(content_item.id),
            "title": "Python Programming Quiz",
            "instructions": "Test your Python knowledge with this comprehensive quiz",
            "time_limit_minutes": 30,
            "attempts_allowed": 2,
            "passing_score": 60.0,
            "shuffle_questions": False,
            "shuffle_answers": True,
            "show_correct_answers": True,
            "show_feedback": True,
            "allow_review": True,
            "questions": [
                {
                    "question_type": "multiple_choice",
                    "question_text": "What is the output of print(type([]))?",
                    "options": [
                        {"id": "a", "text": "<class 'tuple'>"},
                        {"id": "b", "text": "<class 'list'>"},
                        {"id": "c", "text": "<class 'dict'>"},
                        {"id": "d", "text": "<class 'set'>"}
                    ],
                    "correct_answers": ["b"],
                    "explanation": "[] creates an empty list, so type([]) returns <class 'list'>",
                    "points": 3.0,
                    "sequence_order": 1
                },
                {
                    "question_type": "true_false",
                    "question_text": "Python is a compiled language.",
                    "options": [
                        {"id": "true", "text": "True"},
                        {"id": "false", "text": "False"}
                    ],
                    "correct_answers": ["false"],
                    "explanation": "Python is an interpreted language, not compiled.",
                    "points": 2.0,
                    "sequence_order": 2
                },
                {
                    "question_type": "short_answer",
                    "question_text": "What keyword is used to define a function in Python?",
                    "correct_answers": ["def", "DEF"],
                    "explanation": "The 'def' keyword is used to define functions in Python.",
                    "points": 2.0,
                    "sequence_order": 3
                }
            ]
        }

        create_response = instructor_session.post(
            f"{BASE_URL}/api/lms/quiz/",
            json=quiz_data
        )

        if create_response.status_code != 201:
            print(f"❌ Failed to create quiz: {create_response.text}")
            return False

        quiz = create_response.json()
        quiz_id = quiz["id"]
        print(f"✅ Quiz created successfully")
        print(f"   - ID: {quiz_id}")
        print(f"   - Questions: {quiz['question_count']}")
        print(f"   - Total Points: {quiz['total_points']}")

        # Get quiz by content item
        get_by_content_response = instructor_session.get(
            f"{BASE_URL}/api/lms/quiz/by-content-item/{content_item.id}"
        )
        if get_by_content_response.status_code == 200:
            print("✅ Quiz retrieved by content item ID")
        else:
            print(f"❌ Failed to get quiz by content item: {get_by_content_response.text}")

        # 3. Test as Student - Take Quiz
        print("\n🎓 STUDENT FLOW: Taking quiz...")
        student_session = requests.Session()

        # Login as student
        login_response = student_session.post(
            f"{BASE_URL}/api/lms/auth/login",
            data={
                "username": f"student_e2e_{test_id}@test.com",
                "password": "TestPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        student_token = login_response.json()["access_token"]
        student_session.headers.update({"Authorization": f"Bearer {student_token}"})
        print("✅ Student logged in")

        # Get quiz details
        quiz_response = student_session.get(f"{BASE_URL}/api/lms/quiz/{quiz_id}")
        if quiz_response.status_code == 200:
            quiz_info = quiz_response.json()
            print(f"✅ Quiz loaded: {quiz_info['title']}")
            print(f"   - Time limit: {quiz_info['time_limit_minutes']} minutes")
            print(f"   - Attempts allowed: {quiz_info['attempts_allowed']}")
            print(f"   - Passing score: {quiz_info['passing_score']}%")
        else:
            print(f"❌ Failed to get quiz: {quiz_response.text}")
            return False

        # Start quiz attempt
        print("\n🚀 Starting quiz attempt...")
        start_response = student_session.post(
            f"{BASE_URL}/api/lms/quiz/attempt/start",
            json={"quiz_id": quiz_id}
        )

        if start_response.status_code != 200:
            print(f"❌ Failed to start attempt: {start_response.text}")
            return False

        attempt = start_response.json()
        attempt_id = attempt["id"]
        print(f"✅ Quiz attempt started")
        print(f"   - Attempt ID: {attempt_id}")
        print(f"   - Status: {attempt['status']}")

        # Get questions
        questions_response = student_session.get(f"{BASE_URL}/api/lms/quiz/{quiz_id}/questions")
        questions = questions_response.json()
        print(f"✅ Retrieved {len(questions)} questions")

        # Submit answers (mix of correct and incorrect)
        print("\n📝 Submitting answers...")
        responses = []

        # Question 1: Multiple choice - CORRECT
        responses.append({
            "question_id": questions[0]["id"],
            "answer": ["b"]  # Correct: <class 'list'>
        })

        # Question 2: True/False - INCORRECT
        responses.append({
            "question_id": questions[1]["id"],
            "answer": ["true"]  # Incorrect: should be false
        })

        # Question 3: Short answer - CORRECT
        responses.append({
            "question_id": questions[2]["id"],
            "answer": ["def"]  # Correct
        })

        submission = {
            "attempt_id": attempt_id,
            "responses": responses
        }

        submit_response = student_session.post(
            f"{BASE_URL}/api/lms/quiz/attempt/submit",
            json=submission
        )

        if submit_response.status_code != 200:
            print(f"❌ Failed to submit: {submit_response.text}")
            return False

        result = submit_response.json()
        attempt_result = result["attempt"]

        print(f"✅ Quiz submitted successfully!")
        print(f"   - Score: {attempt_result['score']:.1f}%")
        print(f"   - Points: {attempt_result['points_earned']}/{attempt_result['points_possible']}")
        print(f"   - Status: {'PASSED ✅' if attempt_result['passed'] else 'FAILED ❌'}")
        print(f"   - Questions correct: {result['questions_correct']}/{result['questions_answered']}")

        # Expected: 5 points out of 7 (71.4%), should PASS with 60% threshold
        expected_points = 5.0
        if abs(attempt_result['points_earned'] - expected_points) < 0.01:
            print(f"✅ Scoring is correct!")
        else:
            print(f"❌ Scoring error: expected {expected_points} points, got {attempt_result['points_earned']}")

        # Review attempt
        print("\n🔍 Reviewing attempt...")
        review_response = student_session.get(
            f"{BASE_URL}/api/lms/quiz/attempt/{attempt_id}/review"
        )

        if review_response.status_code == 200:
            review = review_response.json()
            print(f"✅ Review loaded successfully")
            for i, q_data in enumerate(review["questions"], 1):
                question = q_data["question"]
                print(f"\n   Q{i}: {question['question_text'][:50]}...")
                print(f"      Answer: {q_data['user_response']}")
                print(f"      Correct: {'✅' if q_data['is_correct'] else '❌'}")
                print(f"      Points: {q_data['points_earned']}/{question['points']}")
        else:
            print(f"❌ Failed to get review: {review_response.text}")

        # Check attempts list
        print("\n📊 Checking attempts history...")
        attempts_response = student_session.get(
            f"{BASE_URL}/api/lms/quiz/attempts/my?quiz_id={quiz_id}"
        )

        if attempts_response.status_code == 200:
            attempts = attempts_response.json()
            print(f"✅ Found {len(attempts)} attempt(s)")
            for att in attempts:
                print(f"   - Attempt {att['attempt_number']}: {att['score']:.1f}% - {att['status']}")
        else:
            print(f"❌ Failed to get attempts: {attempts_response.text}")

        print("\n" + "=" * 60)
        print("🎉 END-TO-END TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        try:
            # Clean up in reverse order
            if "content_item_id" in test_data:
                db_session.query(Quiz).filter(Quiz.content_item_id == test_data["content_item_id"]).delete()
                db_session.query(ContentItem).filter_by(id=test_data["content_item_id"]).delete()
            db_session.query(Lesson).filter(Lesson.module_id == module.id).delete()
            db_session.query(Module).filter(Module.course_version_id == version.id).delete()
            db_session.query(CourseVersion).filter(CourseVersion.course_id == test_data.get("course_id")).delete()
            db_session.query(Course).filter_by(id=test_data.get("course_id")).delete()
            if "student" in test_data:
                db_session.query(LMSUser).filter_by(id=test_data["student"].id).delete()
            if "instructor" in test_data:
                db_session.query(LMSUser).filter_by(id=test_data["instructor"].id).delete()
            db_session.query(Organization).filter_by(id=test_data.get("org_id")).delete()
            db_session.commit()
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            db_session.rollback()
        finally:
            db_session.close()


if __name__ == "__main__":
    success = test_quiz_end_to_end()
    exit(0 if success else 1)