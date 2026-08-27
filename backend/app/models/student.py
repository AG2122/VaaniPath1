"""VaniPath - Student Model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False, default=1)
    school = Column(String(200), nullable=True)
    preferred_language = Column(String(5), default="sat")
    target_language = Column(String(5), default="hi")
    teacher_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    teacher = relationship("User", back_populates="students")
    progress = relationship("StudentProgress", back_populates="student")
    assessments = relationship("Assessment", back_populates="student")
