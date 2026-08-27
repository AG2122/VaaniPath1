"""VaniPath - User Model"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

from app.database.database import Base


class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"
    VALIDATOR = "validator"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mobile = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.TEACHER.value)
    school = Column(String(200), nullable=True)
    preferred_language = Column(String(5), default="hi")
    target_language = Column(String(5), default="sat")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    students = relationship("Student", back_populates="teacher")
    lessons = relationship("Lesson", back_populates="teacher")
    validations = relationship("ValidationItem", back_populates="validator")
