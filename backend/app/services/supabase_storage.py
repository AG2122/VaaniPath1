"""VaniPath - Supabase Storage Service

Handles file uploads/downloads to Supabase Storage buckets.
Falls back gracefully when Supabase is not configured.
"""
import os
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Wrapper around Supabase Storage REST API."""

    BUCKETS = {
        "audio": "vanipath-audio",
        "worksheets": "vanipath-worksheets",
        "flashcards": "vanipath-flashcards",
        "curriculum": "vanipath-curriculum",
    }

    def __init__(self):
        self._client = None

    def _get_client(self):
        """Lazy-init the Supabase Python client."""
        if self._client is not None:
            return self._client
        if not settings.supabase_enabled:
            return None
        try:
            from supabase import create_client
            self._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SECRET_KEY,
            )
            return self._client
        except ImportError:
            logger.warning("supabase package not installed; storage disabled")
            return None
        except Exception as e:
            logger.warning(f"Supabase client init failed: {e}")
            return None

    @property
    def available(self) -> bool:
        return self._get_client() is not None

    async def upload(
        self,
        bucket_type: str,
        path: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        """Upload a file to a Supabase Storage bucket.

        Returns the public URL on success, None on failure.
        """
        client = self._get_client()
        if client is None:
            logger.info(f"Storage unavailable, skipping upload: {bucket_type}/{path}")
            return None

        bucket = self.BUCKETS.get(bucket_type)
        if not bucket:
            logger.error(f"Unknown bucket type: {bucket_type}")
            return None

        try:
            client.storage.from_(bucket).upload(
                path=path,
                file=data,
                file_options={"content-type": content_type},
            )
            # Build public URL
            public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"
            return public_url
        except Exception as e:
            logger.error(f"Upload failed ({bucket}/{path}): {e}")
            return None

    async def download(
        self,
        bucket_type: str,
        path: str,
    ) -> Optional[bytes]:
        """Download a file from a Supabase Storage bucket."""
        client = self._get_client()
        if client is None:
            return None

        bucket = self.BUCKETS.get(bucket_type)
        if not bucket:
            return None

        try:
            data = client.storage.from_(bucket).download(path)
            return data
        except Exception as e:
            logger.error(f"Download failed ({bucket}/{path}): {e}")
            return None

    async def get_public_url(self, bucket_type: str, path: str) -> Optional[str]:
        """Get the public URL for a file."""
        bucket = self.BUCKETS.get(bucket_type)
        if not bucket:
            return None
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"

    async def delete(
        self,
        bucket_type: str,
        paths: list[str],
    ) -> bool:
        """Delete files from a bucket."""
        client = self._get_client()
        if client is None:
            return False

        bucket = self.BUCKETS.get(bucket_type)
        if not bucket:
            return False

        try:
            client.storage.from_(bucket).remove(paths)
            return True
        except Exception as e:
            logger.error(f"Delete failed ({bucket}): {e}")
            return False

    async def list_files(
        self,
        bucket_type: str,
        folder: str = "",
        limit: int = 100,
    ) -> list[dict]:
        """List files in a bucket folder."""
        client = self._get_client()
        if client is None:
            return []

        bucket = self.BUCKETS.get(bucket_type)
        if not bucket:
            return []

        try:
            files = client.storage.from_(bucket).list(
                path=folder,
                options={"limit": limit},
            )
            return files or []
        except Exception as e:
            logger.error(f"List failed ({bucket}/{folder}): {e}")
            return []


# Singleton
supabase_storage = SupabaseStorageService()
