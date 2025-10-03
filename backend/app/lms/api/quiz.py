"""
Quiz API endpoints for creating, managing, and taking quizzes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.core.database import get_db
from app.lms.services.auth_service import get_current_user
from app.lms.models import (
    LMSUser, Quiz, QuizQuestion, QuizAttempt,
    QuizResponse as DBQuizResponse,  # Alias to avoid conflict with Pydantic model
    QuestionType, QuizStatus, ContentItem, Lesson
)
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api/lms/quiz", tags=["LMS Quiz"])


# ============= Pydantic Models =============

class QuestionOption(BaseModel):
    """Option for multiple choice questions"""
    id: str
    text: str


class QuizQuestionCreate(BaseModel):
    """Model for creating a quiz question"""
    question_type: str
    question_text: str
    question_media: Optional[dict] = None
    options: Optional[List[QuestionOption]] = []
    correct_answers: List[str]
    explanation: Optional[str] = None
    hint: Optional[str] = None
    points: float = 1.0
    partial_credit: bool = False
    sequence_order: int
    difficulty_level: int = 3
    tags: List[str] = []


class QuizQuestionUpdate(BaseModel):
    """Model for updating a quiz question"""
    question_type: Optional[str] = None
    question_text: Optional[str] = None
    question_media: Optional[dict] = None
    options: Optional[List[QuestionOption]] = None
    correct_answers: Optional[List[str]] = None
    explanation: Optional[str] = None
    hint: Optional[str] = None
    points: Optional[float] = None
    partial_credit: Optional[bool] = None
    sequence_order: Optional[int] = None
    difficulty_level: Optional[int] = None
    tags: Optional[List[str]] = None


class QuizQuestionResponse(BaseModel):
    """Response model for quiz questions"""
    id: UUID
    quiz_id: UUID
    question_type: str
    question_text: str
    question_media: Optional[dict]
    options: List[dict]
    points: float
    partial_credit: bool
    sequence_order: int
    difficulty_level: int
    tags: List[str]
    hint: Optional[str]
    # Don't include correct_answers in response for students

    class Config:
        from_attributes = True


class QuizCreate(BaseModel):
    """Model for creating a quiz"""
    content_item_id: UUID
    title: str
    instructions: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    attempts_allowed: int = 1
    passing_score: float = 70.0
    shuffle_questions: bool = False
    shuffle_answers: bool = False
    show_correct_answers: bool = True
    show_feedback: bool = True
    allow_review: bool = True
    questions: List[QuizQuestionCreate] = []


class QuizUpdate(BaseModel):
    """Model for updating a quiz"""
    title: Optional[str] = None
    instructions: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    attempts_allowed: Optional[int] = None
    passing_score: Optional[float] = None
    shuffle_questions: Optional[bool] = None
    shuffle_answers: Optional[bool] = None
    show_correct_answers: Optional[bool] = None
    show_feedback: Optional[bool] = None
    allow_review: Optional[bool] = None


class QuizResponse(BaseModel):
    """Response model for quizzes"""
    id: UUID
    content_item_id: UUID
    title: str
    instructions: Optional[str]
    time_limit_minutes: Optional[int]
    attempts_allowed: int
    passing_score: float
    shuffle_questions: bool
    shuffle_answers: bool
    show_correct_answers: bool
    show_feedback: bool
    allow_review: bool
    question_count: int = 0
    total_points: float = 0

    class Config:
        from_attributes = True


class QuizAttemptStart(BaseModel):
    """Model for starting a quiz attempt"""
    quiz_id: UUID


class QuizResponseSubmit(BaseModel):
    """Model for submitting a response to a quiz question"""
    question_id: UUID
    answer: List[str]


class QuizAttemptSubmit(BaseModel):
    """Model for submitting a complete quiz attempt"""
    attempt_id: UUID
    responses: List[QuizResponseSubmit]


class QuizAttemptResponse(BaseModel):
    """Response model for quiz attempts"""
    id: UUID
    quiz_id: UUID
    user_id: UUID
    attempt_number: int
    started_at: datetime
    submitted_at: Optional[datetime]
    time_spent_seconds: Optional[int]
    score: Optional[float]
    points_earned: Optional[float]
    points_possible: Optional[float]
    passed: Optional[bool]
    status: str

    class Config:
        from_attributes = True


class QuizResultResponse(BaseModel):
    """Detailed quiz results after submission"""
    attempt: QuizAttemptResponse
    questions_answered: int
    questions_correct: int
    feedback: Optional[str] = None


# ============= Helper Functions =============

def check_quiz_access(quiz: Quiz, user: LMSUser, db: Session) -> bool:
    """Check if user has access to a quiz"""
    # Instructors always have access (handle both uppercase and lowercase)
    user_role = user.role.upper() if hasattr(user.role, 'upper') else str(user.role).upper()
    if user_role in ["INSTRUCTOR", "ADMIN", "SUPER_ADMIN"]:
        return True

    # Students need to be enrolled in the course
    # For now, we'll assume they have access if the quiz exists
    # TODO: Implement proper enrollment check
    return True


def calculate_quiz_score(attempt: QuizAttempt, db: Session) -> tuple[float, float, float]:
    """Calculate score for a quiz attempt
    Returns: (score_percentage, points_earned, points_possible)
    """
    responses = db.query(DBQuizResponse).filter(
        DBQuizResponse.attempt_id == attempt.id
    ).all()

    points_earned = sum(r.points_earned or 0 for r in responses)

    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == attempt.quiz_id
    ).all()

    points_possible = sum(q.points for q in questions)

    if points_possible > 0:
        score_percentage = (points_earned / points_possible) * 100
    else:
        score_percentage = 0

    return score_percentage, points_earned, points_possible


def grade_response(question: QuizQuestion, answer: List[str]) -> tuple[bool, float]:
    """Grade a single response
    Returns: (is_correct, points_earned)
    """
    if question.question_type == "multiple_choice":
        is_correct = set(answer) == set(question.correct_answers)
        points = question.points if is_correct else 0

    elif question.question_type == "true_false":
        is_correct = answer == question.correct_answers
        points = question.points if is_correct else 0

    elif question.question_type == "short_answer":
        # Check if answer matches any of the acceptable answers (case-insensitive)
        is_correct = any(
            a.lower().strip() in [c.lower().strip() for c in question.correct_answers]
            for a in answer
        )
        points = question.points if is_correct else 0

    else:
        # For essay and other types, manual grading is required
        is_correct = None
        points = 0

    return is_correct, points


# ============= Quiz CRUD Endpoints =============

@router.post("/", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
    quiz_data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Create a new quiz with questions"""
    # Check if user is instructor or admin
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()
    if user_role not in ["INSTRUCTOR", "ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can create quizzes"
        )

    # Verify content item exists
    content_item = db.query(ContentItem).filter(
        ContentItem.id == quiz_data.content_item_id
    ).first()

    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found"
        )

    # Create quiz
    quiz = Quiz(
        content_item_id=quiz_data.content_item_id,
        title=quiz_data.title,
        instructions=quiz_data.instructions,
        time_limit_minutes=quiz_data.time_limit_minutes,
        attempts_allowed=quiz_data.attempts_allowed,
        passing_score=quiz_data.passing_score,
        shuffle_questions=quiz_data.shuffle_questions,
        shuffle_answers=quiz_data.shuffle_answers,
        show_correct_answers=quiz_data.show_correct_answers,
        show_feedback=quiz_data.show_feedback,
        allow_review=quiz_data.allow_review
    )

    db.add(quiz)
    db.flush()

    # Add questions
    total_points = 0
    for q_data in quiz_data.questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_type=q_data.question_type,
            question_text=q_data.question_text,
            question_media=q_data.question_media,
            options=[opt.dict() for opt in q_data.options] if q_data.options else [],
            correct_answers=q_data.correct_answers,
            explanation=q_data.explanation,
            hint=q_data.hint,
            points=q_data.points,
            partial_credit=q_data.partial_credit,
            sequence_order=q_data.sequence_order,
            difficulty_level=q_data.difficulty_level,
            tags=q_data.tags
        )
        db.add(question)
        total_points += q_data.points

    db.commit()
    db.refresh(quiz)

    response = QuizResponse.model_validate(quiz)
    response.question_count = len(quiz_data.questions)
    response.total_points = total_points

    return response


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Get quiz details"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if not check_quiz_access(quiz, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz"
        )

    # Get question count and total points
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).all()

    response = QuizResponse.model_validate(quiz)
    response.question_count = len(questions)
    response.total_points = sum(q.points for q in questions)

    return response


