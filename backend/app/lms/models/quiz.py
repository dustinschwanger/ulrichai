"""
Quiz models for assessments and testing
"""

from sqlalchemy import Column, String, Boolean, JSON, DateTime, Text, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class QuestionType(enum.Enum):
    """Types of quiz questions supported"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    MATCHING = "matching"
    FILL_IN_BLANK = "fill_in_blank"


class QuizStatus(enum.Enum):
    """Status of a quiz attempt"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"


class Quiz(Base):
    """
    Quizzes are assessments that can be added to lessons.
    They contain questions and track student attempts.
    """
    __tablename__ = "lms_quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Link to content item
    content_item_id = Column(UUID(as_uuid=True), ForeignKey("lms_content_items.id"), nullable=False, unique=True)

    # Quiz Information
    title = Column(String(500), nullable=False)
    instructions = Column(Text, nullable=True)

    # Quiz Settings
    time_limit_minutes = Column(Integer, nullable=True)  # None = no time limit
    attempts_allowed = Column(Integer, default=1)  # -1 = unlimited attempts
    passing_score = Column(Numeric(5, 2), default=70.0)  # Percentage

    # Display Settings
    shuffle_questions = Column(Boolean, default=False)
    shuffle_answers = Column(Boolean, default=False)
    show_correct_answers = Column(Boolean, default=True)
    show_feedback = Column(Boolean, default=True)
    allow_review = Column(Boolean, default=True)

    # AI Generation
    ai_generated = Column(Boolean, default=False)
    generation_prompt = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    questions = relationship("QuizQuestion", back_populates="quiz", order_by="QuizQuestion.sequence_order", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz {self.title}>"


class QuizQuestion(Base):
    """
    Individual questions within a quiz.
    Supports various question types with flexible answer formats.
    """
    __tablename__ = "lms_quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Parent quiz
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("lms_quizzes.id"), nullable=False, index=True)

    # Question Details
    question_type = Column(String(50), nullable=False)  # Stores QuestionType enum values as strings
    question_text = Column(Text, nullable=False)
    question_media = Column(JSON, nullable=True)  # {"type": "image", "url": "..."}

    # Answer Options and Correct Answers
    options = Column(JSON, default=[], nullable=True)
    # For multiple choice: [{"id": "a", "text": "Option A"}, ...]
    # For matching: {"left": [...], "right": [...]}

    correct_answers = Column(JSON, nullable=False)
    # For multiple choice: ["a"]
    # For true/false: [true] or [false]
    # For short answer: ["answer1", "answer2"] (alternative correct answers)
    # For matching: [{"left": "1", "right": "a"}, ...]

    # Feedback and Explanation
    explanation = Column(Text, nullable=True)
    hint = Column(Text, nullable=True)

    # Scoring
    points = Column(Numeric(5, 2), default=1.0)
    partial_credit = Column(Boolean, default=False)

    # Order and Metadata
    sequence_order = Column(Integer, nullable=False)
    difficulty_level = Column(Integer, default=3)  # 1-5 scale
    tags = Column(ARRAY(String), default=[], nullable=True)

    # AI Generation
    ai_generated = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    responses = relationship("QuizResponse", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizQuestion {self.question_type.value}: {self.question_text[:50]}...>"


class QuizAttempt(Base):
    """
    Tracks each attempt a user makes at a quiz.
    Records timing, score, and overall status.
    """
    __tablename__ = "lms_quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # User and Quiz
    user_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("lms_quizzes.id"), nullable=False, index=True)

    # Attempt Number
    attempt_number = Column(Integer, nullable=False, default=1)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    time_spent_seconds = Column(Integer, nullable=True)

    # Scoring
    score = Column(Numeric(5, 2), nullable=True)  # Percentage
    points_earned = Column(Numeric(5, 2), nullable=True)
    points_possible = Column(Numeric(5, 2), nullable=True)
    passed = Column(Boolean, nullable=True)

    # Status
    status = Column(String(50), default="in_progress", nullable=False)  # Stores QuizStatus enum values as strings

    # Question Order (if shuffled)
    question_order = Column(JSON, nullable=True)  # Array of question IDs in order shown

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    user = relationship("LMSUser", backref="quiz_attempts")
    responses = relationship("QuizResponse", back_populates="attempt", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizAttempt user={self.user_id} quiz={self.quiz_id} attempt={self.attempt_number}>"


class QuizResponse(Base):
    """
    Individual responses to quiz questions.
    Stores user answers and grading information.
    """
    __tablename__ = "lms_quiz_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Attempt and Question
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("lms_quiz_attempts.id"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("lms_quiz_questions.id"), nullable=False, index=True)

    # User Answer
    answer = Column(JSON, nullable=True)
    # For multiple choice: ["a"] or ["a", "b"] for multi-select
    # For true/false: [true] or [false]
    # For short answer/essay: ["User's text answer"]
    # For matching: [{"left": "1", "right": "b"}, ...]

    # Grading
    is_correct = Column(Boolean, nullable=True)  # None for ungraded
    points_earned = Column(Numeric(5, 2), default=0.0)

    # Feedback
    instructor_feedback = Column(Text, nullable=True)  # For manual grading
    ai_feedback = Column(Text, nullable=True)  # For AI-assisted grading

    # Timing
    time_spent_seconds = Column(Integer, nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    attempt = relationship("QuizAttempt", back_populates="responses")
    question = relationship("QuizQuestion", back_populates="responses")

    def __repr__(self):
        return f"<QuizResponse attempt={self.attempt_id} question={self.question_id}>"