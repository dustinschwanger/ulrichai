"""
Discussions API - Course discussion forums and threads
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from ...core.database import get_db
from ..services.auth_service import get_current_user, require_role
from ..models import (
    LMSUser, Course, Enrollment,
    DiscussionThread, DiscussionReply, DiscussionUpvote
)

router = APIRouter(
    prefix="/api/lms/discussions",
    tags=["Discussions"]
)

# Pydantic models for request/response

class DiscussionThreadCreate(BaseModel):
    course_id: UUID
    lesson_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    category: Optional[str] = Field(None, pattern="^(general|question|announcement|resource)$")
    is_pinned: bool = False
    is_locked: bool = False

class DiscussionThreadUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, pattern="^(general|question|announcement|resource)$")
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_resolved: Optional[bool] = None

class DiscussionReplyCreate(BaseModel):
    content: str = Field(..., min_length=1)
    parent_reply_id: Optional[UUID] = None
    is_answer: bool = False

class DiscussionReplyUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    is_answer: Optional[bool] = None

class DiscussionThreadResponse(BaseModel):
    id: UUID
    course_id: UUID
    lesson_id: Optional[UUID]
    author_id: UUID
    author: dict
    title: str
    content: str
    category: Optional[str]
    is_pinned: bool
    is_locked: bool
    is_resolved: bool
    reply_count: int
    last_activity: datetime
    created_at: datetime
    updated_at: datetime

class DiscussionReplyResponse(BaseModel):
    id: UUID
    thread_id: UUID
    author_id: UUID
    author: dict
    content: str
    parent_reply_id: Optional[UUID]
    is_answer: bool
    upvotes: int
    created_at: datetime
    updated_at: datetime
    replies: List['DiscussionReplyResponse'] = []

# Update forward references
DiscussionReplyResponse.model_rebuild()

def build_author_dict(user: LMSUser) -> dict:
    """Build consistent author info dict for responses"""
    if not user:
        return {"id": "", "first_name": "Unknown", "last_name": "", "email": ""}
    return {
        "id": str(user.id),
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "email": user.email or ""
    }

def check_course_access(db: Session, user: LMSUser, course_id: UUID) -> tuple[bool, bool]:
    """
    Check if user has access to course and their role.
    Returns (has_access, is_instructor) tuple.
    Fast permission checking for discussion access.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return False, False

    user_role = user.role.upper() if hasattr(user.role, 'upper') else str(user.role).upper()
    is_instructor = course.instructor_id == user.id or user_role in ["ADMIN", "SUPER_ADMIN"]

    if is_instructor:
        return True, True

    # Check enrollment for students
    enrollment = db.query(Enrollment).join(Enrollment.cohort).filter(
        Enrollment.user_id == user.id,
        Enrollment.cohort.has(course_version_id=course.versions[0].id if course.versions else None)
    ).first()

    return enrollment is not None, False

# Discussion Thread CRUD Operations

