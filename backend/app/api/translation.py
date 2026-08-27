"""VaniPath - Translation API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.database.database import get_db
from app.schemas import TranslationRequest, TranslationResponse
from app.services.translation_service import translation_service
from app.models.translation import Translation

router = APIRouter(prefix="/api/translation", tags=["Translation"])


@router.post("/text", response_model=TranslationResponse,
             summary="Translate text",
             description="Translate text between Hindi and Santhali with educational context detection.")
def translate_text(data: TranslationRequest, db: Session = Depends(get_db)):
    context = None
    if data.context:
        context = {
            "grade": data.context.grade,
            "subject": data.context.subject,
            "topic": data.context.topic,
        }

    result = translation_service.translate(
        text=data.text,
        source_language=data.source_language,
        target_language=data.target_language,
        context=context,
    )

    if "error" in result:
        return TranslationResponse(
            success=False,
            data={"error": result["error"]},
        )

    # Store translation in database
    translation_record = Translation(
        id=str(uuid.uuid4()),
        source_text=data.text,
        translated_text=result["translated_text"],
        source_language=data.source_language,
        target_language=data.target_language,
        confidence=result["confidence"],
        context_subject=data.context.subject if data.context else None,
        context_grade=data.context.grade if data.context else None,
        context_topic=data.context.topic if data.context else None,
        processing_time_ms=result["processing_time_ms"],
        requires_validation=result["requires_validation"],
    )
    db.add(translation_record)
    db.commit()

    return TranslationResponse(
        success=True,
        data={
            "id": translation_record.id,
            "source_text": result["source_text"],
            "translated_text": result["translated_text"],
            "source_language": result["source_language"],
            "target_language": result["target_language"],
            "confidence": result["confidence"],
            "processing_time_ms": result["processing_time_ms"],
            "requires_validation": result["requires_validation"],
            "warning": result.get("warning"),
            "provider": result.get("provider", "local"),
        },
    )
