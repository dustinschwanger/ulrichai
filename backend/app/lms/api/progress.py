from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

from ...core.database import get_db
from ..services.auth_service import get_current_user
from ..models import (
    LMSUser,
    LessonProgress,
    ContentProgress,
    ModuleProgress,
    Lesson,
    Module,
    Enrollment,
    ContentItem
)

router = APIRouter()


class ContentProgressUpdate(BaseModel):
    progressPercentage: int
    lastPosition: Optional[dict] = None
    completed: Optional[bool] = False


class LessonProgressResponse(BaseModel):
    id: str
    lessonId: str
    status: str
    progressPercentage: int
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    timeSpentSeconds: int
    lastAccessedAt: datetime


class ContentProgressResponse(BaseModel):
    id: str
    contentItemId: str
    progressPercentage: int
    status: str
    lastPosition: Optional[dict] = None
    completed: bool
    completedAt: Optional[datetime] = None


class CourseProgressResponse(BaseModel):
    enrollmentId: str
    courseId: str
    overallProgress: int
    completedLessons: int
    totalLessons: int
    completedModules: int
    totalModules: int
    modules: List[dict] = []


@router.get("/lessons/{lesson_id}/progress", response_model=LessonProgressResponse)
async def get_lesson_progress(
    lesson_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id,
        LessonProgress.enrollment_id == enrollment.id
    ).first()

    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=UUID(lesson_id),
            enrollment_id=enrollment.id,
            status="not_started",
            progress_percentage=0,
            time_spent_seconds=0
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)

    return LessonProgressResponse(
        id=str(progress.id),
        lessonId=str(progress.lesson_id),
        status=progress.status,
        progressPercentage=progress.progress_percentage,
        startedAt=progress.started_at,
        completedAt=progress.completed_at,
        timeSpentSeconds=progress.time_spent_seconds,
        lastAccessedAt=progress.last_accessed_at
    )


@router.post("/lessons/{lesson_id}/start", response_model=LessonProgressResponse)
async def start_lesson(
    lesson_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id,
        LessonProgress.enrollment_id == enrollment.id
    ).first()

    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=UUID(lesson_id),
            enrollment_id=enrollment.id,
            status="in_progress",
            progress_percentage=0,
            time_spent_seconds=0,
            started_at=datetime.utcnow()
        )
        db.add(progress)
    elif progress.status == "not_started":
        progress.status = "in_progress"
        progress.started_at = datetime.utcnow()

    progress.last_accessed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    return LessonProgressResponse(
        id=str(progress.id),
        lessonId=str(progress.lesson_id),
        status=progress.status,
        progressPercentage=progress.progress_percentage,
        startedAt=progress.started_at,
        completedAt=progress.completed_at,
        timeSpentSeconds=progress.time_spent_seconds,
        lastAccessedAt=progress.last_accessed_at
    )


@router.post("/lessons/{lesson_id}/complete", response_model=LessonProgressResponse)
async def complete_lesson(
    lesson_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson_id,
        LessonProgress.enrollment_id == enrollment.id
    ).first()

    if not progress:
        progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=UUID(lesson_id),
            enrollment_id=enrollment.id,
            status="completed",
            progress_percentage=100,
            time_spent_seconds=0,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.status = "completed"
        progress.progress_percentage = 100
        progress.completed_at = datetime.utcnow()
        if not progress.started_at:
            progress.started_at = datetime.utcnow()

    progress.last_accessed_at = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    _update_module_progress(db, current_user.id, lesson.module_id, enrollment.id)
    _update_enrollment_progress(db, enrollment.id)

    return LessonProgressResponse(
        id=str(progress.id),
        lessonId=str(progress.lesson_id),
        status=progress.status,
        progressPercentage=progress.progress_percentage,
        startedAt=progress.started_at,
        completedAt=progress.completed_at,
        timeSpentSeconds=progress.time_spent_seconds,
        lastAccessedAt=progress.last_accessed_at
    )


