"""VaniPath - Santhali Translation Engine

This module provides Hindi <-> Santhali translation using:
1. Validated corrections lookup (with text normalization)
2. FLN terminology database
3. Phrase-level matching (with text normalization)
4. Token-level fallback translation (with anusvar/vowel stripping)
5. Deterministic development fallback

IMPORTANT: This is a development/local translation engine.
It is NOT an AI model. It uses vocabulary databases and rule-based fallback.
Architecture is ready to plug in a real neural translation model.
"""
import json
import os
import random
import re
from typing import Optional, Dict, List, Tuple


class SanthaliTranslationEngine:
    """Local Hindi <-> Santhali translation engine using vocabulary databases."""

    def __init__(self):
        self._vocabulary: Dict[str, str] = {}
        self._reverse_vocabulary: Dict[str, str] = {}
        self._fln_terms: Dict[str, Dict[str, str]] = {}
        self._phrase_translations: Dict[str, str] = {}
        self._reverse_phrase_translations: Dict[str, str] = {}
        self._corrections: Dict[str, str] = {}
        self._normalized_corrections: Dict[str, str] = {}
        self._normalized_phrases: Dict[str, str] = {}
        self._normalized_vocab: Dict[str, str] = {}
        self._loaded = False

    def load_data(self):
        """Load vocabulary, FLN terms, and corrections from data files."""
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "languages", "santhali")

        # Load vocabulary
        vocab_path = os.path.join(data_dir, "vocabulary.json")
        if os.path.exists(vocab_path):
            with open(vocab_path, "r", encoding="utf-8") as f:
                vocab_list = json.load(f)
                for entry in vocab_list:
                    self._vocabulary[entry["hindi"]] = entry["santhali"]
                    self._reverse_vocabulary[entry["santhali"]] = entry["hindi"]

        # Load FLN terms
        fln_path = os.path.join(data_dir, "fln_terms.json")
        if os.path.exists(fln_path):
            with open(fln_path, "r", encoding="utf-8") as f:
                self._fln_terms = json.load(f)
                # Also add to vocabulary
                for category, terms in self._fln_terms.items():
                    if isinstance(terms, dict):
                        for hindi, santhali in terms.items():
                            self._vocabulary[hindi] = santhali
                            self._reverse_vocabulary[santhali] = hindi

        # Load classroom phrases
        phrases_path = os.path.join(data_dir, "classroom_phrases.json")
        if os.path.exists(phrases_path):
            with open(phrases_path, "r", encoding="utf-8") as f:
                phrases = json.load(f)
                for phrase in phrases:
                    self._phrase_translations[phrase["hindi"]] = phrase["santhali"]
                    self._reverse_phrase_translations[phrase["santhali"]] = phrase["hindi"]

        # Load validated corrections
        corrections_path = os.path.join(data_dir, "corrections.json")
        if os.path.exists(corrections_path):
            with open(corrections_path, "r", encoding="utf-8") as f:
                corrections = json.load(f)
                for c in corrections:
                    self._corrections[c["hindi"]] = c["corrected"]
                    # Also store normalized key for flexible matching
                    norm_key = self._normalize_hindi(c["hindi"])
                    if norm_key not in self._normalized_corrections:
                        self._normalized_corrections[norm_key] = c["corrected"]

        # Build normalized indices for phrases and vocabulary
        for hindi, santhali in self._phrase_translations.items():
            norm_key = self._normalize_hindi(hindi)
            if norm_key not in self._normalized_phrases:
                self._normalized_phrases[norm_key] = santhali
        for hindi, santhali in self._vocabulary.items():
            norm_key = self._normalize_hindi(hindi)
            if norm_key not in self._normalized_vocab:
                self._normalized_vocab[norm_key] = santhali

        self._loaded = True

    @staticmethod
    def _normalize_hindi(text: str) -> str:
        """Normalize Hindi text for flexible matching.

        Collapses whitespace, strips trailing danda/punctuation/anusvar,
        so that minor spacing/punctuation differences don't break lookups.
        """
        t = text.strip()
        t = re.sub(r'\s+', ' ', t)
        t = t.rstrip('\u0964 \u0902 \u0901 .,!?;: ')
        return t

    def ensure_loaded(self):
        if not self._loaded:
            self.load_data()

    def translate(self, text: str, source: str = "hi", target: str = "sat",
                  context: Optional[Dict] = None) -> Tuple[str, float, bool]:
        """Translate text between Hindi and Santhali.

        Returns: (translated_text, confidence, requires_validation)
        """
        self.ensure_loaded()

        text = text.strip()
        if not text:
            return text, 1.0, False

        if source == "hi" and target == "sat":
            return self._hi_to_sat(text, context)
        elif source == "sat" and target == "hi":
            return self._sat_to_hi(text, context)
        else:
            return text, 0.0, True

    def _lookup(self, text: str, dictionary: Dict[str, str],
                normalized_index: Optional[Dict[str, str]] = None) -> Optional[str]:
        """Look up text in a dictionary with normalization fallbacks.

        Args:
            text: The text to look up.
            dictionary: The raw dictionary (raw keys -> values).
            normalized_index: Optional pre-built normalized-key index.
        """
        # 1. Exact raw match
        if text in dictionary:
            return dictionary[text]

        # 2. Normalized input against raw keys
        normalized = self._normalize_hindi(text)
        if normalized in dictionary:
            return dictionary[normalized]

        # 3. Normalized input against normalized-key index (fast O(1))
        if normalized_index and normalized in normalized_index:
            return normalized_index[normalized]

        # 4. Try without trailing anusvar/chandrabindu
        for suffix in ('\u0902', '\u0901'):
            if text.endswith(suffix) and text[:-1] in dictionary:
                return dictionary[text[:-1]]
            if normalized.endswith(suffix) and normalized[:-1] in dictionary:
                return dictionary[normalized[:-1]]
            if normalized_index:
                if text.endswith(suffix) and text[:-1] in normalized_index:
                    return normalized_index[text[:-1]]
                if normalized.endswith(suffix) and normalized[:-1] in normalized_index:
                    return normalized_index[normalized[:-1]]

        return None

    def _hi_to_sat(self, text: str, context: Optional[Dict] = None) -> Tuple[str, float, bool]:
        """Hindi -> Santhali translation pipeline."""
        # 1. Check corrections (raw, then normalized, then normalized index)
        correction = self._lookup(text, self._corrections, self._normalized_corrections)
        if correction:
            return correction, 1.0, False

        # 2. Check phrase translations (raw, then normalized, then normalized index)
        phrase = self._lookup(text, self._phrase_translations, self._normalized_phrases)
        if phrase:
            return phrase, 0.98, False

        # 3. Check vocabulary (raw, then normalized, then normalized index)
        vocab_match = self._lookup(text, self._vocabulary, self._normalized_vocab)
        if vocab_match:
            return vocab_match, 0.95, False

        # 4. Token-level translation
        tokens = self._tokenize_hindi(text)
        translated_tokens = []
        matched = 0
        total = len(tokens)

        for token in tokens:
            clean = token.strip('\u0964,!?;:\'"()[]{} ')
            if not clean:
                translated_tokens.append(token)
                continue

            santhali = self._lookup(clean, self._vocabulary, self._normalized_vocab)
            if santhali:
                translated_tokens.append(santhali)
                matched += 1
            else:
                # Fallback: keep the original token (no hallucination)
                translated_tokens.append(clean)

        result = " ".join(translated_tokens)

        # 5. Calculate confidence
        if total == 0:
            confidence = 0.5
        else:
            coverage = matched / total
            confidence = min(0.95, 0.5 + (coverage * 0.45))

        requires_validation = confidence < 0.70

        # 6. Context-aware adjustments
        if context:
            grade = context.get("grade")
            subject = (context.get("subject") or "").lower()
            if subject in self._fln_terms and matched > 0:
                confidence = min(0.98, confidence + 0.05)
            if grade and grade <= 2:
                confidence = min(0.95, confidence + 0.02)

        return result, round(confidence, 2), requires_validation

    def _sat_to_hi(self, text: str, context: Optional[Dict] = None) -> Tuple[str, float, bool]:
        """Santhali -> Hindi translation pipeline."""
        # 1. Check for exact phrase match
        if text in self._reverse_phrase_translations:
            return self._reverse_phrase_translations[text], 0.98, False

        # 2. Check for exact vocabulary match
        if text in self._reverse_vocabulary:
            return self._reverse_vocabulary[text], 0.95, False

        # 3. Token-level reverse translation
        tokens = text.split()
        translated_tokens = []
        matched = 0
        total = len(tokens)

        for token in tokens:
            clean = token.strip('\u0964,!?;:\'"()[]{} ')
            if not clean:
                translated_tokens.append(token)
                continue

            if clean in self._reverse_vocabulary:
                translated_tokens.append(self._reverse_vocabulary[clean])
                matched += 1
            else:
                translated_tokens.append(clean)

        result = " ".join(translated_tokens)

        if total == 0:
            confidence = 0.5
        else:
            coverage = matched / total
            confidence = min(0.95, 0.5 + (coverage * 0.45))

        requires_validation = confidence < 0.70
        return result, round(confidence, 2), requires_validation

    def _tokenize_hindi(self, text: str) -> List[str]:
        """Tokenize Hindi text into words, preserving punctuation."""
        return re.findall(r'\S+', text)

    def get_vocabulary(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """Get vocabulary entries, optionally filtered by category."""
        result = []
        for hindi, santhali in self._vocabulary.items():
            result.append({"hindi": hindi, "santhali": santhali, "category": category or "general"})
        return result

    def add_correction(self, hindi: str, corrected: str):
        """Add a validated correction."""
        self._corrections[hindi] = corrected
        self._vocabulary[hindi] = corrected

    def get_stats(self) -> Dict:
        """Get translation engine statistics."""
        return {
            "vocabulary_size": len(self._vocabulary),
            "phrase_count": len(self._phrase_translations),
            "fln_categories": list(self._fln_terms.keys()),
            "corrections_count": len(self._corrections),
        }


# Global engine instance
translation_engine = SanthaliTranslationEngine()
