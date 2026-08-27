"""VaniPath - Offline-First Service

Provides language packs, content packs, and synchronization
for schools with poor or no internet connectivity.
"""
import uuid
import hashlib
import json
from typing import Dict, List, Optional
from datetime import datetime, timezone

from app.services.flashcard_service import flashcard_service
from app.services.worksheet_service import worksheet_service
from app.services.copilot_service import copilot_service


class OfflineService:
    """Offline-first service for sync and content distribution."""

    def get_sync_manifest(self) -> Dict:
        """Get the current sync manifest with version info."""
        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "sync_id": str(uuid.uuid4()),
            "version": "1.0.0",
            "timestamp": timestamp,
            "checksum": hashlib.md5(timestamp.encode()).hexdigest(),
            "language_pack": {
                "version": "1.0.0",
                "language": "sat",
                "available": True,
            },
            "content_packs": [
                {"type": "curriculum", "grade": 1, "version": "1.0.0"},
                {"type": "curriculum", "grade": 2, "version": "1.0.0"},
                {"type": "flashcards", "version": "1.0.0"},
                {"type": "worksheets", "version": "1.0.0"},
            ],
        }

    def get_language_pack(self) -> Dict:
        """Get the complete Santhali language pack for offline use."""
        # Load vocabulary
        import os
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data", "languages", "santhali")

        vocabulary = []
        fln_terms = {}
        phrases = []

        vocab_path = os.path.join(data_dir, "vocabulary.json")
        if os.path.exists(vocab_path):
            with open(vocab_path, "r", encoding="utf-8") as f:
                vocabulary = json.load(f)

        fln_path = os.path.join(data_dir, "fln_terms.json")
        if os.path.exists(fln_path):
            with open(fln_path, "r", encoding="utf-8") as f:
                fln_terms = json.load(f)

        phrases_path = os.path.join(data_dir, "classroom_phrases.json")
        if os.path.exists(phrases_path):
            with open(phrases_path, "r", encoding="utf-8") as f:
                phrases = json.load(f)

        return {
            "version": "1.0.0",
            "language_code": "sat",
            "language_name": "Santhali",
            "native_name": "ᱥᱟᱱᱛᱟᱲᱤ",
            "vocabulary": vocabulary,
            "fln_terms": fln_terms,
            "classroom_phrases": phrases,
            "checksum": hashlib.md5(json.dumps(vocabulary).encode()).hexdigest(),
        }

    def get_content_pack(self, content_type: str = "all", grade: Optional[int] = None) -> Dict:
        """Get content packs for offline use."""
        pack = {
            "version": "1.0.0",
            "content_type": content_type,
            "grade": grade,
            "items": {},
        }

        if content_type in ("flashcards", "all"):
            categories = flashcard_service.get_categories()
            flashcards = {}
            for cat in categories:
                flashcards[cat["id"]] = flashcard_service.generate(cat["id"], count=cat["count"])
            pack["items"]["flashcards"] = flashcards

        if content_type in ("worksheets", "all"):
            # Generate sample worksheets
            worksheets = []
            for subj in ["Mathematics", "Language"]:
                for topic in ["Counting", "Numbers 1-20", "Addition", "Subtraction"]:
                    ws = worksheet_service.generate(grade or 2, subj, topic, question_count=5)
                    worksheets.append(ws)
            pack["items"]["worksheets"] = worksheets

        if content_type in ("curriculum", "all"):
            topics = ["Numbers 1-20", "Counting", "Addition", "Subtraction", "Shapes", "Letters", "Reading"]
            lessons = []
            for topic in topics:
                lesson = copilot_service.generate_lesson(
                    grade=grade or 2,
                    subject="Mathematics" if topic in ["Numbers 1-20", "Counting", "Addition", "Subtraction", "Shapes"] else "Language",
                    topic=topic,
                )
                lessons.append(lesson)
            pack["items"]["curriculum"] = lessons

        return pack

    def sync(self, device_id: Optional[str], classroom_conversations: Optional[List] = None,
             corrections: Optional[List] = None, assessment_results: Optional[List] = None,
             student_progress: Optional[List] = None) -> Dict:
        """Process an offline sync request.

        Uploads client data and returns updated content.
        """
        uploaded = {
            "classroom_conversations": len(classroom_conversations or []),
            "corrections": len(corrections or []),
            "assessment_results": len(assessment_results or []),
            "student_progress": len(student_progress or []),
        }

        # Process corrections
        if corrections:
            from app.ai.santhali_translation import translation_engine
            for correction in corrections:
                if "hindi" in correction and "corrected" in correction:
                    translation_engine.add_correction(correction["hindi"], correction["corrected"])

        # Return updated content
        updated_content = {
            "language_pack": self.get_language_pack(),
            "validated_translations": [],  # Would contain newly validated translations
            "new_content": self.get_content_pack("all"),
        }

        return {
            "sync_id": str(uuid.uuid4()),
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uploaded": uploaded,
            "updated_content": updated_content,
        }


# Global instance
offline_service = OfflineService()
