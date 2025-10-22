from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class DocumentMetadata(Base):
    """Store metadata for uploaded documents and videos"""
    __tablename__ = 'document_metadata'

    filename = Column(String(500), primary_key=True)  # Primary key
    display_name = Column(String(500), nullable=False)
    document_type = Column(String(100), nullable=False)  # video, article, case-study, etc.
    document_source = Column(String(200), nullable=False)  # institute, upload, dave-ulrich-hr-academy, etc.
    human_capability_domain = Column(String(100), nullable=False, default='hr')
    author = Column(String(200), nullable=True)
    publication_date = Column(String(20), nullable=True)  # Store as ISO date string
    description = Column(Text, nullable=True)
    allow_download = Column(Boolean, default=True)
    show_in_viewer = Column(Boolean, default=True)
    bucket = Column(String(100), default='documents')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'filename': self.filename,
            'displayName': self.display_name,
            'documentType': self.document_type,
            'documentSource': self.document_source,
            'humanCapabilityDomain': self.human_capability_domain,
            'author': self.author,
            'publicationDate': self.publication_date,
            'description': self.description,
            'allowDownload': self.allow_download,
            'showInViewer': self.show_in_viewer,
            'bucket': self.bucket,
            'uploadDate': self.updated_at.isoformat() if self.updated_at else self.created_at.isoformat()
        }
