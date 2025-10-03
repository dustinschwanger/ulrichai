"""
Course Builder API - Comprehensive course management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import os
import shutil
import json
from pathlib import Path

from ...core.database import get_db
from ..services.auth_service import get_current_user, require_role
from ..services.storage_service import storage_service
from ..services.enrollment_service import enrollment_service
from ..models import (
    LMSUser, Course, CourseVersion, Module, Lesson,
    ContentItem, Organization, LessonMedia, Section
)

router = APIRouter(
    prefix="/api/lms/course-builder",
    tags=["Course Builder"]
)

# Configure upload directory
UPLOAD_DIR = Path("uploads/lms")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions by type
ALLOWED_EXTENSIONS = {
    "video": [".mp4", ".webm", ".mov", ".avi", ".mkv"],
    "document": [".pdf", ".doc", ".docx", ".txt", ".ppt", ".pptx"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"],
    "audio": [".mp3", ".wav", ".ogg", ".m4a"],
    "resource": [".pdf", ".doc", ".docx", ".txt", ".zip", ".ppt", ".pptx", ".xls", ".xlsx"]
}

def validate_file_type(filename: str, file_type: str) -> bool:
    """Validate if file extension is allowed for the given type"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS.get(file_type, [])

# Pydantic models for request/response

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    duration_hours: Optional[float] = None
    prerequisites: List[UUID] = Field(default_factory=list)  # Array of course IDs
    tags: List[str] = Field(default_factory=list)
    is_published: bool = False
    is_featured: bool = False

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    duration_hours: Optional[float] = None
    prerequisites: Optional[List[UUID]] = None
    tags: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None

class SectionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: int = Field(..., ge=1)
    is_optional: bool = False
    is_locked: bool = False

class SectionUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    is_optional: Optional[bool] = None
    is_locked: Optional[bool] = None

class ModuleCreate(BaseModel):
    section_id: UUID
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: int = Field(..., ge=1)
    is_optional: bool = False
    estimated_duration_minutes: Optional[int] = None
    learning_objectives: Optional[List[str]] = Field(default_factory=list)

class ModuleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    is_optional: Optional[bool] = None
    estimated_duration_minutes: Optional[int] = None
    learning_objectives: Optional[List[str]] = None

class LessonCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: int = Field(..., ge=1)
    lesson_type: str = Field("standard", pattern="^(standard|video|reading|interactive|quiz|discussion|reflection|poll|embed)$")
    estimated_duration_minutes: Optional[int] = None
    is_required: bool = True
    content_data: Optional[dict] = None

class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    lesson_type: Optional[str] = Field(None, pattern="^(standard|video|reading|interactive|quiz|discussion|reflection|poll|embed)$")
    estimated_duration_minutes: Optional[int] = None
    is_required: Optional[bool] = None
    content_data: Optional[dict] = None

class ContentItemCreate(BaseModel):
    content_type: str = Field(..., pattern="^(video|document|quiz|discussion|reflection|poll|assignment)$")
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: int = Field(..., ge=1)
    is_required: bool = True
    points_possible: Optional[float] = None
    content_data: Optional[dict] = {}

class ContentItemUpdate(BaseModel):
    content_type: Optional[str] = Field(None, pattern="^(video|document|quiz|discussion|reflection|poll|assignment)$")
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    sequence_order: Optional[int] = Field(None, ge=1)
    is_required: Optional[bool] = None
    points_possible: Optional[float] = None
    content_data: Optional[dict] = None

class CourseResponse(BaseModel):
    id: UUID
    organization_id: UUID
    title: str
    slug: str
    description: Optional[str]
    thumbnail_url: Optional[str]
    instructor_id: UUID
    instructor: Optional[dict]
    category: Optional[str]
    subcategory: Optional[str]
    difficulty_level: Optional[str]
    duration_hours: Optional[float]
    prerequisites: List[UUID]
    tags: List[str]
    is_published: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime
    module_count: Optional[int] = 0
    lesson_count: Optional[int] = 0

# Course CRUD Operations

