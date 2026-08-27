"""VaniPath - Language Pack and Offline Models"""
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Integer, Boolean, ForeignKey
from datetime import datetime, timezone

from app.database.database import Base


class SanthaliVocabulary(Base):
    __tablename__ = "santhali_vocabulary"

    id = Column(String, primary_key=True, index=True)
    hindi = Column(String(200), nullable=False, index=True)
    santhali = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)  # numbers, classroom, nature, etc.
    phonetic = Column(String(300), nullable=True)
    usage_example = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    source = Column(String(50), default="dictionary")  # dictionary, validated, ai
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SanthaliPhrase(Base):
    __tablename__ = "santhali_phrases"

    id = Column(String, primary_key=True, index=True)
    hindi = Column(Text, nullable=False)
    santhali = Column(Text, nullable=False)
    english = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # classroom, greeting, instruction
    audio_path = Column(String(500), nullable=True)
    confidence = Column(Float, default=0.98)
    is_cached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LanguagePack(Base):
    __tablename__ = "language_packs"

    id = Column(String, primary_key=True, index=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    language_code = Column(String(5), nullable=False, default="sat")
    vocabulary_count = Column(Integer, default=0)
    phrase_count = Column(Integer, default=0)
    pack_data = Column(JSON, nullable=True)
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ContentPack(Base):
    __tablename__ = "content_packs"

    id = Column(String, primary_key=True, index=True)
    version = Column(String(20), nullable=False, default="1.0.0")
    content_type = Column(String(50), nullable=False)  # curriculum, worksheets, flashcards
    grade = Column(Integer, nullable=True)
    pack_data = Column(JSON, nullable=True)
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class OfflineSync(Base):
    __tablename__ = "offline_sync"

    id = Column(String, primary_key=True, index=True)
    device_id = Column(String(100), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    sync_type = Column(String(50), nullable=False)  # upload, download
    data_type = Column(String(100), nullable=False)  # translations, corrections, assessments, etc.
    data_payload = Column(JSON, nullable=True)
    status = Column(String(20), default="pending")  # pending, synced, failed
    version = Column(String(20), nullable=True)
    checksum = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    synced_at = Column(DateTime, nullable=True)


class AudioCache(Base):
    __tablename__ = "audio_cache"

    id = Column(String, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    language_code = Column(String(5), nullable=False)
    audio_path = Column(String(500), nullable=False)
    duration_ms = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
