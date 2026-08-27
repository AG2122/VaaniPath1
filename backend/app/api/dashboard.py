"""VaniPath - Dashboard API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.translation import Translation
from app.models.lesson import Lesson
from app.models.assessment import Assessment, StudentProgress
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/teacher", tags=["Dashboard"],
            summary="Get teacher dashboard",
            description="Get comprehensive teacher dashboard with stats, recent activity, and recommendations.")
def get_teacher_dashboard(db: Session = Depends(get_db)):
    # Get stats
    student_count = db.query(Student).count()
    lesson_count = db.query(Lesson).count()
    translation_count = db.query(Translation).count()

    # Average translation confidence
    avg_confidence = db.query(func.avg(Translation.confidence)).scalar() or 0

    # Average assessment score
    avg_score = db.query(func.avg(Assessment.score)).filter(
        Assessment.status == "completed"
    ).scalar() or 0

    # Lessons completed (sum of all student progress)
    lessons_completed = db.query(func.sum(StudentProgress.lessons_completed)).scalar() or 0

    # Get recent translations
    recent_translations = db.query(Translation).order_by(
        Translation.created_at.desc()
    ).limit(5).all()

    return {
        "success": True,
        "data": {
            "student_count": student_count,
            "lessons_completed": lessons_completed,
            "translation_count": translation_count,
            "average_score": round(float(avg_score), 1),
            "translation_confidence": round(float(avg_confidence) * 100, 1),
            "offline_status": "ready",
            "recommended_activity": "Practice number comparison using flashcards",
            "recent_translations": [
                {
                    "source_text": t.source_text[:50],
                    "translated_text": t.translated_text[:50],
                    "confidence": t.confidence,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                }
                for t in recent_translations
            ],
            "stats": {
                "total_lessons": lesson_count,
                "total_students": student_count,
                "total_translations": translation_count,
                "active_assessments": db.query(Assessment).filter(
                    Assessment.status == "in_progress"
                ).count(),
                "completed_assessments": db.query(Assessment).filter(
                    Assessment.status == "completed"
                ).count(),
            },
        },
    }


@router.get("/stats", tags=["Dashboard"],
            summary="Get dashboard statistics",
            description="Get high-level dashboard statistics.")
def get_stats(db: Session = Depends(get_db)):
    return {
        "success": True,
        "data": {
            "students": db.query(Student).count(),
            "translations": db.query(Translation).count(),
            "lessons": db.query(Lesson).count(),
            "assessments": db.query(Assessment).filter(
                Assessment.status == "completed"
            ).count(),
            "avg_confidence": round(
                float(db.query(func.avg(Translation.confidence)).scalar() or 0) * 100, 1
            ),
            "avg_score": round(
                float(db.query(func.avg(Assessment.score)).filter(
                    Assessment.status == "completed"
                ).scalar() or 0), 1
            ),
        },
    }
