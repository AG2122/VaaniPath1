"""VaniPath - Translation Service

Translation pipeline:
INPUT → Language validation → Text normalization → Context detection
→ FLN lookup → Vocabulary lookup → Translation → Context correction
→ Validation correction lookup → Confidence calculation → OUTPUT
"""
import time
import json
import os
from typing import Optional, Dict, Tuple
from abc import ABC, abstractmethod

from app.ai.santhali_translation import translation_engine
from app.ai.language_context import context_detector
from app.ai.confidence import confidence_scorer
from app.utils.cache import translation_cache


class TranslationProvider(ABC):
    """Abstract translation provider interface."""

    @abstractmethod
    def translate(self, text: str, source: str, target: str, context: Optional[Dict] = None) -> Dict:
        pass


class CachedTranslationProvider(TranslationProvider):
    """Cache-first translation provider."""

    def translate(self, text: str, source: str, target: str, context: Optional[Dict] = None) -> Optional[Dict]:
        ctx_key = json.dumps(context, sort_keys=True) if context else None
        return translation_cache.get(text, source, target, ctx_key)


class SanthaliDictionaryProvider(TranslationProvider):
    """Local Santhali dictionary + vocabulary translation provider."""

    def translate(self, text: str, source: str, target: str, context: Optional[Dict] = None) -> Optional[Dict]:
        translated, confidence, requires_validation = translation_engine.translate(text, source, target, context)

        if confidence < 0.3:
            return None

        return {
            "translated_text": translated,
            "confidence": confidence,
            "requires_validation": requires_validation,
            "provider": "santhali_dictionary",
        }


class AITranslationProvider(TranslationProvider):
    """AI/cloud translation provider (placeholder for future integration)."""

    def translate(self, text: str, source: str, target: str, context: Optional[Dict] = None) -> Optional[Dict]:
        # This is a placeholder. In production, this would call an actual
        # neural translation API (e.g., IndicTrans, Google Translate API, etc.)
        return None


class TranslationService:
    """Main translation service orchestrating the translation pipeline."""

    def __init__(self):
        self.providers = [
            CachedTranslationProvider(),
            SanthaliDictionaryProvider(),
            AITranslationProvider(),
        ]

    def translate(self, text: str, source_language: str = "hi",
                  target_language: str = "sat", context: Optional[Dict] = None) -> Dict:
        """Execute the full translation pipeline.

        Returns dict with: translated_text, confidence, requires_validation,
        processing_time_ms, provider, warning
        """
        start_time = time.time()

        # Validate languages
        if source_language not in ("hi", "sat"):
            return {"error": f"Unsupported source language: {source_language}"}
        if target_language not in ("hi", "sat"):
            return {"error": f"Unsupported target language: {target_language}"}
        if source_language == target_language:
            return {"error": "Source and target languages must be different"}

        # Normalize text
        text = text.strip()
        if not text:
            return {"error": "Empty text"}

        # Detect educational context
        edu_context = context_detector.detect_context(text, context)

        # Try providers in priority order
        result = None
        for provider in self.providers:
            result = provider.translate(text, source_language, target_language, context)
            if result:
                break

        if result is None:
            return {"error": "Translation failed - no provider could translate this text"}

        # Apply confidence adjustment for context
        adjusted_confidence = confidence_scorer.adjust_for_context(
            result["confidence"], edu_context
        )

        # Score the confidence
        confidence_info = confidence_scorer.score(
            adjusted_confidence,
            result.get("requires_validation", False)
        )

        # Cache the successful translation
        ctx_key = json.dumps(context, sort_keys=True) if context else None
        translation_cache.set(text, source_language, target_language, result, ctx_key)

        processing_time = int((time.time() - start_time) * 1000)

        return {
            "translated_text": result["translated_text"],
            "source_text": text,
            "source_language": source_language,
            "target_language": target_language,
            "confidence": confidence_info["confidence"],
            "requires_validation": confidence_info["requires_validation"],
            "warning": confidence_info.get("warning"),
            "processing_time_ms": processing_time,
            "provider": result.get("provider", "unknown"),
            "context": edu_context,
        }

    def translate_batch(self, texts: list, source: str = "hi",
                        target: str = "sat", context: Optional[Dict] = None) -> list:
        """Translate multiple texts."""
        return [self.translate(t, source, target, context) for t in texts]


# Global instance
translation_service = TranslationService()
