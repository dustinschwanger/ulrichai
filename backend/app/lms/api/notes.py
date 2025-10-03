"""
Lesson Notes API - Personal note-taking for students
Simple and efficient note management for better learning
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from ...core.database import get_db
from ..services.auth_service import get_current_user
from ..models import LMSUser, LessonNote

router = APIRouter()


class NoteCreate(BaseModel):
    lessonId: str
    courseId: str
    content: str
    timestamp: Optional[str] = None
    tags: List[str] = []


class NoteUpdate(BaseModel):
    content: str
    tags: List[str] = []


class NoteResponse(BaseModel):
    id: str
    lessonId: str
    courseId: str
    userId: str
    content: str
    timestamp: Optional[str] = None
    tags: List[str]
    createdAt: datetime
    updatedAt: datetime


@router.get("/lessons/{lesson_id}/notes", response_model=List[NoteResponse])
async def get_lesson_notes(
    lesson_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all notes for a lesson.
    Students see only their own notes for privacy.
    Fast retrieval for smooth studying experience.
    """
    notes = db.query(LessonNote).filter(
        LessonNote.lesson_id == lesson_id,
        LessonNote.user_id == current_user.id
    ).order_by(LessonNote.created_at.desc()).all()

    return [
        NoteResponse(
            id=str(note.id),
            lessonId=note.lesson_id,
            courseId=note.course_id,
            userId=str(note.user_id),
            content=note.content,
            timestamp=note.timestamp,
            tags=note.tags or [],
            createdAt=note.created_at,
            updatedAt=note.updated_at
        )
        for note in notes
    ]


@router.post("/lessons/{lesson_id}/notes", response_model=NoteResponse)
async def create_note(
    lesson_id: str,
    note_data: NoteCreate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new note for a lesson.
    Quick and easy - capture thoughts while learning.
    Supports timestamps for video notes.
    """
    note = LessonNote(
        lesson_id=lesson_id,
        course_id=note_data.courseId,
        user_id=current_user.id,
        content=note_data.content,
        timestamp=note_data.timestamp,
        tags=note_data.tags
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return NoteResponse(
        id=str(note.id),
        lessonId=note.lesson_id,
        courseId=note.course_id,
        userId=str(note.user_id),
        content=note.content,
        timestamp=note.timestamp,
        tags=note.tags or [],
        createdAt=note.created_at,
        updatedAt=note.updated_at
    )


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    note_data: NoteUpdate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update your note content and tags.
    Keep notes organized and current.
    """
    note = db.query(LessonNote).filter(LessonNote.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")

    note.content = note_data.content
    note.tags = note_data.tags
    note.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(note)

    return NoteResponse(
        id=str(note.id),
        lessonId=note.lesson_id,
        courseId=note.course_id,
        userId=str(note.user_id),
        content=note.content,
        timestamp=note.timestamp,
        tags=note.tags or [],
        createdAt=note.created_at,
        updatedAt=note.updated_at
    )


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a note.
    Clean up your notes as you learn.
    """
    note = db.query(LessonNote).filter(LessonNote.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")

    db.delete(note)
    db.commit()

    return {"success": True, "message": "Note deleted successfully"}


@router.get("/courses/{course_id}/notes", response_model=List[NoteResponse])
async def get_course_notes(
    course_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all notes across all lessons in a course.
    Review all your notes in one place for exam prep.
    """
    notes = db.query(LessonNote).filter(
        LessonNote.course_id == course_id,
        LessonNote.user_id == current_user.id
    ).order_by(LessonNote.created_at.desc()).all()

    return [
        NoteResponse(
            id=str(note.id),
            lessonId=note.lesson_id,
            courseId=note.course_id,
            userId=str(note.user_id),
            content=note.content,
            timestamp=note.timestamp,
            tags=note.tags or [],
            createdAt=note.created_at,
            updatedAt=note.updated_at
        )
        for note in notes
    ]


@router.get("/notes/search", response_model=List[NoteResponse])
async def search_notes(
    query: str,
    course_id: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search through your notes by content or tags.
    Find information quickly when reviewing for exams.
    Smart search helps recall key concepts.
    """
    search_query = db.query(LessonNote).filter(
        LessonNote.user_id == current_user.id,
        LessonNote.content.ilike(f"%{query}%")
    )

    if course_id:
        search_query = search_query.filter(LessonNote.course_id == course_id)

    if tag:
        search_query = search_query.filter(LessonNote.tags.contains([tag]))

    notes = search_query.order_by(LessonNote.created_at.desc()).all()

    return [
        NoteResponse(
            id=str(note.id),
            lessonId=note.lesson_id,
            courseId=note.course_id,
            userId=str(note.user_id),
            content=note.content,
            timestamp=note.timestamp,
            tags=note.tags or [],
            createdAt=note.created_at,
            updatedAt=note.updated_at
        )
        for note in notes
    ]