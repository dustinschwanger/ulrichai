from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from ...core.database import get_db
from ..services.auth_service import get_current_user, require_role
from ..models import LMSUser

router = APIRouter(prefix="/api/lms/courses", tags=["LMS Courses"])

# Mock data for development
MOCK_COURSES = [
    {
        "id": str(uuid4()),
        "organizationId": "test-org-id",
        "title": "Introduction to Machine Learning",
        "slug": "intro-to-ml",
        "description": "Learn the fundamentals of machine learning from scratch",
        "shortDescription": "Master ML basics with hands-on projects",
        "thumbnailUrl": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4",
        "instructorId": "instructor-1",
        "instructor": {
            "id": "instructor-1",
            "firstName": "Dr. Sarah",
            "lastName": "Johnson",
            "title": "AI Research Scientist",
            "avatarUrl": None
        },
        "durationHours": 12.5,
        "difficultyLevel": "beginner",
        "category": "Machine Learning",
        "subcategory": "Fundamentals",
        "prerequisites": [],
        "tags": ["machine-learning", "ai", "python", "data-science"],
        "isAiEnhanced": True,
        "isPublished": True,
        "isFeatured": True,
        "publishedAt": "2024-01-15T00:00:00Z",
        "enrollmentType": "open",
        "price": 0,
        "currency": "USD",
        "enrolledCount": 1234,
        "rating": 4.8,
        "reviewCount": 256,
        "features": {
            "hasVideo": True,
            "hasQuiz": True,
            "hasCertificate": True,
            "hasLifetimeAccess": True
        },
        "isBookmarked": False,
        "createdAt": "2024-01-10T00:00:00Z",
        "updatedAt": "2024-01-15T00:00:00Z"
    },
    {
        "id": str(uuid4()),
        "organizationId": "test-org-id",
        "title": "Advanced Python Programming",
        "slug": "advanced-python",
        "description": "Take your Python skills to the next level with advanced concepts",
        "shortDescription": "Deep dive into Python's advanced features",
        "thumbnailUrl": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935",
        "instructorId": "instructor-2",
        "instructor": {
            "id": "instructor-2",
            "firstName": "Michael",
            "lastName": "Chen",
            "title": "Senior Software Engineer",
            "avatarUrl": None
        },
        "durationHours": 20,
        "difficultyLevel": "advanced",
        "category": "Programming",
        "subcategory": "Python",
        "prerequisites": ["Basic Python knowledge", "OOP concepts"],
        "tags": ["python", "programming", "software-engineering"],
        "isAiEnhanced": True,
        "isPublished": True,
        "isFeatured": False,
        "publishedAt": "2024-02-01T00:00:00Z",
        "enrollmentType": "open",
        "price": 49.99,
        "currency": "USD",
        "enrolledCount": 856,
        "rating": 4.9,
        "reviewCount": 189,
        "features": {
            "hasVideo": True,
            "hasQuiz": True,
            "hasCertificate": True,
            "hasLifetimeAccess": True
        },
        "isBookmarked": False,
        "createdAt": "2024-01-25T00:00:00Z",
        "updatedAt": "2024-02-01T00:00:00Z"
    },
    {
        "id": str(uuid4()),
        "organizationId": "test-org-id",
        "title": "Data Visualization with D3.js",
        "slug": "data-viz-d3",
        "description": "Create stunning interactive visualizations with D3.js",
        "shortDescription": "Master data visualization techniques",
        "thumbnailUrl": "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
        "instructorId": "instructor-3",
        "instructor": {
            "id": "instructor-3",
            "firstName": "Emily",
            "lastName": "Rodriguez",
            "title": "Data Visualization Expert",
            "avatarUrl": None
        },
        "durationHours": 15,
        "difficultyLevel": "intermediate",
        "category": "Data Science",
        "subcategory": "Visualization",
        "prerequisites": ["JavaScript basics", "HTML/CSS"],
        "tags": ["d3js", "visualization", "javascript", "data"],
        "isAiEnhanced": False,
        "isPublished": True,
        "isFeatured": True,
        "publishedAt": "2024-01-20T00:00:00Z",
        "enrollmentType": "open",
        "price": 29.99,
        "currency": "USD",
        "enrolledCount": 567,
        "rating": 4.7,
        "reviewCount": 98,
        "features": {
            "hasVideo": True,
            "hasQuiz": False,
            "hasCertificate": True,
            "hasLifetimeAccess": True
        },
        "isBookmarked": False,
        "createdAt": "2024-01-18T00:00:00Z",
        "updatedAt": "2024-01-20T00:00:00Z"
    },
    {
        "id": str(uuid4()),
        "organizationId": "test-org-id",
        "title": "Web Development Bootcamp",
        "slug": "web-dev-bootcamp",
        "description": "Complete web development course from HTML to deployment",
        "shortDescription": "Become a full-stack web developer",
        "thumbnailUrl": "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
        "instructorId": "instructor-4",
        "instructor": {
            "id": "instructor-4",
            "firstName": "Alex",
            "lastName": "Thompson",
            "title": "Full-Stack Developer",
            "avatarUrl": None
        },
        "durationHours": 45,
        "difficultyLevel": "beginner",
        "category": "Web Development",
        "subcategory": "Full-Stack",
        "prerequisites": [],
        "tags": ["html", "css", "javascript", "react", "node"],
        "isAiEnhanced": True,
        "isPublished": True,
        "isFeatured": True,
        "publishedAt": "2024-01-05T00:00:00Z",
        "enrollmentType": "open",
        "price": 79.99,
        "currency": "USD",
        "enrolledCount": 2341,
        "rating": 4.8,
        "reviewCount": 512,
        "features": {
            "hasVideo": True,
            "hasQuiz": True,
            "hasCertificate": True,
            "hasLifetimeAccess": True
        },
        "isBookmarked": False,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-05T00:00:00Z"
    },
    {
        "id": str(uuid4()),
        "organizationId": "test-org-id",
        "title": "React Native Mobile Development",
        "slug": "react-native-mobile",
        "description": "Build cross-platform mobile apps with React Native",
        "shortDescription": "Create iOS and Android apps with one codebase",
        "thumbnailUrl": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c",
        "instructorId": "instructor-5",
        "instructor": {
            "id": "instructor-5",
            "firstName": "Lisa",
            "lastName": "Wang",
            "title": "Mobile App Developer",
            "avatarUrl": None
        },
        "durationHours": 25,
        "difficultyLevel": "intermediate",
        "category": "Mobile Development",
        "subcategory": "React Native",
        "prerequisites": ["React basics", "JavaScript ES6+"],
        "tags": ["react-native", "mobile", "ios", "android"],
        "isAiEnhanced": False,
        "isPublished": True,
        "isFeatured": False,
        "publishedAt": "2024-02-10T00:00:00Z",
        "enrollmentType": "open",
        "price": 59.99,
        "currency": "USD",
        "enrolledCount": 723,
        "rating": 4.6,
        "reviewCount": 145,
        "features": {
            "hasVideo": True,
            "hasQuiz": True,
            "hasCertificate": True,
            "hasLifetimeAccess": False
        },
        "isBookmarked": False,
        "createdAt": "2024-02-05T00:00:00Z",
        "updatedAt": "2024-02-10T00:00:00Z"
    },
    {
        "id": str(uuid4()),
        "organizationId": "test-org-id",
        "title": "Cloud Architecture with AWS",
        "slug": "aws-cloud-architecture",
        "description": "Design and deploy scalable applications on AWS",
        "shortDescription": "Master AWS cloud services and architecture",
        "thumbnailUrl": "https://images.unsplash.com/photo-1451187580459-43490279c0fa",
        "instructorId": "instructor-6",
        "instructor": {
            "id": "instructor-6",
            "firstName": "David",
            "lastName": "Kumar",
            "title": "Cloud Solutions Architect",
            "avatarUrl": None
        },
        "durationHours": 30,
        "difficultyLevel": "advanced",
        "category": "Cloud Computing",
        "subcategory": "AWS",
        "prerequisites": ["Basic cloud concepts", "Linux fundamentals"],
        "tags": ["aws", "cloud", "devops", "architecture"],
        "isAiEnhanced": True,
        "isPublished": True,
        "isFeatured": True,
        "publishedAt": "2024-01-25T00:00:00Z",
        "enrollmentType": "open",
        "price": 89.99,
        "currency": "USD",
        "enrolledCount": 432,
        "rating": 4.9,
        "reviewCount": 87,
        "features": {
            "hasVideo": True,
            "hasQuiz": True,
            "hasCertificate": True,
            "hasLifetimeAccess": True
        },
        "isBookmarked": False,
        "createdAt": "2024-01-20T00:00:00Z",
        "updatedAt": "2024-01-25T00:00:00Z"
    }
]

