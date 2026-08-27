"""VaniPath - Database Seed Script

Run with: python -m app.database.seed

Seeds:
- Demo Teacher
- Demo Student
- Hindi and Santhali language config
- Santhali vocabulary
- FLN terms
- Classroom phrases
- Sample translations
- Grade 1 and 2 curriculum
- Sample lessons, worksheets, flashcards, assessments
- Student progress
- Validated translations
"""
import json
import os
import sys
import uuid

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.database import SessionLocal, create_tables
from app.utils.security import hash_password, generate_id
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.translation import Translation, TranslationFeedback
from app.models.classroom import ClassroomSession, ClassroomMessage
from app.models.lesson import Lesson
from app.models.worksheet import Worksheet, WorksheetQuestion
from app.models.flashcard import Flashcard
from app.models.assessment import Assessment, AssessmentQuestion, StudentProgress
from app.models.validation import ValidationItem, Recommendation
from app.models.language_pack import SanthaliVocabulary, SanthaliPhrase, AudioCache
from app.ai.santhali_translation import translation_engine
from datetime import datetime, timezone


def seed():
    """Seed the database with demo data."""
    print("[SEED] Seeding VaniPath database...")

    # Create tables
    create_tables()

    db = SessionLocal()

    try:
        # ─── Users ───────────────────────────────────────
        teacher_id = generate_id()
        teacher = User(
            id=teacher_id,
            name="Priya Kumari",
            email="teacher@vanipath.in",
            mobile="9876543210",
            password_hash=hash_password("teacher123"),
            role=UserRole.TEACHER.value,
            school="Primary School, Jharkhand",
            preferred_language="hi",
            target_language="sat",
        )
        db.add(teacher)

        validator_id = generate_id()
        validator = User(
            id=validator_id,
            name="Santhali Validator",
            email="validator@vanipath.in",
            password_hash=hash_password("validator123"),
            role=UserRole.VALIDATOR.value,
            school="Community Center",
        )
        db.add(validator)

        admin_id = generate_id()
        admin = User(
            id=admin_id,
            name="Admin",
            email="admin@vanipath.in",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN.value,
        )
        db.add(admin)
        db.commit()

        print("  [OK] Users created (teacher@vanipath.in / teacher123)")

        # ─── Students ────────────────────────────────────
        students = []
        student_data = [
            ("Lakha Hansda", 2, "Primary School, Jharkhand"),
            ("Sita Murmu", 2, "Primary School, Jharkhand"),
            ("Ravi Oraon", 1, "Primary School, Jharkhand"),
            ("Gita Tudu", 2, "Primary School, Jharkhand"),
            ("Mangal Hembram", 1, "Primary School, Jharkhand"),
        ]

        for name, grade, school in student_data:
            student = Student(
                id=generate_id(),
                name=name,
                grade=grade,
                school=school,
                preferred_language="sat",
                target_language="hi",
                teacher_id=teacher_id,
            )
            db.add(student)
            students.append(student)

        db.commit()
        print(f"  [OK] {len(students)} students created")

        # ─── Translations ────────────────────────────────
        translations_data = [
            ("बच्चों, आज हम संख्याओं के बारे में सीखेंगे।", "ᱡᱟᱨᱤᱚᱜ, ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱥᱟᱱᱛᱟᱲᱤ ᱨᱚᱨᱚᱜ ᱵᱟᱝᱨᱚᱢ ᱢᱮ।", 0.96, "mathematics", 2, "numbers"),
            ("अपनी किताब खोलो", "ᱠᱚᱨᱚᱜ ᱠᱤᱛᱟᱜ ᱫᱩᱴᱷᱤᱣᱮ ᱢᱮ", 0.98, None, None, None),
            ("ध्यान से सुनो", "ᱱᱤᱨᱚᱜ ᱥᱟᱛᱟᱨᱚᱜ ᱥᱩᱱᱮ ᱢᱮ", 0.98, None, None, None),
            ("कौन जवाब जानता है?", "ᱠᱩᱱᱚ ᱟᱛᱟᱨᱚᱜ ᱫᱩᱴᱷᱤᱣᱮ ᱠᱚᱱᱚᱜ?", 0.96, None, None, None),
            ("बहुत अच्छा!", "ᱜᱚᱨᱚ ᱥᱟᱢᱚᱜ!", 0.98, None, None, None),
            ("5 + 3 = ?", "5 + 3 = ?", 0.95, "mathematics", 2, "addition"),
            ("पेड़ पर कितने पक्षी बैठे हैं?", "ᱢᱟᱝᱣᱟ ᱠᱚᱨᱚᱜ ᱠᱟᱹᱨᱚᱨᱮ ᱵᱤᱡᱚᱨᱮ ᱥᱟᱲᱮ?", 0.94, "mathematics", 2, "counting"),
            ("गोल आकार कौन सा है?", "ᱜᱩᱨᱳ ᱵᱤᱥᱩᱨᱤ ᱠᱟᱹᱨᱚᱨᱮ?", 0.93, "mathematics", 2, "shapes"),
        ]

        for source, target, conf, subj, grade, topic in translations_data:
            t = Translation(
                id=generate_id(),
                source_text=source,
                translated_text=target,
                source_language="hi",
                target_language="sat",
                confidence=conf,
                context_subject=subj,
                context_grade=grade,
                context_topic=topic,
                processing_time_ms=800,
                requires_validation=conf < 0.70,
                user_id=teacher_id,
            )
            db.add(t)

        db.commit()
        print(f"  [OK] {len(translations_data)} translations created")

        # ─── Lessons ─────────────────────────────────────
        lesson = Lesson(
            id=generate_id(),
            title="Numbers 1-20 - Grade 2",
            description="Learn to count and write numbers 1 to 20 in Hindi and Santhali",
            grade=2,
            subject="Mathematics",
            topic="Numbers 1-20",
            learning_outcome="Students will be able to identify, count, and write numbers 1-20 in both Hindi and Santhali.",
            content=json.dumps({
                "objective": "Students will be able to identify, count, and write numbers 1-20.",
                "explanation": {
                    "hindi": "आज हम संख्याओं 1 से 20 तक सीखेंगे।",
                    "santhali": "ᱮᱢᱟᱡᱮ ᱫᱟᱨᱤ ᱥᱟᱱᱛᱟᱲᱤ 1 ᱠᱚᱨᱟ 20 ᱦᱟᱨᱮ ᱵᱟᱝᱨᱚᱢ ᱢᱮ।"
                },
                "activity": {
                    "hindi": "छात्रों से पेड़ से गिनती के लिए पत्थर लाने को कहें।",
                    "santhali": "ᱡᱟᱨᱤᱚᱜ ᱠᱚᱥᱟᱨᱚᱜ ᱫᱟᱨᱤ ᱜᱤᱱᱚᱨᱮ ᱠᱟᱱᱟᱢᱚᱜ ᱵᱟᱝᱨᱚᱢ।"
                }
            }),
            language="sat",
            teacher_id=teacher_id,
            is_published=True,
        )
        db.add(lesson)

        lesson2 = Lesson(
            id=generate_id(),
            title="Shapes - Grade 2",
            description="Learn basic shapes in Hindi and Santhali",
            grade=2,
            subject="Mathematics",
            topic="Shapes",
            learning_outcome="Students can identify and name basic shapes.",
            language="sat",
            teacher_id=teacher_id,
            is_published=True,
        )
        db.add(lesson2)
        db.commit()
        print("  [OK] Lessons created")

        # ─── Flashcards ──────────────────────────────────
        flashcards_data = [
            ("Animals", "बाघ", "ᱵᱟᱜᱚᱨ", "bagor"),
            ("Animals", "हाथी", "ᱦᱟᱛᱤ", "hati"),
            ("Animals", "मोर", "ᱢᱚᱨᱚᱜ", "morog"),
            ("Animals", "गाय", "ᱜᱟᱭ", "gai"),
            ("Animals", "कुत्ता", "ᱠᱩᱛᱷᱟ", "kuththa"),
            ("Animals", "मुर्गी", "ᱪᱩᱨᱤ", "churi"),
            ("Numbers", "एक", "ᱤᱧ", "ik"),
            ("Numbers", "दो", "ᱰᱩ", "du"),
            ("Numbers", "तीन", "ᱛᱤᱱᱟ", "tina"),
            ("Numbers", "चार", "ᱪᱟᱨᱮᱭ", "charoi"),
            ("Numbers", "पाँच", "ᱰᱩᱛᱤ", "dutte"),
            ("Colors", "लाल", "ᱞᱟᱞ", "lal"),
            ("Colors", "नीला", "ᱱᱤᱞᱚᱨ", "nilor"),
            ("Colors", "हरा", "ᱦᱟᱨᱚ", "harao"),
            ("Family", "माँ", "ᱤᱟᱦᱟ", "iya-ha"),
            ("Family", "पिता", "ᱥᱚᱨᱚᱜ", "sorog"),
            ("Food", "चावल", "ᱥᱟᱝᱚᱛ", "sangoth"),
            ("Food", "रोटी", "ᱪᱩᱨᱤ", "churi"),
            ("Nature", "पेड़", "ᱢᱟᱝᱣᱟ", "mangva"),
            ("Nature", "फूल", "ᱢᱩᱨᱩ", "muru"),
            ("School", "किताब", "ᱠᱤᱛᱟᱜ", "kithag"),
            ("School", "कलम", "ᱠᱟᱞᱟᱢ", "kalom"),
        ]

        for cat, hindi, santhali, phonetic in flashcards_data:
            f = Flashcard(
                id=generate_id(),
                category=cat,
                hindi=hindi,
                santhali=santhali,
                pronunciation=phonetic,
                image_url=f"/images/{cat.lower()}/{hindi}.png",
                audio_url=f"/audio/sat_{santhali}.wav",
                grade=2,
            )
            db.add(f)

        db.commit()
        print(f"  [OK] {len(flashcards_data)} flashcards created")

        # ─── Assessment ──────────────────────────────────
        for student in students[:3]:
            assessment = Assessment(
                id=generate_id(),
                student_id=student.id,
                subject="Mathematics",
                topic="Numbers 1-20",
                grade=student.grade,
                total_questions=5,
                score=80.0,
                correct_answers=4,
                wrong_answers=1,
                weak_topics=json.dumps([{"topic": "Subtraction", "score": 60.0}]),
                strong_topics=json.dumps([{"topic": "Counting", "score": 100.0}, {"topic": "Addition", "score": 100.0}]),
                status="completed",
                completed_at=datetime.now(timezone.utc),
            )
            db.add(assessment)

            progress = StudentProgress(
                id=generate_id(),
                student_id=student.id,
                assessment_id=assessment.id,
                lessons_completed=3,
                assessments_completed=1,
                average_score=80.0,
                learning_streak=1,
                strong_topics=json.dumps([{"topic": "Counting", "score": 100.0}]),
                weak_topics=json.dumps([{"topic": "Subtraction", "score": 60.0}]),
                badges=json.dumps(["First Assessment", "Numbers Master"]),
            )
            db.add(progress)

        db.commit()
        print("  [OK] Assessments and student progress created")

        # ─── Validation Queue ────────────────────────────
        val_items = [
            ("पेड़ पर दो पक्षी हैं", "ᱢᱟᱝᱣᱟ ᱠᱚᱨᱚᱜ ᱰᱩ ᱵᱤᱡᱚᱨᱮ ᱥᱟᱲᱮ", 0.92),
            ("नदी में मछली है", "ᱫᱤᱰᱤ ᱡᱚᱨᱚᱜ ᱥᱟᱢᱟ ᱥᱟᱲᱮ", 0.88),
        ]

        for hindi, ai_trans, conf in val_items:
            v = ValidationItem(
                id=generate_id(),
                hindi=hindi,
                ai_translation=ai_trans,
                confidence=conf,
                status="pending",
                validator_id=None,
            )
            db.add(v)

        # Approved validation
        approved = ValidationItem(
            id=generate_id(),
            hindi="अपनी किताब खोलो",
            ai_translation="ᱠᱚᱨᱚᱜ ᱠᱤᱛᱟᱜ ᱫᱩᱴᱷᱤᱣᱮ ᱢᱮ",
            corrected_translation="ᱠᱚᱨᱚᱜ ᱠᱤᱛᱟᱜ ᱫᱩᱴᱷᱤᱣᱮ ᱢᱮ",
            confidence=0.98,
            status="approved",
            validator_id=validator_id,
        )
        db.add(approved)
        db.commit()
        print("  [OK] Validation queue populated")

        # ─── Load translation engine ─────────────────────
        translation_engine.load_data()
        print(f"  [OK] Translation engine loaded: {translation_engine.get_stats()}")

        print("\n[SEED] Seed completed successfully!")
        print("\nDemo credentials:")
        print("   Teacher:  teacher@vanipath.in / teacher123")
        print("   Validator: validator@vanipath.in / validator123")
        print("   Admin:    admin@vanipath.in / admin123")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
