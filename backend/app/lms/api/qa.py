from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func

from ...core.database import get_db
from ..services.auth_service import get_current_user
from ..models import LMSUser
from ..models.qa import LessonQuestion, QuestionAnswer, question_upvotes, answer_upvotes

router = APIRouter()


class QuestionCreate(BaseModel):
    lessonId: str
    courseId: str
    question: str
    details: Optional[str] = None


class AnswerCreate(BaseModel):
    questionId: str
    answer: str


class QuestionResponse(BaseModel):
    id: str
    lessonId: str
    courseId: str
    userId: str
    userName: str
    userAvatar: str
    question: str
    details: Optional[str] = None
    timestamp: datetime
    upvotes: int
    hasUpvoted: bool
    answers: List['AnswerResponse'] = []


class AnswerResponse(BaseModel):
    id: str
    userId: str
    userName: str
    userAvatar: str
    answer: str
    timestamp: datetime
    upvotes: int
    hasUpvoted: bool
    isInstructor: bool = False
    isAccepted: bool = False


# Allow forward references
QuestionResponse.model_rebuild()


def _user_avatar(user: LMSUser) -> str:
    """Generate user avatar from user name"""
    if user.first_name and user.last_name:
        return f"{user.first_name[0].upper()}{user.last_name[0].upper()}"
    elif user.email:
        return user.email[:2].upper()
    return "U"


def _user_name(user: LMSUser) -> str:
    """Generate display name for user"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.email


@router.get("/lessons/{lesson_id}/questions", response_model=List[QuestionResponse])
async def get_lesson_questions(
    lesson_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all questions for a lesson to help students learn and get help.
    See what other learners have asked and find answers to common questions.
    """
    # Get questions with their authors and answers
    questions = db.query(LessonQuestion)\
        .options(
            joinedload(LessonQuestion.user),
            joinedload(LessonQuestion.answers).joinedload(QuestionAnswer.user),
            joinedload(LessonQuestion.upvoters)
        )\
        .filter(LessonQuestion.lesson_id == lesson_id)\
        .order_by(desc(LessonQuestion.created_at))\
        .all()

    result = []
    for question in questions:
        # Count upvotes and check if current user has upvoted
        question_upvote_count = len(question.upvoters)
        has_upvoted_question = current_user in question.upvoters

        # Process answers
        question_answers = []
        for answer in question.answers:
            answer_upvote_count = len(answer.upvoters)
            has_upvoted_answer = current_user in answer.upvoters

            question_answers.append(AnswerResponse(
                id=str(answer.id),
                userId=str(answer.user_id),
                userName=_user_name(answer.user),
                userAvatar=_user_avatar(answer.user),
                answer=answer.answer,
                timestamp=answer.created_at,
                upvotes=answer_upvote_count,
                hasUpvoted=has_upvoted_answer,
                isInstructor=answer.is_instructor,
                isAccepted=answer.is_accepted
            ))

        # Sort answers: instructor answers first, then by accepted status and upvotes
        question_answers.sort(key=lambda x: (
            not x.isInstructor,  # Instructor answers first
            not x.isAccepted,    # Accepted answers next
            -x.upvotes           # Then by upvotes (descending)
        ))

        result.append(QuestionResponse(
            id=str(question.id),
            lessonId=question.lesson_id,
            courseId=question.course_id,
            userId=str(question.user_id),
            userName=_user_name(question.user),
            userAvatar=_user_avatar(question.user),
            question=question.question,
            details=question.details,
            timestamp=question.created_at,
            upvotes=question_upvote_count,
            hasUpvoted=has_upvoted_question,
            answers=question_answers
        ))

    return result


