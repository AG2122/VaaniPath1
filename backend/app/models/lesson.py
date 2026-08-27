"""VaniPath - Lesson Model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    grade = Column(Integer, nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    learning_outcome = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # JSON content
    language = Column(String(5), default="sat")
    teacher_id = Column(String, ForeignKey("users.id"), nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    teacher = relationship("User", back_populates="lessons")