@router.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new course"""

    # Check if slug is unique within organization
    existing = db.query(Course).filter(
        Course.organization_id == current_user.organization_id,
        Course.slug == course_data.slug
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with slug '{course_data.slug}' already exists"
        )

    # Create course
    course = Course(
        organization_id=current_user.organization_id,
        title=course_data.title,
        slug=course_data.slug,
        description=course_data.description,
        thumbnail_url=course_data.thumbnail_url,
        instructor_id=current_user.id,
        category=course_data.category,
        subcategory=course_data.subcategory,
        difficulty_level=course_data.difficulty_level,
        duration_hours=course_data.duration_hours,
        prerequisites=list(course_data.prerequisites) if course_data.prerequisites else [],
        tags=list(course_data.tags) if course_data.tags else [],
        is_published=course_data.is_published,
        is_featured=course_data.is_featured
    )

    db.add(course)
    db.flush()  # Flush to get the course ID

    # Create initial version with all fields from course
    version = CourseVersion(
        course_id=course.id,
        version_number="1.0",
        version_name="Initial Version",
        title=course.title,
        description=course.description,
        thumbnail_url=course.thumbnail_url,
        duration_hours=course.duration_hours,
        difficulty_level=course.difficulty_level,
        is_active=True,
        is_draft=False,
        is_published=course.is_published,
        created_by=current_user.id
    )
    db.add(version)

    db.commit()
    db.refresh(course)
    db.refresh(version)

    # Return a simple dict response with version info
    return {
        "id": str(course.id),
        "organization_id": str(course.organization_id),
        "title": course.title,
        "slug": course.slug,
        "description": course.description,
        "thumbnail_url": course.thumbnail_url,
        "instructor_id": str(course.instructor_id),
        "category": course.category,
        "subcategory": course.subcategory,
        "difficulty_level": course.difficulty_level,
        "duration_hours": float(course.duration_hours) if course.duration_hours else None,
        "prerequisites": [str(p) for p in course.prerequisites] if course.prerequisites else [],
        "tags": course.tags if course.tags else [],
        "is_published": course.is_published,
        "is_featured": course.is_featured,
        "created_at": course.created_at.isoformat() if course.created_at else None,
        "updated_at": course.updated_at.isoformat() if course.updated_at else None,
        "instructor": {
            "id": str(current_user.id),
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email
        },
        "initial_version": {
            "id": str(version.id),
            "version_number": version.version_number,
            "version_name": version.version_name,
            "is_active": version.is_active,
            "is_published": version.is_published
        }
    }

@router.get("/courses", response_model=List[CourseResponse])
async def get_instructor_courses(
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Get all courses for the current instructor"""

    courses = db.query(Course).filter(
        Course.instructor_id == current_user.id
    ).order_by(Course.updated_at.desc()).all()

    responses = []
    for course in courses:
        # Count modules and lessons
        version = db.query(CourseVersion).filter(
            CourseVersion.course_id == course.id,
            CourseVersion.is_active == True
        ).first()

        module_count = 0
        lesson_count = 0

        if version:
            modules = db.query(Module).filter(
                Module.course_version_id == version.id
            ).all()
            module_count = len(modules)

            for module in modules:
                lessons = db.query(Lesson).filter(
                    Lesson.module_id == module.id
                ).all()
                lesson_count += len(lessons)

        response = CourseResponse(
            id=course.id,
            organization_id=course.organization_id,
            title=course.title,
            slug=course.slug,
            description=course.description,
            thumbnail_url=course.thumbnail_url,
            instructor_id=course.instructor_id,
            category=course.category,
            subcategory=course.subcategory,
            difficulty_level=course.difficulty_level,
            duration_hours=course.duration_hours,
            prerequisites=course.prerequisites,
            tags=course.tags,
            is_published=course.is_published,
            is_featured=course.is_featured,
            created_at=course.created_at,
            updated_at=course.updated_at,
            module_count=module_count,
            lesson_count=lesson_count,
            instructor={
                "id": str(current_user.id),
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "email": current_user.email
            }
        )
        responses.append(response)

    return responses

@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get course details"""

    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Get instructor info
    instructor = db.query(LMSUser).filter(LMSUser.id == course.instructor_id).first()

    response = CourseResponse(
        id=course.id,
        organization_id=course.organization_id,
        title=course.title,
        slug=course.slug,
        description=course.description,
        thumbnail_url=course.thumbnail_url,
        instructor_id=course.instructor_id,
        category=course.category,
        subcategory=course.subcategory,
        difficulty_level=course.difficulty_level,
        duration_hours=course.duration_hours,
        prerequisites=course.prerequisites,
        tags=course.tags,
        is_published=course.is_published,
        is_featured=course.is_featured,
        created_at=course.created_at,
        updated_at=course.updated_at,
        instructor={
            "id": str(instructor.id),
            "first_name": instructor.first_name,
            "last_name": instructor.last_name,
            "email": instructor.email
        } if instructor else None
    )

    return response

@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update course details"""

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission"
        )

    # Update fields
    update_data = course_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    course.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(course)

    response = CourseResponse(
        id=course.id,
        organization_id=course.organization_id,
        title=course.title,
        slug=course.slug,
        description=course.description,
        thumbnail_url=course.thumbnail_url,
        instructor_id=course.instructor_id,
        category=course.category,
        subcategory=course.subcategory,
        difficulty_level=course.difficulty_level,
        duration_hours=course.duration_hours,
        prerequisites=course.prerequisites,
        tags=course.tags,
        is_published=course.is_published,
        is_featured=course.is_featured,
        created_at=course.created_at,
        updated_at=course.updated_at,
        instructor={
            "id": str(current_user.id),
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "email": current_user.email
        }
    )

    return response

@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Delete a course"""

    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission"
        )

    db.delete(course)
    db.commit()

# Section CRUD Operations

@router.post("/courses/{course_id}/sections", status_code=status.HTTP_201_CREATED)
async def create_section(
    course_id: UUID,
    section_data: SectionCreate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new section in a course"""

    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission"
        )

    # Get active version
    version = db.query(CourseVersion).filter(
        CourseVersion.course_id == course_id,
        CourseVersion.is_active == True
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active course version found"
        )

    # Create section
    section = Section(
        course_version_id=version.id,
        title=section_data.title,
        description=section_data.description,
        sequence_order=section_data.sequence_order,
        is_optional=section_data.is_optional,
        is_locked=section_data.is_locked
    )

    db.add(section)
    db.commit()
    db.refresh(section)

    return {"id": section.id, **section_data.dict()}


