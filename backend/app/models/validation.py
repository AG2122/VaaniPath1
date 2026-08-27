"""VaniPath - Validation and Recommendation Models"""
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, JSON, Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class ValidationItem(Base):
    __tablename__ = "validation_queue"

    id = Column(String, primary_key=True, index=True)
    hindi = Column(Text, nullable=False)
    ai_translation = Column(Text, nullable=False)
    corrected_translation = Column(Text, nullable=True)
    source_language = Column(String(5), default="hi")
    target_language = Column(String(5), default="sat")
    confidence = Column(Float, default=0.0)
    status = Column(String(20), default="pending")  # pending, approved, rejected, edited
    validator_id = Column(String, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    audio_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)

    # Relationships
    validator = relationship("User", back_populates="validations")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # flashcard, worksheet, assessment, lesson
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=True)
    topic = Column(String(200), nullable=True)
    reason = Column(Text, nullable=True)
    priority = Column(Integer, default=1)
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
