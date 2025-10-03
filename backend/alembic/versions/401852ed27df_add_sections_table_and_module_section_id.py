"""add_sections_table_and_module_section_id

Revision ID: 401852ed27df
Revises: c3e397e5b0b4
Create Date: 2025-10-02 11:15:22.898269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '401852ed27df'
down_revision: Union[str, Sequence[str], None] = 'c3e397e5b0b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create sections table
    op.create_table(
        'lms_sections',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('course_version_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('is_optional', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('is_locked', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['course_version_id'], ['lms_course_versions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lms_sections_course_version_id'), 'lms_sections', ['course_version_id'], unique=False)

    # Add section_id column to modules table (nullable at first for migration)
    op.add_column('lms_modules', sa.Column('section_id', sa.UUID(), nullable=True))
    op.create_index(op.f('ix_lms_modules_section_id'), 'lms_modules', ['section_id'], unique=False)
    op.create_foreign_key('fk_lms_modules_section_id', 'lms_modules', 'lms_sections', ['section_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove section_id from modules
    op.drop_constraint('fk_lms_modules_section_id', 'lms_modules', type_='foreignkey')
    op.drop_index(op.f('ix_lms_modules_section_id'), table_name='lms_modules')
    op.drop_column('lms_modules', 'section_id')

    # Drop sections table
    op.drop_index(op.f('ix_lms_sections_course_version_id'), table_name='lms_sections')
    op.drop_table('lms_sections')
