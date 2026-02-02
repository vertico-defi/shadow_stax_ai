from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.db.sqlite import create_user, get_user_by_username
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest) -> AuthResponse:
    existing = get_user_by_username(request.username)
    if existing:
        raise HTTPException(status_code=400, detail="username_taken")
    password_hash = hash_password(request.password)
    user_id = create_user(request.username, password_hash)
    token = create_access_token(user_id, request.username)
    return AuthResponse(access_token=token)


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest) -> AuthResponse:
    user = get_user_by_username(request.username)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid_credentials")
    token = create_access_token(int(user["id"]), user["username"])
    return AuthResponse(access_token=token)