MOCK_CATEGORIES = [
    "Machine Learning",
    "Programming",
    "Data Science",
    "Web Development",
    "Mobile Development",
    "Cloud Computing",
    "DevOps",
    "Cybersecurity",
    "Database",
    "AI & Deep Learning"
]

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
    """Get paginated list of courses with filters"""

    # Filter courses based on criteria
    filtered_courses = [c for c in MOCK_COURSES if c["isPublished"] == isPublished]

    if search:
        search_lower = search.lower()
        filtered_courses = [
            c for c in filtered_courses
            if search_lower in c["title"].lower() or search_lower in c["description"].lower()
        ]

    if category:
        filtered_courses = [c for c in filtered_courses if c["category"] == category]

    if difficultyLevel:
        filtered_courses = [c for c in filtered_courses if c["difficultyLevel"] == difficultyLevel]

    if minRating:
        filtered_courses = [c for c in filtered_courses if c["rating"] >= minRating]

    if maxPrice is not None:
        filtered_courses = [c for c in filtered_courses if c["price"] <= maxPrice]

    if minPrice is not None:
        filtered_courses = [c for c in filtered_courses if c["price"] >= minPrice]

    # Sort courses
    if sortBy == "popular":
        filtered_courses.sort(key=lambda x: x["enrolledCount"], reverse=True)
    elif sortBy == "newest":
        filtered_courses.sort(key=lambda x: x["publishedAt"], reverse=True)
    elif sortBy == "rating":
        filtered_courses.sort(key=lambda x: x["rating"], reverse=True)
    elif sortBy == "price":
        filtered_courses.sort(key=lambda x: x["price"])

    # Paginate
    total = len(filtered_courses)
    start = (page - 1) * pageSize
    end = start + pageSize
    paginated_courses = filtered_courses[start:end]

    return {
        "items": paginated_courses,
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "totalPages": (total + pageSize - 1) // pageSize
    }