@router.post("/lessons/{lesson_id}/questions", response_model=QuestionResponse)
async def create_question(
    lesson_id: str,
    question_data: QuestionCreate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ask a question about the lesson content to get help from peers and instructors.
    Don't hesitate to ask - other students often have the same questions!
    """
    # Create new question
    new_question = LessonQuestion(
        lesson_id=lesson_id,
        course_id=question_data.courseId,
        user_id=current_user.id,
        question=question_data.question,
        details=question_data.details
    )

    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    # Load the user relationship
    db.refresh(new_question, ['user'])

    return QuestionResponse(
        id=str(new_question.id),
        lessonId=new_question.lesson_id,
        courseId=new_question.course_id,
        userId=str(new_question.user_id),
        userName=_user_name(new_question.user),
        userAvatar=_user_avatar(new_question.user),
        question=new_question.question,
        details=new_question.details,
        timestamp=new_question.created_at,
        upvotes=0,
        hasUpvoted=False,
        answers=[]
    )


@router.post("/questions/{question_id}/answers", response_model=AnswerResponse)
async def create_answer(
    question_id: str,
    answer_data: AnswerCreate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Help a fellow learner by providing an answer to their question.
    Share your knowledge and contribute to the learning community!
    """
    # Verify question exists
    question = db.query(LessonQuestion).filter(LessonQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Determine if user is instructor
    is_instructor = current_user.role.value in ['instructor', 'admin', 'super_admin']

    # Create new answer
    new_answer = QuestionAnswer(
        question_id=question.id,
        user_id=current_user.id,
        answer=answer_data.answer,
        is_instructor=is_instructor
    )

    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    # Load the user relationship
    db.refresh(new_answer, ['user'])

    return AnswerResponse(
        id=str(new_answer.id),
        userId=str(new_answer.user_id),
        userName=_user_name(new_answer.user),
        userAvatar=_user_avatar(new_answer.user),
        answer=new_answer.answer,
        timestamp=new_answer.created_at,
        upvotes=0,
        hasUpvoted=False,
        isInstructor=new_answer.is_instructor,
        isAccepted=new_answer.is_accepted
    )


@router.post("/questions/{question_id}/upvote")
async def upvote_question(
    question_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upvote a helpful question to help other students find important discussions.
    Your votes help highlight the most valuable learning conversations.
    """
    # Verify question exists
    question = db.query(LessonQuestion).filter(LessonQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check if user has already upvoted
    existing_upvote = db.query(question_upvotes)\
        .filter(question_upvotes.c.user_id == current_user.id)\
        .filter(question_upvotes.c.question_id == question.id)\
        .first()

    if existing_upvote:
        # Remove upvote
        db.execute(
            question_upvotes.delete().where(
                (question_upvotes.c.user_id == current_user.id) &
                (question_upvotes.c.question_id == question.id)
            )
        )
        action = "removed"
    else:
        # Add upvote
        db.execute(
            question_upvotes.insert().values(
                user_id=current_user.id,
                question_id=question.id
            )
        )
        action = "added"

    db.commit()

    # Get updated upvote count
    upvote_count = db.query(func.count(question_upvotes.c.user_id))\
        .filter(question_upvotes.c.question_id == question.id)\
        .scalar()

    return {
        "success": True,
        "action": action,
        "upvotes": upvote_count
    }


@router.post("/answers/{answer_id}/upvote")
async def upvote_answer(
    answer_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upvote helpful answers to highlight the most valuable responses.
    Your votes help other students find the best explanations and solutions.
    """
    # Verify answer exists
    answer = db.query(QuestionAnswer).filter(QuestionAnswer.id == answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Check if user has already upvoted
    existing_upvote = db.query(answer_upvotes)\
        .filter(answer_upvotes.c.user_id == current_user.id)\
        .filter(answer_upvotes.c.answer_id == answer.id)\
        .first()

    if existing_upvote:
        # Remove upvote
        db.execute(
            answer_upvotes.delete().where(
                (answer_upvotes.c.user_id == current_user.id) &
                (answer_upvotes.c.answer_id == answer.id)
            )
        )
        action = "removed"
    else:
        # Add upvote
        db.execute(
            answer_upvotes.insert().values(
                user_id=current_user.id,
                answer_id=answer.id
            )
        )
        action = "added"

    db.commit()

    # Get updated upvote count
    upvote_count = db.query(func.count(answer_upvotes.c.user_id))\
        .filter(answer_upvotes.c.answer_id == answer.id)\
        .scalar()

    return {
        "success": True,
        "action": action,
        "upvotes": upvote_count
    }


@router.put("/answers/{answer_id}/accept")
async def accept_answer(
    answer_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark an answer as the accepted solution to help other students find the best response.
    Only the person who asked the question can accept answers.
    """
    # Get the answer and its question
    answer = db.query(QuestionAnswer)\
        .options(joinedload(QuestionAnswer.question))\
        .filter(QuestionAnswer.id == answer_id)\
        .first()

    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Check if current user is the question author
    if answer.question.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the question author can accept answers")

    # Remove accepted status from other answers for this question
    db.query(QuestionAnswer)\
        .filter(QuestionAnswer.question_id == answer.question_id)\
        .update({"is_accepted": False})

    # Mark this answer as accepted
    answer.is_accepted = True

    db.commit()

    return {"success": True, "message": "Answer accepted successfully"}