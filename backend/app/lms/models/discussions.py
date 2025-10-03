"""
Discussion forum models for course lessons
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class DiscussionThread(Base):
    """
    Discussion threads for course lessons.
    Simple and intuitive for students and instructors.
    """
    __tablename__ = "lms_discussion_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    course_id = Column(UUID(as_uuid=True), ForeignKey("lms_courses.id"), nullable=False, index=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lms_lessons.id"), nullable=True, index=True)

    author_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)

    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)

    category = Column(String(50), default="general")

    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)

    upvotes = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)

    last_activity_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    author = relationship("LMSUser", backref="discussion_threads", foreign_keys=[author_id])
    replies = relationship("DiscussionReply", back_populates="thread", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DiscussionThread {self.title[:30]}>"


class DiscussionReply(Base):
    """
    Replies to discussion threads.
    Supports nested conversations.
    """
    __tablename__ = "lms_discussion_replies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    thread_id = Column(UUID(as_uuid=True), ForeignKey("lms_discussion_threads.id"), nullable=False, index=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)

    parent_reply_id = Column(UUID(as_uuid=True), ForeignKey("lms_discussion_replies.id"), nullable=True)

    content = Column(Text, nullable=False)

    is_solution = Column(Boolean, default=False)

    upvotes = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    thread = relationship("DiscussionThread", back_populates="replies")
    author = relationship("LMSUser", backref="discussion_replies", foreign_keys=[author_id])

    parent_reply = relationship("DiscussionReply", remote_side=[id], backref="child_replies")

    def __repr__(self):
        return f"<DiscussionReply {self.id}>"


class DiscussionUpvote(Base):
    """
    Tracks upvotes on threads and replies.
    Prevents duplicate upvotes per user.
    """
    __tablename__ = "lms_discussion_upvotes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), ForeignKey("lms_users.id"), nullable=False, index=True)

    thread_id = Column(UUID(as_uuid=True), ForeignKey("lms_discussion_threads.id"), nullable=True, index=True)
    reply_id = Column(UUID(as_uuid=True), ForeignKey("lms_discussion_replies.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<DiscussionUpvote user={self.user_id}>"