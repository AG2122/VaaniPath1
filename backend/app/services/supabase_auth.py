"""VaniPath - Supabase Auth Integration

Optional layer that validates Supabase JWTs alongside the existing
JWT auth system. When Supabase is not configured, everything falls
back to the built-in auth.

NEVER expose SUPABASE_SECRET_KEY through this module.
"""
import logging
from typing import Optional
from datetime import datetime, timezone

from app.config import settings
from app.database.database import SessionLocal
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def _get_supabase_client():
    """Lazy-init the Supabase Python client."""
    if not settings.supabase_enabled:
        return None
    try:
        from supabase import create_client
        return create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SECRET_KEY,
        )
    except ImportError:
        return None
    except Exception as e:
        logger.warning(f"Supabase client init failed: {e}")
        return None


def verify_supabase_token(token: str) -> Optional[dict]:
    """Verify a Supabase JWT and return the user payload.

    Returns None if:
    - Supabase is not configured
    - Token is invalid
    - User not found
    """
    client = _get_supabase_client()
    if client is None:
        return None

    try:
        # Use the Supabase auth client to verify the JWT
        # The auth.get_user() method validates the token
        user_response = client.auth.get_user(token)
        if user_response and user_response.user:
            supa_user = user_response.user
            return {
                "supabase_id": supa_user.id,
                "email": supa_user.email,
                "phone": supa_user.phone,
                "created_at": supa_user.created_at,
            }
    except Exception as e:
        logger.debug(f"Supabase token verification failed: {e}")
    return None


def sync_supabase_user(supa_payload: dict) -> Optional[User]:
    """Sync a Supabase-authenticated user into the local database.

    If the user already exists (matched by email), return them.
    Otherwise, create a new local user with a generated ID.
    """
    db = SessionLocal()
    try:
        email = supa_payload.get("email")
        if not email:
            return None

        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return existing

        # Create new user from Supabase auth data
        from app.utils.security import generate_id
        new_user = User(
            id=generate_id(),
            name=email.split("@")[0].replace(".", " ").title(),
            email=email,
            mobile=supa_payload.get("phone", ""),
            password_hash="supabase-managed",  # Not used for auth
            role=UserRole.TEACHER.value,
            preferred_language="hi",
            target_language="sat",
            is_active=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"Synced Supabase user: {email}")
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to sync Supabase user: {e}")
        return None
    finally:
        db.close()


async def supabase_login(email: str, password: str) -> Optional[dict]:
    """Login via Supabase Auth and return tokens.

    Returns None if Supabase is not configured or login fails.
    This is an alternative to the built-in JWT login.
    """
    client = _get_supabase_client()
    if client is None:
        return None

    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        if response and response.session:
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at,
            }
    except Exception as e:
        logger.debug(f"Supabase login failed: {e}")
    return None


async def supabase_register(email: str, password: str, name: str = "") -> Optional[dict]:
    """Register via Supabase Auth and sync to local DB."""
    client = _get_supabase_client()
    if client is None:
        return None

    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password,
        })
        if response and response.user:
            # Sync to local DB
            supa_payload = {
                "supabase_id": response.user.id,
                "email": response.user.email,
            }
            local_user = sync_supabase_user(supa_payload)
            return {
                "user": local_user,
                "access_token": response.session.access_token if response.session else None,
            }
    except Exception as e:
        logger.error(f"Supabase registration failed: {e}")
    return None


class SupabaseAuthProvider:
    """Optional auth provider that checks Supabase tokens first,
    then falls back to the built-in JWT system.

    Use this as a dependency in FastAPI routes:
        current_user: User = Depends(supabase_auth_provider.get_current_user)
    """

    def __init__(self):
        pass

    async def get_current_user_optional(self, token: Optional[str] = None):
        """Try Supabase token first, then fall back to built-in auth."""
        if token and settings.supabase_enabled:
            payload = verify_supabase_token(token)
            if payload:
                user = sync_supabase_user(payload)
                if user:
                    return user
        # Fallback: return None (caller should use built-in auth)
        return None


# Singleton
supabase_auth = SupabaseAuthProvider()
