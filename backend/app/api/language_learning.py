"""VaniPath - Language Learning API (Teacher Santhali Learning)"""
from fastapi import APIRouter
from app.schemas import PracticeRequest, SuccessResponse

router = APIRouter(prefix="/api/language-learning", tags=["Language Learning"])


@router.get("/phrases", tags=["Language Learning"],
            summary="Get learning phrases",
            description="Get Hindi-Santhali phrases for teacher language learning.")
def get_learning_phrases():
    """Provide phrases with Hindi, Santhali, pronunciation, and meaning."""
    phrases = [
        {
            "id": "1",
            "hindi": "नमस्ते",
            "santhali": "ᱡᱚᱨᱟ",
            "english": "Hello",
            "pronunciation": "jora",
            "audio_url": "/audio/learning/namaste.wav",
            "meaning": "Greeting - use when meeting someone",
        },
        {
            "id": "2",
            "hindi": "आप कैसे हैं?",
            "santhali": "ᱠᱮ ᱥᱟᱢᱚᱜ ᱥᱟᱲᱮ?",
            "english": "How are you?",
            "pronunciation": "ke samao sate?",
            "audio_url": "/audio/learning/how_are_you.wav",
            "meaning": "Asking about someone's well-being",
        },
        {
            "id": "3",
            "hindi": "मेरा नाम ___ है",
            "santhali": "ᱤᱦᱟ ᱚᱞᱚᱨᱮ ___ ᱟ",
            "english": "My name is ___",
            "pronunciation": "iya horo ___ ae",
            "audio_url": "/audio/learning/my_name.wav",
            "meaning": "Introducing yourself",
        },
        {
            "id": "4",
            "hindi": "धन्यवाद",
            "santhali": "ᱰᱟᱨᱟ᱃",
            "english": "Thank you",
            "pronunciation": "darag",
            "audio_url": "/audio/learning/thank_you.wav",
            "meaning": "Expressing gratitude",
        },
        {
            "id": "5",
            "hindi": "हाँ",
            "santhali": "ᱦᱮᱭ",
            "english": "Yes",
            "pronunciation": "hey",
            "audio_url": "/audio/learning/yes.wav",
            "meaning": "Affirmative response",
        },
        {
            "id": "6",
            "hindi": "नहीं",
            "santhali": "ᱞᱟᱹᱨ",
            "english": "No",
            "pronunciation": "lar",
            "audio_url": "/audio/learning/no.wav",
            "meaning": "Negative response",
        },
        {
            "id": "7",
            "hindi": "अच्छा",
            "santhali": "ᱥᱟᱢᱚᱜ",
            "english": "Good",
            "pronunciation": "somog",
            "audio_url": "/audio/learning/good.wav",
            "meaning": "Positive adjective",
        },
        {
            "id": "8",
            "hindi": "किताब",
            "santhali": "ᱠᱤᱛᱟᱜ",
            "english": "Book",
            "pronunciation": "kithag",
            "audio_url": "/audio/learning/book.wav",
            "meaning": "Classroom object",
        },
        {
            "id": "9",
            "hindi": "पानी",
            "santhali": "ᱦᱚᱨᱚᱜ",
            "english": "Water",
            "pronunciation": "horog",
            "audio_url": "/audio/learning/water.wav",
            "meaning": "Essential word for classroom",
        },
        {
            "id": "10",
            "hindi": "एक, दो, तीन",
            "santhali": "ᱤᱧ, ᱰᱩ, ᱛᱤᱱᱟ",
            "english": "One, Two, Three",
            "pronunciation": "ik, du, tina",
            "audio_url": "/audio/learning/counting.wav",
            "meaning": "Basic counting",
        },
    ]

    return {
        "success": True,
        "data": {
            "phrases": phrases,
            "count": len(phrases),
        },
    }


@router.post("/practice", tags=["Language Learning"],
             summary="Practice a phrase",
             description="Submit a practice attempt for a language learning phrase.")
def practice_phrase(data: PracticeRequest):
    # Simple practice tracking
    return {
        "success": True,
        "data": {
            "phrase_id": data.phrase_id,
            "user_answer": data.user_answer,
            "feedback": "Keep practicing! Your pronunciation is improving.",
            "score": 85,
        },
    }


@router.get("/progress", tags=["Language Learning"],
            summary="Get language learning progress",
            description="Get teacher's Santhali learning progress.")
def get_learning_progress():
    return {
        "success": True,
        "data": {
            "phrases_learned": 10,
            "total_phrases": 50,
            "accuracy": 85,
            "streak": 3,
            "level": "Beginner",
            "next_milestone": "Learn 20 phrases for Level 2",
        },
    }
