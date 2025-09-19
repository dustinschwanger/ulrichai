"""Add password and name fields to LMSUser

Revision ID: f013b7a976b4
Revises: 124d5477cfbd
Create Date: 2025-09-18 23:39:15.219635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f013b7a976b4'
down_revision: Union[str, Sequence[str], None] = '124d5477cfbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password and name fields to LMSUser."""
    # Add new columns
    op.add_column('lms_users', sa.Column('password_hash', sa.String(length=255), nullable=True))
    op.add_column('lms_users', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('lms_users', sa.Column('last_name', sa.String(length=100), nullable=True))

    # Set default values for existing rows
    op.execute("""
        UPDATE lms_users
        SET password_hash = 'temp_hash',
            first_name = SPLIT_PART(full_name, ' ', 1),
            last_name = COALESCE(SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1), '')
        WHERE full_name IS NOT NULL
    """)

    # Make columns non-nullable after setting values
    op.alter_column('lms_users', 'password_hash', nullable=False)
    op.alter_column('lms_users', 'first_name', nullable=False)
    op.alter_column('lms_users', 'last_name', nullable=False)

    # Drop the old column
    op.drop_column('lms_users', 'full_name')


def downgrade() -> None:
    """Revert to full_name field."""
    # Add full_name column back
    op.add_column('lms_users', sa.Column('full_name', sa.VARCHAR(length=255), nullable=True))

    # Populate full_name from first_name and last_name
    op.execute("""
        UPDATE lms_users
        SET full_name = CONCAT(first_name, ' ', last_name)
    """)

    # Make full_name non-nullable
    op.alter_column('lms_users', 'full_name', nullable=False)

    # Drop the new columns
    op.drop_column('lms_users', 'last_name')
    op.drop_column('lms_users', 'first_name')
    op.drop_column('lms_users', 'password_hash')