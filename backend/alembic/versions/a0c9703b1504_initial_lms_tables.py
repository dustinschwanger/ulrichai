"""Initial LMS tables

Revision ID: a0c9703b1504
Revises:
Create Date: 2025-09-18 23:23:39.600799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a0c9703b1504'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create LMS tables."""
    # Create organizations table
    op.create_table('lms_organizations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('logo_url', sa.Text(), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True, server_default='#0066CC'),
        sa.Column('secondary_color', sa.String(length=7), nullable=True, server_default='#FF6600'),
        sa.Column('custom_domain', sa.String(length=255), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('features', sa.JSON(), nullable=False, server_default='{"ai_chat": true, "ai_course_builder": true, "discussions": true, "reflections": true, "white_labeling": false}'),
        sa.Column('subscription_tier', sa.String(length=50), nullable=True, server_default='basic'),
        sa.Column('max_users', sa.Integer(), nullable=True, server_default='100'),
        sa.Column('max_courses', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('storage_limit_gb', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
        sa.UniqueConstraint('custom_domain')
    )
    op.create_index(op.f('ix_lms_organizations_name'), 'lms_organizations', ['name'], unique=False)
    op.create_index(op.f('ix_lms_organizations_slug'), 'lms_organizations', ['slug'], unique=True)

    # Create users table
    op.create_table('lms_users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('role', sa.Enum('STUDENT', 'INSTRUCTOR', 'ADMIN', 'SUPER_ADMIN', name='userrole'), nullable=False, server_default='STUDENT'),
        sa.Column('permissions', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('company_name', sa.String(length=255), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=True),
        sa.Column('department', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=255), nullable=True),
        sa.Column('company_size', sa.String(length=50), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('learning_goals', postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('preferred_learning_style', sa.String(length=50), nullable=True),
        sa.Column('time_zone', sa.String(length=50), nullable=True, server_default='UTC'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('profile_data', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('onboarding_completed', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['lms_organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_lms_users_email'), 'lms_users', ['email'], unique=True)
    op.create_index(op.f('ix_lms_users_organization_id'), 'lms_users', ['organization_id'], unique=False)

    # Create courses table
    op.create_table('lms_courses',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('slug', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('instructor_id', sa.UUID(), nullable=False),
        sa.Column('duration_hours', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('difficulty_level', sa.String(length=50), nullable=True, server_default='beginner'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('prerequisites', postgresql.ARRAY(sa.UUID()), nullable=False, server_default='{}'),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('is_ai_enhanced', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('ai_features', sa.JSON(), nullable=False, server_default='{"ai_chat": true, "ai_summaries": false, "ai_quiz_generation": false, "ai_personalization": false}'),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_featured', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('enrollment_type', sa.String(length=50), nullable=True, server_default='open'),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True, server_default='0.00'),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['instructor_id'], ['lms_users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['lms_organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lms_courses_organization_id'), 'lms_courses', ['organization_id'], unique=False)

    # Create course versions table
    op.create_table('lms_course_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('course_id', sa.UUID(), nullable=False),
        sa.Column('version_number', sa.String(length=20), nullable=False),
        sa.Column('version_name', sa.String(length=255), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_draft', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_ai_generated', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('ai_generation_data', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['lms_courses.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['lms_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('course_id', 'version_number')
    )
    op.create_index(op.f('ix_lms_course_versions_course_id'), 'lms_course_versions', ['course_id'], unique=False)

    # Create cohorts table
    op.create_table('lms_cohorts',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('course_version_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('enrollment_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('pacing_type', sa.String(length=50), nullable=True, server_default='self_paced'),
        sa.Column('max_students', sa.Integer(), nullable=True),
        sa.Column('is_waitlist_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('settings', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('discussion_visibility', sa.String(length=50), nullable=True, server_default='cohort'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_enrollable', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_version_id'], ['lms_course_versions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_lms_cohorts_course_version_id'), 'lms_cohorts', ['course_version_id'], unique=False)

    # Create modules table
    op.create_table('lms_modules',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('course_version_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('learning_objectives', postgresql.ARRAY(sa.Text()), nullable=False, server_default='{}'),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_optional', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_locked', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('unlock_requirements', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_version_id'], ['lms_course_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lms_modules_course_version_id'), 'lms_modules', ['course_version_id'], unique=False)

    # Create enrollments table
    op.create_table('lms_enrollments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('cohort_id', sa.UUID(), nullable=False),
        sa.Column('enrollment_status', sa.String(length=50), nullable=True, server_default='active'),
        sa.Column('enrollment_type', sa.String(length=50), nullable=True, server_default='student'),
        sa.Column('progress_percentage', sa.Numeric(precision=5, scale=2), nullable=True, server_default='0.0'),
        sa.Column('completed_modules', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('completed_lessons', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('enrolled_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_grade', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('final_grade', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('certificate_issued', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('certificate_issued_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['cohort_id'], ['lms_cohorts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['lms_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'cohort_id')
    )
    op.create_index(op.f('ix_lms_enrollments_cohort_id'), 'lms_enrollments', ['cohort_id'], unique=False)
    op.create_index(op.f('ix_lms_enrollments_user_id'), 'lms_enrollments', ['user_id'], unique=False)

    # Create lessons table
    op.create_table('lms_lessons',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('module_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('lesson_type', sa.String(length=50), nullable=True, server_default='standard'),
        sa.Column('estimated_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('passing_criteria', sa.JSON(), nullable=True),
        sa.Column('ai_enhanced_content', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['lms_modules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lms_lessons_module_id'), 'lms_lessons', ['module_id'], unique=False)

    # Create content items table
    op.create_table('lms_content_items',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('lesson_id', sa.UUID(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('content_data', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('is_required', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('points_possible', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('completion_criteria', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['lesson_id'], ['lms_lessons.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lms_content_items_lesson_id'), 'lms_content_items', ['lesson_id'], unique=False)


def downgrade() -> None:
    """Drop LMS tables."""
    # Drop tables in reverse order of creation (due to foreign key constraints)
    op.drop_index(op.f('ix_lms_content_items_lesson_id'), table_name='lms_content_items')
    op.drop_table('lms_content_items')

    op.drop_index(op.f('ix_lms_lessons_module_id'), table_name='lms_lessons')
    op.drop_table('lms_lessons')

    op.drop_index(op.f('ix_lms_enrollments_user_id'), table_name='lms_enrollments')
    op.drop_index(op.f('ix_lms_enrollments_cohort_id'), table_name='lms_enrollments')
    op.drop_table('lms_enrollments')

    op.drop_index(op.f('ix_lms_modules_course_version_id'), table_name='lms_modules')
    op.drop_table('lms_modules')

    op.drop_index(op.f('ix_lms_cohorts_course_version_id'), table_name='lms_cohorts')
    op.drop_table('lms_cohorts')

    op.drop_index(op.f('ix_lms_course_versions_course_id'), table_name='lms_course_versions')
    op.drop_table('lms_course_versions')

    op.drop_index(op.f('ix_lms_courses_organization_id'), table_name='lms_courses')
    op.drop_table('lms_courses')

    op.drop_index(op.f('ix_lms_users_organization_id'), table_name='lms_users')
    op.drop_index(op.f('ix_lms_users_email'), table_name='lms_users')
    op.drop_table('lms_users')

    op.drop_index(op.f('ix_lms_organizations_slug'), table_name='lms_organizations')
    op.drop_index(op.f('ix_lms_organizations_name'), table_name='lms_organizations')
    op.drop_table('lms_organizations')

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS userrole")