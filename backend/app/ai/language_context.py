"""VaniPath - Educational Language Context Detection"""
import re
from typing import Dict, Optional, List, Tuple


# Educational subject keywords for Hindi
HINDI_MATH_KEYWORDS = {
    "numbers", "counting", "addition", "subtraction", "shapes", "patterns",
    "संख्या", "गिनती", "जोड़", "घटाव", "आकार", "पैटर्न",
    "गणित", "mathematics", "math", "गुणा", "भाग", "बराबर",
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "plus", "minus", "equal", "number", "one", "two", "three",
    "एक", "दो", "तीन", "चार", "पाँच", "छह", "सात", "आठ", "नौ", "दस",
}

HINDI_LANGUAGE_KEYWORDS = {
    "letters", "words", "reading", "writing", "vocabulary",
    "अक्षर", "शब्द", "पढ़ना", "लिखना", "भाषा",
    "वाक्य", "वर्ण", "मात्रा", "चंद्रबिंदु",
}

HINDI_CLASSROOM_KEYWORDS = {
    "classroom", "teacher", "student", "book", "listen", "repeat",
    "कक्षा", "शिक्षक", "विद्यार्थी", "किताब", "सुनो", "दोहराओ",
    "बैठो", "खड़े हो", "देखो", "पढ़ो", "लिखो",
}


class LanguageContextDetector:
    """Detects educational context from Hindi text for better translation."""

    def detect_context(self, text: str, provided_context: Optional[Dict] = None) -> Dict:
        """Detect educational context from text and optional provided context."""
        if provided_context:
            return {
                "subject": provided_context.get("subject", "general"),
                "topic": provided_context.get("topic", ""),
                "grade": provided_context.get("grade", 1),
                "detected_subject": self._detect_subject(text),
                "grade_level": self._detect_grade_level(provided_context.get("grade", 1)),
            }

        detected_subject = self._detect_subject(text)
        grade_level = self._detect_grade_level(1)

        return {
            "subject": detected_subject,
            "topic": "",
            "grade": 1,
            "detected_subject": detected_subject,
            "grade_level": grade_level,
        }

    def _detect_subject(self, text: str) -> str:
        """Detect the educational subject from text content."""
        text_lower = text.lower()

        math_score = sum(1 for kw in HINDI_MATH_KEYWORDS if kw in text_lower)
        lang_score = sum(1 for kw in HINDI_LANGUAGE_KEYWORDS if kw in text_lower)
        classroom_score = sum(1 for kw in HINDI_CLASSROOM_KEYWORDS if kw in text_lower)

        scores = {
            "mathematics": math_score,
            "language": lang_score,
            "classroom": classroom_score,
        }

        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "general"
        return best

    def _detect_grade_level(self, grade: int) -> str:
        """Determine grade-appropriate language complexity."""
        if grade <= 1:
            return "beginner"
        elif grade <= 3:
            return "elementary"
        else:
            return "intermediate"

    def get_cultural_context(self, topic: str, grade: int = 1) -> Dict:
        """Generate culturally relevant context for Santhali-speaking students."""
        cultural_elements = {
            "animals": ["हिरन", "हाथी", "मोर", "नाग", "मछली"],
            "nature": ["पेड़", "फूल", "नदी", "पहाड़", "बारिश"],
            "family": ["माँ", "बाप", "दादा", "दादी", "भाई", "बहन"],
            "food": ["चावल", "दाल", "रोटी", "फल", "सब्ज़ी"],
            "village": ["घर", "खेत", "पशु", "बाज़ार", "मंदिर"],
        }

        topic_lower = topic.lower()
        relevant = []
        for category, items in cultural_elements.items():
            if category in topic_lower or any(item in topic_lower for item in items):
                relevant.extend(items)

        if not relevant:
            relevant = cultural_elements["nature"][:3]

        return {
            "suggested_examples": relevant[:5],
            "cultural_notes": "Use examples from village life, nature, and local environment.",
            "grade_appropriate": True,
        }


# Global instance
context_detector = LanguageContextDetector()
