"""VaniPath - Online TTS Provider

Provides online text-to-speech for Santali in Online mode.

IMPORTANT HONESTY NOTE:
No production-ready Santali (sat-IN) TTS API exists from any major provider
(Azure, Google Cloud, AWS, ElevenLabs, Deepgram, PlayHT, Murf).

Edge TTS (free Microsoft) is used as a PROTOTYPE provider. It pronounces
Santali vocabulary through Hindi phonetics. This is NOT genuine Santali
pronunciation but is the closest available solution for a hackathon demo.

Architecture: When a genuine Santali TTS API becomes available, implement
a new provider class inheriting from OnlineTTSProvider and register it.
"""
import asyncio
import hashlib
import os
from typing import Dict, Optional

from app.config import settings


class OnlineTTSProvider:
    """Base class for online TTS providers."""

    name: str = "base"

    async def synthesize(self, text: str, language: str = "sat") -> Dict:
        raise NotImplementedError


class EdgeTTSProvider(OnlineTTSProvider):
    """Online TTS using Microsoft Edge TTS (free, requires internet).

    Uses a Hindi voice to pronounce Santali vocabulary.
    This is a PROTOTYPE — not genuine Santali speech.
    """

    name = "edge-tts"

    def __init__(self):
        self.voice = settings.ONLINE_TTS_VOICE or "hi-IN-SwaraNeural"

    async def synthesize(self, text: str, language: str = "sat") -> Dict:
        try:
            import edge_tts
        except ImportError:
            return {
                "audio_url": None,
                "error": "edge-tts not installed. Run: pip install edge-tts",
                "provider": self.name,
            }

        if not text.strip():
            return {"audio_url": None, "error": "Empty text", "provider": self.name}

        # Transliterate Ol Chiki to Devanagari for Edge TTS
        devanagari_text = self._olchiki_to_devanagari(text)

        # Generate unique filename
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()[:16]
        filename = f"online_{text_hash}.mp3"
        audio_dir = os.path.abspath(settings.AUDIO_CACHE_DIR)
        output_path = os.path.join(audio_dir, filename)

        try:
            communicate = edge_tts.Communicate(devanagari_text, self.voice)
            await communicate.save(output_path)
        except Exception as e:
            return {
                "audio_url": None,
                "error": f"Edge TTS failed: {str(e)}",
                "provider": self.name,
            }

        if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
            return {
                "audio_url": None,
                "error": "Edge TTS produced empty audio",
                "provider": self.name,
            }

        file_size = os.path.getsize(output_path)
        return {
            "audio_url": f"/audio/{filename}",
            "file_size_bytes": file_size,
            "language": language,
            "text": text,
            "provider": self.name,
            "voice": self.voice,
            "note": "Hindi-voiced Santali vocabulary (prototype). Not genuine Santali pronunciation.",
        }

    @staticmethod
    def _olchiki_to_devanagari(text: str) -> str:
        """Transliterate Ol Chiki to Devanagari for Edge TTS processing."""
        mapping = {
            "\u1c50": "\u0966", "\u1c51": "\u0967", "\u1c52": "\u0968",
            "\u1c53": "\u0969", "\u1c54": "\u096a", "\u1c55": "\u096b",
            "\u1c56": "\u0905", "\u1c57": "\u0906", "\u1c58": "\u0907",
            "\u1c59": "\u0908", "\u1c5a": "\u0909", "\u1c5b": "\u090a",
            "\u1c5c": "\u0915", "\u1c5d": "\u0916", "\u1c5e": "\u0917",
            "\u1c5f": "\u0918", "\u1c60": "\u0919", "\u1c61": "\u091a",
            "\u1c62": "\u091b", "\u1c63": "\u091c", "\u1c64": "\u091d",
            "\u1c65": "\u091e", "\u1c66": "\u091f", "\u1c67": "\u0920",
            "\u1c68": "\u0921", "\u1c69": "\u0922", "\u1c6a": "\u0923",
            "\u1c6b": "\u0924", "\u1c6c": "\u0925", "\u1c6d": "\u0926",
            "\u1c6e": "\u0927", "\u1c6f": "\u0928", "\u1c70": "\u092a",
            "\u1c71": "\u092b", "\u1c72": "\u092c", "\u1c73": "\u092d",
            "\u1c74": "\u092e", "\u1c75": "\u092f", "\u1c76": "\u0930",
            "\u1c77": "\u0932", "\u1c78": "\u093e", "\u1c79": "\u093e",
            "\u1c7a": "\u094d\u092f", "\u1c7b": "\u094d\u0930",
            "\u1c7c": "\u0902", "\u1c7d": "", "\u1c7e": "\u0964",
            "\u1c7f": "\u0964",
        }
        return "".join(mapping.get(c, c) for c in text)


def get_online_tts_provider() -> Optional[OnlineTTSProvider]:
    """Get the configured online TTS provider, or None if disabled."""
    provider_name = settings.ONLINE_TTS_PROVIDER or "none"
    if provider_name == "edge":
        return EdgeTTSProvider()
    return None
