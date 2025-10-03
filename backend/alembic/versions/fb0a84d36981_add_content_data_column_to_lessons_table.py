"""Add content_data column to lessons table

Revision ID: fb0a84d36981
Revises: 8f2dfb7cee8f
Create Date: 2025-09-19 15:36:31.377597

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'fb0a84d36981'
down_revision: Union[str, Sequence[str], None] = '8f2dfb7cee8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add content_data column to lms_lessons table
    op.add_column('lms_lessons', sa.Column('content_data', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove content_data column from lms_lessons table
    op.drop_column('lms_lessons', 'content_data')