@router.put("/sections/{section_id}")
async def update_section(
    section_id: UUID,
    section_data: SectionUpdate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update a section"""

    section = db.query(Section).filter(Section.id == section_id).first()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )

    # Verify ownership through course version
    version = db.query(CourseVersion).filter(
        CourseVersion.id == section.course_version_id
    ).first()

    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course version not found")

    course = db.query(Course).filter(
        Course.id == version.course_id,
        Course.instructor_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this section"
        )

    # Update section fields
    for field, value in section_data.dict(exclude_unset=True).items():
        setattr(section, field, value)

    db.commit()
    db.refresh(section)

    return {"id": section.id, **section_data.dict(exclude_unset=True)}


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: UUID,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Delete a section"""

    section = db.query(Section).filter(Section.id == section_id).first()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )

    # Verify ownership
    version = db.query(CourseVersion).filter(
        CourseVersion.id == section.course_version_id
    ).first()

    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course version not found")

    course = db.query(Course).filter(
        Course.id == version.course_id,
        Course.instructor_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this section"
        )

    db.delete(section)
    db.commit()

    return None


# Module CRUD Operations

@router.post("/courses/{course_id}/modules", status_code=status.HTTP_201_CREATED)
async def create_module(
    course_id: UUID,
    module_data: ModuleCreate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new module in a course"""

    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission"
        )

    # Get active version
    version = db.query(CourseVersion).filter(
        CourseVersion.course_id == course_id,
        CourseVersion.is_active == True
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active course version found"
        )

    # Verify section belongs to this course version
    section = db.query(Section).filter(
        Section.id == module_data.section_id,
        Section.course_version_id == version.id
    ).first()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Section not found or doesn't belong to this course version"
        )

    # Create module
    module = Module(
        section_id=module_data.section_id,
        course_version_id=version.id,
        title=module_data.title,
        description=module_data.description,
        sequence_order=module_data.sequence_order,
        is_optional=module_data.is_optional,
        estimated_duration_minutes=module_data.estimated_duration_minutes,
        learning_objectives=module_data.learning_objectives if module_data.learning_objectives else []
    )

    db.add(module)
    db.commit()
    db.refresh(module)

    return {"id": module.id, **module_data.dict()}

@router.get("/courses/{course_id}/modules")
async def get_course_modules(
    course_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all modules for a course"""

    # Get active version
    version = db.query(CourseVersion).filter(
        CourseVersion.course_id == course_id,
        CourseVersion.is_active == True
    ).first()

    if not version:
        return []

    modules = db.query(Module).filter(
        Module.course_version_id == version.id
    ).order_by(Module.sequence_order).all()

    return [
        {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "sequence_order": m.sequence_order,
            "is_optional": m.is_optional,
            "estimated_duration_minutes": m.estimated_duration_minutes,
            "learning_objectives": m.learning_objectives,
            "created_at": m.created_at,
            "updated_at": m.updated_at
        }
        for m in modules
    ]

@router.put("/modules/{module_id}")
async def update_module(
    module_id: UUID,
    module_data: ModuleUpdate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update a module"""

    # Get module with course info for permission check
    module = db.query(Module).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Module.id == module_id,
        Course.instructor_id == current_user.id
    ).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or you don't have permission"
        )

    # Update fields
    update_data = module_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)

    module.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(module)

    return {
        "id": module.id,
        "title": module.title,
        "description": module.description,
        "sequence_order": module.sequence_order,
        "is_optional": module.is_optional,
        "estimated_duration_minutes": module.estimated_duration_minutes,
        "learning_objectives": module.learning_objectives,
        "updated_at": module.updated_at
    }

@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: UUID,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Delete a module"""

    # Get module with course info for permission check
    module = db.query(Module).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Module.id == module_id,
        Course.instructor_id == current_user.id
    ).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or you don't have permission"
        )

    db.delete(module)
    db.commit()

# Lesson CRUD Operations

