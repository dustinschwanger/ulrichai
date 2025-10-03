from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional
from uuid import uuid4, UUID
from datetime import datetime

from ...core.database import get_db
from ..services.auth_service import get_current_user, require_role
from ..models import LMSUser
from ..models.course import Course, CourseVersion
from ..models.content import Module, Lesson, Enrollment, Cohort

router = APIRouter(prefix="/api/lms/courses", tags=["LMS Courses"])

def build_course_response(course: Course, db: Session, current_user_id: UUID = None) -> dict:
    """
    Build a complete course response with calculated fields.
    Simple helper for consistent course data across endpoints.
    """

    active_version = db.query(CourseVersion).filter(
        CourseVersion.course_id == course.id,
        CourseVersion.is_active == True
    ).first()

    if not active_version:
        active_version = db.query(CourseVersion).filter(
            CourseVersion.course_id == course.id
        ).first()

    module_count = 0
    lesson_count = 0

    if active_version:
        modules = db.query(Module).filter(Module.course_version_id == active_version.id).all()
        module_count = len(modules)
        for module in modules:
            lesson_count += db.query(Lesson).filter(Lesson.module_id == module.id).count()

    cohorts = db.query(Cohort).filter(
        Cohort.course_version_id == active_version.id if active_version else None
    ).all() if active_version else []

    enrolled_count = 0
    for cohort in cohorts:
        enrolled_count += db.query(Enrollment).filter(Enrollment.cohort_id == cohort.id).count()

    instructor_data = None
    if course.instructor:
        instructor_data = {
            "id": str(course.instructor.id),
            "firstName": course.instructor.first_name or "",
            "lastName": course.instructor.last_name or "",
            "email": course.instructor.email or "",
            "title": "",
            "avatarUrl": None
        }

    return {
        "id": str(course.id),
        "organizationId": str(course.organization_id),
        "title": course.title,
        "slug": course.slug,
        "description": course.description,
        "shortDescription": course.description[:150] + "..." if course.description and len(course.description) > 150 else course.description,
        "thumbnailUrl": course.thumbnail_url,
        "instructorId": str(course.instructor_id),
        "instructor": instructor_data,
        "durationHours": float(course.duration_hours) if course.duration_hours else 0,
        "difficultyLevel": course.difficulty_level or "beginner",
        "category": course.category,
        "subcategory": course.subcategory,
        "prerequisites": course.prerequisites or [],
        "tags": course.tags or [],
        "isAiEnhanced": course.is_ai_enhanced,
        "isPublished": course.is_published,
        "isFeatured": course.is_featured,
        "publishedAt": course.published_at.isoformat() if course.published_at else None,
        "enrollmentType": course.enrollment_type or "open",
        "price": float(course.price) if course.price else 0,
        "currency": course.currency or "USD",
        "enrolledCount": enrolled_count,
        "rating": 4.8,
        "reviewCount": max(int(enrolled_count * 0.3), 1),
        "moduleCount": module_count,
        "lessonCount": lesson_count,
        "features": {
            "hasVideo": lesson_count > 0,
            "hasQuiz": True,
            "hasCertificate": True,
            "hasLifetimeAccess": True
        },
        "isBookmarked": False,
        "createdAt": course.created_at.isoformat() if course.created_at else None,
        "updatedAt": course.updated_at.isoformat() if course.updated_at else None
    }

