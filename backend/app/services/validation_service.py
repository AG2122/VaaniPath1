"""VaniPath - Community Validation Service"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timezone


class ValidationService:
    """Community validation service for translation quality control."""

    def __init__(self):
        self._validation_queue: List[Dict] = []

    def get_pending(self) -> List[Dict]:
        """Get all pending validation items."""
        return [v for v in self._validation_queue if v["status"] == "pending"]

    def submit(self, hindi: str, ai_translation: str, confidence: float = 0.0,
               notes: Optional[str] = None, validator_id: Optional[str] = None) -> Dict:
        """Submit a new validation item."""
        item = {
            "id": str(uuid.uuid4()),
            "hindi": hindi,
            "ai_translation": ai_translation,
            "corrected_translation": None,
            "confidence": confidence,
            "status": "pending",
            "validator_id": validator_id,
            "notes": notes,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._validation_queue.append(item)
        return item

    def approve(self, item_id: str, validator_id: Optional[str] = None) -> Optional[Dict]:
        """Approve a validation item."""
        for item in self._validation_queue:
            if item["id"] == item_id:
                item["status"] = "approved"
                item["validator_id"] = validator_id
                item["reviewed_at"] = datetime.now(timezone.utc).isoformat()

                # Add to the translation engine's corrections
                from app.ai.santhali_translation import translation_engine
                translation_engine.add_correction(item["hindi"], item["ai_translation"])

                return item
        return None

    def reject(self, item_id: str, validator_id: Optional[str] = None,
               notes: Optional[str] = None) -> Optional[Dict]:
        """Reject a validation item."""
        for item in self._validation_queue:
            if item["id"] == item_id:
                item["status"] = "rejected"
                item["validator_id"] = validator_id
                item["notes"] = notes
                item["reviewed_at"] = datetime.now(timezone.utc).isoformat()
                return item
        return None

    def edit(self, item_id: str, corrected_translation: str,
             validator_id: Optional[str] = None) -> Optional[Dict]:
        """Edit a validation item with a corrected translation."""
        for item in self._validation_queue:
            if item["id"] == item_id:
                item["corrected_translation"] = corrected_translation
                item["status"] = "approved"
                item["validator_id"] = validator_id
                item["reviewed_at"] = datetime.now(timezone.utc).isoformat()

                # Add the correction to the translation engine
                from app.ai.santhali_translation import translation_engine
                translation_engine.add_correction(item["hindi"], corrected_translation)

                return item
        return None

    def get_all(self) -> List[Dict]:
        """Get all validation items."""
        return self._validation_queue

    def get_by_id(self, item_id: str) -> Optional[Dict]:
        """Get a specific validation item."""
        for item in self._validation_queue:
            if item["id"] == item_id:
                return item
        return None


# Global instance
validation_service = ValidationService()