@router.post("/modules/{module_id}/lessons", status_code=status.HTTP_201_CREATED)
async def create_lesson(
    module_id: UUID,
    lesson_data: LessonCreate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new lesson in a module"""

    # Verify module ownership through course
    module = db.query(Module).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Module.id == module_id,
        Course.instructor_id == current_user.id
    ).first()

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found or you don't have permission"
        )

    # Create lesson
    lesson = Lesson(
        module_id=module_id,
        title=lesson_data.title,
        description=lesson_data.description,
        sequence_order=lesson_data.sequence_order,
        lesson_type=lesson_data.lesson_type,
        estimated_duration_minutes=lesson_data.estimated_duration_minutes,
        is_required=lesson_data.is_required,
        content_data=lesson_data.content_data if lesson_data.content_data else {}
    )

    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    return {"id": lesson.id, **lesson_data.dict()}

@router.get("/modules/{module_id}/lessons")
async def get_module_lessons(
    module_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all lessons for a module"""

    lessons = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).order_by(Lesson.sequence_order).all()

    result = []
    for l in lessons:
        # Get media files from the relationship
        media_files = [
            {
                "id": str(m.id),
                "type": m.media_type,
                "title": m.title,
                "description": m.description,
                "filename": m.filename,
                "storage": m.storage,
                "bucket": m.bucket,
                "path": m.path,
                "url": m.url,
                "size": m.size,
                "uploaded_at": m.uploaded_at.isoformat() if m.uploaded_at else None
            }
            for m in l.media_files
        ]

        # Add media_files to content_data for backward compatibility with frontend
        content_data = dict(l.content_data) if l.content_data else {}
        content_data["media_files"] = media_files

        result.append({
            "id": l.id,
            "title": l.title,
            "description": l.description,
            "sequence_order": l.sequence_order,
            "lesson_type": l.lesson_type,
            "estimated_duration_minutes": l.estimated_duration_minutes,
            "is_required": l.is_required,
            "content_data": content_data,
            "created_at": l.created_at,
            "updated_at": l.updated_at
        })

    return result

@router.put("/lessons/{lesson_id}")
async def update_lesson(
    lesson_id: UUID,
    lesson_data: LessonUpdate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update a lesson"""

    # Get lesson with course info for permission check
    lesson = db.query(Lesson).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Lesson.id == lesson_id,
        Course.instructor_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found or you don't have permission"
        )

    # Update fields
    # Note: media_files are now managed in separate LessonMedia table, not in content_data
    update_data = lesson_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "content_data" and value is not None:
            # Simply merge content_data (media_files are no longer stored here)
            existing_content = lesson.content_data or {}
            new_content = value or {}
            merged_content = {**existing_content, **new_content}

            # Remove media_files if present (shouldn't be sent from frontend anymore)
            merged_content.pop("media_files", None)

            lesson.content_data = merged_content
        else:
            setattr(lesson, field, value)

    lesson.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(lesson)

    return {
        "id": lesson.id,
        "title": lesson.title,
        "description": lesson.description,
        "sequence_order": lesson.sequence_order,
        "lesson_type": lesson.lesson_type,
        "estimated_duration_minutes": lesson.estimated_duration_minutes,
        "is_required": lesson.is_required,
        "content_data": lesson.content_data,
        "updated_at": lesson.updated_at
    }

@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: UUID,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Delete a lesson"""

    # Get lesson with course info for permission check
    lesson = db.query(Lesson).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Lesson.id == lesson_id,
        Course.instructor_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found or you don't have permission"
        )

    db.delete(lesson)
    db.commit()

# Content Item CRUD Operations

