"""add_discussions_notes_qa_progress_tracking_tables

Revision ID: 5e14c3d15825
Revises: 302339f89470
Create Date: 2025-09-26 11:57:33.375819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e14c3d15825'
down_revision: Union[str, Sequence[str], None] = '302339f89470'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add essential LMS tables for discussions, notes, Q&A, and progress tracking.
    Designed for simplicity and ease of use for both students and instructors.
    """
    from sqlalchemy.dialects.postgresql import UUID

    op.create_table(
        'lms_discussion_threads',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('course_id', UUID(as_uuid=True), sa.ForeignKey('lms_courses.id'), nullable=False, index=True),
        sa.Column('lesson_id', UUID(as_uuid=True), sa.ForeignKey('lms_lessons.id'), nullable=True, index=True),
        sa.Column('author_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False, index=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), default='general'),
        sa.Column('is_pinned', sa.Boolean(), default=False),
        sa.Column('is_locked', sa.Boolean(), default=False),
        sa.Column('is_resolved', sa.Boolean(), default=False),
        sa.Column('upvotes', sa.Integer(), default=0),
        sa.Column('reply_count', sa.Integer(), default=0),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )

    op.create_table(
        'lms_discussion_replies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('thread_id', UUID(as_uuid=True), sa.ForeignKey('lms_discussion_threads.id'), nullable=False, index=True),
        sa.Column('author_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False, index=True),
        sa.Column('parent_reply_id', UUID(as_uuid=True), sa.ForeignKey('lms_discussion_replies.id'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_solution', sa.Boolean(), default=False),
        sa.Column('upvotes', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )

    op.create_table(
        'lms_discussion_upvotes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False, index=True),
        sa.Column('thread_id', UUID(as_uuid=True), sa.ForeignKey('lms_discussion_threads.id'), nullable=True, index=True),
        sa.Column('reply_id', UUID(as_uuid=True), sa.ForeignKey('lms_discussion_replies.id'), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )

    op.create_table(
        'lesson_notes',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('lesson_id', sa.String(), nullable=False),
        sa.Column('course_id', sa.String(), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.String(), nullable=True),
        sa.Column('tags', sa.JSON(), default=[]),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )

    op.create_table(
        'lesson_questions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('lesson_id', sa.String(), nullable=False),
        sa.Column('course_id', sa.String(), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )

    op.create_table(
        'question_answers',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('question_id', UUID(as_uuid=True), sa.ForeignKey('lesson_questions.id'), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('is_instructor', sa.Boolean(), default=False),
        sa.Column('is_accepted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now())
    )

    op.create_table(
        'question_upvotes',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), primary_key=True),
        sa.Column('question_id', UUID(as_uuid=True), sa.ForeignKey('lesson_questions.id'), primary_key=True)
    )

    op.create_table(
        'answer_upvotes',
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), primary_key=True),
        sa.Column('answer_id', UUID(as_uuid=True), sa.ForeignKey('question_answers.id'), primary_key=True)
    )

    op.create_table(
        'lms_lesson_progress',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False, index=True),
        sa.Column('lesson_id', UUID(as_uuid=True), sa.ForeignKey('lms_lessons.id'), nullable=False, index=True),
        sa.Column('enrollment_id', UUID(as_uuid=True), sa.ForeignKey('lms_enrollments.id'), nullable=False, index=True),
        sa.Column('status', sa.String(50), default='not_started', nullable=False),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent_seconds', sa.Integer(), default=0),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )

    op.create_table(
        'lms_content_progress',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False, index=True),
        sa.Column('content_item_id', UUID(as_uuid=True), sa.ForeignKey('lms_content_items.id'), nullable=False, index=True),
        sa.Column('lesson_progress_id', UUID(as_uuid=True), sa.ForeignKey('lms_lesson_progress.id'), nullable=False),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('status', sa.String(50), default='not_started'),
        sa.Column('last_position', sa.JSON(), nullable=True),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )

    op.create_table(
        'lms_module_progress',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('lms_users.id'), nullable=False, index=True),
        sa.Column('module_id', UUID(as_uuid=True), sa.ForeignKey('lms_modules.id'), nullable=False, index=True),
        sa.Column('enrollment_id', UUID(as_uuid=True), sa.ForeignKey('lms_enrollments.id'), nullable=False, index=True),
        sa.Column('completed_lessons', sa.Integer(), default=0),
        sa.Column('total_lessons', sa.Integer(), nullable=False),
        sa.Column('progress_percentage', sa.Integer(), default=0),
        sa.Column('is_complete', sa.Boolean(), default=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )


def downgrade() -> None:
    """Remove all tables added in this migration."""
    op.drop_table('lms_module_progress')
    op.drop_table('lms_content_progress')
    op.drop_table('lms_lesson_progress')
    op.drop_table('answer_upvotes')
    op.drop_table('question_upvotes')
    op.drop_table('question_answers')
    op.drop_table('lesson_questions')
    op.drop_table('lesson_notes')
    op.drop_table('lms_discussion_upvotes')
    op.drop_table('lms_discussion_replies')
    op.drop_table('lms_discussion_threads')