@router.post("/threads", response_model=DiscussionThreadResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion_thread(
    thread_data: DiscussionThreadCreate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a discussion thread.
    Simple and quick - students can start discussions easily.
    Instructors can pin/lock threads for announcements.
    """
    has_access, is_instructor = check_course_access(db, current_user, thread_data.course_id)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="Enroll in the course to participate in discussions"
        )

    thread = DiscussionThread(
        course_id=thread_data.course_id,
        lesson_id=thread_data.lesson_id,
        author_id=current_user.id,
        title=thread_data.title,
        content=thread_data.content,
        category=thread_data.category or "general",
        is_pinned=thread_data.is_pinned if is_instructor else False,
        is_locked=thread_data.is_locked if is_instructor else False
    )

    db.add(thread)
    db.commit()
    db.refresh(thread)

    return DiscussionThreadResponse(
        id=thread.id,
        course_id=thread.course_id,
        lesson_id=thread.lesson_id,
        author_id=thread.author_id,
        author=build_author_dict(current_user),
        title=thread.title,
        content=thread.content,
        category=thread.category,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        is_resolved=thread.is_resolved,
        reply_count=0,
        last_activity=thread.last_activity_at,
        created_at=thread.created_at,
        updated_at=thread.updated_at
    )

@router.get("/threads", response_model=List[DiscussionThreadResponse])
async def get_discussion_threads(
    course_id: UUID,
    lesson_id: Optional[UUID] = None,
    category: Optional[str] = None,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all discussion threads for a course/lesson.
    Optimized with eager loading for fast display.
    Pinned threads always appear first for visibility.
    """
    has_access, _ = check_course_access(db, current_user, course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to course discussions")

    query = db.query(DiscussionThread).options(
        joinedload(DiscussionThread.author)
    ).filter(DiscussionThread.course_id == course_id)

    if lesson_id:
        query = query.filter(DiscussionThread.lesson_id == lesson_id)
    if category:
        query = query.filter(DiscussionThread.category == category)

    query = query.order_by(
        DiscussionThread.is_pinned.desc(),
        DiscussionThread.last_activity_at.desc()
    )

    threads = query.all()

    return [
        DiscussionThreadResponse(
            id=t.id,
            course_id=t.course_id,
            lesson_id=t.lesson_id,
            author_id=t.author_id,
            author=build_author_dict(t.author),
            title=t.title,
            content=t.content,
            category=t.category,
            is_pinned=t.is_pinned,
            is_locked=t.is_locked,
            is_resolved=t.is_resolved,
            reply_count=t.reply_count,
            last_activity=t.last_activity_at,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in threads
    ]

@router.get("/threads/{thread_id}", response_model=DiscussionThreadResponse)
async def get_discussion_thread(
    thread_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get single thread details with author info.
    Fast loading with optimized queries for smooth user experience.
    """
    thread = db.query(DiscussionThread).options(
        joinedload(DiscussionThread.author)
    ).filter(DiscussionThread.id == thread_id).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    has_access, _ = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    return DiscussionThreadResponse(
        id=thread.id,
        course_id=thread.course_id,
        lesson_id=thread.lesson_id,
        author_id=thread.author_id,
        author=build_author_dict(thread.author),
        title=thread.title,
        content=thread.content,
        category=thread.category,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        is_resolved=thread.is_resolved,
        reply_count=thread.reply_count,
        last_activity=thread.last_activity_at,
        created_at=thread.created_at,
        updated_at=thread.updated_at
    )

@router.put("/threads/{thread_id}", response_model=DiscussionThreadResponse)
async def update_discussion_thread(
    thread_id: UUID,
    thread_data: DiscussionThreadUpdate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a discussion thread.
    Authors can edit content, instructors control moderation features.
    Clear permission model keeps discussions organized.
    """
    thread = db.query(DiscussionThread).options(
        joinedload(DiscussionThread.author)
    ).filter(DiscussionThread.id == thread_id).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    has_access, is_instructor = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    is_author = thread.author_id == current_user.id
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()

    # Check permissions - author can edit content, instructor can moderate
    if not is_author and not is_instructor and user_role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this thread"
        )

    # Update fields based on permissions
    update_data = thread_data.dict(exclude_unset=True)

    # Only instructors can change moderation settings
    if not is_instructor and user_role not in ["ADMIN", "SUPER_ADMIN"]:
        update_data.pop("is_pinned", None)
        update_data.pop("is_locked", None)
        update_data.pop("is_resolved", None)

    for field, value in update_data.items():
        setattr(thread, field, value)

    thread.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(thread)

    return DiscussionThreadResponse(
        id=thread.id,
        course_id=thread.course_id,
        lesson_id=thread.lesson_id,
        author_id=thread.author_id,
        author=build_author_dict(thread.author),
        title=thread.title,
        content=thread.content,
        category=thread.category,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        is_resolved=thread.is_resolved,
        reply_count=thread.reply_count,
        last_activity=thread.last_activity_at,
        created_at=thread.created_at,
        updated_at=thread.updated_at
    )

@router.delete("/threads/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion_thread(
    thread_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a discussion thread and all replies.
    Cascade delete ensures clean removal.
    Only authors and instructors can delete for moderation.
    """
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    has_access, is_instructor = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    is_author = thread.author_id == current_user.id
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()

    if not is_author and not is_instructor and user_role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this thread"
        )

    # Delete thread (cascade will handle replies and upvotes)
    db.delete(thread)
    db.commit()

# Discussion Reply CRUD Operations

@router.post("/threads/{thread_id}/replies", response_model=DiscussionReplyResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion_reply(
    thread_id: UUID,
    reply_data: DiscussionReplyCreate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a reply to a discussion thread.
    Students engage easily, instructors can mark solutions.
    Updates thread activity for fresh discussions.
    """
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    has_access, is_instructor = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    if thread.is_locked:
        raise HTTPException(
            status_code=403,
            detail="This thread is locked and cannot accept new replies"
        )

    # Validate parent reply exists if specified
    if reply_data.parent_reply_id:
        parent_reply = db.query(DiscussionReply).filter(
            DiscussionReply.id == reply_data.parent_reply_id,
            DiscussionReply.thread_id == thread_id
        ).first()
        if not parent_reply:
            raise HTTPException(status_code=404, detail="Parent reply not found")

    # Create reply
    reply = DiscussionReply(
        thread_id=thread_id,
        author_id=current_user.id,
        content=reply_data.content,
        parent_reply_id=reply_data.parent_reply_id,
        is_solution=reply_data.is_answer if is_instructor else False
    )

    db.add(reply)

    # Update thread activity and reply count
    thread.reply_count += 1
    thread.last_activity_at = datetime.now(timezone.utc)

    # Mark thread as resolved if this is marked as solution by instructor
    if reply_data.is_answer and is_instructor:
        thread.is_resolved = True

    db.commit()
    db.refresh(reply)

    return DiscussionReplyResponse(
        id=reply.id,
        thread_id=reply.thread_id,
        author_id=reply.author_id,
        author=build_author_dict(current_user),
        content=reply.content,
        parent_reply_id=reply.parent_reply_id,
        is_answer=reply.is_solution,
        upvotes=reply.upvotes,
        created_at=reply.created_at,
        updated_at=reply.updated_at,
        replies=[]
    )

@router.get("/threads/{thread_id}/replies", response_model=List[DiscussionReplyResponse])
async def get_discussion_replies(
    thread_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all replies for a discussion thread.
    Builds reply tree for nested conversations.
    Solutions appear first for quick help.
    """
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == thread_id).first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    has_access, _ = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    # Get all replies for this thread with authors
    replies = db.query(DiscussionReply).options(
        joinedload(DiscussionReply.author)
    ).filter(DiscussionReply.thread_id == thread_id).all()

    # Build reply tree structure
    reply_map = {}
    root_replies = []

    # First pass: create all reply objects
    for reply in replies:
        reply_obj = DiscussionReplyResponse(
            id=reply.id,
            thread_id=reply.thread_id,
            author_id=reply.author_id,
            author=build_author_dict(reply.author),
            content=reply.content,
            parent_reply_id=reply.parent_reply_id,
            is_answer=reply.is_solution,
            upvotes=reply.upvotes,
            created_at=reply.created_at,
            updated_at=reply.updated_at,
            replies=[]
        )
        reply_map[reply.id] = reply_obj

    # Second pass: build tree structure
    for reply_id, reply_obj in reply_map.items():
        if reply_obj.parent_reply_id and reply_obj.parent_reply_id in reply_map:
            reply_map[reply_obj.parent_reply_id].replies.append(reply_obj)
        else:
            root_replies.append(reply_obj)

    # Sort root replies: solutions first, then by upvotes and date
    root_replies.sort(key=lambda x: (-x.is_answer, -x.upvotes, x.created_at))

    # Sort nested replies by upvotes and date
    def sort_nested_replies(replies_list):
        replies_list.sort(key=lambda x: (-x.upvotes, x.created_at))
        for reply in replies_list:
            if reply.replies:
                sort_nested_replies(reply.replies)

    sort_nested_replies(root_replies)

    return root_replies

@router.post("/replies/{reply_id}/upvote", response_model=dict)
async def upvote_reply(
    reply_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle upvote on a reply.
    Simple interaction for community engagement.
    Prevents duplicate votes per user.
    """
    reply = db.query(DiscussionReply).filter(DiscussionReply.id == reply_id).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    # Check access to the thread/course
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == reply.thread_id).first()
    has_access, _ = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    # Check if user already upvoted this reply
    existing_upvote = db.query(DiscussionUpvote).filter(
        DiscussionUpvote.user_id == current_user.id,
        DiscussionUpvote.reply_id == reply_id
    ).first()

    if existing_upvote:
        # Remove upvote
        db.delete(existing_upvote)
        reply.upvotes = max(0, reply.upvotes - 1)
        action = "removed"
    else:
        # Add upvote
        upvote = DiscussionUpvote(
            user_id=current_user.id,
            reply_id=reply_id
        )
        db.add(upvote)
        reply.upvotes += 1
        action = "added"

    db.commit()
    db.refresh(reply)

    return {"message": f"Upvote {action}", "upvotes": reply.upvotes}

@router.put("/replies/{reply_id}", response_model=DiscussionReplyResponse)
async def update_discussion_reply(
    reply_id: UUID,
    reply_data: DiscussionReplyUpdate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a discussion reply.
    Authors edit content, instructors mark solutions.
    Keeps conversations accurate and helpful.
    """
    reply = db.query(DiscussionReply).options(
        joinedload(DiscussionReply.author)
    ).filter(DiscussionReply.id == reply_id).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    # Check access and permissions
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == reply.thread_id).first()
    has_access, is_instructor = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    is_author = reply.author_id == current_user.id
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()

    if not is_author and not is_instructor and user_role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this reply"
        )

    # Update fields based on permissions
    update_data = reply_data.dict(exclude_unset=True)

    # Only instructors can mark as solution
    if not is_instructor and user_role not in ["ADMIN", "SUPER_ADMIN"]:
        update_data.pop("is_answer", None)

    for field, value in update_data.items():
        if field == "is_answer":
            reply.is_solution = value
        else:
            setattr(reply, field, value)

    reply.updated_at = datetime.now(timezone.utc)

    # Update thread resolved status if marking as solution
    if "is_answer" in update_data and update_data["is_answer"] and is_instructor:
        thread.is_resolved = True

    db.commit()
    db.refresh(reply)

    return DiscussionReplyResponse(
        id=reply.id,
        thread_id=reply.thread_id,
        author_id=reply.author_id,
        author=build_author_dict(reply.author),
        content=reply.content,
        parent_reply_id=reply.parent_reply_id,
        is_answer=reply.is_solution,
        upvotes=reply.upvotes,
        created_at=reply.created_at,
        updated_at=reply.updated_at,
        replies=[]
    )

@router.delete("/replies/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion_reply(
    reply_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a discussion reply and its children.
    Maintains conversation flow while allowing moderation.
    Updates thread reply count automatically.
    """
    reply = db.query(DiscussionReply).filter(DiscussionReply.id == reply_id).first()

    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")

    # Check access and permissions
    thread = db.query(DiscussionThread).filter(DiscussionThread.id == reply.thread_id).first()
    has_access, is_instructor = check_course_access(db, current_user, thread.course_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to this discussion")

    is_author = reply.author_id == current_user.id
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()

    if not is_author and not is_instructor and user_role not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this reply"
        )

    # Count replies to delete (including nested ones)
    def count_replies_to_delete(reply_id: UUID) -> int:
        child_replies = db.query(DiscussionReply).filter(
            DiscussionReply.parent_reply_id == reply_id
        ).all()

        count = 1  # Count this reply
        for child in child_replies:
            count += count_replies_to_delete(child.id)

        return count

    replies_deleted = count_replies_to_delete(reply_id)

    # Delete reply (cascade will handle children and upvotes)
    db.delete(reply)

    # Update thread reply count
    thread.reply_count = max(0, thread.reply_count - replies_deleted)

    db.commit()