"""VaniPath - Speech Translation API"""
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.database.database import get_db
from app.schemas import SpeechTranslateResponse
from app.services.speech_service import speech_service
from app.services.translation_service import translation_service
from app.services.tts_service import tts_service
from app.utils.audio import validate_audio_format, validate_file_size
from app.models.translation import Translation

router = APIRouter(prefix="/api/speech", tags=["Speech"])


@router.post("/translate", response_model=SpeechTranslateResponse,
             summary="Translate speech to speech",
             description="Full voice translation pipeline: STT → Translation → TTS")
async def speech_translate(
    audio: UploadFile = File(..., description="Audio file to translate"),
    source_language: str = Form(default="hi"),
    target_language: str = Form(default="sat"),
    grade: Optional[int] = Form(default=None),
    subject: Optional[str] = Form(default=None),
    topic: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
):
    # Validate audio file
    if not validate_audio_format(audio.filename):
        return SpeechTranslateResponse(
            success=False,
            data={"error": "Unsupported audio format"},
        )

    audio_data = await audio.read()
    if not validate_file_size(len(audio_data)):
        return SpeechTranslateResponse(
            success=False,
            data={"error": f"File too large. Max size: 10MB"},
        )

    # Step 1: Speech-to-Text
    stt_result = speech_service.transcribe(audio_data, source_language)

    if not stt_result.get("text"):
        return SpeechTranslateResponse(
            success=False,
            data={"error": "Could not transcribe audio"},
        )

    # Step 2: Translate
    context = {}
    if grade:
        context["grade"] = grade
    if subject:
        context["subject"] = subject
    if topic:
        context["topic"] = topic

    translation_result = translation_service.translate(
        text=stt_result["text"],
        source_language=source_language,
        target_language=target_language,
        context=context if context else None,
    )

    if "error" in translation_result:
        return SpeechTranslateResponse(
            success=False,
            data={"error": translation_result["error"]},
        )

    # Step 3: Text-to-Speech
    tts_result = tts_service.synthesize(
        translation_result["translated_text"],
        target_language,
    )

    # Store translation
    record = Translation(
        id=str(uuid.uuid4()),
        source_text=stt_result["text"],
        translated_text=translation_result["translated_text"],
        source_language=source_language,
        target_language=target_language,
        confidence=translation_result["confidence"],
        processing_time_ms=translation_result["processing_time_ms"],
        requires_validation=translation_result["requires_validation"],
    )
    db.add(record)
    db.commit()

    return SpeechTranslateResponse(
        success=True,
        data={
            "source_text": stt_result["text"],
            "translated_text": translation_result["translated_text"],
            "audio_url": tts_result.get("audio_url"),
            "confidence": translation_result["confidence"],
            "processing_time_ms": translation_result["processing_time_ms"],
            "target_language": target_language,
            "stt_confidence": stt_result.get("confidence", 0),
            "requires_validation": translation_result["requires_validation"],
        },
    )


@router.post("/stt", tags=["Speech"],
             summary="Speech to text",
             description="Convert audio to text using speech recognition.")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form(default="hi"),
):
    audio_data = await audio.read()
    result = speech_service.transcribe(audio_data, language)
    return {"success": True, "data": result}


@router.post("/tts", tags=["Speech"],
             summary="Text to speech",
             description="Convert text to audio using text-to-speech.")
def text_to_speech(
    text: str = Form(...),
    language: str = Form(default="sat"),
):
    result = tts_service.synthesize(text, language)
    return {"success": True, "data": result}
