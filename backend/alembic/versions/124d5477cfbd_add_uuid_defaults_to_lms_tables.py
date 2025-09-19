"""Add UUID defaults to LMS tables

Revision ID: 124d5477cfbd
Revises: a0c9703b1504
Create Date: 2025-09-18 23:52:44.901447

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '124d5477cfbd'
down_revision: Union[str, Sequence[str], None] = 'a0c9703b1504'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add UUID generation defaults to all LMS tables."""
    # Add UUID generation extension if not exists
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Set default UUID generation for each table
    op.alter_column('lms_organizations', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_users', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_courses', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_course_versions', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_modules', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_lessons', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_content_items', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_cohorts', 'id',
                    server_default=sa.text('uuid_generate_v4()'))

    op.alter_column('lms_enrollments', 'id',
                    server_default=sa.text('uuid_generate_v4()'))


def downgrade() -> None:
    """Remove UUID generation defaults."""
    # Remove default UUID generation for each table
    op.alter_column('lms_organizations', 'id', server_default=None)
    op.alter_column('lms_users', 'id', server_default=None)
    op.alter_column('lms_courses', 'id', server_default=None)
    op.alter_column('lms_course_versions', 'id', server_default=None)
    op.alter_column('lms_modules', 'id', server_default=None)
    op.alter_column('lms_lessons', 'id', server_default=None)
    op.alter_column('lms_content_items', 'id', server_default=None)
    op.alter_column('lms_cohorts', 'id', server_default=None)
    op.alter_column('lms_enrollments', 'id', server_default=None)