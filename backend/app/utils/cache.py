"""VaniPath - Smart Cache"""
import time
import json
from typing import Optional, Any, Dict
from collections import OrderedDict


class TranslationCache:
    """In-memory LRU cache for translations and phrases."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._ttl = ttl_seconds

    def _make_key(self, text: str, source_lang: str, target_lang: str, context: Optional[str] = None) -> str:
        ctx = context or ""
        return f"{source_lang}:{target_lang}:{text}:{ctx}"

    def get(self, text: str, source_lang: str, target_lang: str, context: Optional[str] = None) -> Optional[Any]:
        key = self._make_key(text, source_lang, target_lang, context)
        if key in self._cache:
            # Check TTL
            if time.time() - self._timestamps.get(key, 0) > self._ttl:
                self._evict(key)
                return None
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def set(self, text: str, source_lang: str, target_lang: str, value: Any, context: Optional[str] = None):
        key = self._make_key(text, source_lang, target_lang, context)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        self._timestamps[key] = time.time()
        # Evict oldest if over limit
        while len(self._cache) > self._max_size:
            oldest_key, _ = self._cache.popitem(last=False)
            self._timestamps.pop(oldest_key, None)

    def _evict(self, key: str):
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def clear(self):
        self._cache.clear()
        self._timestamps.clear()

    @property
    def size(self) -> int:
        return len(self._cache)

    def get_popular(self, limit: int = 20) -> list:
        """Return most recently accessed entries."""
        items = []
        for key in reversed(list(self._cache.keys())):
            if len(items) >= limit:
                break
            items.append({"key": key, "value": self._cache[key]})
        return items


# Global cache instance
translation_cache = TranslationCache()


class PhraseCache:
    """Cache for pre-generated classroom phrases."""

    def __init__(self):
        self._phrases: Dict[str, list] = {}

    def get_phrases(self, category: str = "classroom") -> Optional[list]:
        return self._phrases.get(category)

    def set_phrases(self, category: str, phrases: list):
        self._phrases[category] = phrases

    def get_all(self) -> list:
        all_phrases = []
        for phrases in self._phrases.values():
            all_phrases.extend(phrases)
        return all_phrases


phrase_cache = PhraseCache()