@router.post("/lessons/{lesson_id}/content", status_code=status.HTTP_201_CREATED)
async def create_content_item(
    lesson_id: UUID,
    content_data: ContentItemCreate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new content item in a lesson"""

    # Verify lesson ownership through module and course
    lesson = db.query(Lesson).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Lesson.id == lesson_id,
        Course.instructor_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found or you don't have permission"
        )

    # Create content item
    content_item = ContentItem(
        lesson_id=lesson_id,
        content_type=content_data.content_type,
        title=content_data.title,
        description=content_data.description,
        sequence_order=content_data.sequence_order,
        is_required=content_data.is_required,
        points_possible=content_data.points_possible,
        content_data=content_data.content_data or {}
    )

    db.add(content_item)
    db.commit()
    db.refresh(content_item)

    return {"id": content_item.id, **content_data.dict()}

@router.get("/lessons/{lesson_id}/content")
async def get_lesson_content(
    lesson_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all content items for a lesson"""

    content_items = db.query(ContentItem).filter(
        ContentItem.lesson_id == lesson_id
    ).order_by(ContentItem.sequence_order).all()

    return [
        {
            "id": c.id,
            "content_type": c.content_type,
            "title": c.title,
            "description": c.description,
            "sequence_order": c.sequence_order,
            "is_required": c.is_required,
            "points_possible": c.points_possible,
            "content_data": c.content_data,
            "created_at": c.created_at,
            "updated_at": c.updated_at
        }
        for c in content_items
    ]

@router.put("/content/{content_id}")
async def update_content_item(
    content_id: UUID,
    content_data: ContentItemUpdate,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update a content item"""

    # Get content item with course info for permission check
    content_item = db.query(ContentItem).join(
        Lesson
    ).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        ContentItem.id == content_id,
        Course.instructor_id == current_user.id
    ).first()

    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found or you don't have permission"
        )

    # Update fields
    update_data = content_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content_item, field, value)

    content_item.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(content_item)

    return {
        "id": content_item.id,
        "content_type": content_item.content_type,
        "title": content_item.title,
        "description": content_item.description,
        "sequence_order": content_item.sequence_order,
        "is_required": content_item.is_required,
        "points_possible": content_item.points_possible,
        "content_data": content_item.content_data,
        "updated_at": content_item.updated_at
    }

# Media Upload Endpoints

@router.post("/lessons/{lesson_id}/upload")
async def upload_lesson_media(
    lesson_id: UUID,
    file: UploadFile = File(...),
    media_type: str = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    # RAG metadata fields
    display_name: Optional[str] = Form(None),
    document_source: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    capability_domain: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    publication_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"]))
):
    """Upload media file for a lesson with RAG metadata for AI indexing"""

    # Verify lesson ownership through module and course
    lesson = db.query(Lesson).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Lesson.id == lesson_id,
        Course.instructor_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found or you don't have permission"
        )

    # Validate file type
    if not validate_file_type(file.filename, media_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for {media_type}. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS.get(media_type, []))}"
        )

    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid4()}_{file.filename}"

    # Read file content
    file_content = await file.read()

    # Determine content type
    content_type_map = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".avi": "video/x-msvideo",
        ".mkv": "video/x-matroska",
        ".pdf": "application/pdf",
        ".doc": "application/msword",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
    }
    content_type = content_type_map.get(file_extension.lower(), "application/octet-stream")

    # Try to upload to Supabase
    supabase_uploaded = False
    media_info = None

    if storage_service.is_available():
        try:
            # Determine bucket based on media type
            bucket_map = {
                "video": "lms-videos",
                "document": "lms-documents",
                "resource": "lms-resources",
                "audio": "lms-resources",
                "image": "lms-resources"
            }
            bucket = bucket_map.get(media_type, "lms-resources")

            # Upload to Supabase
            upload_path = f"lessons/{lesson_id}"
            result = await storage_service.upload_file(
                file_content=file_content,
                filename=unique_filename,
                bucket=bucket,
                path=upload_path,
                content_type=content_type
            )

            media_info = {
                "id": str(uuid4()),
                "type": media_type,
                "filename": file.filename,
                "bucket": bucket,
                "path": result["path"],
                "storage": "supabase",
                "size": result["size"],
                "title": title or file.filename,
                "description": description,
                "uploaded_at": result["uploaded_at"]
            }

            supabase_uploaded = True

        except Exception as e:
            import logging
            logging.error(f"Supabase upload failed, falling back to local storage: {e}")

    # Fallback to local storage if Supabase failed
    if not supabase_uploaded:
        media_dir = UPLOAD_DIR / "lessons" / str(lesson_id) / media_type
        media_dir.mkdir(parents=True, exist_ok=True)

        file_path = media_dir / unique_filename
        with file_path.open("wb") as buffer:
            buffer.write(file_content)

        media_info = {
            "id": str(uuid4()),
            "type": media_type,
            "filename": file.filename,
            "path": str(file_path.relative_to("uploads")),
            "url": f"/api/lms/course-builder/media/{file_path.relative_to('uploads')}",
            "storage": "local",
            "size": file_path.stat().st_size,
            "title": title or file.filename,
            "description": description,
            "uploaded_at": datetime.now(timezone.utc).isoformat()
        }

    # Parse publication_date if provided
    pub_date = None
    if publication_date:
        try:
            from dateutil import parser
            pub_date = parser.parse(publication_date)
        except:
            pass

    # Create LessonMedia record with RAG metadata
    lesson_media = LessonMedia(
        lesson_id=lesson_id,
        title=title or file.filename,
        description=description,
        media_type=media_type,
        filename=file.filename,
        storage=media_info.get("storage"),
        bucket=media_info.get("bucket"),
        path=media_info.get("path"),
        url=media_info.get("url"),
        size=media_info.get("size"),
        content_type=content_type,
        sequence_order=db.query(LessonMedia).filter(LessonMedia.lesson_id == lesson_id).count() + 1,
        # RAG metadata
        display_name=display_name,
        document_source=document_source,
        document_type=document_type,
        capability_domain=capability_domain,
        author=author,
        publication_date=pub_date,
        transcription_status='pending' if media_type == 'video' else None
    )

    db.add(lesson_media)
    lesson.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(lesson_media)

    # Trigger video processing for video files (async background task)
    if media_type == 'video' and storage_service.is_available():
        import asyncio
        from ..services.video_indexing_service import video_indexing_service
        # Pass media_id only - service will create its own DB session
        media_id_str = str(lesson_media.id)
        asyncio.create_task(video_indexing_service.process_lesson_video(media_id_str))

    return {
        "message": f"File uploaded successfully to {media_info.get('storage', 'storage')}",
        "media": {
            "id": str(lesson_media.id),
            "type": lesson_media.media_type,
            "title": lesson_media.title,
            "description": lesson_media.description,
            "filename": lesson_media.filename,
            "storage": lesson_media.storage,
            "bucket": lesson_media.bucket,
            "path": lesson_media.path,
            "url": lesson_media.url,
            "size": lesson_media.size,
            "uploaded_at": lesson_media.uploaded_at.isoformat() if lesson_media.uploaded_at else None
        }
    }

@router.get("/media/{file_path:path}")
async def get_media_file(
    file_path: str,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Serve media files"""

    full_path = Path("uploads") / file_path

    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    # You might want to add permission checks here based on the file path

    return FileResponse(full_path)

@router.get("/lessons/{lesson_id}/media/{media_id}/signed-url")
async def get_signed_media_url(
    lesson_id: UUID,
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(get_current_user)
):
    """Generate a signed URL for accessing media with enrollment verification"""

    # Check if user has access to this lesson
    if not enrollment_service.can_user_access_lesson(db, current_user.id, lesson_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to access this content"
        )

    # Get the media file from LessonMedia table
    media_file = db.query(LessonMedia).filter(
        LessonMedia.id == media_id,
        LessonMedia.lesson_id == lesson_id
    ).first()

    if not media_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )

    # If stored in Supabase, generate signed URL
    if media_file.storage == "supabase":
        bucket = media_file.bucket
        path = media_file.path

        if not bucket or not path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid media file metadata"
            )

        signed_url = storage_service.generate_signed_url(
            bucket=bucket,
            file_path=path,
            expires_in=3600
        )

        if not signed_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate signed URL"
            )

        return {
            "url": signed_url,
            "expires_in": 3600,
            "media": {
                "id": str(media_file.id),
                "type": media_file.media_type,
                "title": media_file.title,
                "filename": media_file.filename
            }
        }

    # If stored locally, return the local URL
    elif media_file.storage == "local":
        return {
            "url": media_file.url,
            "expires_in": None,
            "media": {
                "id": str(media_file.id),
                "type": media_file.media_type,
                "title": media_file.title,
                "filename": media_file.filename
            }
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unknown storage type"
        )

