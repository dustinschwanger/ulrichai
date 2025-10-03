#!/usr/bin/env python3
"""Test script for Quiz models"""

import asyncio
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import models
from app.lms.models import (
    Quiz, QuizQuestion, QuizAttempt, QuizResponse,
    QuestionType, QuizStatus,
    Course, CourseVersion, Module, Lesson, ContentItem,
    Organization, LMSUser
)

def test_quiz_creation():
    """Test creating quiz records"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables")

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Initialize variables for cleanup
    org = None
    user = None
    course = None
    course_version = None
    module = None
    lesson = None
    content_item = None
    quiz = None
    attempt = None

    try:
        # Generate unique identifiers for this test run
        test_id = str(uuid.uuid4())[:8]

        # First, create prerequisites (Organization, User, Course, Module, Lesson, ContentItem)
        print("Creating test organization...")
        org = Organization(
            name=f"Test Organization {test_id}",
            slug=f"test-org-{test_id}"
        )
        session.add(org)
        session.flush()

        print("Creating test user...")
        user = LMSUser(
            organization_id=org.id,
            email=f"quiz_test_{test_id}@test.com",
            password_hash="$2b$12$dummy_hash_for_testing",  # Dummy hash for testing
            first_name="Quiz",
            last_name="Tester",
            role="instructor"
        )
        session.add(user)
        session.flush()

        print("Creating test course...")
        course = Course(
            organization_id=org.id,
            title="Test Course for Quizzes",
            slug=f"test-course-quiz-{test_id}",
            instructor_id=user.id
        )
        session.add(course)
        session.flush()

        print("Creating test course version...")
        course_version = CourseVersion(
            course_id=course.id,
            version_number="1.0",
            title="Test Course v1.0",
            is_active=True,
            created_by=user.id
        )
        session.add(course_version)
        session.flush()

        print("Creating test module...")
        module = Module(
            course_version_id=course_version.id,
            title="Test Module",
            sequence_order=1
        )
        session.add(module)
        session.flush()

        print("Creating test lesson...")
        lesson = Lesson(
            module_id=module.id,
            title="Test Lesson with Quiz",
            sequence_order=1,
            lesson_type="assessment"
        )
        session.add(lesson)
        session.flush()

        print("Creating test content item...")
        content_item = ContentItem(
            lesson_id=lesson.id,
            content_type="quiz",
            title="Module 1 Quiz",
            sequence_order=1,
            content_data={"quiz_id": str(uuid.uuid4())}
        )
        session.add(content_item)
        session.flush()

        # Now create the quiz
        print("\n✓ Prerequisites created successfully!")
        print("\nCreating quiz...")
        quiz = Quiz(
            content_item_id=content_item.id,
            title="Python Fundamentals Quiz",
            instructions="Answer all questions to the best of your ability.",
            time_limit_minutes=30,
            attempts_allowed=2,
            passing_score=80.0,
            shuffle_questions=False,
            show_correct_answers=True
        )
        session.add(quiz)
        session.flush()
        print(f"✓ Quiz created: {quiz.title}")

        # Create quiz questions
        print("\nCreating quiz questions...")

        # Multiple choice question
        q1 = QuizQuestion(
            quiz_id=quiz.id,
            question_type=QuestionType.MULTIPLE_CHOICE.value,
            question_text="What is the output of print(2 ** 3)?",
            options=[
                {"id": "a", "text": "6"},
                {"id": "b", "text": "8"},
                {"id": "c", "text": "9"},
                {"id": "d", "text": "12"}
            ],
            correct_answers=["b"],
            explanation="The ** operator is for exponentiation. 2 ** 3 = 2 × 2 × 2 = 8",
            points=1.0,
            sequence_order=1
        )
        session.add(q1)
        print(f"✓ Question 1 added: {q1.question_text[:30]}...")

        # True/False question
        q2 = QuizQuestion(
            quiz_id=quiz.id,
            question_type=QuestionType.TRUE_FALSE.value,
            question_text="Python is a statically typed programming language.",
            options=[
                {"id": "true", "text": "True"},
                {"id": "false", "text": "False"}
            ],
            correct_answers=["false"],
            explanation="Python is dynamically typed, meaning variable types are determined at runtime.",
            points=1.0,
            sequence_order=2
        )
        session.add(q2)
        print(f"✓ Question 2 added: {q2.question_text[:30]}...")

        # Short answer question
        q3 = QuizQuestion(
            quiz_id=quiz.id,
            question_type=QuestionType.SHORT_ANSWER.value,
            question_text="What keyword is used to define a function in Python?",
            correct_answers=["def", "DEF"],
            explanation="The 'def' keyword is used to define functions in Python.",
            points=1.0,
            sequence_order=3
        )
        session.add(q3)
        print(f"✓ Question 3 added: {q3.question_text[:30]}...")

        session.flush()

        # Create a quiz attempt
        print("\nCreating quiz attempt...")
        attempt = QuizAttempt(
            user_id=user.id,
            quiz_id=quiz.id,
            attempt_number=1,
            status=QuizStatus.IN_PROGRESS.value
        )
        session.add(attempt)
        session.flush()
        print(f"✓ Quiz attempt created for user {user.email}")

        # Create responses
        print("\nCreating quiz responses...")

        # Response to question 1 (correct)
        r1 = QuizResponse(
            attempt_id=attempt.id,
            question_id=q1.id,
            answer=["b"],
            is_correct=True,
            points_earned=1.0
        )
        session.add(r1)

        # Response to question 2 (correct)
        r2 = QuizResponse(
            attempt_id=attempt.id,
            question_id=q2.id,
            answer=["false"],
            is_correct=True,
            points_earned=1.0
        )
        session.add(r2)

        # Response to question 3 (correct)
        r3 = QuizResponse(
            attempt_id=attempt.id,
            question_id=q3.id,
            answer=["def"],
            is_correct=True,
            points_earned=1.0
        )
        session.add(r3)

        print("✓ Quiz responses created")

        # Update attempt with score
        attempt.score = 100.0
        attempt.points_earned = 3.0
        attempt.points_possible = 3.0
        attempt.passed = True
        attempt.status = QuizStatus.GRADED.value

        # Commit all changes
        session.commit()
        print("\n✅ All quiz data created successfully!")

        # Query and display the data
        print("\n" + "="*50)
        print("QUERYING QUIZ DATA")
        print("="*50)

        # Query the quiz with questions
        quiz_from_db = session.query(Quiz).filter_by(title="Python Fundamentals Quiz").first()
        print(f"\nQuiz: {quiz_from_db.title}")
        print(f"  - Time Limit: {quiz_from_db.time_limit_minutes} minutes")
        print(f"  - Passing Score: {quiz_from_db.passing_score}%")
        print(f"  - Questions: {len(quiz_from_db.questions)}")

        for q in quiz_from_db.questions:
            print(f"\n  Question {q.sequence_order}: {q.question_text}")
            print(f"    Type: {q.question_type}")
            print(f"    Points: {q.points}")

        # Query attempts
        attempts = session.query(QuizAttempt).filter_by(quiz_id=quiz_from_db.id).all()
        print(f"\nQuiz Attempts: {len(attempts)}")
        for att in attempts:
            print(f"  - Attempt {att.attempt_number}: Score {att.score}% - {att.status}")

        print("\n✅ Test completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        raise
    finally:
        # Clean up test data
        print("\nCleaning up test data...")
        try:
            if attempt:
                session.query(QuizResponse).filter_by(attempt_id=attempt.id).delete()
                session.query(QuizAttempt).filter_by(id=attempt.id).delete()
            if quiz:
                session.query(QuizQuestion).filter_by(quiz_id=quiz.id).delete()
                session.query(Quiz).filter_by(id=quiz.id).delete()
            if content_item:
                session.query(ContentItem).filter_by(id=content_item.id).delete()
            if lesson:
                session.query(Lesson).filter_by(id=lesson.id).delete()
            if module:
                session.query(Module).filter_by(id=module.id).delete()
            if course_version:
                session.query(CourseVersion).filter_by(id=course_version.id).delete()
            if course:
                session.query(Course).filter_by(id=course.id).delete()
            if user:
                session.query(LMSUser).filter_by(id=user.id).delete()
            if org:
                session.query(Organization).filter_by(id=org.id).delete()
            session.commit()
            print("✓ Test data cleaned up")
        except Exception as e:
            print(f"Warning during cleanup: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    test_quiz_creation()