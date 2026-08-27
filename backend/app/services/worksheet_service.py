"""VaniPath - Bilingual Worksheet Generator Service"""
from typing import Dict, List, Optional
import random


# Question bank organized by subject and topic
QUESTION_BANK = {
    "Mathematics": {
        "Counting": [
            {"type": "mcq", "hindi": "पेड़ पर कितने पक्षी बैठे हैं?", "santhali": "ᱢᱟᱝᱣᱟ ᱠᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱵᱤᱡᱚᱨᱮ ᱥᱟᱲᱮ?", "options": ["3", "5", "7"], "answer": "5"},
            {"type": "mcq", "hindi": "नदी में कितनी मछलियाँ हैं?", "santhali": "ᱫᱤᱰᱤ ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱥᱟᱢᱟ?", "options": ["2", "4", "6"], "answer": "4"},
            {"type": "fill_blank", "hindi": "1, 2, 3, ___, 5", "santhali": "1, 2, 3, ___, 5", "options": [], "answer": "4"},
            {"type": "mcq", "hindi": "बाज़ार में कितने आम हैं?", "santhali": "ᱵᱟᱡᱟᱨᱮ ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱢᱟᱝᱣᱟ ᱥᱟᱲᱮ?", "options": ["6", "8", "10"], "answer": "8"},
            {"type": "mcq", "hindi": "घर में कितने कमरे हैं?", "santhali": "ᱜᱚᱨᱚᱜ ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱠᱚᱨᱚᱜ ᱥᱟᱲᱮ?", "options": ["2", "3", "4"], "answer": "3"},
            {"type": "counting", "hindi": "गिनिए: ★★★★★★ - कितने तारे?", "santhali": "ᱜᱤᱱᱚᱨᱮ: ★★★★★★ - ᱠᱟᱹᱨᱚᱨᱮ ᱫᱟᱨᱤᱚᱜ?", "options": ["5", "6", "7"], "answer": "6"},
            {"type": "mcq", "hindi": "वर्ग में कितने बच्चे हैं?", "santhali": "ᱣᱟᱨᱜ ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱡᱟᱨᱤᱚᱜ ᱥᱟᱲᱮ?", "options": ["10", "15", "20"], "answer": "15"},
            {"type": "fill_blank", "hindi": "5 + 3 = ___", "santhali": "5 + 3 = ___", "options": [], "answer": "8"},
            {"type": "mcq", "hindi": "दो पक्षी और तीन पक्षी मिलाकर कुल कितने?", "santhali": "ᱰᱩ ᱵᱤᱡᱚᱨᱮ ᱟᱨ ᱛᱤᱱᱟ ᱵᱤᱡᱚᱨᱮ ᱡᱚᱨᱚᱜ ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ?", "options": ["4", "5", "6"], "answer": "5"},
            {"type": "mcq", "hindi": "8 में से 3 निकालें, बचेंगे कितने?", "santhali": "8 ᱡᱚᱨᱚᱜ 3 ᱦᱟᱛᱮᱭᱟᱜ, ᱠᱟᱱᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ?", "options": ["3", "4", "5"], "answer": "5"},
        ],
        "Numbers 1-20": [
            {"type": "mcq", "hindi": "15 के बाद कौन सी संख्या आती है?", "santhali": "15 ᱨᱚᱨᱟ ᱠᱟᱹᱨᱚᱨᱮ ᱥᱟᱱᱛᱟᱲᱤ ᱟᱠᱟ?", "options": ["14", "16", "17"], "answer": "16"},
            {"type": "mcq", "hindi": "20 से छोटी कौन सी संख्या है?", "santhali": "20 ᱨᱚᱨᱚᱜ ᱪᱩᱨᱤ ᱠᱟᱹᱨᱚᱨᱮ ᱥᱟᱱᱛᱟᱲᱤ?", "options": ["18", "21", "22"], "answer": "18"},
            {"type": "fill_blank", "hindi": "10 + 5 = ___", "santhali": "10 + 5 = ___", "options": [], "answer": "15"},
            {"type": "mcq", "hindi": "12 और 8 का योग कितना?", "santhali": "12 ᱟᱨ 8 ᱠᱚᱨᱚᱜ ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ?", "options": ["18", "20", "22"], "answer": "20"},
            {"type": "matching", "hindi": "मिलाएं: एक=1, दो=__, तीन=3", "santhali": "ᱢᱤᱵᱟᱜ: 1=ᱤᱧ, __=ᱰᱩ, 3=ᱛᱤᱱᱟ", "options": ["1", "2", "3"], "answer": "2"},
            {"type": "mcq", "hindi": "किस संख्या में 5 और 7 जोड़ें?", "santhali": "ᱠᱟᱹᱨᱚᱨᱮ ᱡᱚᱨᱚᱜ 5 ᱟᱨ 7 ᱡᱚᱨᱚᱨᱚᱜ?", "options": ["10", "11", "12"], "answer": "12"},
            {"type": "fill_blank", "hindi": "___ बराबर 9 + 1", "santhali": "___ ᱵᱟᱨᱟᱨᱚᱜ 9 ᱡᱚᱨᱚᱨᱚᱜ 1", "options": [], "answer": "10"},
            {"type": "mcq", "hindi": "14 में से 6 घटाएं, बचेगा?", "santhali": "14 ᱡᱚᱨᱚᱜ 6 ᱜᱩᱴᱟᱨᱚᱨᱟ, ᱠᱟᱱᱚᱜ?", "options": ["6", "7", "8"], "answer": "8"},
            {"type": "mcq", "hindi": "सबसे बड़ी संख्या कौन सी है?", "santhali": "ᱥᱚᱵᱚᱥᱚᱜ ᱢᱩᱜᱤᱜ ᱥᱟᱱᱛᱟᱲᱤ ᱠᱟᱹᱨᱚᱨᱮ?", "options": ["11", "9", "13"], "answer": "13"},
            {"type": "mcq", "hindi": "3 गुना 4 बराबर?", "santhali": "3 ᱜᱩᱱᱟ 4 ᱵᱟᱨᱟᱨᱚᱜ?", "options": ["7", "10", "12"], "answer": "12"},
        ],
        "Addition": [
            {"type": "mcq", "hindi": "4 + 3 = ?", "santhali": "4 + 3 = ?", "options": ["5", "6", "7"], "answer": "7"},
            {"type": "mcq", "hindi": "8 + 2 = ?", "santhali": "8 + 2 = ?", "options": ["9", "10", "11"], "answer": "10"},
            {"type": "fill_blank", "hindi": "6 + 4 = ___", "santhali": "6 + 4 = ___", "options": [], "answer": "10"},
            {"type": "mcq", "hindi": "पेड़ पर 7 पक्षी, आए 5 और। कुल कितने?", "santhali": "ᱢᱟᱝᱣᱟ ᱠᱚᱨᱚᱜ 7 ᱵᱤᱡᱚᱨᱮ, 5 ᱡᱚᱨᱚᱜ। ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ?", "options": ["10", "11", "12"], "answer": "12"},
            {"type": "mcq", "hindi": "5 + 5 = ?", "santhali": "5 + 5 = ?", "options": ["8", "9", "10"], "answer": "10"},
            {"type": "fill_blank", "hindi": "9 + 1 = ___", "santhali": "9 + 1 = ___", "options": [], "answer": "10"},
            {"type": "mcq", "hindi": "3 + 7 = ?", "santhali": "3 + 7 = ?", "options": ["8", "9", "10"], "answer": "10"},
            {"type": "mcq", "hindi": "6 + 6 = ?", "santhali": "6 + 6 = ?", "options": ["10", "11", "12"], "answer": "12"},
            {"type": "mcq", "hindi": "2 + 8 = ?", "santhali": "2 + 8 = ?", "options": ["8", "9", "10"], "answer": "10"},
            {"type": "fill_blank", "hindi": "7 + 3 = ___", "santhali": "7 + 3 = ___", "options": [], "answer": "10"},
            {"type": "mcq", "hindi": "माँ ने 4 रोटी बनाईं, पापा ने 6 बनाएं। कुल?", "santhali": "ᱤᱟᱦᱟ 4 ᱨᱚᱴᱤ ᱵᱟᱱᱟᱭᱤ, ᱥᱚᱨᱚᱜ 6 ᱵᱟᱱᱟᱭᱚᱜ। ᱡᱚᱨᱚᱜ?", "options": ["8", "9", "10"], "answer": "10"},
        ],
        "Subtraction": [
            {"type": "mcq", "hindi": "7 - 3 = ?", "santhali": "7 - 3 = ?", "options": ["3", "4", "5"], "answer": "4"},
            {"type": "mcq", "hindi": "10 - 4 = ?", "santhali": "10 - 4 = ?", "options": ["5", "6", "7"], "answer": "6"},
            {"type": "fill_blank", "hindi": "9 - 5 = ___", "santhali": "9 - 5 = ___", "options": [], "answer": "4"},
            {"type": "mcq", "hindi": "10 में से 3 खाएं, बचेंगे?", "santhali": "10 ᱡᱚᱨᱚᱜ 3 ᱠᱟᱭᱚᱜ, ᱠᱟᱱᱚᱜ?", "options": ["5", "6", "7"], "answer": "7"},
            {"type": "mcq", "hindi": "8 - 8 = ?", "santhali": "8 - 8 = ?", "options": ["0", "1", "2"], "answer": "0"},
            {"type": "fill_blank", "hindi": "6 - 2 = ___", "santhali": "6 - 2 = ___", "options": [], "answer": "4"},
            {"type": "mcq", "hindi": "15 में से 5 गिनें, बचेगा?", "santhali": "15 ᱡᱚᱨᱚᱜ 5 ᱜᱤᱱᱚᱨᱮ, ᱠᱟᱱᱚᱜ?", "options": ["8", "9", "10"], "answer": "10"},
            {"type": "mcq", "hindi": "12 - 7 = ?", "santhali": "12 - 7 = ?", "options": ["4", "5", "6"], "answer": "5"},
            {"type": "mcq", "hindi": "20 में से 10 निकालें, बचेगा?", "santhali": "20 ᱡᱚᱨᱚᱜ 10 ᱦᱟᱛᱮᱭᱟᱜ, ᱠᱟᱱᱚᱜ?", "options": ["8", "9", "10"], "answer": "10"},
            {"type": "fill_blank", "hindi": "14 - 6 = ___", "santhali": "14 - 6 = ___", "options": [], "answer": "8"},
        ],
        "Shapes": [
            {"type": "mcq", "hindi": "गोल आकार कौन सा है?", "santhali": "ᱜᱩᱨᱳ ᱵᱤᱥᱩᱨᱤ ᱠᱟᱹᱨᱚᱨᱮ?", "options": ["वर्ग", "गोल", "त्रिकोण"], "answer": "गोल"},
            {"type": "mcq", "hindi": "पतंग किस आकार की होती है?", "santhali": "ᱯᱟᱛᱚᱝ ᱠᱟᱹᱨᱚᱨᱮ ᱵᱤᱥᱩᱨᱤ ᱟᱠᱟ?", "options": ["गोल", "चौकोर", "त्रिकोण"], "answer": "त्रिकोण"},
            {"type": "mcq", "hindi": "बिस्कुट किस आकार का होता है?", "santhali": "ᱵᱤᱥᱱᱟᱠᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱵᱤᱥᱩᱨᱤ?", "options": ["गोल", "चौकोर", "आयत"], "answer": "गोल"},
            {"type": "mcq", "hindi": "रुमाल किस आकार का होता है?", "santhali": "ᱨᱩᱢᱟᱞ ᱠᱟᱹᱨᱚᱨᱮ ᱵᱤᱥᱩᱨᱤ?", "options": ["गोल", "चौकोर", "त्रिकोण"], "answer": "चौकोर"},
            {"type": "mcq", "hindi": "त्रिकोण में कितनी भुजाएँ होती हैं?", "santhali": "ᱛᱤᱨᱤᱠᱚᱱᱚᱜ ᱡᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱵᱩᱡᱟᱜ ᱥᱟᱲᱮ?", "options": ["2", "3", "4"], "answer": "3"},
        ],
    },
    "Language": {
        "Letters": [
            {"type": "mcq", "hindi": "क के बाद कौन सा अक्षर आता है?", "santhali": "ᱠᱟ ᱨᱚᱨᱟ ᱠᱟᱹᱨᱚᱨᱮ ᱚᱞᱚᱨᱮ ᱟᱠᱟ?", "options": ["ख", "ग", "घ"], "answer": "ख"},
            {"type": "mcq", "hindi": "ओल चिकी किस भाषा की लिपि है?", "santhali": "ᱳᱞ ᱪᱤᱠᱤ ᱠᱟᱹᱨᱚᱨᱮ ᱦᱤᱱᱚᱜ ᱚᱞᱚᱨᱮ?", "options": ["हिंदी", "संथाली", "बांग्ला"], "answer": "संथाली"},
        ],
        "Reading": [
            {"type": "mcq", "hindi": "📚 का मतलब है", "santhali": "📚 ᱠᱚᱨᱚᱜ ᱞᱟᱹᱨᱮ", "options": ["किताब", "कलम", "कुर्सी"], "answer": "किताब"},
            {"type": "mcq", "hindi": "🎓 का मतलब है", "santhali": "🎓 ᱠᱚᱨᱚᱜ ᱞᱟᱹᱨᱮ", "options": ["गेंद", "टोपी", "फूल"], "answer": "टोपी"},
        ],
    },
}


