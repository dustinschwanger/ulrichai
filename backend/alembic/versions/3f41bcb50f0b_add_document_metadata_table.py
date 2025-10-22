"""add document metadata table

Revision ID: 3f41bcb50f0b
Revises: 
Create Date: 2025-10-22 14:27:09.656643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f41bcb50f0b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'document_metadata',
        sa.Column('filename', sa.String(500), primary_key=True),
        sa.Column('display_name', sa.String(500), nullable=False),
        sa.Column('document_type', sa.String(100), nullable=False),
        sa.Column('document_source', sa.String(200), nullable=False),
        sa.Column('human_capability_domain', sa.String(100), nullable=False, server_default='hr'),
        sa.Column('author', sa.String(200), nullable=True),
        sa.Column('publication_date', sa.String(20), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('allow_download', sa.Boolean, server_default='true'),
        sa.Column('show_in_viewer', sa.Boolean, server_default='true'),
        sa.Column('bucket', sa.String(100), server_default='documents'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('document_metadata')
