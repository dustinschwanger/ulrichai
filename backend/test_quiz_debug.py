#!/usr/bin/env python3
"""Debug Quiz API to understand scoring issue"""

import requests
import json
from uuid import uuid4

# API base URL
BASE_URL = "http://localhost:8000"

def test_quiz_grading():
    session = requests.Session()

    # Read test credentials
    with open("test_credentials.txt", "r") as f:
        lines = f.readlines()
        creds = {}
        for line in lines:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                creds[key] = value

    # Login
    login_data = {
        "username": creds.get("INSTRUCTOR_EMAIL", "instructor_c483612d@test.com"),
        "password": creds.get("PASSWORD", "TestPassword123!")
    }

    print("🔑 Logging in...")
    response = session.post(
        f"{BASE_URL}/api/lms/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    data = response.json()
    token = data["access_token"]
    session.headers.update({"Authorization": f"Bearer {token}"})

    # Create course structure
    print("\n📚 Creating course structure...")

    # Create course
    course_data = {
        "title": "Debug Quiz Course",
        "slug": f"debug-quiz-{uuid4().hex[:8]}",
        "description": "Course for debugging quiz",
        "difficulty_level": "intermediate",
        "is_published": True
    }

    response = session.post(f"{BASE_URL}/api/lms/courses/", json=course_data)
    if response.status_code != 201:
        print(f"❌ Failed to create course: {response.text}")
        return
    course = response.json()
    course_id = course["id"]
    version_id = course["active_version_id"]

    # Create module
    module_data = {
        "course_version_id": version_id,
        "title": "Debug Module",
        "sequence_order": 1
    }

    response = session.post(f"{BASE_URL}/api/lms/courses/modules", json=module_data)
    module = response.json()

    # Create lesson
    lesson_data = {
        "module_id": module["id"],
        "title": "Debug Lesson",
        "sequence_order": 1,
        "lesson_type": "assessment"
    }

    response = session.post(f"{BASE_URL}/api/lms/courses/lessons", json=lesson_data)
    lesson = response.json()

    # Create content item
    content_data = {
        "lesson_id": lesson["id"],
        "content_type": "quiz",
        "title": "Debug Quiz",
        "sequence_order": 1,
        "is_required": True,
        "points_possible": 10,
        "content_data": {}
    }

    response = session.post(f"{BASE_URL}/api/lms/courses/content", json=content_data)
    content = response.json()
    content_item_id = content["id"]

    # Create quiz
    print("\n📝 Creating quiz with specific questions...")
    quiz_data = {
        "content_item_id": content_item_id,
        "title": "Debug Quiz",
        "instructions": "Testing grading",
        "time_limit_minutes": 30,
        "attempts_allowed": 2,
        "passing_score": 70.0,
        "questions": [
            {
                "question_type": "multiple_choice",
                "question_text": "What is 1 + 1?",
                "options": [
                    {"id": "a", "text": "1"},
                    {"id": "b", "text": "2"},
                    {"id": "c", "text": "3"},
                    {"id": "d", "text": "4"}
                ],
                "correct_answers": ["b"],
                "points": 2.0,
                "sequence_order": 1
            }
        ]
    }

    response = session.post(f"{BASE_URL}/api/lms/quiz/", json=quiz_data)
    if response.status_code != 201:
        print(f"❌ Failed to create quiz: {response.text}")
        return

    quiz = response.json()
    quiz_id = quiz["id"]
    print(f"✅ Quiz created: {quiz_id}")

    # Get questions to see what was stored
    print("\n📖 Getting quiz questions...")
    response = session.get(f"{BASE_URL}/api/lms/quiz/{quiz_id}/questions")
    questions = response.json()

    for q in questions:
        print(f"\nQuestion: {q['question_text']}")
        print(f"Type: {q['question_type']}")
        print(f"Correct answers: {q['correct_answers']}")
        print(f"Options: {q['options']}")

    # Start attempt
    print("\n🚀 Starting quiz attempt...")
    response = session.post(
        f"{BASE_URL}/api/lms/quiz/attempt/start",
        json={"quiz_id": quiz_id}
    )

    attempt = response.json()
    attempt_id = attempt["id"]
    print(f"✅ Attempt started: {attempt_id}")

    # Submit answers
    print("\n✍️ Submitting answer ['b'] for question...")
    responses = [
        {
            "question_id": questions[0]["id"],
            "answer": ["b"]  # This is the correct answer
        }
    ]

    submission_data = {
        "attempt_id": attempt_id,
        "responses": responses
    }

    print(f"Submission data: {json.dumps(submission_data, indent=2)}")

    response = session.post(
        f"{BASE_URL}/api/lms/quiz/attempt/submit",
        json=submission_data
    )

    if response.status_code != 200:
        print(f"❌ Failed to submit: {response.text}")
        return

    result = response.json()
    attempt_result = result["attempt"]

    print(f"\n📊 Results:")
    print(f"Score: {attempt_result['score']}%")
    print(f"Points: {attempt_result['points_earned']}/{attempt_result['points_possible']}")
    print(f"Passed: {attempt_result['passed']}")

    # Get review to see details
    print("\n🔍 Getting detailed review...")
    response = session.get(f"{BASE_URL}/api/lms/quiz/attempt/{attempt_id}/review")
    review = response.json()

    for q_data in review["questions"]:
        question = q_data["question"]
        print(f"\nQuestion: {question['question_text']}")
        print(f"User answer: {q_data['user_response']}")
        print(f"Correct answer: {question['correct_answers']}")
        print(f"Is correct: {q_data['is_correct']}")
        print(f"Points earned: {q_data['points_earned']}/{question['points']}")


if __name__ == "__main__":
    test_quiz_grading()