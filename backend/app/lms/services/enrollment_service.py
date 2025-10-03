import logging
from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from app.lms.models.content import Enrollment, Cohort, Module, Lesson
from app.lms.models.course import Course
from app.lms.models.user import LMSUser, UserRole

logger = logging.getLogger(__name__)

class EnrollmentService:

    @staticmethod
    def is_user_enrolled_in_course(
        db: Session,
        user_id: UUID,
        course_id: UUID
    ) -> bool:
        try:
            enrollment = db.query(Enrollment).join(Cohort).filter(
                Enrollment.user_id == user_id,
                Cohort.course_id == course_id,
                Enrollment.enrollment_status.in_(["active", "completed"])
            ).first()

            return enrollment is not None

        except Exception as e:
            logger.error(f"Error checking enrollment: {e}")
            return False

    @staticmethod
    def is_user_instructor_of_course(
        db: Session,
        user_id: UUID,
        course_id: UUID
    ) -> bool:
        try:
            course = db.query(Course).filter(
                Course.id == course_id,
                Course.instructor_id == user_id
            ).first()

            return course is not None

        except Exception as e:
            logger.error(f"Error checking instructor status: {e}")
            return False

    @staticmethod
    def is_user_admin(
        db: Session,
        user_id: UUID
    ) -> bool:
        try:
            user = db.query(LMSUser).filter(
                LMSUser.id == user_id,
                LMSUser.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
            ).first()

            return user is not None

        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False

    @staticmethod
    def can_user_access_lesson(
        db: Session,
        user_id: UUID,
        lesson_id: UUID
    ) -> bool:
        try:
            # Check admin status first - admins have access to everything
            if EnrollmentService.is_user_admin(db, user_id):
                logger.info(f"Admin user {user_id} granted access to lesson {lesson_id}")
                return True

            lesson = db.query(Lesson).join(Module).filter(
                Lesson.id == lesson_id
            ).first()

            if not lesson or not lesson.module:
                logger.warning(f"Lesson {lesson_id} not found or incomplete structure")
                return False

            # Navigate through Module -> CourseVersion -> Course
            course_id = lesson.module.course_version.course_id

            if EnrollmentService.is_user_instructor_of_course(db, user_id, course_id):
                return True

            if EnrollmentService.is_user_enrolled_in_course(db, user_id, course_id):
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking lesson access: {e}")
            return False

    @staticmethod
    def get_course_id_for_lesson(
        db: Session,
        lesson_id: UUID
    ) -> Optional[UUID]:
        try:
            lesson = db.query(Lesson).join(Module).filter(
                Lesson.id == lesson_id
            ).first()

            if lesson and lesson.module and lesson.module.course_version:
                return lesson.module.course_version.course_id

            return None

        except Exception as e:
            logger.error(f"Error getting course for lesson: {e}")
            return None

enrollment_service = EnrollmentService()
