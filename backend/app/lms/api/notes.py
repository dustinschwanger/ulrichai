from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import uuid4

router = APIRouter()

# In-memory storage (replace with database in production)
NOTES = {}

# Mock user for development
MOCK_USER = {
    "id": "user123",
    "name": "Current User",
    "avatar": "CU"
}


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
async def get_lesson_notes(lesson_id: str):
    """Get all notes for a specific lesson for the current user"""
    user_notes = []

    for note_id, note in NOTES.items():
        if note["lessonId"] == lesson_id and note["userId"] == MOCK_USER["id"]:
            user_notes.append(NoteResponse(
                id=note_id,
                lessonId=note["lessonId"],
                courseId=note["courseId"],
                userId=note["userId"],
                content=note["content"],
                timestamp=note.get("timestamp"),
                tags=note["tags"],
                createdAt=note["createdAt"],
                updatedAt=note["updatedAt"]
            ))

    # Sort by creation time (newest first)
    user_notes.sort(key=lambda x: x.createdAt, reverse=True)
    return user_notes


@router.post("/lessons/{lesson_id}/notes", response_model=NoteResponse)
async def create_note(lesson_id: str, note_data: NoteCreate):
    """Create a new note for a lesson"""
    note_id = f"note-{str(uuid4())[:8]}"

    note = {
        "lessonId": lesson_id,
        "courseId": note_data.courseId,
        "userId": MOCK_USER["id"],
        "content": note_data.content,
        "timestamp": note_data.timestamp,
        "tags": note_data.tags,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    NOTES[note_id] = note

    return NoteResponse(
        id=note_id,
        **note
    )


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_data: NoteUpdate):
    """Update an existing note"""
    if note_id not in NOTES:
        raise HTTPException(status_code=404, detail="Note not found")

    note = NOTES[note_id]

    # Verify ownership
    if note["userId"] != MOCK_USER["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to update this note")

    # Update note
    note["content"] = note_data.content
    note["tags"] = note_data.tags
    note["updatedAt"] = datetime.utcnow()

    return NoteResponse(
        id=note_id,
        **note
    )


@router.delete("/notes/{note_id}")
async def delete_note(note_id: str):
    """Delete a note"""
    if note_id not in NOTES:
        raise HTTPException(status_code=404, detail="Note not found")

    note = NOTES[note_id]

    # Verify ownership
    if note["userId"] != MOCK_USER["id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this note")

    del NOTES[note_id]
    return {"success": True, "message": "Note deleted successfully"}


@router.get("/courses/{course_id}/notes", response_model=List[NoteResponse])
async def get_course_notes(course_id: str):
    """Get all notes for a specific course for the current user"""
    course_notes = []

    for note_id, note in NOTES.items():
        if note["courseId"] == course_id and note["userId"] == MOCK_USER["id"]:
            course_notes.append(NoteResponse(
                id=note_id,
                lessonId=note["lessonId"],
                courseId=note["courseId"],
                userId=note["userId"],
                content=note["content"],
                timestamp=note.get("timestamp"),
                tags=note["tags"],
                createdAt=note["createdAt"],
                updatedAt=note["updatedAt"]
            ))

    # Sort by creation time (newest first)
    course_notes.sort(key=lambda x: x.createdAt, reverse=True)
    return course_notes


@router.get("/notes/search")
async def search_notes(query: str, course_id: Optional[str] = None, tag: Optional[str] = None):
    """Search notes by content, optionally filter by course or tag"""
    results = []

    for note_id, note in NOTES.items():
        # Only search user's own notes
        if note["userId"] != MOCK_USER["id"]:
            continue

        # Apply filters
        if course_id and note["courseId"] != course_id:
            continue

        if tag and tag not in note["tags"]:
            continue

        # Search in content
        if query.lower() in note["content"].lower():
            results.append(NoteResponse(
                id=note_id,
                lessonId=note["lessonId"],
                courseId=note["courseId"],
                userId=note["userId"],
                content=note["content"],
                timestamp=note.get("timestamp"),
                tags=note["tags"],
                createdAt=note["createdAt"],
                updatedAt=note["updatedAt"]
            ))

    return results