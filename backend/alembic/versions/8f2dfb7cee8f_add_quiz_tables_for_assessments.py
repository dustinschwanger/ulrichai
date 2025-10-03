"""Add quiz tables for assessments

Revision ID: 8f2dfb7cee8f
Revises: f013b7a976b4
Create Date: 2025-09-19 13:32:19.018794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f2dfb7cee8f'
down_revision: Union[str, Sequence[str], None] = 'f013b7a976b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create lms_quizzes table
    op.create_table(
        'lms_quizzes',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('content_item_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=True),
        sa.Column('attempts_allowed', sa.Integer(), default=1),
        sa.Column('passing_score', sa.Numeric(5, 2), default=70.0),
        sa.Column('shuffle_questions', sa.Boolean(), default=False),
        sa.Column('shuffle_answers', sa.Boolean(), default=False),
        sa.Column('show_correct_answers', sa.Boolean(), default=True),
        sa.Column('show_feedback', sa.Boolean(), default=True),
        sa.Column('allow_review', sa.Boolean(), default=True),
        sa.Column('ai_generated', sa.Boolean(), default=False),
        sa.Column('generation_prompt', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['content_item_id'], ['lms_content_items.id']),
        sa.UniqueConstraint('content_item_id')
    )

    # Create lms_quiz_questions table
    op.create_table(
        'lms_quiz_questions',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('quiz_id', sa.UUID(), nullable=False),
        sa.Column('question_type', sa.String(50), nullable=False),  # Changed from Enum to String
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_media', sa.JSON(), nullable=True),
        sa.Column('options', sa.JSON(), default=[], nullable=True),
        sa.Column('correct_answers', sa.JSON(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('hint', sa.Text(), nullable=True),
        sa.Column('points', sa.Numeric(5, 2), default=1.0),
        sa.Column('partial_credit', sa.Boolean(), default=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('difficulty_level', sa.Integer(), default=3),
        sa.Column('tags', sa.ARRAY(sa.String()), default=[], nullable=True),
        sa.Column('ai_generated', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['quiz_id'], ['lms_quizzes.id'])
    )
    op.create_index('ix_lms_quiz_questions_quiz_id', 'lms_quiz_questions', ['quiz_id'])

    # Create lms_quiz_attempts table
    op.create_table(
        'lms_quiz_attempts',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('quiz_id', sa.UUID(), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False, default=1),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=True),
        sa.Column('score', sa.Numeric(5, 2), nullable=True),
        sa.Column('points_earned', sa.Numeric(5, 2), nullable=True),
        sa.Column('points_possible', sa.Numeric(5, 2), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(50), default='in_progress', nullable=False),  # Changed from Enum to String
        sa.Column('question_order', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['lms_users.id']),
        sa.ForeignKeyConstraint(['quiz_id'], ['lms_quizzes.id'])
    )
    op.create_index('ix_lms_quiz_attempts_user_id', 'lms_quiz_attempts', ['user_id'])
    op.create_index('ix_lms_quiz_attempts_quiz_id', 'lms_quiz_attempts', ['quiz_id'])

    # Create lms_quiz_responses table
    op.create_table(
        'lms_quiz_responses',
        sa.Column('id', sa.UUID(), nullable=False, default=sa.text('gen_random_uuid()')),
        sa.Column('attempt_id', sa.UUID(), nullable=False),
        sa.Column('question_id', sa.UUID(), nullable=False),
        sa.Column('answer', sa.JSON(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('points_earned', sa.Numeric(5, 2), default=0.0),
        sa.Column('instructor_feedback', sa.Text(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['attempt_id'], ['lms_quiz_attempts.id']),
        sa.ForeignKeyConstraint(['question_id'], ['lms_quiz_questions.id'])
    )
    op.create_index('ix_lms_quiz_responses_attempt_id', 'lms_quiz_responses', ['attempt_id'])
    op.create_index('ix_lms_quiz_responses_question_id', 'lms_quiz_responses', ['question_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_index('ix_lms_quiz_responses_question_id', 'lms_quiz_responses')
    op.drop_index('ix_lms_quiz_responses_attempt_id', 'lms_quiz_responses')
    op.drop_table('lms_quiz_responses')

    op.drop_index('ix_lms_quiz_attempts_quiz_id', 'lms_quiz_attempts')
    op.drop_index('ix_lms_quiz_attempts_user_id', 'lms_quiz_attempts')
    op.drop_table('lms_quiz_attempts')

    op.drop_index('ix_lms_quiz_questions_quiz_id', 'lms_quiz_questions')
    op.drop_table('lms_quiz_questions')

    op.drop_table('lms_quizzes')
