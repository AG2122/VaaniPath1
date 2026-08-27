"""VaniPath - Authentication API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.database import get_db
from app.models.user import User
from app.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.utils.security import (
    hash_password, verify_password, create_access_token,
    get_current_user, generate_id
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse,
             summary="Register a new user",
             description="Register a new teacher or validator account.")
def register(data: UserRegister, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=generate_id(),
        name=data.name,
        email=data.email,
        mobile=data.mobile,
        password_hash=hash_password(data.password),
        role=data.role,
        school=data.school,
        preferred_language="hi",
        target_language="sat",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role})

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "school": user.school,
        }
    )


@router.post("/login", response_model=TokenResponse,
             summary="Login",
             description="Login with email and password.")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.id, "role": user.role})

    return TokenResponse(
        access_token=token,
        user={
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "school": user.school,
        }
    )


@router.get("/me", response_model=UserResponse,
            summary="Get current user profile",
            description="Get the authenticated user's profile.")
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        mobile=current_user.mobile,
        role=current_user.role,
        school=current_user.school,
        preferred_language=current_user.preferred_language,
        target_language=current_user.target_language,
        created_at=current_user.created_at,
    )
