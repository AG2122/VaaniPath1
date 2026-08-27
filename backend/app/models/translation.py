"""VaniPath - Translation Models"""
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class Translation(Base):
    __tablename__ = "translations"

    id = Column(String, primary_key=True, index=True)
    source_text = Column(Text, nullable=False)
    translated_text = Column(Text, nullable=False)
    source_language = Column(String(5), nullable=False)
    target_language = Column(String(5), nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    context_subject = Column(String(100), nullable=True)
    context_grade = Column(Integer, nullable=True)
    context_topic = Column(String(200), nullable=True)
    processing_time_ms = Column(Integer, default=0)
    requires_validation = Column(Boolean, default=False)
    is_validated = Column(Boolean, default=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    feedback = relationship("TranslationFeedback", back_populates="translation")


class TranslationFeedback(Base):
    __tablename__ = "translation_feedback"

    id = Column(String, primary_key=True, index=True)
    translation_id = Column(String, ForeignKey("translations.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    corrected_text = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    translation = relationship("Translation", back_populates="feedback")
