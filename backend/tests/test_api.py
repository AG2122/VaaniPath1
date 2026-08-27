"""VaniPath - Integration Tests

Tests for: Auth, Translation, Speech, Classroom, Copilot,
Worksheets, Flashcards, Assessment, Validation, Offline.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app
from app.database.database import create_tables, engine, Base
from app.database.seed import seed
from app.utils.cache import translation_cache

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Create fresh database and seed before tests."""
    Base.metadata.drop_all(bind=engine)
    create_tables()
    seed()
    yield
    Base.metadata.drop_all(bind=engine)


# ─── Health Check ──────────────────────────────────────
class TestHealth:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "VaniPath"
        assert data["translation"] == "Hindi ↔ Santhali"

    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_api_info(self):
        response = client.get("/api/info")
        assert response.status_code == 200
        data = response.json()
        assert "hi" in data["supported_languages"]
        assert "sat" in data["supported_languages"]
        # Verify Ho and Mundari are NOT present
        assert "Ho" not in str(data)
        assert "Mundari" not in str(data)


# ─── Authentication ────────────────────────────────────
class TestAuth:
    def test_register(self):
        response = client.post("/api/auth/register", json={
            "name": "Test Teacher",
            "email": "test@vanipath.in",
            "password": "test123",
            "role": "teacher",
            "school": "Test School",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["name"] == "Test Teacher"

    def test_register_duplicate(self):
        response = client.post("/api/auth/register", json={
            "name": "Duplicate",
            "email": "teacher@vanipath.in",
            "password": "test123",
            "role": "teacher",
        })
        assert response.status_code == 400

    def test_login(self):
        response = client.post("/api/auth/login", json={
            "email": "teacher@vanipath.in",
            "password": "teacher123",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self):
        response = client.post("/api/auth/login", json={
            "email": "teacher@vanipath.in",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_get_me(self):
        login_resp = client.post("/api/auth/login", json={
            "email": "teacher@vanipath.in",
            "password": "teacher123",
        })
        token = login_resp.json()["access_token"]
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        assert response.json()["email"] == "teacher@vanipath.in"


# ─── Translation ───────────────────────────────────────
class TestTranslation:
    def test_hi_to_sat(self):
        response = client.post("/api/translation/text", json={
            "text": "अपनी किताब खोलो",
            "source_language": "hi",
            "target_language": "sat",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "translated_text" in data["data"]
        assert data["data"]["source_language"] == "hi"
        assert data["data"]["target_language"] == "sat"
        assert data["data"]["confidence"] > 0
        assert data["data"]["processing_time_ms"] >= 0

    def test_sat_to_hi(self):
        response = client.post("/api/translation/text", json={
            "text": "ᱡᱚᱨᱟ",
            "source_language": "sat",
            "target_language": "hi",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "translated_text" in data["data"]

    def test_translation_with_context(self):
        response = client.post("/api/translation/text", json={
            "text": "बच्चों, आज हम संख्याओं के बारे में सीखेंगे।",
            "source_language": "hi",
            "target_language": "sat",
            "context": {
                "grade": 2,
                "subject": "mathematics",
                "topic": "numbers",
            },
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["confidence"] > 0

    def test_invalid_language(self):
        response = client.post("/api/translation/text", json={
            "text": "Hello",
            "source_language": "en",
            "target_language": "sat",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False

    def test_same_language(self):
        response = client.post("/api/translation/text", json={
            "text": "Hello",
            "source_language": "hi",
            "target_language": "hi",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False


# ─── Speech Translation ────────────────────────────────
class TestSpeech:
    def test_stt(self):
        import io
        wav_data = b'\x00' * 1000
        response = client.post("/api/speech/stt",
            files={"audio": ("test.wav", io.BytesIO(wav_data), "audio/wav")},
            data={"language": "hi"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_tts(self):
        response = client.post("/api/speech/tts",
            data={"text": "Hello", "language": "sat"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_speech_translate(self):
        import io
        wav_data = b'\x00' * 1000
        response = client.post("/api/speech/translate",
            files={"audio": ("test.wav", io.BytesIO(wav_data), "audio/wav")},
            data={
                "source_language": "hi",
                "target_language": "sat",
                "grade": "2",
                "subject": "mathematics",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "source_text" in data["data"]
        assert "translated_text" in data["data"]
        assert "audio_url" in data["data"]


# ─── Classroom ─────────────────────────────────────────
class TestClassroom:
    def test_teacher_to_student(self):
        response = client.post("/api/classroom/teacher-to-student", json={
            "text": "अपनी किताब खोलो",
            "grade": 2,
            "subject": "Mathematics",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "translated_text" in data["data"]
        assert "session_id" in data["data"]

    def test_student_to_teacher(self):
        response = client.post("/api/classroom/student-to-teacher", json={
            "text": "ᱡᱚᱨᱟ",
            "grade": 2,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "translated_text" in data["data"]

    def test_classroom_phrases(self):
        response = client.get("/api/classroom/phrases")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] > 0
        phrase = data["data"]["phrases"][0]
        assert "hindi" in phrase
        assert "santhali" in phrase
        # Verify no Ho or Mundari language references
        for p in data["data"]["phrases"]:
            assert "munda" not in str(p).lower()
            assert "mundari" not in str(p).lower()

    def test_session_history(self):
        create_resp = client.post("/api/classroom/teacher-to-student", json={
            "text": "बच्चों, आज हम संख्याओं के बारे में सीखेंगे।",
            "grade": 2,
        })
        session_id = create_resp.json()["data"]["session_id"]
        response = client.get(f"/api/classroom/{session_id}/history")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_messages"] > 0


# ─── Copilot ───────────────────────────────────────────
class TestCopilot:
    def test_generate_lesson(self):
        response = client.post("/api/copilot/lesson", json={
            "grade": 2,
            "subject": "Mathematics",
            "topic": "Numbers 1-20",
            "language": "sat",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "objective" in data["data"]
        assert "explanation" in data["data"]
        assert "hindi" in data["data"]["explanation"]
        assert "santhali" in data["data"]["explanation"]
        assert "activity" in data["data"]
        assert "homework" in data["data"]
        # No Ho or Mundari
        assert "Ho" not in str(data["data"])
        assert "Mundari" not in str(data["data"])

    def test_generate_lesson_generic(self):
        response = client.post("/api/copilot/lesson", json={
            "grade": 2,
            "subject": "Mathematics",
            "topic": "Patterns",
            "language": "sat",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


# ─── Worksheets ────────────────────────────────────────
class TestWorksheets:
    def test_generate_worksheet(self):
        response = client.post("/api/worksheets/generate", json={
            "grade": 2,
            "subject": "Mathematics",
            "topic": "Counting",
            "question_count": 5,
            "language": "sat",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["questions"]) == 5
        q = data["data"]["questions"][0]
        assert "hindi" in q
        assert "santhali" in q
        assert "answer" in q
        assert "question_number" in q

    def test_get_worksheet(self):
        # Generate first
        gen_resp = client.post("/api/worksheets/generate", json={
            "grade": 2,
            "subject": "Mathematics",
            "topic": "Counting",
            "question_count": 3,
        })
        ws_id = gen_resp.json()["data"]["worksheet_id"]
        response = client.get(f"/api/worksheets/{ws_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["questions"]) == 3


# ─── Flashcards ────────────────────────────────────────
class TestFlashcards:
    def test_generate_flashcards(self):
        response = client.post("/api/flashcards/generate", json={
            "category": "Animals",
            "count": 4,
            "grade": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]["flashcards"]) == 4
        card = data["data"]["flashcards"][0]
        assert "hindi" in card
        assert "santhali" in card
        assert "pronunciation" in card

    def test_get_categories(self):
        response = client.get("/api/flashcards/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] > 0
        cats = [c["id"] for c in data["data"]["categories"]]
        assert "Animals" in cats
        assert "Numbers" in cats
        assert "Colors" in cats
        assert "Family" in cats
        assert "Food" in cats
        assert "Nature" in cats
        assert "School" in cats


# ─── Assessment ────────────────────────────────────────
class TestAssessment:
    def test_generate_assessment(self):
        response = client.post("/api/assessment/generate", json={
            "subject": "Mathematics",
            "topic": "Numbers 1-20",
            "grade": 2,
            "question_count": 5,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "assessment_id" in data["data"]
        assert len(data["data"]["questions"]) == 5

    def test_submit_assessment(self):
        gen_resp = client.post("/api/assessment/generate", json={
            "subject": "Mathematics",
            "topic": "Numbers 1-20",
            "grade": 2,
            "question_count": 3,
        })
        assessment_id = gen_resp.json()["data"]["assessment_id"]
        questions = gen_resp.json()["data"]["questions"]
        answers = [{"question_id": q["id"], "answer": q["correct_answer"]} for q in questions]
        response = client.post("/api/assessment/submit", json={
            "assessment_id": assessment_id,
            "answers": answers,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["score"] == 100.0
        assert data["data"]["correct_answers"] == 3


# ─── Validation ────────────────────────────────────────
class TestValidation:
    def test_submit_validation(self):
        response = client.post("/api/validation/submit", json={
            "hindi": "नदी में मछली है",
            "ai_translation": "ᱫᱤᱰᱤ ᱡᱚᱨᱚᱜ ᱥᱟᱢᱟ ᱥᱟᱲᱮ",
            "confidence": 0.88,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "pending"

    def test_get_pending(self):
        response = client.get("/api/validation/pending")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] > 0

    def test_approve_validation(self):
        submit_resp = client.post("/api/validation/submit", json={
            "hindi": "Test phrase",
            "ai_translation": "ᱱᱩᱯᱚᱨᱚ ᱝᱚᱞᱚᱨ",
            "confidence": 0.90,
        })
        item_id = submit_resp.json()["data"]["id"]
        response = client.post(f"/api/validation/{item_id}/approve")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "approved"


# ─── Offline ───────────────────────────────────────────
class TestOffline:
    def test_sync_manifest(self):
        response = client.get("/api/offline/sync-manifest")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sync_id" in data["data"]
        assert "language_pack" in data["data"]

    def test_language_pack(self):
        response = client.get("/api/offline/language-pack")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "vocabulary" in data["data"]
        assert len(data["data"]["vocabulary"]) > 0
        assert "fln_terms" in data["data"]
        assert "classroom_phrases" in data["data"]

    def test_content_pack(self):
        response = client.get("/api/offline/content-pack")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]

    def test_sync(self):
        response = client.post("/api/offline/sync", json={
            "device_id": "test-device",
            "corrections": [
                {"hindi": "test", "corrected": "ᱱᱩᱯᱚᱨᱚ"}
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "success"
        assert data["data"]["uploaded"]["corrections"] == 1


# ─── Students ──────────────────────────────────────────
class TestStudents:
    def test_create_student(self):
        response = client.post("/api/students/", json={
            "name": "New Student",
            "grade": 1,
            "school": "Test School",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_list_students(self):
        response = client.get("/api/students/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] > 0


# ─── Dashboard ─────────────────────────────────────────
class TestDashboard:
    def test_teacher_dashboard(self):
        response = client.get("/api/dashboard/teacher")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "student_count" in data["data"]
        assert "translation_count" in data["data"]
        assert "translation_confidence" in data["data"]

    def test_stats(self):
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


# ─── Cache ─────────────────────────────────────────────
class TestCache:
    def test_popular_cache(self):
        response = client.get("/api/cache/popular")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "items" in data["data"]


# ─── Language Learning ─────────────────────────────────
class TestLanguageLearning:
    def test_get_phrases(self):
        response = client.get("/api/language-learning/phrases")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["count"] > 0
        for phrase in data["data"]["phrases"]:
            assert "santhali" in phrase
            assert "hindi" in phrase

    def test_practice(self):
        response = client.post("/api/language-learning/practice", json={
            "phrase_id": "1",
            "user_answer": "ᱡᱚᱨᱟ",
        })
        assert response.status_code == 200

    def test_progress(self):
        response = client.get("/api/language-learning/progress")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
