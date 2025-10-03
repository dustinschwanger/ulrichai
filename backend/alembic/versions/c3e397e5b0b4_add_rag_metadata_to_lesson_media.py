"""add_rag_metadata_to_lesson_media

Revision ID: c3e397e5b0b4
Revises: f5c0a0514702
Create Date: 2025-10-02 10:24:54.113050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3e397e5b0b4'
down_revision: Union[str, Sequence[str], None] = 'f5c0a0514702'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add RAG metadata fields to lms_lesson_media table."""
    op.add_column('lms_lesson_media', sa.Column('display_name', sa.String(length=500), nullable=True))
    op.add_column('lms_lesson_media', sa.Column('document_source', sa.String(length=200), nullable=True))
    op.add_column('lms_lesson_media', sa.Column('document_type', sa.String(length=100), nullable=True))
    op.add_column('lms_lesson_media', sa.Column('capability_domain', sa.String(length=100), nullable=True))
    op.add_column('lms_lesson_media', sa.Column('author', sa.String(length=300), nullable=True))
    op.add_column('lms_lesson_media', sa.Column('publication_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('lms_lesson_media', sa.Column('is_indexed', sa.String(length=10), server_default='no', nullable=True))
    op.add_column('lms_lesson_media', sa.Column('indexed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('lms_lesson_media', sa.Column('transcription_status', sa.String(length=20), server_default='pending', nullable=True))
    op.add_column('lms_lesson_media', sa.Column('transcription_data', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove RAG metadata fields from lms_lesson_media table."""
    op.drop_column('lms_lesson_media', 'transcription_data')
    op.drop_column('lms_lesson_media', 'transcription_status')
    op.drop_column('lms_lesson_media', 'indexed_at')
    op.drop_column('lms_lesson_media', 'is_indexed')
    op.drop_column('lms_lesson_media', 'publication_date')
    op.drop_column('lms_lesson_media', 'author')
    op.drop_column('lms_lesson_media', 'capability_domain')
    op.drop_column('lms_lesson_media', 'document_type')
    op.drop_column('lms_lesson_media', 'document_source')
    op.drop_column('lms_lesson_media', 'display_name')
