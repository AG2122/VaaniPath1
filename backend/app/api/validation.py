"""VaniPath - Community Validation API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas import ValidationSubmitRequest, SuccessResponse
from app.services.validation_service import validation_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/validation", tags=["Community Validation"])


@router.get("/pending", tags=["Validation"],
            summary="Get pending validations",
            description="Get all translations pending community validation.")
def get_pending_validations():
    items = validation_service.get_pending()
    return {
        "success": True,
        "data": {
            "items": items,
            "count": len(items),
        },
    }


@router.post("/submit", tags=["Validation"],
             summary="Submit for validation",
             description="Submit a translation to the community validation queue.")
def submit_for_validation(data: ValidationSubmitRequest):
    item = validation_service.submit(
        hindi=data.hindi,
        ai_translation=data.ai_translation,
        confidence=data.confidence,
        notes=data.notes,
    )

    return {
        "success": True,
        "data": item,
    }


@router.put("/{item_id}", tags=["Validation"],
            summary="Update validation item",
            description="Edit a validation item with a corrected translation.")
def update_validation(item_id: str, corrected_translation: str, notes: str = ""):
    item = validation_service.edit(
        item_id=item_id,
        corrected_translation=corrected_translation,
    )

    if not item:
        return SuccessResponse(success=False, message="Validation item not found")

    return {
        "success": True,
        "data": item,
    }


@router.post("/{item_id}/approve", tags=["Validation"],
             summary="Approve validation",
             description="Approve a validated translation.")
def approve_validation(item_id: str):
    item = validation_service.approve(item_id)
    if not item:
        return SuccessResponse(success=False, message="Validation item not found")

    return {
        "success": True,
        "data": item,
    }


@router.post("/{item_id}/reject", tags=["Validation"],
             summary="Reject validation",
             description="Reject a validation item.")
def reject_validation(item_id: str, notes: str = ""):
    item = validation_service.reject(item_id, notes=notes)
    if not item:
        return SuccessResponse(success=False, message="Validation item not found")

    return {
        "success": True,
        "data": item,
    }


@router.get("/", tags=["Validation"],
            summary="Get all validation items",
            description="Get all validation items regardless of status.")
def get_all_validations():
    items = validation_service.get_all()
    return {
        "success": True,
        "data": {
            "items": items,
            "count": len(items),
        },
    }