@router.get("/courses/{course_id}/media")
async def get_course_media(
    course_id: UUID,
    media_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"]))
):
    """Get all media files for a course, optionally filtered by media_type"""

    # Verify course ownership
    course = db.query(Course).filter(
        Course.id == course_id,
        Course.instructor_id == current_user.id
    ).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found or you don't have permission"
        )

    # Get active version
    version = db.query(CourseVersion).filter(
        CourseVersion.course_id == course_id,
        CourseVersion.is_active == True
    ).first()

    if not version:
        return []

    # Get all media files for all lessons in this course
    # Join LessonMedia -> Lesson -> Module -> Section -> CourseVersion
    query = db.query(LessonMedia, Lesson, Module, Section).join(
        Lesson, LessonMedia.lesson_id == Lesson.id
    ).join(
        Module, Lesson.module_id == Module.id
    ).join(
        Section, Module.section_id == Section.id
    ).filter(
        Section.course_version_id == version.id
    )

    # Filter by media type if specified
    if media_type:
        query = query.filter(LessonMedia.media_type == media_type)

    # Order by upload date (newest first)
    query = query.order_by(LessonMedia.uploaded_at.desc())

    results = query.all()

    # Format response
    media_list = []
    for media, lesson, module, section in results:
        media_list.append({
            "id": str(media.id),
            "media_type": media.media_type,
            "title": media.title,
            "description": media.description,
            "filename": media.filename,
            "storage": media.storage,
            "bucket": media.bucket,
            "path": media.path,
            "url": media.url,
            "size": media.size,
            "content_type": media.content_type,
            "uploaded_at": media.uploaded_at.isoformat() if media.uploaded_at else None,
            "lesson": {
                "id": str(lesson.id),
                "title": lesson.title,
                "module": {
                    "id": str(module.id),
                    "title": module.title,
                    "section": {
                        "id": str(section.id),
                        "title": section.title
                    }
                }
            }
        })

    return media_list


@router.post("/lessons/{lesson_id}/media/link")
async def link_existing_media_to_lesson(
    lesson_id: UUID,
    media_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"]))
):
    """Link an existing media file to a lesson (creates a copy of the media record)"""

    # Verify lesson ownership
    lesson = db.query(Lesson).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Lesson.id == lesson_id,
        Course.instructor_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found or you don't have permission"
        )

    # Find the source media
    try:
        media_uuid = UUID(media_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid media ID format"
        )

    source_media = db.query(LessonMedia).filter(
        LessonMedia.id == media_uuid
    ).first()

    if not source_media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source media not found"
        )

    # Create a new LessonMedia record linked to this lesson (referencing the same file)
    new_media = LessonMedia(
        lesson_id=lesson_id,
        title=source_media.title,
        description=source_media.description,
        media_type=source_media.media_type,
        filename=source_media.filename,
        storage=source_media.storage,
        bucket=source_media.bucket,
        path=source_media.path,
        url=source_media.url,
        size=source_media.size,
        content_type=source_media.content_type,
        sequence_order=db.query(LessonMedia).filter(LessonMedia.lesson_id == lesson_id).count() + 1,
        # Copy RAG metadata
        display_name=source_media.display_name,
        document_source=source_media.document_source,
        document_type=source_media.document_type,
        capability_domain=source_media.capability_domain,
        author=source_media.author,
        publication_date=source_media.publication_date,
        transcription_status=source_media.transcription_status,
        transcription_text=source_media.transcription_text,
        chunks_indexed=source_media.chunks_indexed,
    )

    db.add(new_media)
    lesson.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(new_media)

    return {
        "message": "Media linked successfully",
        "media": {
            "id": str(new_media.id),
            "type": new_media.media_type,
            "title": new_media.title,
            "description": new_media.description,
            "filename": new_media.filename,
            "storage": new_media.storage,
            "bucket": new_media.bucket,
            "path": new_media.path,
            "url": new_media.url,
            "size": new_media.size,
            "uploaded_at": new_media.uploaded_at.isoformat() if new_media.uploaded_at else None
        }
    }


