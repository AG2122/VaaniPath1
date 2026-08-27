"""VaniPath Backend - Main Application

AI-assisted real-time translation and curriculum-generation platform
for mother-tongue-based primary education.

Hindi ↔ Santhali translation prototype for SIH26042.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time
import os

from app.config import settings
from app.database.database import create_tables
from app.ai.santhali_translation import translation_engine

# Import all API routers
from app.api.auth import router as auth_router
from app.api.translation import router as translation_router
from app.api.speech import router as speech_router
from app.api.classroom import router as classroom_router
from app.api.copilot import router as copilot_router
from app.api.worksheets import router as worksheets_router
from app.api.flashcards import router as flashcards_router
from app.api.assessment import router as assessment_router
from app.api.students import router as students_router
from app.api.validation import router as validation_router
from app.api.language_learning import router as language_learning_router
from app.api.offline import router as offline_router
from app.api.dashboard import router as dashboard_router


app = FastAPI(
    title="VaniPath API",
    description=(
        "AI-assisted real-time translation and curriculum-generation platform "
        "for mother-tongue-based primary education.\n\n"
        "**Hindi ↔ Santhali** translation prototype.\n\n"
        "Problem Statement: SIH26042 - Real-Time Translation Tool for "
        "Mother Tongue-Based Primary Education\n\n"
        "Target: Hindi-speaking teachers teaching primary-school students who speak Santhali."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
        },
    )


# Register all routers
app.include_router(auth_router)
app.include_router(translation_router)
app.include_router(speech_router)
app.include_router(classroom_router)
app.include_router(copilot_router)
app.include_router(worksheets_router)
app.include_router(flashcards_router)
app.include_router(assessment_router)
app.include_router(students_router)
app.include_router(validation_router)
app.include_router(language_learning_router)
app.include_router(offline_router)
app.include_router(dashboard_router)


# Health check
@app.get("/", tags=["Health"])
def root():
    """Root endpoint - API health check."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "translation": "Hindi ↔ Santhali",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "translation_engine": translation_engine.get_stats() if translation_engine._loaded else "not_loaded",
    }


@app.get("/api/info", tags=["Health"],
         summary="API information",
         description="Get API version and available endpoints.")
def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "supported_languages": {
            "hi": {"name": "Hindi", "native_name": "हिन्दी"},
            "sat": {"name": "Santhali", "native_name": "ᱥᱟᱱᱛᱟᱲᱤ", "enabled": True},
        },
        "endpoints": {
            "auth": "/api/auth",
            "translation": "/api/translation",
            "speech": "/api/speech",
            "classroom": "/api/classroom",
            "copilot": "/api/copilot",
            "worksheets": "/api/worksheets",
            "flashcards": "/api/flashcards",
            "assessment": "/api/assessment",
            "students": "/api/students",
            "validation": "/api/validation",
            "language_learning": "/api/language-learning",
            "offline": "/api/offline",
            "dashboard": "/api/dashboard",
        },
    }


# Cache popular endpoint
@app.get("/api/cache/popular", tags=["Cache"],
         summary="Get popular cached translations",
         description="Get most frequently used translations from cache.")
def get_popular_cache():
    from app.utils.cache import translation_cache
    items = translation_cache.get_popular(limit=20)
    return {
        "success": True,
        "data": {
            "items": items,
            "cache_size": translation_cache.size,
        },
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    # Create database tables
    create_tables()

    # Load translation engine data
    translation_engine.load_data()

    # Ensure audio directory exists
    os.makedirs(settings.AUDIO_CACHE_DIR, exist_ok=True)

    print(f"[START] {settings.APP_NAME} v{settings.APP_VERSION} started")
    print(f"[INFO] Translation engine: {translation_engine.get_stats()}")
    print(f"[INFO] API docs: http://localhost:{settings.PORT}/docs")
