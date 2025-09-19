from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# In-memory storage (replace with database in production)
QUESTIONS = {}
ANSWERS = {}
UPVOTES = {
    "questions": {},
    "answers": {}
}

# Mock user for development
MOCK_USER = {
    "id": "user123",
    "name": "Current User",
    "avatar": "CU",
    "isInstructor": False
}


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


@router.get("/lessons/{lesson_id}/questions", response_model=List[QuestionResponse])
async def get_lesson_questions(lesson_id: str):
    """Get all questions for a specific lesson"""
    lesson_questions = []

    for q_id, question in QUESTIONS.items():
        if question["lessonId"] == lesson_id:
            # Get answers for this question
            question_answers = []
            for a_id, answer in ANSWERS.items():
                if answer["questionId"] == q_id:
                    answer_upvotes = UPVOTES["answers"].get(a_id, [])
                    question_answers.append(AnswerResponse(
                        id=a_id,
                        userId=answer["userId"],
                        userName=answer["userName"],
                        userAvatar=answer["userAvatar"],
                        answer=answer["answer"],
                        timestamp=answer["timestamp"],
                        upvotes=len(answer_upvotes),
                        hasUpvoted=MOCK_USER["id"] in answer_upvotes,
                        isInstructor=answer.get("isInstructor", False),
                        isAccepted=answer.get("isAccepted", False)
                    ))

            # Get question upvotes
            question_upvotes = UPVOTES["questions"].get(q_id, [])

            lesson_questions.append(QuestionResponse(
                id=q_id,
                lessonId=question["lessonId"],
                courseId=question["courseId"],
                userId=question["userId"],
                userName=question["userName"],
                userAvatar=question["userAvatar"],
                question=question["question"],
                details=question.get("details"),
                timestamp=question["timestamp"],
                upvotes=len(question_upvotes),
                hasUpvoted=MOCK_USER["id"] in question_upvotes,
                answers=question_answers
            ))

    # Sort by timestamp (newest first)
    lesson_questions.sort(key=lambda x: x.timestamp, reverse=True)
    return lesson_questions


@router.post("/lessons/{lesson_id}/questions", response_model=QuestionResponse)
async def create_question(lesson_id: str, question_data: QuestionCreate):
    """Create a new question for a lesson"""
    question_id = f"q-{str(uuid4())[:8]}"

    question = {
        "lessonId": lesson_id,
        "courseId": question_data.courseId,
        "userId": MOCK_USER["id"],
        "userName": MOCK_USER["name"],
        "userAvatar": MOCK_USER["avatar"],
        "question": question_data.question,
        "details": question_data.details,
        "timestamp": datetime.utcnow()
    }

    QUESTIONS[question_id] = question
    UPVOTES["questions"][question_id] = []

    return QuestionResponse(
        id=question_id,
        **question,
        upvotes=0,
        hasUpvoted=False,
        answers=[]
    )


@router.post("/questions/{question_id}/answers", response_model=AnswerResponse)
async def create_answer(question_id: str, answer_data: AnswerCreate):
    """Create an answer for a question"""
    if question_id not in QUESTIONS:
        raise HTTPException(status_code=404, detail="Question not found")

    answer_id = f"a-{str(uuid4())[:8]}"

    answer = {
        "questionId": question_id,
        "userId": MOCK_USER["id"],
        "userName": MOCK_USER["name"],
        "userAvatar": MOCK_USER["avatar"],
        "answer": answer_data.answer,
        "timestamp": datetime.utcnow(),
        "isInstructor": MOCK_USER.get("isInstructor", False),
        "isAccepted": False
    }

    ANSWERS[answer_id] = answer
    UPVOTES["answers"][answer_id] = []

    return AnswerResponse(
        id=answer_id,
        userId=answer["userId"],
        userName=answer["userName"],
        userAvatar=answer["userAvatar"],
        answer=answer["answer"],
        timestamp=answer["timestamp"],
        upvotes=0,
        hasUpvoted=False,
        isInstructor=answer["isInstructor"],
        isAccepted=answer["isAccepted"]
    )


@router.post("/questions/{question_id}/upvote")
async def upvote_question(question_id: str):
    """Toggle upvote on a question"""
    if question_id not in QUESTIONS:
        raise HTTPException(status_code=404, detail="Question not found")

    if question_id not in UPVOTES["questions"]:
        UPVOTES["questions"][question_id] = []

    upvotes = UPVOTES["questions"][question_id]
    user_id = MOCK_USER["id"]

    if user_id in upvotes:
        upvotes.remove(user_id)
        action = "removed"
    else:
        upvotes.append(user_id)
        action = "added"

    return {
        "success": True,
        "action": action,
        "upvotes": len(upvotes)
    }


@router.post("/answers/{answer_id}/upvote")
async def upvote_answer(answer_id: str):
    """Toggle upvote on an answer"""
    if answer_id not in ANSWERS:
        raise HTTPException(status_code=404, detail="Answer not found")

    if answer_id not in UPVOTES["answers"]:
        UPVOTES["answers"][answer_id] = []

    upvotes = UPVOTES["answers"][answer_id]
    user_id = MOCK_USER["id"]

    if user_id in upvotes:
        upvotes.remove(user_id)
        action = "removed"
    else:
        upvotes.append(user_id)
        action = "added"

    return {
        "success": True,
        "action": action,
        "upvotes": len(upvotes)
    }


@router.put("/answers/{answer_id}/accept")
async def accept_answer(answer_id: str):
    """Mark an answer as accepted (only question author can do this)"""
    if answer_id not in ANSWERS:
        raise HTTPException(status_code=404, detail="Answer not found")

    answer = ANSWERS[answer_id]
    question = QUESTIONS.get(answer["questionId"])

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # In production, check if current user is the question author
    # For now, allow any user to accept

    # Remove accepted status from other answers
    for a_id, a in ANSWERS.items():
        if a["questionId"] == answer["questionId"]:
            a["isAccepted"] = False

    # Mark this answer as accepted
    ANSWERS[answer_id]["isAccepted"] = True

    return {"success": True, "message": "Answer accepted"}