@router.put("/content/{content_item_id}/progress", response_model=ContentProgressResponse)
async def update_content_progress(
    content_item_id: str,
    progress_data: ContentProgressUpdate,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content_item = db.query(ContentItem).filter(ContentItem.id == content_item_id).first()
    if not content_item:
        raise HTTPException(status_code=404, detail="Content item not found")

    lesson = db.query(Lesson).filter(Lesson.id == content_item.lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == lesson.course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course")

    lesson_progress = db.query(LessonProgress).filter(
        LessonProgress.user_id == current_user.id,
        LessonProgress.lesson_id == lesson.id,
        LessonProgress.enrollment_id == enrollment.id
    ).first()

    if not lesson_progress:
        lesson_progress = LessonProgress(
            user_id=current_user.id,
            lesson_id=lesson.id,
            enrollment_id=enrollment.id,
            status="in_progress",
            progress_percentage=0,
            time_spent_seconds=0,
            started_at=datetime.utcnow()
        )
        db.add(lesson_progress)
        db.commit()
        db.refresh(lesson_progress)

    content_progress = db.query(ContentProgress).filter(
        ContentProgress.user_id == current_user.id,
        ContentProgress.content_item_id == content_item_id,
        ContentProgress.lesson_progress_id == lesson_progress.id
    ).first()

    if not content_progress:
        content_progress = ContentProgress(
            user_id=current_user.id,
            content_item_id=UUID(content_item_id),
            lesson_progress_id=lesson_progress.id,
            progress_percentage=progress_data.progressPercentage,
            status="in_progress" if progress_data.progressPercentage < 100 else "completed",
            last_position=progress_data.lastPosition,
            completed=progress_data.completed or progress_data.progressPercentage >= 100,
            completed_at=datetime.utcnow() if (progress_data.completed or progress_data.progressPercentage >= 100) else None
        )
        db.add(content_progress)
    else:
        content_progress.progress_percentage = progress_data.progressPercentage
        content_progress.last_position = progress_data.lastPosition
        content_progress.status = "completed" if progress_data.progressPercentage >= 100 else "in_progress"

        if progress_data.completed or progress_data.progressPercentage >= 100:
            content_progress.completed = True
            if not content_progress.completed_at:
                content_progress.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(content_progress)

    _update_lesson_progress_from_content(db, lesson_progress.id)

    return ContentProgressResponse(
        id=str(content_progress.id),
        contentItemId=str(content_progress.content_item_id),
        progressPercentage=content_progress.progress_percentage,
        status=content_progress.status,
        lastPosition=content_progress.last_position,
        completed=content_progress.completed,
        completedAt=content_progress.completed_at
    )


@router.get("/courses/{course_id}/progress", response_model=CourseProgressResponse)
async def get_course_progress(
    course_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Not enrolled in this course")

    modules = db.query(Module)\
        .filter(Module.course_id == course_id)\
        .order_by(Module.order_index)\
        .all()

    total_lessons = db.query(func.count(Lesson.id))\
        .join(Module)\
        .filter(Module.course_id == course_id)\
        .scalar() or 0

    completed_lessons = db.query(func.count(LessonProgress.id))\
        .join(Lesson)\
        .join(Module)\
        .filter(
            Module.course_id == course_id,
            LessonProgress.user_id == current_user.id,
            LessonProgress.enrollment_id == enrollment.id,
            LessonProgress.status == "completed"
        )\
        .scalar() or 0

    module_data = []
    completed_modules = 0

    for module in modules:
        module_lessons = db.query(func.count(Lesson.id))\
            .filter(Lesson.module_id == module.id)\
            .scalar() or 0

        module_completed = db.query(func.count(LessonProgress.id))\
            .join(Lesson)\
            .filter(
                Lesson.module_id == module.id,
                LessonProgress.user_id == current_user.id,
                LessonProgress.enrollment_id == enrollment.id,
                LessonProgress.status == "completed"
            )\
            .scalar() or 0

        module_progress_pct = (module_completed / module_lessons * 100) if module_lessons > 0 else 0

        if module_progress_pct >= 100:
            completed_modules += 1

        module_data.append({
            "moduleId": str(module.id),
            "moduleName": module.title,
            "completedLessons": module_completed,
            "totalLessons": module_lessons,
            "progressPercentage": int(module_progress_pct)
        })

    overall_progress = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

    enrollment.progress_percentage = int(overall_progress)
    db.commit()

    return CourseProgressResponse(
        enrollmentId=str(enrollment.id),
        courseId=str(enrollment.course_id),
        overallProgress=int(overall_progress),
        completedLessons=completed_lessons,
        totalLessons=total_lessons,
        completedModules=completed_modules,
        totalModules=len(modules),
        modules=module_data
    )


def _update_lesson_progress_from_content(db: Session, lesson_progress_id: UUID):
    lesson_progress = db.query(LessonProgress).filter(LessonProgress.id == lesson_progress_id).first()
    if not lesson_progress:
        return

    lesson = db.query(Lesson).filter(Lesson.id == lesson_progress.lesson_id).first()
    if not lesson:
        return

    total_content = db.query(func.count(ContentItem.id))\
        .filter(ContentItem.lesson_id == lesson.id)\
        .scalar() or 0

    if total_content == 0:
        return

    completed_content = db.query(func.count(ContentProgress.id))\
        .filter(
            ContentProgress.lesson_progress_id == lesson_progress_id,
            ContentProgress.completed == True
        )\
        .scalar() or 0

    lesson_progress.progress_percentage = int((completed_content / total_content) * 100)

    if lesson_progress.progress_percentage >= 100 and lesson_progress.status != "completed":
        lesson_progress.status = "completed"
        lesson_progress.completed_at = datetime.utcnow()

        _update_module_progress(db, lesson_progress.user_id, lesson.module_id, lesson_progress.enrollment_id)
        _update_enrollment_progress(db, lesson_progress.enrollment_id)

    db.commit()


def _update_module_progress(db: Session, user_id: UUID, module_id: UUID, enrollment_id: UUID):
    total_lessons = db.query(func.count(Lesson.id))\
        .filter(Lesson.module_id == module_id)\
        .scalar() or 0

    if total_lessons == 0:
        return

    completed_lessons = db.query(func.count(LessonProgress.id))\
        .join(Lesson)\
        .filter(
            Lesson.module_id == module_id,
            LessonProgress.user_id == user_id,
            LessonProgress.enrollment_id == enrollment_id,
            LessonProgress.status == "completed"
        )\
        .scalar() or 0

    module_progress = db.query(ModuleProgress).filter(
        ModuleProgress.user_id == user_id,
        ModuleProgress.module_id == module_id,
        ModuleProgress.enrollment_id == enrollment_id
    ).first()

    progress_pct = int((completed_lessons / total_lessons) * 100)

    if not module_progress:
        module_progress = ModuleProgress(
            user_id=user_id,
            module_id=module_id,
            enrollment_id=enrollment_id,
            completed_lessons=completed_lessons,
            total_lessons=total_lessons,
            progress_percentage=progress_pct,
            is_complete=(progress_pct >= 100),
            completed_at=datetime.utcnow() if progress_pct >= 100 else None
        )
        db.add(module_progress)
    else:
        module_progress.completed_lessons = completed_lessons
        module_progress.total_lessons = total_lessons
        module_progress.progress_percentage = progress_pct
        module_progress.is_complete = (progress_pct >= 100)
        if progress_pct >= 100 and not module_progress.completed_at:
            module_progress.completed_at = datetime.utcnow()

    db.commit()


def _update_enrollment_progress(db: Session, enrollment_id: UUID):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        return

    total_lessons = db.query(func.count(Lesson.id))\
        .join(Module)\
        .filter(Module.course_id == enrollment.course_id)\
        .scalar() or 0

    if total_lessons == 0:
        enrollment.progress_percentage = 0
        db.commit()
        return

    completed_lessons = db.query(func.count(LessonProgress.id))\
        .join(Lesson)\
        .join(Module)\
        .filter(
            Module.course_id == enrollment.course_id,
            LessonProgress.user_id == enrollment.user_id,
            LessonProgress.enrollment_id == enrollment_id,
            LessonProgress.status == "completed"
        )\
        .scalar() or 0

    enrollment.progress_percentage = int((completed_lessons / total_lessons) * 100)
    db.commit()