class WorksheetService:
    """Bilingual worksheet generator service."""

    def generate(self, grade: int, subject: str, topic: str,
                 question_count: int = 10, language: str = "sat") -> Dict:
        """Generate a bilingual worksheet."""
        subject_bank = QUESTION_BANK.get(subject, {})
        topic_questions = subject_bank.get(topic, [])

        if not topic_questions:
            # Try to find questions from any topic in the subject
            for t, qs in subject_bank.items():
                topic_questions.extend(qs)
            if not topic_questions:
                # Generate generic questions
                topic_questions = self._generate_generic_questions(subject, topic, question_count)

        # Select and limit questions
        if len(topic_questions) > question_count:
            selected = random.sample(topic_questions, question_count)
        else:
            selected = topic_questions[:question_count]

        # Format questions
        questions = []
        for i, q in enumerate(selected, 1):
            questions.append({
                "question_number": i,
                "question_type": q.get("type", "mcq"),
                "hindi": q["hindi"],
                "santhali": q["santhali"],
                "options": q.get("options", []),
                "answer": q["answer"],
            })

        return {
            "grade": grade,
            "subject": subject,
            "topic": topic,
            "language": language,
            "question_count": len(questions),
            "questions": questions,
        }

    def _generate_generic_questions(self, subject: str, topic: str, count: int) -> list:
        """Generate generic questions when no specific bank exists."""
        questions = []
        for i in range(min(count, 5)):
            questions.append({
                "type": "mcq",
                "hindi": f"प्रश्न {i+1}: {topic} के बारे में सही उत्तर चुनें",
                "santhali": f"ᱠᱚᱨᱚᱜ {i+1}: {topic} ᱨᱚᱨᱚᱜ ᱥᱟᱢᱚᱜ ᱟᱛᱟᱨᱚᱜ ᱫᱩᱴᱷᱤᱣᱮ ᱢᱮ",
                "options": ["क", "ख", "ग"],
                "answer": "क",
            })
        return questions


# Global instance
worksheet_service = WorksheetService()