@router.get("/categories", response_model=List[str])
async def get_categories(
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of course categories"""
    return MOCK_CATEGORIES

@router.get("/{course_id}", response_model=dict)
async def get_course(
    course_id: str,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get course details by ID"""
    for course in MOCK_COURSES:
        if course["id"] == course_id:
            return course
    raise HTTPException(status_code=404, detail="Course not found")

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
    # Find the course
    course_found = None
    for course in MOCK_COURSES:
        if course["id"] == course_id:
            course_found = course
            break

    if not course_found:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if already enrolled
    user_id = str(current_user.id)
    if user_id not in USER_ENROLLMENTS:
        USER_ENROLLMENTS[user_id] = []

    for enrollment in USER_ENROLLMENTS[user_id]:
        if enrollment["id"] == course_id:
            return {"message": "Already enrolled in this course", "enrollment": enrollment}

    # Create enrollment
    enrollment = {
        **course_found,
        "enrollmentId": str(uuid4()),
        "userId": current_user.id,
        "courseId": course_id,
        "enrollmentStatus": "active",
        "progressPercentage": 0,
        "completedModules": 0,
        "totalModules": 8,
        "completedLessons": 0,
        "totalLessons": 32,
        "enrolledAt": datetime.utcnow().isoformat(),
        "lastAccessedAt": None,
        "estimatedCompletion": None,
        "nextLesson": None,
        "certificate": {
            "available": False,
            "earnedAt": None,
            "certificateUrl": None
        }
    }

    USER_ENROLLMENTS[user_id].append(enrollment)
    return enrollment

@router.get("/enrollments/my", response_model=List[dict])
async def get_my_enrollments(
    status: Optional[str] = None,
    current_user: LMSUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's course enrollments"""
    user_id = str(current_user.id)

    # Return enrolled courses if user has enrollments
    if user_id in USER_ENROLLMENTS:
        enrolled_courses = USER_ENROLLMENTS[user_id]
        if status:
            enrolled_courses = [e for e in enrolled_courses if e["enrollmentStatus"] == status]
        return enrolled_courses

    # Otherwise return default mock enrolled courses with progress
    enrolled_courses = []

    # Take first 3 courses as enrolled by default
    for i, course in enumerate(MOCK_COURSES[:3]):
        enrollment = {
            **course,
            "enrollmentId": str(uuid4()),
            "enrollmentStatus": "active",
            "progressPercentage": [45, 80, 15][i],  # Different progress levels
            "completedModules": [3, 7, 1][i],
            "totalModules": [7, 9, 8][i],
            "completedLessons": [12, 28, 3][i],
            "totalLessons": [28, 35, 32][i],
            "lastAccessedAt": ["2025-01-18T10:30:00Z", "2025-01-19T08:15:00Z", "2025-01-17T14:45:00Z"][i],
            "enrolledAt": ["2024-12-15T00:00:00Z", "2024-11-20T00:00:00Z", "2025-01-10T00:00:00Z"][i],
            "estimatedCompletion": ["2025-02-15", "2025-01-25", "2025-03-01"][i],
            "nextLesson": {
                "id": str(uuid4()),
                "title": ["Variables and Data Types", "Advanced State Management", "Python Basics"][i],
                "moduleTitle": ["Module 4: Core Concepts", "Module 8: Advanced Topics", "Module 2: Getting Started"][i],
                "duration": [15, 20, 25][i]
            },
            "certificate": {
                "available": [False, True, False][i],
                "earnedAt": [None, "2025-01-19T08:30:00Z", None][i],
                "certificateUrl": [None, "/certificates/abc123", None][i]
            }
        }

        if not status or status == "active":
            enrolled_courses.append(enrollment)

    # Store these default enrollments for the user
    USER_ENROLLMENTS[user_id] = enrolled_courses

    return enrolled_courses