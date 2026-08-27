"""VaniPath - Translation Confidence Scoring"""
from typing import Dict, Tuple


class ConfidenceScorer:
    """Calculates and categorizes translation confidence scores."""

    LEVELS = {
        "high": (0.90, 1.00),
        "medium": (0.70, 0.89),
        "low": (0.0, 0.69),
    }

    def score(self, confidence: float, requires_validation: bool = False) -> Dict:
        """Return structured confidence information.

        Args:
            confidence: Float between 0 and 1
            requires_validation: Whether the translation needs human review

        Returns:
            Dict with confidence, level, requires_validation, warning
        """
        confidence = max(0.0, min(1.0, confidence))

        if confidence >= 0.90:
            level = "high"
        elif confidence >= 0.70:
            level = "medium"
        else:
            level = "low"
            requires_validation = True

        result = {
            "confidence": round(confidence, 2),
            "level": level,
            "requires_validation": requires_validation,
        }

        if level == "low":
            result["warning"] = "Translation may require human validation"
        else:
            result["warning"] = None

        return result

    def adjust_for_context(self, base_confidence: float, context: Dict) -> float:
        """Adjust confidence based on educational context availability."""
        adjusted = base_confidence

        if context.get("subject"):
            adjusted = min(1.0, adjusted + 0.03)
        if context.get("grade"):
            adjusted = min(1.0, adjusted + 0.02)
        if context.get("topic"):
            adjusted = min(1.0, adjusted + 0.02)

        return round(adjusted, 2)

    def batch_score(self, translations: list) -> list:
        """Score a batch of translations."""
        return [self.score(t.get("confidence", 0)) for t in translations]


# Global instance
confidence_scorer = ConfidenceScorer()
