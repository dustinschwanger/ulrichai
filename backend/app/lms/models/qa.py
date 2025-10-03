from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

# Association table for question upvotes
question_upvotes = Table(
    'question_upvotes',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('lms_users.id'), primary_key=True),
    Column('question_id', UUID(as_uuid=True), ForeignKey('lesson_questions.id'), primary_key=True)
)

# Association table for answer upvotes
answer_upvotes = Table(
    'answer_upvotes',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('lms_users.id'), primary_key=True),
    Column('answer_id', UUID(as_uuid=True), ForeignKey('question_answers.id'), primary_key=True)
)


class LessonQuestion(Base):
    __tablename__ = "lesson_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lesson_id = Column(String, nullable=False)
    course_id = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('lms_users.id'), nullable=False)
    question = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("LMSUser")
    answers = relationship("QuestionAnswer", back_populates="question", cascade="all, delete-orphan")
    upvoters = relationship("LMSUser", secondary=question_upvotes)


class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey('lesson_questions.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('lms_users.id'), nullable=False)
    answer = Column(Text, nullable=False)
    is_instructor = Column(Boolean, default=False)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    question = relationship("LessonQuestion", back_populates="answers")
    user = relationship("LMSUser")
    upvoters = relationship("LMSUser", secondary=answer_upvotes)