@router.get("/{quiz_id}/questions", response_model=List[QuizQuestionResponse])
def get_quiz_questions(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Get all questions for a quiz (without correct answers for students)"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if not check_quiz_access(quiz, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz"
        )

    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).order_by(QuizQuestion.sequence_order).all()

    return questions


@router.put("/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: UUID,
    quiz_update: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Update quiz settings"""
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()
    if user_role not in ["INSTRUCTOR", "ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can update quizzes"
        )

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    # Update fields
    update_data = quiz_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(quiz, field, value)

    db.commit()
    db.refresh(quiz)

    # Get question count and total points
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz_id
    ).all()

    response = QuizResponse.model_validate(quiz)
    response.question_count = len(questions)
    response.total_points = sum(q.points for q in questions)

    return response


@router.delete("/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Delete a quiz and all related data"""
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()
    if user_role not in ["INSTRUCTOR", "ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can delete quizzes"
        )

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    db.delete(quiz)
    db.commit()


# ============= Quiz Lookup Endpoints =============

@router.get("/by-content-item/{content_item_id}", response_model=QuizResponse)
def get_quiz_by_content_item(
    content_item_id: UUID,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Get quiz by content item ID"""
    quiz = db.query(Quiz).filter(Quiz.content_item_id == content_item_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found for this content item"
        )

    if not check_quiz_access(quiz, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz"
        )

    # Get question count and total points
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == quiz.id
    ).all()

    response = QuizResponse.model_validate(quiz)
    response.question_count = len(questions)
    response.total_points = sum(q.points for q in questions)

    return response


# ============= Quiz Taking Endpoints =============

@router.post("/attempt/start", response_model=QuizAttemptResponse)
def start_quiz_attempt(
    attempt_data: QuizAttemptStart,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Start a new quiz attempt"""
    quiz = db.query(Quiz).filter(Quiz.id == attempt_data.quiz_id).first()

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )

    if not check_quiz_access(quiz, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this quiz"
        )

    # Check previous attempts
    previous_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == attempt_data.quiz_id,
        QuizAttempt.user_id == current_user.id
    ).count()

    if quiz.attempts_allowed != -1 and previous_attempts >= quiz.attempts_allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum attempts ({quiz.attempts_allowed}) reached"
        )

    # Create new attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=attempt_data.quiz_id,
        attempt_number=previous_attempts + 1,
        status=QuizStatus.IN_PROGRESS.value
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


