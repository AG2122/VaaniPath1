"""VaniPath - Worksheet Models"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class Worksheet(Base):
    __tablename__ = "worksheets"

    id = Column(String, primary_key=True, index=True)
    title = Column(String(200), nullable=True)
    grade = Column(Integer, nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    question_count = Column(Integer, default=10)
    language = Column(String(5), default="sat")
    teacher_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    questions = relationship("WorksheetQuestion", back_populates="worksheet", cascade="all, delete-orphan")


class WorksheetQuestion(Base):
    __tablename__ = "worksheet_questions"

    id = Column(String, primary_key=True, index=True)
    worksheet_id = Column(String, ForeignKey("worksheets.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_type = Column(String(50), default="mcq")  # mcq, fill_blank, matching, counting, picture
    hindi_text = Column(Text, nullable=False)
    santhali_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    worksheet = relationship("Worksheet", back_populates="questions")
