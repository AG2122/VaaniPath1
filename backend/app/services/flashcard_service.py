"""VaniPath - Bilingual Flashcard Generator Service"""
from typing import Dict, List, Optional
import random
import uuid


# Flashcard database organized by category
FLASHCARD_DB = {
    "Animals": [
        {"hindi": "बाघ", "santhali": "ᱵᱟᱜᱚᱨ", "pronunciation": "bagor", "image_url": "/images/animals/tiger.png"},
        {"hindi": "हाथी", "santhali": "ᱦᱟᱛᱤ", "pronunciation": "hati", "image_url": "/images/animals/elephant.png"},
        {"hindi": "मोर", "santhali": "ᱢᱚᱨᱚᱜ", "pronunciation": "morog", "image_url": "/images/animals/peacock.png"},
        {"hindi": "गाय", "santhali": "ᱜᱟᱭ", "pronunciation": "gai", "image_url": "/images/animals/cow.png"},
        {"hindi": "कुत्ता", "santhali": "ᱠᱩᱛᱷᱟ", "pronunciation": "kuththa", "image_url": "/images/animals/dog.png"},
        {"hindi": "बिल्ली", "santhali": "ᱢᱩᱨᱮᱢ", "pronunciation": "murem", "image_url": "/images/animals/cat.png"},
        {"hindi": "मछली", "santhali": "ᱥᱟᱢᱟ", "pronunciation": "sama", "image_url": "/images/animals/fish.png"},
        {"hindi": "मुर्गी", "santhali": "ᱪᱩᱨᱤ", "pronunciation": "churi", "image_url": "/images/animals/hen.png"},
        {"hindi": "हिरण", "santhali": "ᱦᱤᱨᱚᱱ", "pronunciation": "hiroñ", "image_url": "/images/animals/deer.png"},
        {"hindi": "नाग", "santhali": "ᱜᱟᱨᱚᱢ", "pronunciation": "garom", "image_url": "/images/animals/snake.png"},
        {"hindi": "बंदर", "santhali": "ᱢᱤᱱᱚᱢ", "pronunciation": "minom", "image_url": "/images/animals/monkey.png"},
        {"hindi": "भालू", "santhali": "ᱜᱩᱨᱩ", "pronunciation": "guru", "image_url": "/images/animals/bear.png"},
    ],
    "Numbers": [
        {"hindi": "एक", "santhali": "ᱤᱧ", "pronunciation": "ik", "image_url": "/images/numbers/1.png"},
        {"hindi": "दो", "santhali": "ᱰᱩ", "pronunciation": "du", "image_url": "/images/numbers/2.png"},
        {"hindi": "तीन", "santhali": "ᱛᱤᱱᱟ", "pronunciation": "tina", "image_url": "/images/numbers/3.png"},
        {"hindi": "चार", "santhali": "ᱪᱟᱨᱮᱭ", "pronunciation": "charoi", "image_url": "/images/numbers/4.png"},
        {"hindi": "पाँच", "santhali": "ᱰᱩᱛᱤ", "pronunciation": "dutte", "image_url": "/images/numbers/5.png"},
        {"hindi": "छह", "santhali": "ᱨᱩᱫᱮ", "pronunciation": "rudea", "image_url": "/images/numbers/6.png"},
        {"hindi": "सात", "santhali": "ᱠᱩᱵᱤ", "pronunciation": "kubi", "image_url": "/images/numbers/7.png"},
        {"hindi": "आठ", "santhali": "ᱤᱨᱟᱜ", "pronunciation": "irae", "image_url": "/images/numbers/8.png"},
        {"hindi": "नौ", "santhali": "ᱤᱱᱩ", "pronunciation": "inu", "image_url": "/images/numbers/9.png"},
        {"hindi": "दस", "santhali": "ᱜᱟᱨᱚ", "pronunciation": "garao", "image_url": "/images/numbers/10.png"},
    ],
    "Colors": [
        {"hindi": "लाल", "santhali": "ᱞᱟᱞ", "pronunciation": "lal", "image_url": "/images/colors/red.png"},
        {"hindi": "नीला", "santhali": "ᱱᱤᱞᱚᱨ", "pronunciation": "nilor", "image_url": "/images/colors/blue.png"},
        {"hindi": "हरा", "santhali": "ᱦᱟᱨᱚ", "pronunciation": "harao", "image_url": "/images/colors/green.png"},
        {"hindi": "पीला", "santhali": "ᱰᱟᱲᱮᱜ", "pronunciation": "dadaeg", "image_url": "/images/colors/yellow.png"},
        {"hindi": "सफ़ेद", "santhali": "ᱥᱟᱝᱨᱤᱢ", "pronunciation": "sangrim", "image_url": "/images/colors/white.png"},
        {"hindi": "काला", "santhali": "ᱦᱩᱨᱩᱢ", "pronunciation": "hurum", "image_url": "/images/colors/black.png"},
        {"hindi": "नारंगी", "santhali": "ᱢᱚᱨᱚᱜᱤ", "pronunciation": "morogik", "image_url": "/images/colors/orange.png"},
        {"hindi": "बैंगनी", "santhali": "ᱫᱩᱨᱚᱜ", "pronunciation": "durug", "image_url": "/images/colors/purple.png"},
    ],
    "Family": [
        {"hindi": "माँ", "santhali": "ᱤᱟᱦᱟ", "pronunciation": "iya-ha", "image_url": "/images/family/mother.png"},
        {"hindi": "पिता", "santhali": "ᱥᱚᱨᱚᱜ", "pronunciation": "sorog", "image_url": "/images/family/father.png"},
        {"hindi": "दादा", "santhali": "ᱨᱤᱝᱤ", "pronunciation": "ringi", "image_url": "/images/family/grandfather.png"},
        {"hindi": "दादी", "santhali": "ᱨᱤᱝᱤ", "pronunciation": "ringi-sae", "image_url": "/images/family/grandmother.png"},
        {"hindi": "भाई", "santhali": "ᱵᱟᱨᱤ", "pronunciation": "bari", "image_url": "/images/family/brother.png"},
        {"hindi": "बहन", "santhali": "ᱥᱩᱱᱤ", "pronunciation": "suni", "image_url": "/images/family/sister.png"},
        {"hindi": "चाचा", "santhali": "ᱪᱟᱪᱟ", "pronunciation": "chacha", "image_url": "/images/family/uncle.png"},
        {"hindi": "चाची", "santhali": "ᱪᱟᱪᱤ", "pronunciation": "chachi", "image_url": "/images/family/aunt.png"},
    ],
    "Food": [
        {"hindi": "चावल", "santhali": "ᱥᱟᱝᱚᱛ", "pronunciation": "sangoth", "image_url": "/images/food/rice.png"},
        {"hindi": "रोटी", "santhali": "ᱪᱩᱨᱤ", "pronunciation": "churi", "image_url": "/images/food/roti.png"},
        {"hindi": "दाल", "santhali": "ᱫᱟᱞ", "pronunciation": "dal", "image_url": "/images/food/dal.png"},
        {"hindi": "फल", "santhali": "ᱢᱟᱝᱣᱟ", "pronunciation": "mang-va", "image_url": "/images/food/fruit.png"},
        {"hindi": "आम", "santhali": "ᱢᱟᱝᱣᱟ", "pronunciation": "mang-va", "image_url": "/images/food/mango.png"},
        {"hindi": "सेब", "santhali": "ᱥᱟᱡᱚ", "pronunciation": "sajo", "image_url": "/images/food/apple.png"},
        {"hindi": "दूध", "santhali": "ᱢᱩᱢᱟ", "pronunciation": "muma", "image_url": "/images/food/milk.png"},
        {"hindi": "पानी", "santhali": "ᱦᱚᱨᱚᱜ", "pronunciation": "horog", "image_url": "/images/food/water.png"},
    ],
    "Nature": [
        {"hindi": "पेड़", "santhali": "ᱢᱟᱝᱣᱟ", "pronunciation": "mangva", "image_url": "/images/nature/tree.png"},
        {"hindi": "फूल", "santhali": "ᱢᱩᱨᱩ", "pronunciation": "muru", "image_url": "/images/nature/flower.png"},
        {"hindi": "नदी", "santhali": "ᱫᱤᱰᱤ", "pronunciation": "didhi", "image_url": "/images/nature/river.png"},
        {"hindi": "पहाड़", "santhali": "ᱯᱚᱨᱚᱜ", "pronunciation": "porog", "image_url": "/images/nature/mountain.png"},
        {"hindi": "बारिश", "santhali": "ᱫᱟᱨᱚ", "pronunciation": "daraao", "image_url": "/images/nature/rain.png"},
        {"hindi": "सूरज", "santhali": "ᱥᱟᱨᱤ", "pronunciation": "sari", "image_url": "/images/nature/sun.png"},
        {"hindi": "चाँद", "santhali": "ᱫᱦᱤ", "pronunciation": "dahi", "image_url": "/images/nature/moon.png"},
        {"hindi": "तारा", "santhali": "ᱫᱦᱤ", "pronunciation": "dahi", "image_url": "/images/nature/star.png"},
    ],
    "School": [
        {"hindi": "किताब", "santhali": "ᱠᱤᱛᱟᱜ", "pronunciation": "kithag", "image_url": "/images/school/book.png"},
        {"hindi": "कलम", "santhali": "ᱠᱟᱞᱟᱢ", "pronunciation": "kalom", "image_url": "/images/school/pen.png"},
        {"hindi": "कक्षा", "santhali": "ᱠᱚᱨᱚᱜ", "pronunciation": "korok", "image_url": "/images/school/classroom.png"},
        {"hindi": "शिक्षक", "santhali": "ᱜᱟᱨᱚᱲ", "pronunciation": "garaod", "image_url": "/images/school/teacher.png"},
        {"hindi": "विद्यार्थी", "santhali": "ᱡᱟᱨᱤᱚᱜ", "pronunciation": "jariog", "image_url": "/images/school/student.png"},
        {"hindi": "बोर्ड", "santhali": "ᱵᱚᱨᱰ", "pronunciation": "borod", "image_url": "/images/school/board.png"},
        {"hindi": "पेंसिल", "santhali": "ᱯᱮᱱᱥᱤᱞ", "pronunciation": "pensil", "image_url": "/images/school/pencil.png"},
        {"hindi": "रबड़", "santhali": "ᱨᱚᱵᱚᱫ", "pronunciation": "robod", "image_url": "/images/school/eraser.png"},
    ],
}


