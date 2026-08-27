"""VaniPath - AI Teacher Copilot Service

Generates culturally relevant bilingual lesson plans for
Hindi-speaking teachers teaching Santhali-speaking students.
"""
import json
from typing import Dict, Optional

from app.services.translation_service import translation_service
from app.ai.language_context import context_detector


# Sample lesson templates organized by subject and topic
LESSON_TEMPLATES = {
    "Mathematics": {
        "Numbers 1-20": {
            "objective": "Students will be able to identify, count, and write numbers 1-20 in both Hindi and Santhali.",
            "explanation": {
                "hindi": "आज हम संख्याओं 1 से 20 तक सीखेंगे। हम गिनना, पहचानना और लिखना सीखेंगे।",
                "santhali": "ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱥᱟᱱᱛᱟᱲᱤ 1 ᱠᱚᱨᱟ 20 ᱦᱟᱨᱮ ᱵᱟᱝᱨᱚᱢ ᱢᱮ। ᱫᱟᱨᱤ ᱜᱤᱱᱚᱨᱮ, ᱫᱩᱴᱷᱤᱣᱮ ᱟᱨ ᱚᱞᱚᱨᱮ ᱵᱟᱝᱨᱚᱢ ᱢᱮ।",
                "english": "Today we will learn numbers 1 to 20. We will learn to count, recognize and write them."
            },
            "cultural_examples": [
                "Count mangoes from the tree ( Indians use mangoes for counting practice )",
                "Use pebbles and sticks from the village path",
                "Count family members: mother, father, grandmother, grandfather, siblings",
            ],
            "activity": {
                "hindi": "छात्रों से पेड़ से गिनती के लिए पत्थर या आम लाने को कहें।",
                "santhali": "ᱡᱟᱨᱤᱚᱜ ᱠᱚᱥᱟᱨᱚᱜ ᱫᱟᱨᱤ ᱜᱤᱱᱚᱨᱮ ᱠᱟᱱᱟᱢᱚᱜ ᱵᱟᱝᱨᱚᱢ।",
            },
            "practice_questions": [
                {
                    "hindi": "पेड़ पर कितने आम हैं?",
                    "santhali": "ᱢᱟᱝᱣᱟ ᱠᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱥᱟᱲᱟ?",
                    "options": ["3", "5", "7"],
                    "answer": "5"
                },
                {
                    "hindi": "दो और तीन बराबर कितना?",
                    "santhali": "ᱰᱩ ᱟᱨ ᱛᱤᱱᱟ ᱵᱟᱨᱟᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ?",
                    "options": ["4", "5", "6"],
                    "answer": "5"
                },
            ],
            "assessment_questions": [
                {"hindi": "लिखिए 15 के बाद कौन सी संख्या आती है", "santhali": "ᱚᱞᱚᱨᱮ 15 ᱨᱚᱨᱟ ᱠᱟᱹᱨᱚᱨᱮ ᱥᱟᱱᱛᱟᱲᱤ ᱟᱠᱟ"},
                {"hindi": "गिनिए: 1,2,3,4, ___,6", "santhali": "ᱜᱤᱱᱚᱨᱮ: 1,2,3,4, ___,6"},
            ],
            "homework": {
                "hindi": "�र पर 1 से 20 तक गिनती का अभ्यास करें। परिवार के सदस्यों को गिनें।",
                "santhali": "ᱜᱚᱨᱚᱜ ᱠᱚᱨᱟ 1 ᱠᱚᱨᱟ 20 ᱦᱟᱨᱮ ᱜᱤᱱᱚᱨᱮ ᱠᱚᱨᱚᱜ ᱢᱟᱨᱮᱡᱟᱨᱮ ᱵᱟᱝᱨᱚᱢ। ᱥᱟᱨᱤᱡᱚᱨᱤ ᱡᱚᱨᱚᱜ ᱜᱤᱱᱚᱨᱮ ᱢᱮ।"
            },
            "santhali_terms": {
                "numbers": "ᱥᱟᱱᱛᱟᱲᱤ",
                "counting": "ᱜᱤᱱᱚᱨᱮ",
                "one": "ᱤᱧ",
                "two": "ᱰᱩ",
                "three": "ᱛᱤᱱᱟ",
            }
        },
        "Counting": {
            "objective": "Students will count objects accurately up to 20 and match numerals to quantities.",
            "explanation": {
                "hindi": "आज हम वस्तुओं की गिनती करेंगे और संख्या के साथ मिलाएंगे।",
                "santhali": "ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱵᱤᱥᱩᱨᱤᱡᱚᱨᱚᱜ ᱜᱤᱱᱚᱨᱮ ᱵᱟᱝᱨᱚᱢ ᱟᱨ ᱥᱟᱱᱛᱟᱲᱤ ᱥᱟᱛᱟᱨᱚᱜ ᱢᱮᱴᱤᱭᱟᱜ ᱢᱮ।",
                "english": "Today we will count objects and match them to numbers."
            },
            "cultural_examples": [
                "Count fruits in the market",
                "Count beads for a necklace",
                "Count fish caught in the river",
            ],
            "activity": {
                "hindi": "प्रत्येक छात्र को 10 पत्थर दें और उन्हें गिनने को कहें।",
                "santhali": "ᱯᱩᱴᱚᱢ ᱠᱟᱱᱟ ᱡᱟᱨᱤᱚᱜ 10 ᱞᱤᱛᱮᱨ ᱵᱟᱰᱟᱭᱮ ᱟᱨ ᱠᱚᱥᱚᱜ ᱜᱤᱱᱚᱨᱮ ᱵᱟᱝᱨᱚᱢ।"
            },
            "practice_questions": [],
            "assessment_questions": [],
            "homework": {
                "hindi": "अपने कमरे में 10 चीज़ें गिनें और लिखें।",
                "santhali": "ᱠᱚᱨᱚᱜ ᱡᱚᱨᱚᱜ 10 ᱫᱤᱱᱚᱨᱚᱜ ᱜᱤᱱᱚᱨᱮ ᱟᱨ ᱚᱞᱚᱨᱮ ᱢᱮ।"
            },
            "santhali_terms": {
                "counting": "ᱜᱤᱱᱚᱨᱮ",
                "objects": "ᱵᱤᱥᱩᱨᱤ",
                "together": "ᱡᱚᱨᱚᱜ",
            }
        },
        "Addition": {
            "objective": "Students will perform simple addition within 20 using objects and number lines.",
            "explanation": {
                "hindi": "जोड़ना मतलब दो संख्याओं को मिलाना। आज हम आसान जोड़ सीखेंगे।",
                "santhali": "ᱡᱚᱨᱚᱨᱚᱜ ᱞᱟᱹᱨᱮ ᱰᱩ ᱥᱟᱱᱛᱟᱲᱤ ᱡᱚᱨᱚᱜ ᱢᱟᱴᱤᱭᱟᱜ ᱢᱮ। ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱟᱥᱟᱱ ᱡᱚᱨᱚᱨᱚᱜ ᱵᱟᱝᱨᱚᱢ।",
                "english": "Addition means combining two numbers. Today we will learn easy addition."
            },
            "cultural_examples": [
                "If you have 3 mangoes and get 2 more, how many do you have?",
                "Count fish: catch 5 in morning, 3 in evening - total?",
            ],
            "activity": {
                "hindi": "छात्रों को पत्थर दें। पहले 3 रखें, फिर 2 और जोड़ें।",
                "santhali": "ᱡᱟᱨᱤᱚᱜ ᱞᱤᱛᱮᱨ ᱵᱟᱰᱟᱭᱮ। ᱫᱟᱨᱤ 3 ᱟᱨᱮᱭᱟᱜ, ᱛᱤᱱᱚᱜ 2 ᱡᱚᱨᱚᱨᱚᱜ ᱢᱮ।"
            },
            "practice_questions": [],
            "assessment_questions": [],
            "homework": {"hindi": "3 + 2 = ? और 5 + 4 = ? गिनकर देखें।", "santhali": "3 + 2 = ? ᱟᱨ 5 + 4 = ? ᱜᱤᱱᱚᱨᱮ ᱫᱟᱨᱤᱚᱜ।"},
            "santhali_terms": {"addition": "ᱡᱚᱨᱚᱨᱚᱜ", "plus": "ᱡᱚᱨᱚᱨᱚᱜ", "total": "ᱡᱚᱨᱚᱜ"}
        },
        "Subtraction": {
            "objective": "Students will perform simple subtraction within 20.",
            "explanation": {
                "hindi": "घटाना मतलब कुछ हटाना। आज हम घटाव सीखेंगे।",
                "santhali": "ᱜᱩᱴᱟᱨᱚᱜ ᱞᱟᱹᱨᱮ ᱠᱩᱪᱷᱚ ᱦᱟᱛᱮ ᱢᱮ। ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱜᱩᱴᱟᱨᱚᱜ ᱵᱟᱝᱨᱚᱢ।",
                "english": "Subtraction means taking away. Today we will learn subtraction."
            },
            "cultural_examples": ["You have 5 mangoes, eat 2 - how many left?"],
            "activity": {"hindi": "5 पत्थर रखें, 2 उठाएं। बाकी गिनें।", "santhali": "5 ᱞᱤᱛᱮᱨ ᱟᱨᱮᱭᱟᱜ, 2 ᱦᱟᱛᱮᱭᱟᱜ। ᱠᱟᱱᱚᱜ ᱜᱤᱱᱚᱨᱮ ᱢᱮ।"},
            "practice_questions": [],
            "assessment_questions": [],
            "homework": {"hindi": "8 - 3 = ? और 10 - 5 = ? गिनकर देखें।", "santhali": "8 - 3 = ? ᱟᱨ 10 - 5 = ? ᱜᱤᱱᱚᱨᱮ ᱫᱟᱨᱤᱚᱜ।"},
            "santhali_terms": {"subtraction": "ᱜᱩᱴᱟᱨᱚᱜ", "minus": "ᱜᱩᱴᱟᱨᱚᱜ", "remaining": "ᱠᱟᱱᱚᱜ"}
        },
        "Shapes": {
            "objective": "Students will identify and name basic shapes in Hindi and Santhali.",
            "explanation": {
                "hindi": "आज हम आकार सीखेंगे - गोल, वर्ग, त्रिकोण।",
                "santhali": "ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱵᱤᱥᱩᱨᱤ ᱥᱩᱨᱳᱨᱚᱜ ᱵᱟᱝᱨᱚᱢ - ᱜᱩᱨᱳ, ᱫᱩᱠᱟ, ᱛᱤᱨᱤᱠᱚᱱᱚᱜ।",
                "english": "Today we will learn shapes - circle, square, triangle."
            },
            "cultural_examples": ["Sun is round, school window is square, leaf is triangular"],
            "activity": {"hindi": "कमरे में गोल, वर्ग और त्रिकोण ढूंढें।", "santhali": "ᱠᱚᱨᱚᱜ ᱡᱚᱨᱚᱜ ᱜᱩᱨᱳ, ᱫᱩᱠᱟ ᱟᱨ ᱛᱤᱨᱤᱠᱚᱱᱚᱜ ᱫᱩᱴᱷᱤᱣᱮ ᱢᱮ।"},
            "practice_questions": [],
            "assessment_questions": [],
            "homework": {"hindi": "घर में गोल और चौकोर चीज़ें ढूंढें।", "santhali": "ᱜᱚᱨᱚᱜ ᱡᱚᱨᱚᱜ ᱜᱩᱨᱳ ᱟᱨ ᱫᱩᱠᱟ ᱫᱤᱱᱚᱨᱚᱜ ᱫᱩᱴᱷᱤᱣᱮ ᱢᱮ।"},
            "santhali_terms": {"circle": "ᱜᱩᱨᱳ", "square": "ᱫᱩᱠᱟ", "triangle": "ᱛᱤᱨᱤᱠᱚᱱᱚᱜ"}
        },
    },
    "Language": {
        "Letters": {
            "objective": "Students will recognize and write Devanagari and Ol Chiki letters.",
            "explanation": {
                "hindi": "आज हम अक्षर सीखेंगे। हिंदी में देवनागरी और संथाली में ओल चिकी लिपि।",
                "santhali": "ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱚᱞᱚᱨᱮ ᱵᱟᱝᱨᱚᱢ। ᱦᱤᱱᱛᱤ ᱡᱚᱨᱚᱜ ᱰᱟᱣᱝᱟᱨᱤ ᱟᱨ ᱥᱟᱱᱛᱟᱲᱤ ᱡᱚᱨᱚᱜ ᱳᱞ ᱪᱤᱠᱤ ᱚᱞᱚᱨᱮ।",
                "english": "Today we will learn letters. Devanagari for Hindi and Ol Chiki for Santhali."
            },
            "cultural_examples": [],
            "activity": {"hindi": "दोनों लिपियों में अपना नाम लिखने का अभ्यास करें।", "santhali": "ᱰᱩᱱᱚᱜ ᱚᱞᱚᱨᱮ ᱡᱚᱨᱚᱜ ᱠᱚᱨᱚᱜ ᱚᱞᱚᱨᱮ ᱵᱟᱝᱨᱚᱢ।"},
            "practice_questions": [],
            "assessment_questions": [],
            "homework": {"hindi": "अपना नाम दोनों लिपियों में लिखें।", "santhali": "ᱠᱚᱨᱚᱜ ᱚᱞᱚᱨᱮ ᱰᱩᱱᱚᱜ ᱚᱞᱚᱨᱮ ᱡᱚᱨᱚᱜ ᱢᱮ।"},
            "santhali_terms": {}
        },
        "Reading": {
            "objective": "Students will read simple sentences in Hindi and Santhali.",
            "explanation": {
                "hindi": "आज हम पढ़ना सीखेंगे। सरल वाक्य पढ़ेंगे।",
                "santhali": "ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱛᱟᱢᱮᱨᱮ ᱵᱟᱝᱨᱚᱢ। ᱥᱟᱨᱤᱟᱜ ᱣᱟᱠᱩᱭᱟ ᱛᱟᱢᱮᱨᱮ ᱢᱮ।",
                "english": "Today we will learn reading. We will read simple sentences."
            },
            "cultural_examples": [],
            "activity": {"hindi": "बाइलिंगुअल किताब से पढ़ें।", "santhali": "ᱵᱟᱭᱞᱤᱝᱩᱠᱟᱞ ᱠᱤᱛᱟᱜ ᱛᱟᱢᱮᱨᱮ ᱢᱮ।"},
            "practice_questions": [],
            "assessment_questions": [],
            "homework": {"hindi": "किताब से एक वाक्य पढ़ें।", "santhali": "ᱠᱤᱛᱟᱜ ᱨᱚᱨᱚᱜ ᱤᱧ ᱣᱟᱠᱩᱭᱟ ᱛᱟᱢᱮᱨᱮ ᱢᱮ।"},
            "santhali_terms": {}
        },
    },
}


