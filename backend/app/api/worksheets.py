"""VaniPath - Worksheet API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.database.database import get_db
from app.schemas import WorksheetGenerateRequest, SuccessResponse
from app.services.worksheet_service import worksheet_service
from app.models.worksheet import Worksheet, WorksheetQuestion

router = APIRouter(prefix="/api/worksheets", tags=["Worksheets"])


@router.post("/generate", response_model=SuccessResponse,
             summary="Generate bilingual worksheet",
             description="Generate a bilingual Hindi-Santhali worksheet with multiple question types.")
def generate_worksheet(data: WorksheetGenerateRequest, db: Session = Depends(get_db)):
    result = worksheet_service.generate(
        grade=data.grade,
        subject=data.subject,
        topic=data.topic,
        question_count=data.question_count,
        language=data.language,
    )

    # Store worksheet in database
    worksheet_id = str(uuid.uuid4())
    worksheet = Worksheet(
        id=worksheet_id,
        title=f"{data.subject} - {data.topic}",
        grade=data.grade,
        subject=data.subject,
        topic=data.topic,
        question_count=len(result["questions"]),
        language=data.language,
    )
    db.add(worksheet)

    for q in result["questions"]:
        question = WorksheetQuestion(
            id=str(uuid.uuid4()),
            worksheet_id=worksheet_id,
            question_number=q["question_number"],
            question_type=q["question_type"],
            hindi_text=q["hindi"],
            santhali_text=q["santhali"],
            options=q.get("options"),
            correct_answer=q["answer"],
        )
        db.add(question)

    db.commit()

    return SuccessResponse(
        success=True,
        data={
            "worksheet_id": worksheet_id,
            "title": worksheet.title,
            "grade": data.grade,
            "subject": data.subject,
            "topic": data.topic,
            "question_count": len(result["questions"]),
            "questions": result["questions"],
        },
    )


@router.get("/{worksheet_id}", response_model=SuccessResponse,
            summary="Get worksheet by ID",
            description="Retrieve a previously generated worksheet.")
def get_worksheet(worksheet_id: str, db: Session = Depends(get_db)):
    worksheet = db.query(Worksheet).filter(Worksheet.id == worksheet_id).first()
    if not worksheet:
        return SuccessResponse(success=False, message="Worksheet not found")

    questions = db.query(WorksheetQuestion).filter(
        WorksheetQuestion.worksheet_id == worksheet_id
    ).order_by(WorksheetQuestion.question_number).all()

    return SuccessResponse(
        success=True,
        data={
            "worksheet_id": worksheet.id,
            "title": worksheet.title,
            "grade": worksheet.grade,
            "subject": worksheet.subject,
            "topic": worksheet.topic,
            "questions": [
                {
                    "question_number": q.question_number,
                    "question_type": q.question_type,
                    "hindi": q.hindi_text,
                    "santhali": q.santhali_text,
                    "options": q.options,
                    "answer": q.correct_answer,
                }
                for q in questions
            ],
        },
    )