@router.delete("/lessons/{lesson_id}/media/{media_id}")
async def delete_lesson_media(
    lesson_id: UUID,
    media_id: str,
    db: Session = Depends(get_db),
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"]))
):
    """Delete a media file from a lesson"""

    # Verify lesson ownership through module and course
    lesson = db.query(Lesson).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        Lesson.id == lesson_id,
        Course.instructor_id == current_user.id
    ).first()

    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found or you don't have permission"
        )

    # Find media in LessonMedia table
    try:
        media_uuid = UUID(media_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid media ID format"
        )

    media = db.query(LessonMedia).filter(
        LessonMedia.id == media_uuid,
        LessonMedia.lesson_id == lesson_id
    ).first()

    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media file not found"
        )

    # Delete physical file if stored locally
    if media.storage == "local" and media.path:
        file_path = Path("uploads") / Path(media.path)
        if file_path.exists():
            file_path.unlink()

    # Delete database record
    db.delete(media)
    lesson.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Media file deleted successfully"}

@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_item(
    content_id: UUID,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Delete a content item"""

    # Get content item with course info for permission check
    content_item = db.query(ContentItem).join(
        Lesson
    ).join(
        Module
    ).join(
        CourseVersion
    ).join(
        Course
    ).filter(
        ContentItem.id == content_id,
        Course.instructor_id == current_user.id
    ).first()

    if not content_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content item not found or you don't have permission"
        )

    db.delete(content_item)
    db.commit()

# Course Structure - Get full course with modules, lessons, and content

@router.get("/courses/{course_id}/structure")
async def get_course_structure(
    course_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete course structure with modules, lessons, and content items"""

    # Get course
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Get active version
    version = db.query(CourseVersion).filter(
        CourseVersion.course_id == course_id,
        CourseVersion.is_active == True
    ).first()

    if not version:
        return {
            "course": {
                "id": course.id,
                "title": course.title,
                "description": course.description
            },
            "sections": []
        }

    # Get sections with modules, lessons, and content
    sections = db.query(Section).filter(
        Section.course_version_id == version.id
    ).order_by(Section.sequence_order).all()

    structure = {
        "course": {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "is_published": course.is_published,
            "instructor_id": course.instructor_id
        },
        "sections": []
    }

    for section in sections:
        section_data = {
            "id": section.id,
            "title": section.title,
            "description": section.description,
            "sequence_order": section.sequence_order,
            "is_optional": section.is_optional,
            "is_locked": section.is_locked,
            "modules": []
        }

        # Get modules for this section
        modules = db.query(Module).filter(
            Module.section_id == section.id
        ).order_by(Module.sequence_order).all()

        for module in modules:
            module_data = {
                "id": module.id,
                "title": module.title,
                "description": module.description,
                "sequence_order": module.sequence_order,
                "is_optional": module.is_optional,
                "estimated_duration_minutes": module.estimated_duration_minutes,
                "learning_objectives": module.learning_objectives,
                "lessons": []
            }

            lessons = db.query(Lesson).filter(
                Lesson.module_id == module.id
            ).order_by(Lesson.sequence_order).all()

            for lesson in lessons:
                # Get media files from the LessonMedia relationship
                media_files = [
                    {
                        "id": str(m.id),
                        "type": m.media_type,
                        "title": m.title,
                        "description": m.description,
                        "filename": m.filename,
                        "storage": m.storage,
                        "bucket": m.bucket,
                        "path": m.path,
                        "url": m.url,
                        "size": m.size,
                        "uploaded_at": m.uploaded_at.isoformat() if m.uploaded_at else None
                    }
                    for m in lesson.media_files
                ]

                # Add media_files to content_data for backward compatibility
                content_data = dict(lesson.content_data) if lesson.content_data else {}
                content_data["media_files"] = media_files

                lesson_data = {
                    "id": lesson.id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "sequence_order": lesson.sequence_order,
                    "lesson_type": lesson.lesson_type,
                    "estimated_duration_minutes": lesson.estimated_duration_minutes,
                    "is_required": lesson.is_required,
                    "content_data": content_data,
                    "content_items": []
                }

                content_items = db.query(ContentItem).filter(
                    ContentItem.lesson_id == lesson.id
                ).order_by(ContentItem.sequence_order).all()

                for content in content_items:
                    lesson_data["content_items"].append({
                        "id": content.id,
                        "content_type": content.content_type,
                        "title": content.title,
                        "sequence_order": content.sequence_order,
                        "is_required": content.is_required
                    })

                module_data["lessons"].append(lesson_data)

            section_data["modules"].append(module_data)

        structure["sections"].append(section_data)

    return structure


# Course Version Management Endpoints

@router.post("/courses/{course_id}/versions")
async def create_course_version(
    course_id: UUID,
    version_data: dict,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Create a new version for a course."""
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check permissions - admin can create versions for any course
    if current_user.role != "ADMIN" and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to create versions for this course"
        )

    # Get highest version number
    last_version = db.query(CourseVersion)\
        .filter(CourseVersion.course_id == course_id)\
        .order_by(CourseVersion.version_number.desc())\
        .first()

    if last_version:
        # Parse version number and increment
        try:
            version_parts = last_version.version_number.split('.')
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            new_version_number = f"{major}.{minor + 1}"
        except:
            new_version_number = "2.0"
    else:
        new_version_number = "1.0"

    # Create new version
    new_version = CourseVersion(
        course_id=course_id,
        version_number=version_data.get("version_number", new_version_number),
        version_name=version_data.get("version_name", f"Version {new_version_number}"),
        title=course.title,
        description=version_data.get("description", course.description),
        thumbnail_url=course.thumbnail_url,
        duration_hours=course.duration_hours,
        difficulty_level=course.difficulty_level,
        prerequisites=course.prerequisites if course.prerequisites else [],
        learning_outcomes=[],
        is_active=version_data.get("is_active", False),
        is_draft=version_data.get("is_draft", True),
        is_published=False,
        settings={},
        is_ai_generated=False,
        created_by=current_user.id
    )

    # Add to session first
    db.add(new_version)
    db.flush()  # This assigns the ID

    # If copying from existing version
    source_version_id = version_data.get("source_version_id")
    if source_version_id:
        source_version = db.query(CourseVersion)\
            .filter(CourseVersion.id == source_version_id)\
            .first()
        if source_version:
            # Copy modules and lessons
            for module in source_version.modules:
                new_module = Module(
                    course_version_id=new_version.id,
                    title=module.title,
                    description=module.description,
                    sequence_order=module.sequence_order
                )
                db.add(new_module)
                db.flush()

                # Copy lessons
                for lesson in module.lessons:
                    new_lesson = Lesson(
                        module_id=new_module.id,
                        title=lesson.title,
                        lesson_type=lesson.lesson_type,
                        content=lesson.content,
                        content_data=lesson.content_data,
                        sequence_order=lesson.sequence_order,
                        duration_minutes=lesson.duration_minutes,
                        is_published=False
                    )
                    db.add(new_lesson)

    # Commit all changes
    db.commit()
    db.refresh(new_version)

    # Return the version data
    return {
        "id": new_version.id,
        "course_id": new_version.course_id,
        "version_number": new_version.version_number,
        "version_name": new_version.version_name,
        "title": new_version.title,
        "description": new_version.description,
        "is_active": new_version.is_active,
        "is_draft": new_version.is_draft,
        "is_published": new_version.is_published,
        "created_at": new_version.created_at,
        "created_by": new_version.created_by
    }


@router.get("/courses/{course_id}/versions")
async def get_course_versions(
    course_id: UUID,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all versions for a course."""
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Get all versions for this course
    versions = db.query(CourseVersion)\
        .filter(CourseVersion.course_id == course_id)\
        .order_by(CourseVersion.created_at.desc())\
        .all()

    # Format response
    version_list = []
    for version in versions:
        # Count modules and lessons for this version
        module_count = db.query(Module).filter(Module.course_version_id == version.id).count()
        lesson_count = 0

        modules = db.query(Module).filter(Module.course_version_id == version.id).all()
        for module in modules:
            lesson_count += db.query(Lesson).filter(Lesson.module_id == module.id).count()

        version_data = {
            "id": str(version.id),
            "course_id": str(version.course_id),
            "version_number": version.version_number,
            "version_name": version.version_name,
            "title": version.title,
            "description": version.description,
            "is_active": version.is_active,
            "is_draft": version.is_draft,
            "is_published": version.is_published,
            "module_count": module_count,
            "lesson_count": lesson_count,
            "created_at": version.created_at,
            "updated_at": version.updated_at,
            "created_by": str(version.created_by) if version.created_by else None
        }
        version_list.append(version_data)

    return version_list


@router.patch("/courses/{course_id}/versions/{version_id}")
async def update_course_version(
    course_id: UUID,
    version_id: UUID,
    updates: dict,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Update a course version."""
    # First check course exists
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check permissions - admin can update versions for any course
    if current_user.role != "ADMIN" and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update versions for this course"
        )

    version = db.query(CourseVersion)\
        .filter(CourseVersion.id == version_id, CourseVersion.course_id == course_id)\
        .first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )

    # Update fields
    for key, value in updates.items():
        if hasattr(version, key):
            setattr(version, key, value)

    version.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(version)

    return {"message": "Version updated successfully", "version_id": version.id}


@router.delete("/courses/{course_id}/versions/{version_id}")
async def delete_course_version(
    course_id: UUID,
    version_id: UUID,
    current_user: LMSUser = Depends(require_role(["INSTRUCTOR", "ADMIN"])),
    db: Session = Depends(get_db)
):
    """Delete a course version."""
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Check permissions - admin can delete versions for any course
    if current_user.role != "ADMIN" and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete versions for this course"
        )

    # Don't allow deletion if it's the only version
    version_count = db.query(CourseVersion)\
        .filter(CourseVersion.course_id == course_id)\
        .count()

    if version_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete the only version of a course"
        )

    version = db.query(CourseVersion)\
        .filter(CourseVersion.id == version_id, CourseVersion.course_id == course_id)\
        .first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found"
        )

    db.delete(version)
    db.commit()

    return {"message": "Version deleted successfully"}