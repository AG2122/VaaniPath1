"""VaniPath - Text-to-Speech Service"""
import os
from typing import Dict, Optional
from app.utils.audio import get_audio_path, get_audio_url, ensure_audio_dir


class TTSService:
    """Text-to-speech service abstraction.

    In development mode, returns audio path references.
    Architecture ready for integration with Google TTS, Azure TTS, etc.
    """

    def __init__(self):
        self.provider = "local"
        ensure_audio_dir()

    def synthesize(self, text: str, language: str = "sat") -> Dict:
        """Convert text to speech audio.

        Returns: {"audio_url": "...", "audio_path": "...", "duration_ms": 0, "file_size_bytes": 0}
        """
        if not text.strip():
            return {"error": "Empty text", "audio_url": None}

        audio_path = get_audio_path(text, language)
        audio_url = get_audio_url(text, language)

        # Development fallback: create a placeholder audio reference
        # In production, this would generate actual audio via TTS engine
        if not os.path.exists(audio_path):
            # Create a minimal placeholder file for development
            ensure_audio_dir()
            try:
                with open(audio_path, "wb") as f:
                    # Minimal WAV header (silent audio placeholder)
                    f.write(b'\x00' * 44)  # Placeholder
            except Exception:
                pass

        # Estimate duration
        words = len(text.split())
        wpm = 130 if language == "sat" else 150
        duration_ms = int((words / wpm) * 60 * 1000)

        file_size = 0
        try:
            file_size = os.path.getsize(audio_path)
        except OSError:
            pass

        return {
            "audio_url": audio_url,
            "audio_path": audio_path,
            "duration_ms": max(duration_ms, 500),
            "file_size_bytes": file_size,
            "language": language,
            "text": text,
            "provider": "local_fallback",
        }

    def synthesize_phrase(self, text: str, language: str = "sat") -> Dict:
        """Synthesize a short phrase with optimized settings."""
        return self.synthesize(text, language)


# Global instance
tts_service = TTSService()
