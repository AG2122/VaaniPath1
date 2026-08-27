"""VaniPath - Student Management API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database.database import get_db
from app.schemas import StudentCreate, SuccessResponse, ProgressResponse
from app.models.student import Student
from app.models.assessment import StudentProgress
from app.services.assessment_service import assessment_service

router = APIRouter(prefix="/api/students", tags=["Students"])


@router.post("/", response_model=SuccessResponse,
             summary="Create a student",
             description="Create a new student record.")
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    student = Student(
        id=str(uuid.uuid4()),
        name=data.name,
        grade=data.grade,
        school=data.school,
        preferred_language="sat",
        target_language="hi",
    )
    db.add(student)
    db.commit()

    return SuccessResponse(
        success=True,
        data={
            "student_id": student.id,
            "name": student.name,
            "grade": student.grade,
        },
    )


@router.get("/", tags=["Students"],
            summary="List students",
            description="Get all students.")
def list_students(db: Session = Depends(get_db)):
    students = db.query(Student).all()
    return {
        "success": True,
        "data": {
            "students": [
                {
                    "id": s.id,
                    "name": s.name,
                    "grade": s.grade,
                    "school": s.school,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in students
            ],
            "count": len(students),
        },
    }


@router.get("/{student_id}", tags=["Students"],
            summary="Get student details",
            description="Get student details by ID.")
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "success": True,
        "data": {
            "id": student.id,
            "name": student.name,
            "grade": student.grade,
            "school": student.school,
            "preferred_language": student.preferred_language,
            "created_at": student.created_at.isoformat() if student.created_at else None,
        },
    }


@router.get("/{student_id}/progress", response_model=ProgressResponse,
            summary="Get student progress",
            description="Get comprehensive student progress including lessons, scores, and learning streak.")
def get_student_progress(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return ProgressResponse(
            success=False,
            data={"error": "Student not found"},
        )

    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == student_id
    ).order_by(StudentProgress.created_at.desc()).first()

    if not progress:
        return ProgressResponse(
            success=True,
            data={
                "student_id": student_id,
                "name": student.name,
                "grade": student.grade,
                "lessons_completed": 0,
                "assessments_completed": 0,
                "average_score": 0,
                "learning_streak": 0,
                "strong_topics": [],
                "weak_topics": [],
                "recommended_activity": "Start with basic flashcards",
                "badges": [],
            },
        )

    # Get recommendations
    weak = progress.weak_topics or []
    recommendations = assessment_service.get_recommendations(student_id, weak)

    return ProgressResponse(
        success=True,
        data={
            "student_id": student_id,
            "name": student.name,
            "grade": student.grade,
            "lessons_completed": progress.lessons_completed,
            "assessments_completed": progress.assessments_completed,
            "average_score": progress.average_score,
            "learning_streak": progress.learning_streak,
            "strong_topics": progress.strong_topics or [],
            "weak_topics": progress.weak_topics or [],
            "recommended_activity": recommendations[0]["title"] if recommendations else "Start with flashcards",
            "recommendations": recommendations,
            "badges": progress.badges or [],
            "last_activity": progress.last_activity_at.isoformat() if progress.last_activity_at else None,
        },
    )


@router.get("/{student_id}/recommendations", tags=["Students"],
            summary="Get student recommendations",
            description="Get personalized learning recommendations based on student progress.")
def get_recommendations(student_id: str, db: Session = Depends(get_db)):
    progress = db.query(StudentProgress).filter(
        StudentProgress.student_id == student_id
    ).order_by(StudentProgress.created_at.desc()).first()

    if not progress:
        return {
            "success": True,
            "data": {
                "recommendations": [
                    {
                        "activity_type": "flashcard",
                        "title": "Start with Numbers flashcards",
                        "description": "Begin your learning journey with basic numbers",
                        "priority": 1,
                    }
                ],
            },
        }

    weak = progress.weak_topics or []
    recommendations = assessment_service.get_recommendations(student_id, weak)

    return {
        "success": True,
        "data": {
            "recommendations": recommendations,
        },
    }