class FlashcardService:
    """Bilingual flashcard generator service."""

    def generate(self, category: str = "Animals", count: int = 6,
                 grade: int = 1, language: str = "sat") -> List[Dict]:
        """Generate flashcards for a given category."""
        cards = FLASHCARD_DB.get(category, [])

        if not cards:
            # Fallback: use Animals
            cards = FLASHCARD_DB.get("Animals", [])

        # Select cards
        if len(cards) > count:
            selected = random.sample(cards, count)
        else:
            selected = cards[:count]

        result = []
        for card in selected:
            result.append({
                "id": str(uuid.uuid4()),
                "image_url": card.get("image_url"),
                "hindi": card["hindi"],
                "santhali": card["santhali"],
                "audio_url": f"/audio/sat_{card['santhali']}.wav",
                "pronunciation": card.get("pronunciation", ""),
                "category": category,
                "grade": grade,
            })

        return result

    def get_categories(self) -> List[Dict]:
        """Get available flashcard categories."""
        return [
            {"id": "Animals", "name": "Animals", "hindi": "जानवर", "santhali": "ᱵᱤᱥᱩ", "count": len(FLASHCARD_DB.get("Animals", []))},
            {"id": "Numbers", "name": "Numbers", "hindi": "संख्या", "santhali": "ᱥᱟᱱᱛᱟᱲᱤ", "count": len(FLASHCARD_DB.get("Numbers", []))},
            {"id": "Colors", "name": "Colors", "hindi": "रंग", "santhali": "ᱨᱚᱜ", "count": len(FLASHCARD_DB.get("Colors", []))},
            {"id": "Family", "name": "Family", "hindi": "परिवार", "santhali": "ᱥᱟᱨᱤᱡᱚᱨ", "count": len(FLASHCARD_DB.get("Family", []))},
            {"id": "Food", "name": "Food", "hindi": "खाना", "santhali": "ᱦᱟᱨᱚ", "count": len(FLASHCARD_DB.get("Food", []))},
            {"id": "Nature", "name": "Nature", "hindi": "प्रकृति", "santhali": "ᱫᱚᱨᱚᱜ", "count": len(FLASHCARD_DB.get("Nature", []))},
            {"id": "School", "name": "School", "hindi": "स्कूल", "santhali": "ᱠᱚᱨᱚᱜ", "count": len(FLASHCARD_DB.get("School", []))},
        ]


# Global instance
flashcard_service = FlashcardService()
