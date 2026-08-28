"""VaniPath - Offline TTS Service

TIER 1: Offline phrase/audio cache
  - Pre-generated audio files for all classroom phrases
  - Stored in data/audio/sat_*.mp3
  - Phrase hash -> audio file mapping in data/audio/phrase_map.json
  - Zero network. Zero inference. Pure file lookup.
  - Supports exact match, text match, and longest-substring match.

TIER 2 (future): Lightweight offline Santali TTS
  - Architecture ready for sherpa-onnx / piper Santali model
  - When a Santali model becomes available, plug it in here

Runtime dependencies: NONE (no edge-tts, no cloud API)
Build tool: build_audio_cache.py (one-time, requires internet)
"""
import hashlib
import json
import os
from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.utils.audio import ensure_audio_dir
from app.services.online_tts_provider import get_online_tts_provider


def _run_async(coro):
    """Run an async coroutine from a sync context. Creates a new event loop."""
    import asyncio
    loop = None
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = None
    except RuntimeError:
        loop = None
    if loop is None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TTSService:
    """Offline phrase-based TTS for Santali.

    Looks up pre-generated audio files by phrase hash.
    Zero network. Zero inference. Minimal RAM.
    """

    def __init__(self):
        self.provider = "offline-cache"
        self._phrase_map: Optional[Dict] = None
        self._audio_dir: Optional[str] = None
        self._text_index: Optional[Dict[str, str]] = None  # text -> audio_url
        self._load_phrase_map()

    def _load_phrase_map(self):
        """Load the phrase hash -> audio file mapping."""
        ensure_audio_dir()
        self._audio_dir = os.path.abspath(settings.AUDIO_CACHE_DIR)
        map_path = os.path.join(self._audio_dir, "phrase_map.json")

        if os.path.exists(map_path):
            with open(map_path, "r", encoding="utf-8") as f:
                self._phrase_map = json.load(f)
        else:
            self._phrase_map = {}

        # Build text index for substring matching
        self._text_index = {}
        for h, entry in self._phrase_map.items():
            text = entry.get("text", "")
            audio_path = entry.get("audio_path", "")
            audio_url = entry.get("audio_url", "")
            if text and audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
                self._text_index[text] = audio_url

    @staticmethod
    def _phrase_hash(text: str) -> str:
        """Generate deterministic hash for a phrase."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()[:16]

    def _find_best_match(self, text: str) -> Optional[Tuple[str, str]]:
        """Find the best audio match for text.

        Strategy:
        1. Exact hash match (fastest)
        2. Exact text match in phrase_map
        3. Longest-substring match from cached phrases

        Returns (audio_url, match_type) or None.
        """
        if not self._phrase_map or not self._text_index:
            return None

        # 1. Exact hash match
        h = self._phrase_hash(text)
        entry = self._phrase_map.get(h)
        if entry:
            audio_path = entry.get("audio_path", "")
            if audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
                return (entry.get("audio_url", ""), "exact")

        # 2. Exact text match
        if text in self._text_index:
            return (self._text_index[text], "exact")

        # 3. Longest-substring match
        # Sort cached phrases by length descending so first match is longest
        sorted_phrases = sorted(self._text_index.keys(), key=len, reverse=True)
        for phrase in sorted_phrases:
            if phrase in text and len(phrase) >= 4:
                return (self._text_index[phrase], "segment")

        return None

    def synthesize(self, text: str, language: str = "sat",
                    mode: str = "offline") -> Dict:
        """Look up pre-generated audio or call online TTS.

        mode: "offline" (default) or "online"
        """
        if not text.strip():
            return {"error": "Empty text", "audio_url": None}

        if self._phrase_map is None:
            self._load_phrase_map()

        # Online mode: try online TTS first
        if mode == "online":
            provider = get_online_tts_provider()
            if provider:
                import concurrent.futures
                try:
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(
                            _run_async, provider.synthesize(text, language)
                        )
                        result = future.result(timeout=15)
                except Exception as e:
                    result = {"audio_url": None, "error": str(e), "provider": provider.name}

                if result.get("audio_url"):
                    result["audio_unavailable"] = False
                    result["match_type"] = "online"
                    return result

                # Online failed, fall through to offline cache
                result["online_failed"] = True
                result["online_error"] = result.get("error", "Online TTS failed")

        # Offline mode (or online fallback): check local cache
        match = self._find_best_match(text)

        if match:
            audio_url, match_type = match
            response = {
                "audio_url": audio_url,
                "duration_ms": self._estimate_duration(text),
                "language": language,
                "text": text,
                "provider": "offline-cache",
                "voice": "pre-generated",
                "match_type": match_type,
                "audio_unavailable": False,
            }
            if mode == "online" and result.get("online_failed"):
                response["fallback_reason"] = result.get("online_error", "Online TTS unavailable")
            return response

        # No audio available at all
        if mode == "online":
            return {
                "audio_url": None,
                "audio_unavailable": True,
                "error": "Online audio unavailable — no offline audio for this sentence.",
                "provider": "online+offline",
                "cached_phrases": len(self._text_index),
            }

        return {
            "audio_url": None,
            "audio_unavailable": True,
            "error": "Offline Santali audio unavailable for this sentence",
            "provider": "offline-cache",
            "cached_phrases": len(self._text_index),
            "hint": "This sentence is not in the offline audio cache. Translation is still available.",
        }

    def _estimate_duration(self, text: str) -> int:
        """Estimate audio duration in ms."""
        words = len(text.split())
        return max(int((words / 130) * 60 * 1000), 500)

    def synthesize_phrase(self, text: str, language: str = "sat") -> Dict:
        """Synthesize a short phrase (same as synthesize for cache lookup)."""
        return self.synthesize(text, language)

    def health_check(self) -> Dict:
        """Check TTS service availability."""
        if self._phrase_map is None:
            self._load_phrase_map()

        cached_count = 0
        for entry in self._phrase_map.values():
            audio_path = entry.get("audio_path", "")
            if audio_path and os.path.exists(audio_path) and os.path.getsize(audio_path) > 100:
                cached_count += 1

        return {
            "available": cached_count > 0,
            "provider": "offline-cache",
            "cached_phrases": cached_count,
            "total_mappings": len(self._phrase_map),
            "audio_dir": self._audio_dir,
            "note": "Pre-generated audio. Replace with genuine Santali recordings when available.",
        }


# Global instance
tts_service = TTSService()
