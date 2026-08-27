"""VaniPath - Audio Utilities"""
import os
import hashlib
from typing import Optional
from app.config import settings


def ensure_audio_dir():
    """Ensure the audio directory exists."""
    os.makedirs(settings.AUDIO_CACHE_DIR, exist_ok=True)


def get_audio_path(text: str, language: str) -> str:
    """Generate a file path for cached audio based on text and language."""
    ensure_audio_dir()
    text_hash = hashlib.md5(f"{text}:{language}".encode()).hexdigest()
    return os.path.join(settings.AUDIO_CACHE_DIR, f"{language}_{text_hash}.wav")


def get_audio_url(text: str, language: str) -> str:
    """Generate a relative URL path for audio."""
    text_hash = hashlib.md5(f"{text}:{language}".encode()).hexdigest()
    return f"/audio/{language}_{text_hash}.wav"


def validate_audio_format(filename: str) -> bool:
    """Validate that the audio file format is allowed."""
    allowed = settings.ALLOWED_AUDIO_FORMATS.split(",")
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in allowed


def validate_file_size(size_bytes: int) -> bool:
    """Validate that the file size is within limits."""
    return size_bytes <= settings.max_upload_size_bytes


def get_audio_duration_estimate(text: str, language: str = "hi") -> int:
    """Estimate audio duration in ms based on text length."""
    words = len(text.split())
    # Rough estimate: 150 words per minute for Hindi, 130 for Santhali
    wpm = 130 if language == "sat" else 150
    return int((words / wpm) * 60 * 1000)
