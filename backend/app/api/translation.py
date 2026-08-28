"""VaniPath - Translation API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.database.database import get_db
from app.schemas import TranslationRequest, TranslationResponse
from app.services.translation_service import translation_service
from app.models.translation import Translation

router = APIRouter(prefix="/api/translation", tags=["Translation"])


def _extract_context(ctx) -> dict:
    """Extract a plain dict from a TranslationContext model, raw dict, or None."""
    if ctx is None:
        return None
    if isinstance(ctx, dict):
        return ctx
    # Pydantic model – pull attributes
    return {
        "grade": getattr(ctx, "grade", None),
        "subject": getattr(ctx, "subject", None),
        "topic": getattr(ctx, "topic", None),
    }


@router.post("/text", response_model=TranslationResponse,
             summary="Translate text",
             description="Translate text between Hindi and Santhali with educational context detection.")
def translate_text(data: TranslationRequest, db: Session = Depends(get_db)):
    ctx = _extract_context(data.context)

    result = translation_service.translate(
        text=data.text,
        source_language=data.source_language,
        target_language=data.target_language,
        context=ctx,
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
        context_subject=ctx.get("subject") if ctx else None,
        context_grade=ctx.get("grade") if ctx else None,
        context_topic=ctx.get("topic") if ctx else None,
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
