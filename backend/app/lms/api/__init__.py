"""
LMS API module.
"""

from .organizations import router as organizations_router
from .auth import router as auth_router
from .courses import router as courses_router
from .qa import router as qa_router
from .notes import router as notes_router
from .quiz import router as quiz_router
from .course_builder import router as course_builder_router
from .discussions import router as discussions_router
from .progress import router as progress_router

__all__ = ["organizations_router", "auth_router", "courses_router", "qa_router", "notes_router", "quiz_router", "course_builder_router", "discussions_router", "progress_router"]