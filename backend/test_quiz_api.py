#!/usr/bin/env python3
"""Test script for Quiz API endpoints"""

import requests
import json
from uuid import uuid4
from typing import Optional

# API base URL
BASE_URL = "http://localhost:8000"

# Test data
test_user_email = f"quiz_instructor_{uuid4().hex[:8]}@test.com"
test_password = "TestPassword123!"
test_org_slug = f"test-org-{uuid4().hex[:8]}"


class QuizAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.user_id = None
        self.org_id = None
        self.course_id = None
        self.content_item_id = None
        self.quiz_id = None
        self.attempt_id = None

    def register_and_login(self):
        """Login with test user credentials"""
        # Read test credentials from file
        try:
            with open("test_credentials.txt", "r") as f:
                lines = f.readlines()
                creds = {}
                for line in lines:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        creds[key] = value

            instructor_email = creds.get("INSTRUCTOR_EMAIL", "instructor_c483612d@test.com")
            password = creds.get("PASSWORD", "TestPassword123!")
            self.org_id = creds.get("ORG_ID")
        except:
            # Fallback credentials if file doesn't exist
            instructor_email = "instructor_c483612d@test.com"
            password = "TestPassword123!"

        login_data = {
            "username": instructor_email,
            "password": password
        }

        print(f"🔑 Logging in as: {instructor_email}")
        response = self.session.post(
            f"{BASE_URL}/api/lms/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False

        data = response.json()
        self.token = data["access_token"]
        self.user_id = data["user"]["id"]
        if not self.org_id:
            self.org_id = data["user"]["organization_id"]

        # Set authorization header
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

        print(f"✅ Logged in as: {instructor_email}")
        return True

    def create_course_structure(self):
        """Create a course with module, lesson, and content item"""
        print("\n📚 Creating course structure...")

        # Create course
        course_data = {
            "title": "Quiz Test Course",
            "slug": f"quiz-test-{uuid4().hex[:8]}",
            "description": "Course for testing quiz functionality",
            "difficulty_level": "intermediate",
            "is_published": True
        }

        response = self.session.post(f"{BASE_URL}/api/lms/courses", json=course_data)
        if response.status_code != 201:
            print(f"❌ Failed to create course: {response.text}")
            return False

        course = response.json()
        self.course_id = course["id"]
        course_version_id = course["active_version_id"]
        print(f"✅ Course created: {course['title']}")

        # Create module
        module_data = {
            "course_version_id": course_version_id,
            "title": "Module 1: Introduction",
            "description": "Introduction module with quiz",
            "sequence_order": 1,
            "learning_objectives": ["Understand basic concepts", "Complete the quiz"]
        }

        response = self.session.post(f"{BASE_URL}/api/lms/courses/modules", json=module_data)
        if response.status_code != 201:
            print(f"❌ Failed to create module: {response.text}")
            return False

        module = response.json()
        module_id = module["id"]
        print(f"✅ Module created: {module['title']}")

        # Create lesson
        lesson_data = {
            "module_id": module_id,
            "title": "Lesson 1: Quiz Assessment",
            "description": "Complete this quiz to test your knowledge",
            "sequence_order": 1,
            "lesson_type": "assessment"
        }

        response = self.session.post(f"{BASE_URL}/api/lms/courses/lessons", json=lesson_data)
        if response.status_code != 201:
            print(f"❌ Failed to create lesson: {response.text}")
            return False

        lesson = response.json()
        lesson_id = lesson["id"]
        print(f"✅ Lesson created: {lesson['title']}")

        # Create content item for quiz
        content_data = {
            "lesson_id": lesson_id,
            "content_type": "quiz",
            "title": "Python Basics Quiz",
            "sequence_order": 1,
            "is_required": True,
            "points_possible": 10,
            "content_data": {}
        }

        response = self.session.post(f"{BASE_URL}/api/lms/courses/content", json=content_data)
        if response.status_code != 201:
            print(f"❌ Failed to create content item: {response.text}")
            return False

        content = response.json()
        self.content_item_id = content["id"]
        print(f"✅ Content item created for quiz")

        return True

    def test_create_quiz(self):
        """Test creating a quiz with questions"""
        print("\n🎯 Creating quiz...")

        quiz_data = {
            "content_item_id": self.content_item_id,
            "title": "Python Fundamentals Quiz",
            "instructions": "Answer all questions to test your Python knowledge",
            "time_limit_minutes": 30,
            "attempts_allowed": 2,
            "passing_score": 70.0,
            "shuffle_questions": False,
            "shuffle_answers": True,
            "show_correct_answers": True,
            "show_feedback": True,
            "allow_review": True,
            "questions": [
                {
                    "question_type": "multiple_choice",
                    "question_text": "What is the output of print(2 ** 3)?",
                    "options": [
                        {"id": "a", "text": "6"},
                        {"id": "b", "text": "8"},
                        {"id": "c", "text": "9"},
                        {"id": "d", "text": "12"}
                    ],
                    "correct_answers": ["b"],
                    "explanation": "The ** operator is for exponentiation. 2 ** 3 = 2 × 2 × 2 = 8",
                    "points": 2.0,
                    "sequence_order": 1,
                    "difficulty_level": 2
                },
                {
                    "question_type": "true_false",
                    "question_text": "Python is a statically typed language.",
                    "options": [
                        {"id": "true", "text": "True"},
                        {"id": "false", "text": "False"}
                    ],
                    "correct_answers": ["false"],
                    "explanation": "Python is dynamically typed.",
                    "points": 1.0,
                    "sequence_order": 2,
                    "difficulty_level": 1
                },
                {
                    "question_type": "short_answer",
                    "question_text": "What keyword is used to define a function in Python?",
                    "correct_answers": ["def", "DEF"],
                    "explanation": "The 'def' keyword is used to define functions.",
                    "points": 2.0,
                    "sequence_order": 3,
                    "difficulty_level": 1
                }
            ]
        }

        response = self.session.post(f"{BASE_URL}/api/lms/quiz/", json=quiz_data)

        if response.status_code != 201:
            print(f"❌ Failed to create quiz: {response.text}")
            return False

        quiz = response.json()
        self.quiz_id = quiz["id"]

        print(f"✅ Quiz created: {quiz['title']}")
        print(f"   - ID: {quiz['id']}")
        print(f"   - Questions: {quiz['question_count']}")
        print(f"   - Total Points: {quiz['total_points']}")

        return True

    def test_get_quiz(self):
        """Test getting quiz details"""
        print("\n📖 Getting quiz details...")

        response = self.session.get(f"{BASE_URL}/api/lms/quiz/{self.quiz_id}")

        if response.status_code != 200:
            print(f"❌ Failed to get quiz: {response.text}")
            return False

        quiz = response.json()
        print(f"✅ Quiz retrieved: {quiz['title']}")
        print(f"   - Time limit: {quiz['time_limit_minutes']} minutes")
        print(f"   - Attempts allowed: {quiz['attempts_allowed']}")
        print(f"   - Passing score: {quiz['passing_score']}%")

        return True

    def test_get_questions(self):
        """Test getting quiz questions"""
        print("\n❓ Getting quiz questions...")

        response = self.session.get(f"{BASE_URL}/api/lms/quiz/{self.quiz_id}/questions")

        if response.status_code != 200:
            print(f"❌ Failed to get questions: {response.text}")
            return False

        questions = response.json()
        print(f"✅ Retrieved {len(questions)} questions:")

        for q in questions:
            print(f"   Q{q['sequence_order']}: {q['question_text'][:50]}...")
            print(f"       Type: {q['question_type']}, Points: {q['points']}")

        return True

    def test_start_attempt(self):
        """Test starting a quiz attempt"""
        print("\n🚀 Starting quiz attempt...")

        attempt_data = {
            "quiz_id": self.quiz_id
        }

        response = self.session.post(f"{BASE_URL}/api/lms/quiz/attempt/start", json=attempt_data)

        if response.status_code != 200:
            print(f"❌ Failed to start attempt: {response.text}")
            return False

        attempt = response.json()
        self.attempt_id = attempt["id"]

        print(f"✅ Quiz attempt started")
        print(f"   - Attempt ID: {attempt['id']}")
        print(f"   - Attempt #: {attempt['attempt_number']}")
        print(f"   - Status: {attempt['status']}")

        return True

    def test_submit_attempt(self):
        """Test submitting quiz responses"""
        print("\n📝 Submitting quiz responses...")

        # Get questions to know their IDs
        response = self.session.get(f"{BASE_URL}/api/lms/quiz/{self.quiz_id}/questions")
        questions = response.json()

        # Prepare responses
        responses = []
        for q in questions:
            if q["question_type"] == "multiple_choice":
                answer = ["b"]  # Correct answer
            elif q["question_type"] == "true_false":
                answer = ["false"]  # Correct answer
            elif q["question_type"] == "short_answer":
                answer = ["def"]  # Correct answer
            else:
                answer = ["unknown"]

            responses.append({
                "question_id": q["id"],
                "answer": answer
            })

        submission_data = {
            "attempt_id": self.attempt_id,
            "responses": responses
        }

        response = self.session.post(f"{BASE_URL}/api/lms/quiz/attempt/submit", json=submission_data)

        if response.status_code != 200:
            print(f"❌ Failed to submit attempt: {response.text}")
            return False

        result = response.json()
        attempt = result["attempt"]

        print(f"✅ Quiz submitted and graded!")
        print(f"   - Score: {attempt['score']:.1f}%")
        print(f"   - Points: {attempt['points_earned']}/{attempt['points_possible']}")
        print(f"   - Passed: {'✅ Yes' if attempt['passed'] else '❌ No'}")
        print(f"   - Questions correct: {result['questions_correct']}/{result['questions_answered']}")

        return True

    def test_review_attempt(self):
        """Test reviewing quiz attempt"""
        print("\n🔍 Reviewing quiz attempt...")

        response = self.session.get(f"{BASE_URL}/api/lms/quiz/attempt/{self.attempt_id}/review")

        if response.status_code != 200:
            print(f"❌ Failed to review attempt: {response.text}")
            return False

        review = response.json()

        print(f"✅ Quiz review retrieved: {review['quiz_title']}")
        print(f"   Score: {review['attempt']['score']:.1f}%")

        for i, q_data in enumerate(review["questions"], 1):
            q = q_data["question"]
            print(f"\n   Question {i}: {q['question_text'][:50]}...")
            print(f"   Your answer: {q_data['user_response']}")
            print(f"   Correct: {'✅' if q_data['is_correct'] else '❌'}")
            print(f"   Points: {q_data['points_earned']}/{q['points']}")
            if q_data["explanation"]:
                print(f"   Explanation: {q_data['explanation'][:100]}...")

        return True

    def test_my_attempts(self):
        """Test getting user's attempts"""
        print("\n📊 Getting my quiz attempts...")

        response = self.session.get(f"{BASE_URL}/api/lms/quiz/attempts/my?quiz_id={self.quiz_id}")

        if response.status_code != 200:
            print(f"❌ Failed to get attempts: {response.text}")
            return False

        attempts = response.json()

        print(f"✅ Retrieved {len(attempts)} attempt(s)")
        for attempt in attempts:
            print(f"   Attempt {attempt['attempt_number']}: Score {attempt['score']:.1f}% - {attempt['status']}")

        return True

    def cleanup(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")

        # Note: In a real test, we would delete the created resources
        # For now, we'll just note that cleanup would happen here

        print("✅ Cleanup complete")

    def run_all_tests(self):
        """Run all quiz API tests"""
        print("=" * 50)
        print("🧪 QUIZ API TEST SUITE")
        print("=" * 50)

        # Setup
        if not self.register_and_login():
            print("❌ Failed to register and login")
            return

        if not self.create_course_structure():
            print("❌ Failed to create course structure")
            return

        # Quiz CRUD Tests
        tests = [
            ("Create Quiz", self.test_create_quiz),
            ("Get Quiz", self.test_get_quiz),
            ("Get Questions", self.test_get_questions),
            ("Start Attempt", self.test_start_attempt),
            ("Submit Attempt", self.test_submit_attempt),
            ("Review Attempt", self.test_review_attempt),
            ("Get My Attempts", self.test_my_attempts),
        ]

        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))

        # Cleanup
        self.cleanup()

        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)

        passed = sum(1 for _, success in results if success)
        total = len(results)

        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")

        print(f"\n🏁 Tests Passed: {passed}/{total}")

        if passed == total:
            print("🎉 All tests passed!")
        else:
            print("⚠️ Some tests failed. Please review the output above.")


if __name__ == "__main__":
    tester = QuizAPITester()
    tester.run_all_tests()