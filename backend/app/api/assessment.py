"""VaniPath - Assessment API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timezone

from app.database.database import get_db
from app.schemas import AssessmentGenerateRequest, AssessmentSubmitRequest, AssessmentSubmitResponse, SuccessResponse
from app.services.assessment_service import assessment_service
from app.models.assessment import Assessment, AssessmentQuestion, StudentProgress

router = APIRouter(prefix="/api/assessment", tags=["Assessment"])


@router.post("/generate", response_model=SuccessResponse,
             summary="Generate adaptive assessment",
             description="Generate an adaptive assessment with questions tailored to the student's level.")
def generate_assessment(data: AssessmentGenerateRequest, db: Session = Depends(get_db)):
    result = assessment_service.generate(
        student_id=data.student_id,
        subject=data.subject,
        topic=data.topic,
        grade=data.grade,
        question_count=data.question_count,
        language=data.language,
    )

    # Store assessment in database
    assessment = Assessment(
        id=result["assessment_id"],
        student_id=data.student_id,
        subject=data.subject,
        topic=data.topic,
        grade=data.grade,
        total_questions=result["total_questions"],
        status="pending",
    )
    db.add(assessment)

    for q in result["questions"]:
        aq = AssessmentQuestion(
            id=q["id"],
            assessment_id=result["assessment_id"],
            question_number=q["question_number"],
            question_type=q["question_type"],
            hindi_text=q["hindi_text"],
            santhali_text=q["santhali_text"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            topic=q.get("topic"),
        )
        db.add(aq)

    db.commit()

    return SuccessResponse(
        success=True,
        data=result,
    )


@router.post("/submit", response_model=AssessmentSubmitResponse,
             summary="Submit assessment answers",
             description="Submit answers and get results with adaptive recommendations.")
def submit_assessment(data: AssessmentSubmitRequest, db: Session = Depends(get_db)):
    # Get assessment questions from database
    assessment = db.query(Assessment).filter(Assessment.id == data.assessment_id).first()
    if not assessment:
        return AssessmentSubmitResponse(
            success=False,
            data={"error": "Assessment not found"},
        )

    questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.assessment_id == data.assessment_id
    ).all()

    questions_list = [
        {
            "id": q.id,
            "hindi_text": q.hindi_text,
            "santhali_text": q.santhali_text,
            "correct_answer": q.correct_answer,
            "topic": q.topic,
        }
        for q in questions
    ]

    # Submit and evaluate
    result = assessment_service.submit(
        assessment_id=data.assessment_id,
        answers=[{"question_id": a["question_id"], "answer": a["answer"]} for a in data.answers],
        questions=questions_list,
    )

    # Update assessment record
    assessment.score = result["score"]
    assessment.correct_answers = result["correct_answers"]
    assessment.wrong_answers = result["wrong_answers"]
    assessment.weak_topics = result["weak_topics"]
    assessment.strong_topics = result["strong_topics"]
    assessment.status = "completed"
    assessment.completed_at = datetime.now(timezone.utc)
    db.commit()

    # Update student progress if student_id exists
    if assessment.student_id:
        progress = db.query(StudentProgress).filter(
            StudentProgress.student_id == assessment.student_id
        ).first()

        if not progress:
            progress = StudentProgress(
                id=str(uuid.uuid4()),
                student_id=assessment.student_id,
                assessment_id=data.assessment_id,
                lessons_completed=0,
                assessments_completed=1,
                average_score=result["score"],
                learning_streak=1,
                strong_topics=result["strong_topics"],
                weak_topics=result["weak_topics"],
            )
            db.add(progress)
        else:
            progress.assessments_completed += 1
            progress.average_score = (
                (progress.average_score * (progress.assessments_completed - 1) + result["score"])
                / progress.assessments_completed
            )
            progress.strong_topics = result["strong_topics"]
            progress.weak_topics = result["weak_topics"]
            progress.last_activity_at = datetime.now(timezone.utc)

        db.commit()

    return AssessmentSubmitResponse(
        success=True,
        data=result,
    )


@router.get("/{assessment_id}", tags=["Assessment"],
            summary="Get assessment details",
            description="Get assessment details and questions.")
def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        return SuccessResponse(success=False, message="Assessment not found")

    questions = db.query(AssessmentQuestion).filter(
        AssessmentQuestion.assessment_id == assessment_id
    ).order_by(AssessmentQuestion.question_number).all()

    return SuccessResponse(
        success=True,
        data={
            "assessment_id": assessment.id,
            "subject": assessment.subject,
            "topic": assessment.topic,
            "grade": assessment.grade,
            "total_questions": assessment.total_questions,
            "score": assessment.score,
            "status": assessment.status,
            "questions": [
                {
                    "id": q.id,
                    "question_number": q.question_number,
                    "question_type": q.question_type,
                    "hindi": q.hindi_text,
                    "santhali": q.santhali_text,
                    "options": q.options,
                    "topic": q.topic,
                }
                for q in questions
            ],
        },
    )
