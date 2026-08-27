"""VaniPath - Flashcard API"""
from fastapi import APIRouter
from app.schemas import FlashcardGenerateRequest, SuccessResponse
from app.services.flashcard_service import flashcard_service

router = APIRouter(prefix="/api/flashcards", tags=["Flashcards"])


@router.post("/generate", response_model=SuccessResponse,
             summary="Generate bilingual flashcards",
             description="Generate Hindi-Santhali flashcards for a given category.")
def generate_flashcards(data: FlashcardGenerateRequest):
    cards = flashcard_service.generate(
        category=data.category,
        count=data.count,
        grade=data.grade,
        language=data.language,
    )

    return SuccessResponse(
        success=True,
        data={
            "flashcards": cards,
            "category": data.category,
            "count": len(cards),
        },
    )


@router.get("/categories", tags=["Flashcards"],
            summary="Get flashcard categories",
            description="Get available flashcard categories.")
def get_categories():
    categories = flashcard_service.get_categories()
    return {
        "success": True,
        "data": {
            "categories": categories,
            "count": len(categories),
        },
    }


@router.get("/{category}", tags=["Flashcards"],
            summary="Get flashcards by category",
            description="Get all flashcards for a specific category.")
def get_flashcards_by_category(category: str, count: int = 10):
    cards = flashcard_service.generate(category=category, count=count)
    return {
        "success": True,
        "data": {
            "flashcards": cards,
            "category": category,
            "count": len(cards),
        },
    }
