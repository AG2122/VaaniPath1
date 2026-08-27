"""VaniPath - Flashcard Model"""
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from datetime import datetime, timezone

from app.database.database import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # Animals, Numbers, Colors, Family, Food, Nature, School
    hindi = Column(String(200), nullable=False)
    santhali = Column(String(200), nullable=False)
    pronunciation = Column(String(300), nullable=True)
    image_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    grade = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