class CopilotService:
    """AI Teacher Copilot service for lesson generation."""

    def generate_lesson(self, grade: int, subject: str, topic: str,
                        learning_outcome: Optional[str] = None,
                        language: str = "sat") -> Dict:
        """Generate a complete bilingual lesson plan."""
        # Look up template
        subject_templates = LESSON_TEMPLATES.get(subject, {})
        template = subject_templates.get(topic, None)

        if template is None:
            # Generate a generic lesson
            template = self._generate_generic_lesson(grade, subject, topic, learning_outcome, language)

        # Translate any missing Santhali content
        result = {
            "grade": grade,
            "subject": subject,
            "topic": topic,
            "language": language,
            "objective": template.get("objective", ""),
            "explanation": template.get("explanation", {}),
            "cultural_examples": template.get("cultural_examples", []),
            "activity": template.get("activity", {}),
            "practice_questions": template.get("practice_questions", []),
            "assessment_questions": template.get("assessment_questions", []),
            "homework": template.get("homework", {}),
            "santhali_terms": template.get("santhali_terms", {}),
            "learning_outcome": learning_outcome or template.get("objective", ""),
        }

        return result

    def _generate_generic_lesson(self, grade: int, subject: str, topic: str,
                                  learning_outcome: Optional[str], language: str) -> Dict:
        """Generate a generic lesson when no template exists."""
        objective = learning_outcome or f"Students will learn about {topic} in {subject}."

        explanation_hindi = f"आज हम {subject} में {topic} के बारे में सीखेंगे।"
        result = translation_service.translate(
            explanation_hindi, "hi", language,
            context={"grade": grade, "subject": subject, "topic": topic}
        )
        explanation_santhali = result.get("translated_text", "")

        return {
            "objective": objective,
            "explanation": {
                "hindi": explanation_hindi,
                "santhali": explanation_santhali,
                "english": objective,
            },
            "cultural_examples": [
                "Use examples from the student's village and natural environment",
                "Connect to family and community activities",
                "Reference local plants, animals, and daily objects",
            ],
            "activity": {
                "hindi": f"छात्रों के साथ {topic} का अभ्यास करें।",
                "santhali": f"ᱡᱟᱨᱤᱚᱜ ᱥᱟᱛᱟᱨᱚᱜ {topic} ᱠᱚᱨᱚᱜ ᱢᱟᱨᱮᱡᱟᱨᱮ ᱵᱟᱝᱨᱚᱢ।",
            },
            "practice_questions": [],
            "assessment_questions": [],
            "homework": {
                "hindi": f"घर पर {topic} का अभ्यास करें।",
                "santhali": f"ᱜᱚᱨᱚᱜ ᱠᱚᱨᱟ {topic} ᱠᱚᱨᱚᱜ ᱢᱟᱨᱮᱡᱟᱨᱮ ᱵᱟᱝᱨᱚᱢ।"
            },
            "santhali_terms": {},
        }


# Global instance
copilot_service = CopilotService()
