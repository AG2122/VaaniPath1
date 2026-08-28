"""VaniPath Backend - Configuration"""
from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "VaniPath"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./vanipath.db"

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_PUBLISHABLE_KEY: str = ""
    SUPABASE_SECRET_KEY: str = ""

    @property
    def is_postgresql(self) -> bool:
        return self.DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://", "postgres://"))

    @property
    def supabase_enabled(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_SECRET_KEY)

    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Translation
    TRANSLATION_MODEL: str = "local"
    ENABLE_AI_TRANSLATION: bool = False
    AI_TRANSLATION_API_KEY: str = ""

    # Speech
    STT_PROVIDER: str = "local"
    TTS_PROVIDER: str = "local"
    AUDIO_CACHE_DIR: str = "./data/audio"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173","http://localhost:8080"]'

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_AUDIO_FORMATS: str = "wav,mp3,ogg,m4a"

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
