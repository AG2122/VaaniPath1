"""VaniPath - Pydantic Schemas"""
import re
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


# ─── Auth ──────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., description="Email address")
    mobile: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: str = Field(default="teacher")
    school: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    mobile: Optional[str] = None
    role: str
    school: Optional[str] = None
    preferred_language: str = "hi"
    target_language: str = "sat"
    created_at: Optional[datetime] = None


# ─── Translation ───────────────────────────────────────
class TranslationContext(BaseModel):
    grade: Optional[int] = None
    subject: Optional[str] = None
    topic: Optional[str] = None


def _parse_context_string(raw: str) -> Optional[Dict[str, Any]]:
    """Parse a freeform context string like 'grade_2_mathematics' into a dict.

    Supported formats:
      grade_2_mathematics        -> {grade: 2, subject: mathematics}
      grade_2_math_numbers       -> {grade: 2, subject: mathematics, topic: numbers}
      mathematics                -> {subject: mathematics}
      numbers                    -> {topic: numbers}
      (empty string)             -> None
    """
    if not raw or not raw.strip():
        return None

    raw = raw.strip().lower()
    result: Dict[str, Any] = {}

    # Extract grade: look for "grade_N" or just a leading number
    grade_match = re.search(r'grade[_\s]*(\d+)', raw)
    if grade_match:
        result["grade"] = int(grade_match.group(1))

    # Known subject keywords (order matters – try longest first)
    SUBJECT_KEYWORDS = [
        "mathematics", "maths", "math",
        "language", "reading", "writing",
        "science", "classroom", "general",
    ]
    for subj in SUBJECT_KEYWORDS:
        if subj in raw:
            result["subject"] = subj
            break

    # Known topic keywords
    TOPIC_KEYWORDS = [
        "numbers", "counting", "addition", "subtraction",
        "multiplication", "division", "shapes", "patterns",
        "letters", "words", "reading", "writing",
    ]
    for topic in TOPIC_KEYWORDS:
        if topic in raw:
            result["topic"] = topic
            break

    return result if result else None


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000,
                       description="Text to translate")
    source_language: str = Field(default="hi",
                                description="Source language code (hi or sat)")
    target_language: str = Field(default="sat",
                                description="Target language code (hi or sat)")
    context: Optional[Union[TranslationContext, str, Dict[str, Any]]] = Field(
        default=None,
        description=(
            "Educational context. Accepts a structured object "
            '{"grade": 2, "subject": "mathematics", "topic": "numbers"}, '
            "or a freeform string like \"grade_2_mathematics\". "
            "Structured format is preferred."
        )
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_context(cls, values: Any) -> Any:
        """Allow context to be a string, dict, or TranslationContext."""
        if isinstance(values, dict) and "context" in values:
            ctx = values["context"]
            if isinstance(ctx, str):
                parsed = _parse_context_string(ctx)
                values["context"] = parsed  # will become dict -> TranslationContext
            # dict values pass through and Pydantic coerces them to TranslationContext
        return values


class TranslationResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


# ─── Speech ────────────────────────────────────────────
class SpeechTranslateRequest(BaseModel):
    source_language: str = "hi"
    target_language: str = "sat"
    grade: Optional[int] = None
    subject: Optional[str] = None
    topic: Optional[str] = None


class SpeechTranslateResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


# ─── Classroom ─────────────────────────────────────────
class ClassroomTranslateRequest(BaseModel):
    session_id: Optional[str] = None
    text: str = Field(..., min_length=1, max_length=5000)
    grade: Optional[int] = None
    subject: Optional[str] = None


class ClassroomPhrase(BaseModel):
    hindi: str
    santhali: str
    english: str
    audio_url: Optional[str] = None
    confidence: float = 0.98


# ─── Copilot ───────────────────────────────────────────
class LessonGenerateRequest(BaseModel):
    grade: int = Field(default=2, ge=1, le=5)
    subject: str = Field(default="Mathematics")
    topic: str = Field(default="Numbers 1-20")
    learning_outcome: Optional[str] = None
    language: str = Field(default="sat")


class LessonPlanResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


# ─── Worksheet ─────────────────────────────────────────
class WorksheetGenerateRequest(BaseModel):
    grade: int = Field(default=2, ge=1, le=5)
    subject: str = Field(default="Mathematics")
    topic: str = Field(default="Counting")
    question_count: int = Field(default=10, ge=1, le=50)
    language: str = Field(default="sat")


class WorksheetQuestionResponse(BaseModel):
    question_number: int
    question_type: str
    hindi: str
    santhali: str
    options: Optional[List[str]] = None
    answer: str


# ─── Flashcard ─────────────────────────────────────────
class FlashcardGenerateRequest(BaseModel):
    category: str = Field(default="Animals")
    count: int = Field(default=6, ge=1, le=20)
    grade: int = Field(default=1)
    language: str = "sat"


class FlashcardResponse(BaseModel):
    id: str
    image_url: Optional[str] = None
    hindi: str
    santhali: str
    audio_url: Optional[str] = None
    pronunciation: Optional[str] = None
    category: str


# ─── Assessment ────────────────────────────────────────
class AssessmentGenerateRequest(BaseModel):
    student_id: Optional[str] = None
    subject: str = "Mathematics"
    topic: str = "Numbers"
    grade: int = Field(default=2, ge=1, le=5)
    question_count: int = Field(default=10, ge=1, le=30)
    language: str = "sat"


class AssessmentSubmitRequest(BaseModel):
    assessment_id: str
    answers: List[Dict[str, str]]  # [{"question_id": "...", "answer": "..."}]


class AssessmentSubmitResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


# ─── Student ───────────────────────────────────────────
class StudentResponse(BaseModel):
    id: str
    name: str
    grade: int
    school: Optional[str] = None
    preferred_language: str = "sat"
    created_at: Optional[datetime] = None


class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    grade: int = Field(default=1, ge=1, le=5)
    school: Optional[str] = None


class ProgressResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]


# ─── Validation ────────────────────────────────────────
class ValidationSubmitRequest(BaseModel):
    hindi: str
    ai_translation: str
    corrected_translation: Optional[str] = None
    confidence: float = 0.0
    notes: Optional[str] = None


class ValidationResponse(BaseModel):
    id: str
    hindi: str
    ai_translation: str
    corrected_translation: Optional[str] = None
    confidence: float
    status: str
    validator_id: Optional[str] = None
    created_at: Optional[datetime] = None


# ─── Language Learning ────────────────────────────────
class PracticeRequest(BaseModel):
    phrase_id: str
    user_answer: str


class LanguageLearningPhrase(BaseModel):
    id: str
    hindi: str
    santhali: str
    english: str
    pronunciation: Optional[str] = None
    audio_url: Optional[str] = None


# ─── Offline ───────────────────────────────────────────
class SyncRequest(BaseModel):
    device_id: Optional[str] = None
    classroom_conversations: Optional[List[Dict[str, Any]]] = None
    corrections: Optional[List[Dict[str, Any]]] = None
    assessment_results: Optional[List[Dict[str, Any]]] = None
    student_progress: Optional[List[Dict[str, Any]]] = None


class SyncManifest(BaseModel):
    version: str
    timestamp: str
    checksum: str
    sync_id: str
    language_pack: Dict[str, Any]
    content_packs: List[Dict[str, Any]]


# ─── Generic ───────────────────────────────────────────
class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None


class DashboardResponse(BaseModel):
    success: bool = True
    data: Dict[str, Any]
