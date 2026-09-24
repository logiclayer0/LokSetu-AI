from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "citizen"


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


fake_users_db = {}


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    fake_users_db[user.email] = {
        "full_name": user.full_name,
        "email": user.email,
        "hashed_password": hash_password(user.password),
        "role": user.role
    }
    return {"message": "User registered successfully", "email": user.email, "role": user.role}


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(
        access_token=create_access_token(user["email"]),
        refresh_token=create_refresh_token(user["email"]),
        role=user["role"]
    )


@router.post("/login-with-role", response_model=TokenResponse)
async def login_with_role(payload: UserLogin):
    user = fake_users_db.get(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user["role"] != payload.role:
        raise HTTPException(
            status_code=403,
            detail=f"This account is registered as '{user['role']}', not '{payload.role}'"
        )
    return TokenResponse(
        access_token=create_access_token(user["email"]),
        refresh_token=create_refresh_token(user["email"]),
        role=user["role"]
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str):
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    subject = payload.get("sub")
    return TokenResponse(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
        role="citizen"
    )


@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    user = fake_users_db.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"full_name": user["full_name"], "email": user["email"], "role": user["role"]}