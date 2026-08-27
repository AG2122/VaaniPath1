"""VaniPath - Classroom Translation API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from app.database.database import get_db
from app.schemas import ClassroomTranslateRequest, SuccessResponse
from app.services.translation_service import translation_service
from app.services.tts_service import tts_service
from app.models.classroom import ClassroomSession, ClassroomMessage
from app.utils.security import generate_id

router = APIRouter(prefix="/api/classroom", tags=["Classroom"])


@router.post("/teacher-to-student", response_model=SuccessResponse,
             summary="Teacher to Student translation",
             description="Translate teacher's Hindi speech to Santhali for students.")
def teacher_to_student(data: ClassroomTranslateRequest, db: Session = Depends(get_db)):
    # Get or create session
    session = None
    if data.session_id:
        session = db.query(ClassroomSession).filter(
            ClassroomSession.id == data.session_id
        ).first()

    if not session:
        session = ClassroomSession(
            id=generate_id(),
            grade=data.grade,
            subject=data.subject,
            is_active=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Translate Hindi → Santhali
    context = {}
    if data.grade:
        context["grade"] = data.grade
    if data.subject:
        context["subject"] = data.subject

    result = translation_service.translate(
        text=data.text,
        source_language="hi",
        target_language="sat",
        context=context if context else None,
    )

    if "error" in result:
        return SuccessResponse(
            success=False,
            message=result["error"],
        )

    # Generate audio
    tts_result = tts_service.synthesize(result["translated_text"], "sat")

    # Store message
    message = ClassroomMessage(
        id=generate_id(),
        session_id=session.id,
        speaker="teacher",
        source_language="hi",
        target_language="sat",
        source_text=data.text,
        translated_text=result["translated_text"],
        confidence=result["confidence"],
        audio_path=tts_result.get("audio_url"),
    )
    db.add(message)
    db.commit()

    return SuccessResponse(
        success=True,
        data={
            "session_id": session.id,
            "message_id": message.id,
            "source_text": data.text,
            "translated_text": result["translated_text"],
            "audio_url": tts_result.get("audio_url"),
            "confidence": result["confidence"],
            "speaker": "teacher",
            "processing_time_ms": result["processing_time_ms"],
        },
    )


@router.post("/student-to-teacher", response_model=SuccessResponse,
             summary="Student to Teacher translation",
             description="Translate student's Santhali response to Hindi for teacher.")
def student_to_teacher(data: ClassroomTranslateRequest, db: Session = Depends(get_db)):
    # Get or create session
    session = None
    if data.session_id:
        session = db.query(ClassroomSession).filter(
            ClassroomSession.id == data.session_id
        ).first()

    if not session:
        session = ClassroomSession(
            id=generate_id(),
            grade=data.grade,
            subject=data.subject,
            is_active=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Translate Santhali → Hindi
    context = {}
    if data.grade:
        context["grade"] = data.grade
    if data.subject:
        context["subject"] = data.subject

    result = translation_service.translate(
        text=data.text,
        source_language="sat",
        target_language="hi",
        context=context if context else None,
    )

    if "error" in result:
        return SuccessResponse(
            success=False,
            message=result["error"],
        )

    # Store message
    message = ClassroomMessage(
        id=generate_id(),
        session_id=session.id,
        speaker="student",
        source_language="sat",
        target_language="hi",
        source_text=data.text,
        translated_text=result["translated_text"],
        confidence=result["confidence"],
    )
    db.add(message)
    db.commit()

    return SuccessResponse(
        success=True,
        data={
            "session_id": session.id,
            "message_id": message.id,
            "source_text": data.text,
            "translated_text": result["translated_text"],
            "confidence": result["confidence"],
            "speaker": "student",
            "processing_time_ms": result["processing_time_ms"],
        },
    )


@router.get("/phrases", tags=["Classroom"],
            summary="Get classroom phrases",
            description="Get common teacher phrases with Hindi and Santhali translations.")
def get_phrases():
    from app.services.flashcard_service import flashcard_service
    import json
    import os

    phrases_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "..",
        "data", "languages", "santhali", "classroom_phrases.json"
    )

    phrases = []
    if os.path.exists(phrases_path):
        with open(phrases_path, "r", encoding="utf-8") as f:
            phrases = json.load(f)

    return {
        "success": True,
        "data": {
            "phrases": phrases,
            "count": len(phrases),
        },
    }


@router.get("/{session_id}/history", tags=["Classroom"],
            summary="Get session translation history",
            description="Get all translations for a classroom session.")
def get_session_history(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ClassroomMessage).filter(
        ClassroomMessage.session_id == session_id
    ).order_by(ClassroomMessage.created_at).all()

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "messages": [
                {
                    "id": m.id,
                    "speaker": m.speaker,
                    "source_text": m.source_text,
                    "translated_text": m.translated_text,
                    "source_language": m.source_language,
                    "target_language": m.target_language,
                    "confidence": m.confidence,
                    "audio_path": m.audio_path,
                    "timestamp": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ],
            "total_messages": len(messages),
        },
    }
