"""VaniPath - Classroom Models"""
from sqlalchemy import Column, String, Float, DateTime, Text, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class ClassroomSession(Base):
    __tablename__ = "classroom_sessions"

    id = Column(String, primary_key=True, index=True)
    teacher_id = Column(String, ForeignKey("users.id"), nullable=True)
    grade = Column(Integer, nullable=True)
    subject = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)

    # Relationships
    messages = relationship("ClassroomMessage", back_populates="session")


class ClassroomMessage(Base):
    __tablename__ = "classroom_messages"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("classroom_sessions.id"), nullable=False)
    speaker = Column(String(50), nullable=False)  # "teacher" or "student"
    source_language = Column(String(5), nullable=False)
    target_language = Column(String(5), nullable=False)
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    confidence = Column(Float, default=0.0)
    audio_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    session = relationship("ClassroomSession", back_populates="messages")