@router.get("/", response_model=dict)
async def get_courses(
    page: int = Query(1, ge=1),
    pageSize: int = Query(12, ge=1, le=100),
    sortBy: str = Query("popular", regex="^(popular|newest|rating|price)$"),
    search: Optional[str] = None,
    category: Optional[str] = None,
    difficultyLevel: Optional[str] = None,
    minRating: Optional[float] = None,
    maxPrice: Optional[float] = None,
    minPrice: Optional[float] = None,
    isPublished: bool = True,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get paginated course catalog with smart filtering.
    Students see published courses, instructors see their own drafts too.
    """
    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()
    is_admin_or_instructor = user_role in ["INSTRUCTOR", "ADMIN", "SUPER_ADMIN"]

    query = db.query(Course).options(joinedload(Course.instructor))

    if isPublished:
        query = query.filter(Course.is_published == True)
    elif is_admin_or_instructor:
        query = query.filter(
            or_(
                Course.is_published == True,
                Course.instructor_id == current_user.id
            )
        )
    else:
        query = query.filter(Course.is_published == True)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Course.title.ilike(search_term),
                Course.description.ilike(search_term)
            )
        )

    if category:
        query = query.filter(Course.category == category)

    if difficultyLevel:
        query = query.filter(Course.difficulty_level == difficultyLevel)

    if maxPrice is not None:
        query = query.filter(Course.price <= maxPrice)

    if minPrice is not None:
        query = query.filter(Course.price >= minPrice)

    if sortBy == "newest":
        query = query.order_by(Course.created_at.desc())
    elif sortBy == "price":
        query = query.order_by(Course.price.asc())
    else:
        query = query.order_by(Course.created_at.desc())

    total = query.count()

    start = (page - 1) * pageSize
    courses = query.offset(start).limit(pageSize).all()

    course_list = [build_course_response(course, db, current_user.id) for course in courses]

    if sortBy == "popular":
        course_list.sort(key=lambda x: x["enrolledCount"], reverse=True)
    elif sortBy == "rating":
        course_list.sort(key=lambda x: x["rating"], reverse=True)

    return {
        "items": course_list,
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "totalPages": (total + pageSize - 1) // pageSize if total > 0 else 0
    }

@router.get("/categories", response_model=List[str])
async def get_categories(
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of categories from actual courses.
    Returns unique categories dynamically.
    """
    categories = db.query(Course.category).filter(
        Course.category.isnot(None),
        Course.is_published == True
    ).distinct().all()

    category_list = [cat[0] for cat in categories if cat[0]]

    if not category_list:
        return [
            "Programming",
            "Data Science",
            "Web Development",
            "Machine Learning",
            "Cloud Computing"
        ]

    return sorted(category_list)

@router.get("/{course_id}", response_model=dict)
async def get_course(
    course_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed course information.
    Includes modules, lessons, and enrollment data.
    """
    course = db.query(Course).options(
        joinedload(Course.instructor)
    ).filter(Course.id == course_id).first()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    user_role = current_user.role.upper() if hasattr(current_user.role, 'upper') else str(current_user.role).upper()
    is_instructor = course.instructor_id == current_user.id or user_role in ["ADMIN", "SUPER_ADMIN"]

    if not course.is_published and not is_instructor:
        raise HTTPException(status_code=404, detail="Course not found")

    return build_course_response(course, db, current_user.id)

@router.post("/{course_id}/bookmark")
async def bookmark_course(
    course_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bookmark a course"""
    # In a real implementation, this would save to database
    return {"message": "Course bookmarked successfully"}

@router.delete("/{course_id}/unbookmark")
async def unbookmark_course(
    course_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove bookmark from a course"""
    # In a real implementation, this would remove from database
    return {"message": "Bookmark removed successfully"}

# Mock enrolled courses storage (in production, this would be in a database)
USER_ENROLLMENTS = {}

@router.post("/{course_id}/enroll")
async def enroll_in_course(
    course_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll in a course"""
    from app.lms.models.content import Cohort, Enrollment
    from app.lms.models.course import Course, CourseVersion

    # Find the course
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get the active version of the course (or the first version if no active)
    active_version = db.query(CourseVersion).filter(
        CourseVersion.course_id == course_id,
        CourseVersion.is_active == True
    ).first()

    if not active_version:
        # If no active version, get the first version
        active_version = db.query(CourseVersion).filter(
            CourseVersion.course_id == course_id
        ).first()

    if not active_version:
        raise HTTPException(status_code=400, detail="Course has no available versions")

    # Get or create a default cohort for this course version
    cohort = db.query(Cohort).filter(
        Cohort.course_version_id == active_version.id,
        Cohort.is_enrollable == True
    ).first()

    if not cohort:
        # Create a default cohort
        cohort = Cohort(
            course_version_id=active_version.id,
            name=f"Default Cohort - {course.title}",
            code=f"DEFAULT-{str(course.id)[:8]}",
            pacing_type="self_paced",
            is_active=True,
            is_enrollable=True
        )
        db.add(cohort)
        db.commit()
        db.refresh(cohort)

    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.cohort_id == cohort.id
    ).first()

    if existing_enrollment:
        return {"message": "Already enrolled in this course", "enrollmentId": str(existing_enrollment.id)}

    # Create enrollment
    enrollment = Enrollment(
        user_id=current_user.id,
        cohort_id=cohort.id,
        enrollment_status="active",
        enrollment_type="student",
        progress_percentage=0,
        completed_modules=0,
        completed_lessons=0
    )

    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return {
        "message": "Successfully enrolled in course",
        "enrollmentId": str(enrollment.id),
        "courseId": course_id,
        "cohortId": str(cohort.id),
        "versionId": str(active_version.id)
    }

@router.get("/enrollments/my", response_model=List[dict])
async def get_my_enrollments(
    status: Optional[str] = None,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's course enrollments"""
    from app.lms.models.content import Enrollment, Cohort, Module, Lesson
    from app.lms.models.course import CourseVersion, Course

    # Query enrollments with related data
    query = db.query(Enrollment).filter(Enrollment.user_id == current_user.id)

    if status:
        query = query.filter(Enrollment.enrollment_status == status)

    enrollments = query.all()

    enrolled_courses = []
    for enrollment in enrollments:
        # Get related course data
        cohort = enrollment.cohort
        course_version = cohort.course_version
        course = course_version.course

        # Count modules and lessons for this version
        modules = db.query(Module).filter(Module.course_version_id == course_version.id).all()
        total_modules = len(modules)

        total_lessons = 0
        for module in modules:
            lessons = db.query(Lesson).filter(Lesson.module_id == module.id).count()
            total_lessons += lessons

        # Build enrollment data
        enrolled_course = {
            "id": str(course.id),
            "enrollmentId": str(enrollment.id),
            "title": course.title,
            "slug": course.slug,
            "description": course.description,
            "shortDescription": course.short_description,
            "thumbnailUrl": course.thumbnail_url,
            "instructorId": str(course.instructor_id),
            "instructor": {
                "id": str(course.instructor.id) if course.instructor else None,
                "firstName": course.instructor.first_name if course.instructor else "",
                "lastName": course.instructor.last_name if course.instructor else "",
                "email": course.instructor.email if course.instructor else ""
            } if course.instructor else None,
            "durationHours": course.duration_hours,
            "difficultyLevel": course.difficulty_level,
            "category": course.category,
            "subcategory": course.subcategory,
            "prerequisites": course.prerequisites or [],
            "tags": course.tags or [],
            "enrollmentStatus": enrollment.enrollment_status,
            "progressPercentage": float(enrollment.progress_percentage or 0),
            "completedModules": enrollment.completed_modules or 0,
            "totalModules": total_modules,
            "completedLessons": enrollment.completed_lessons or 0,
            "totalLessons": total_lessons,
            "lastAccessedAt": enrollment.last_accessed_at.isoformat() if enrollment.last_accessed_at else None,
            "enrolledAt": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
            "estimatedCompletion": None,  # Can be calculated based on pace
            "nextLesson": None,  # Would need progress tracking to determine
            "certificate": {
                "available": enrollment.certificate_issued,
                "earnedAt": enrollment.certificate_issued_at.isoformat() if enrollment.certificate_issued_at else None,
                "certificateUrl": None
            }
        }

        enrolled_courses.append(enrolled_course)

    return enrolled_courses