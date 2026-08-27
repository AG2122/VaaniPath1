"""VaniPath - AI Teacher Copilot API"""
from fastapi import APIRouter
from app.schemas import LessonGenerateRequest, LessonPlanResponse
from app.services.copilot_service import copilot_service

router = APIRouter(prefix="/api/copilot", tags=["AI Teacher Copilot"])


@router.post("/lesson", response_model=LessonPlanResponse,
             summary="Generate lesson plan",
             description="Generate a culturally relevant bilingual lesson plan for Hindi-speaking teachers teaching Santhali-speaking students.")
def generate_lesson(data: LessonGenerateRequest):
    result = copilot_service.generate_lesson(
        grade=data.grade,
        subject=data.subject,
        topic=data.topic,
        learning_outcome=data.learning_outcome,
        language=data.language,
    )

    return LessonPlanResponse(
        success=True,
        data=result,
    )
