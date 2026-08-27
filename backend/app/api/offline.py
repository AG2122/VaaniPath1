"""VaniPath - Offline Sync API"""
from fastapi import APIRouter
from app.schemas import SyncRequest, SuccessResponse
from app.services.offline_service import offline_service

router = APIRouter(prefix="/api/offline", tags=["Offline"])


@router.get("/sync-manifest", tags=["Offline"],
            summary="Get sync manifest",
            description="Get the current sync manifest with version info and available content packs.")
def get_sync_manifest():
    manifest = offline_service.get_sync_manifest()
    return {
        "success": True,
        "data": manifest,
    }


@router.get("/language-pack", tags=["Offline"],
            summary="Get language pack",
            description="Download the complete Santhali language pack for offline use. Includes vocabulary, FLN terms, and classroom phrases.")
def get_language_pack():
    pack = offline_service.get_language_pack()
    return {
        "success": True,
        "data": pack,
    }


@router.get("/content-pack", tags=["Offline"],
            summary="Get content pack",
            description="Download curriculum content, worksheets, and flashcards for offline use.")
def get_content_pack(content_type: str = "all", grade: int = None):
    pack = offline_service.get_content_pack(content_type, grade)
    return {
        "success": True,
        "data": pack,
    }


@router.post("/sync", tags=["Offline"],
             summary="Synchronize data",
             description="Upload offline data and receive updated content.")
def sync_data(data: SyncRequest):
    result = offline_service.sync(
        device_id=data.device_id,
        classroom_conversations=data.classroom_conversations,
        corrections=data.corrections,
        assessment_results=data.assessment_results,
        student_progress=data.student_progress,
    )
    return {
        "success": True,
        "data": result,
    }
