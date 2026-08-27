"""VaniPath - Assessment Models"""
from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey, Integer, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=True)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    grade = Column(Integer, nullable=True)
    total_questions = Column(Integer, default=10)
    score = Column(Float, default=0.0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    weak_topics = Column(JSON, nullable=True)
    strong_topics = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    student = relationship("Student", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    progress = relationship("StudentProgress", back_populates="assessment")


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id = Column(String, primary_key=True, index=True)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_type = Column(String(50), default="mcq")
    hindi_text = Column(Text, nullable=False)
    santhali_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    topic = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    assessment = relationship("Assessment", back_populates="questions")


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"), nullable=False)
    assessment_id = Column(String, ForeignKey("assessments.id"), nullable=True)
    lessons_completed = Column(Integer, default=0)
    assessments_completed = Column(Integer, default=0)
    average_score = Column(Float, default=0.0)
    learning_streak = Column(Integer, default=0)
    strong_topics = Column(JSON, nullable=True)
    weak_topics = Column(JSON, nullable=True)
    badges = Column(JSON, nullable=True)
    last_activity_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    student = relationship("Student", back_populates="progress")
    assessment = relationship("Assessment", back_populates="progress")