@router.post("/attempt/submit", response_model=QuizResultResponse)
def submit_quiz_attempt(
    submission: QuizAttemptSubmit,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Submit a completed quiz attempt with all responses"""
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == submission.attempt_id,
        QuizAttempt.user_id == current_user.id
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found"
        )

    if attempt.status != QuizStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This quiz attempt has already been submitted"
        )

    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()

    # Process each response
    questions_correct = 0
    for response_data in submission.responses:
        question = db.query(QuizQuestion).filter(
            QuizQuestion.id == response_data.question_id,
            QuizQuestion.quiz_id == attempt.quiz_id
        ).first()

        if not question:
            continue

        # Grade the response
        is_correct, points_earned = grade_response(question, response_data.answer)

        if is_correct:
            questions_correct += 1

        # Save the response
        response = DBQuizResponse(
            attempt_id=attempt.id,
            question_id=question.id,
            answer=response_data.answer,
            is_correct=is_correct,
            points_earned=points_earned,
            answered_at=datetime.now(timezone.utc)
        )
        db.add(response)

    # Flush to ensure responses are available for scoring
    db.flush()

    # Calculate final score
    score, points_earned, points_possible = calculate_quiz_score(attempt, db)

    # Update attempt
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.time_spent_seconds = int((attempt.submitted_at - attempt.started_at).total_seconds())
    attempt.score = score
    attempt.points_earned = points_earned
    attempt.points_possible = points_possible
    attempt.passed = score >= quiz.passing_score
    attempt.status = QuizStatus.GRADED.value

    db.commit()
    db.refresh(attempt)

    # Prepare result
    result = QuizResultResponse(
        attempt=QuizAttemptResponse.model_validate(attempt),
        questions_answered=len(submission.responses),
        questions_correct=questions_correct,
        feedback="Congratulations!" if attempt.passed else "Keep studying and try again!"
    )

    return result


@router.get("/attempts/my", response_model=List[QuizAttemptResponse])
def get_my_attempts(
    quiz_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Get current user's quiz attempts"""
    query = db.query(QuizAttempt).filter(
        QuizAttempt.user_id == current_user.id
    )

    if quiz_id:
        query = query.filter(QuizAttempt.quiz_id == quiz_id)

    attempts = query.order_by(QuizAttempt.started_at.desc()).all()

    return attempts


@router.get("/attempt/{attempt_id}/review")
def review_quiz_attempt(
    attempt_id: UUID,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Review a completed quiz attempt with questions and responses"""
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found"
        )

    # Check access: user can review their own attempts, instructors can review all
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()
    if attempt.user_id != current_user.id and user_role not in ["INSTRUCTOR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to review this attempt"
        )

    quiz = db.query(Quiz).filter(Quiz.id == attempt.quiz_id).first()

    if not quiz.allow_review and user_role not in ["INSTRUCTOR", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Review is not allowed for this quiz"
        )

    # Get all questions and responses
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.quiz_id == attempt.quiz_id
    ).order_by(QuizQuestion.sequence_order).all()

    responses = db.query(DBQuizResponse).filter(
        DBQuizResponse.attempt_id == attempt_id
    ).all()

    response_map = {r.question_id: r for r in responses}

    # Build review data
    review_data = {
        "attempt": QuizAttemptResponse.model_validate(attempt),
        "quiz_title": quiz.title,
        "questions": []
    }

    for question in questions:
        q_data = {
            "question": QuizQuestionResponse.model_validate(question),
            "user_response": None,
            "is_correct": None,
            "points_earned": 0,
            "correct_answers": question.correct_answers if quiz.show_correct_answers else None,
            "explanation": question.explanation if quiz.show_feedback else None
        }

        if question.id in response_map:
            resp = response_map[question.id]
            q_data["user_response"] = resp.answer
            q_data["is_correct"] = resp.is_correct
            q_data["points_earned"] = float(resp.points_earned) if resp.points_earned else 0

        review_data["questions"].append(q_data)

    return review_data