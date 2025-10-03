#!/usr/bin/env python3
"""Debug quiz scoring by examining what gets stored and compared"""

import os
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

def debug_quiz_scoring():
    """Debug the quiz scoring mechanism"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    test_id = uuid4().hex[:8]

    try:
        print("🏗️ Setting up test environment...")

        # Create organization
        org = Organization(
            name=f"Debug Org {test_id}",
            slug=f"debug-{test_id}"
        )
        db_session.add(org)
        db_session.flush()

        # Create instructor
        auth_service = AuthService(db_session)
        instructor = auth_service.register_user(
            email=f"debug_{test_id}@test.com",
            password="TestPassword123!",
            first_name="Debug",
            last_name="Instructor",
            organization_id=org.id,
            role="INSTRUCTOR"
        )

        # Create course
        course = Course(
            organization_id=org.id,
            title=f"Debug Course {test_id}",
            slug=f"debug-course-{test_id}",
            instructor_id=instructor.id,
            is_published=True
        )
        db_session.add(course)
        db_session.flush()

        # Create version
        version = CourseVersion(
            course_id=course.id,
            version_number="1.0",
            title=course.title,
            is_active=True,
            created_by=instructor.id
        )
        db_session.add(version)
        db_session.flush()

        # Create module
        module = Module(
            course_version_id=version.id,
            title="Debug Module",
            sequence_order=1
        )
        db_session.add(module)
        db_session.flush()

        # Create lesson
        lesson = Lesson(
            module_id=module.id,
            title="Debug Lesson",
            sequence_order=1,
            lesson_type="assessment"
        )
        db_session.add(lesson)
        db_session.flush()

        # Create content item
        content_item = ContentItem(
            lesson_id=lesson.id,
            content_type="quiz",
            title="Debug Quiz",
            sequence_order=1,
            is_required=True,
            points_possible=10.0,
            content_data={}
        )
        db_session.add(content_item)
        db_session.flush()

        db_session.commit()

        print("✅ Test environment created")

        # Now test via API
        session = requests.Session()

        # Login
        print("\n🔑 Logging in...")
        login_response = session.post(
            f"{BASE_URL}/api/lms/auth/login",
            data={
                "username": f"debug_{test_id}@test.com",
                "password": "TestPassword123!"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        token_data = login_response.json()
        token = token_data["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})

        # Create quiz with single question
        print("\n📝 Creating simple quiz...")
        quiz_data = {
            "content_item_id": str(content_item.id),
            "title": "Debug Quiz",
            "instructions": "Testing scoring",
            "time_limit_minutes": 30,
            "attempts_allowed": 2,
            "passing_score": 70.0,
            "questions": [
                {
                    "question_type": "multiple_choice",
                    "question_text": "What is 2 + 2?",
                    "options": [
                        {"id": "a", "text": "3"},
                        {"id": "b", "text": "4"},
                        {"id": "c", "text": "5"},
                        {"id": "d", "text": "6"}
                    ],
                    "correct_answers": ["b"],
                    "explanation": "2 + 2 = 4",
                    "points": 10.0,
                    "sequence_order": 1
                }
            ]
        }

        create_response = session.post(
            f"{BASE_URL}/api/lms/quiz/",
            json=quiz_data
        )

        if create_response.status_code != 201:
            print(f"❌ Failed to create quiz: {create_response.text}")
            return

        quiz = create_response.json()
        quiz_id = quiz["id"]
        print(f"✅ Quiz created with ID: {quiz_id}")

        # Get the question to see what was stored
        print("\n📖 Getting stored question...")
        questions_response = session.get(f"{BASE_URL}/api/lms/quiz/{quiz_id}/questions")
        questions = questions_response.json()

        for q in questions:
            print(f"Stored question:")
            print(f"  - Text: {q['question_text']}")
            print(f"  - Type: {q['question_type']} (type: {type(q['question_type'])})")
            print(f"  - Points: {q['points']}")
            print(f"  - Options: {q.get('options', 'Not provided')}")

        # Check database directly
        print("\n🔍 Checking database directly...")
        db_question = db_session.query(QuizQuestion).filter(
            QuizQuestion.quiz_id == quiz_id
        ).first()

        print(f"Database question:")
        print(f"  - Type: {db_question.question_type} (type: {type(db_question.question_type)})")
        print(f"  - Correct answers: {db_question.correct_answers} (type: {type(db_question.correct_answers)})")

        # Start attempt
        print("\n🚀 Starting quiz attempt...")
        attempt_response = session.post(
            f"{BASE_URL}/api/lms/quiz/attempt/start",
            json={"quiz_id": quiz_id}
        )

        attempt = attempt_response.json()
        attempt_id = attempt["id"]

        # Submit correct answer
        print("\n✍️ Submitting correct answer ['b']...")
        submission_data = {
            "attempt_id": attempt_id,
            "responses": [
                {
                    "question_id": questions[0]["id"],
                    "answer": ["b"]
                }
            ]
        }

        print(f"Submission data: {json.dumps(submission_data, indent=2)}")

        submit_response = session.post(
            f"{BASE_URL}/api/lms/quiz/attempt/submit",
            json=submission_data
        )

        if submit_response.status_code != 200:
            print(f"❌ Failed to submit: {submit_response.text}")
            return

        result = submit_response.json()
        attempt_result = result["attempt"]

        print(f"\n📊 Results:")
        print(f"Score: {attempt_result['score']}%")
        print(f"Points: {attempt_result['points_earned']}/{attempt_result['points_possible']}")
        print(f"Passed: {attempt_result['passed']}")

        if attempt_result['score'] == 0:
            print("\n❌ PROBLEM: Score is 0% even though correct answer was submitted!")

            # Check what was stored as the response
            print("\n🔍 Checking stored response...")
            db_response = db_session.query(DBQuizResponse).filter(
                DBQuizResponse.attempt_id == attempt_id
            ).first()

            if db_response:
                print(f"Stored response:")
                print(f"  - Answer: {db_response.answer} (type: {type(db_response.answer)})")
                print(f"  - Is correct: {db_response.is_correct}")
                print(f"  - Points earned: {db_response.points_earned}")
            else:
                print("No response found in database!")

        else:
            print("\n✅ SUCCESS: Quiz scored correctly!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db_session.rollback()
        raise
    finally:
        # Cleanup
        try:
            db_session.query(ContentItem).filter_by(id=content_item.id).delete()
            db_session.query(Lesson).filter_by(id=lesson.id).delete()
            db_session.query(Module).filter_by(id=module.id).delete()
            db_session.query(CourseVersion).filter_by(id=version.id).delete()
            db_session.query(Course).filter_by(id=course.id).delete()
            db_session.query(LMSUser).filter_by(id=instructor.id).delete()
            db_session.query(Organization).filter_by(id=org.id).delete()
            db_session.commit()
            print("\n🧹 Cleaned up test data")
        except:
            pass
        db_session.close()


if __name__ == "__main__":
    debug_quiz_scoring()