# ============================================================
# app/api/auth.py
# API for authentication
# ============================================================


import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, status  # FastAPI routing and errors
from pydantic import BaseModel, EmailStr                        # request/response validation
from datetime import datetime
from sqlalchemy.orm import Session                              # database session type
from app.database import get_db                                 # database dependency
from app.models import User                                     # User table model
from app.services.auth_service import (                         # your auth logic from file 1
    hash_function_pwd,
    verify_pwd,
    create_token
)
from sqlalchemy import select


router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    usr_exists = db.query(User).filter(User.email == request.email).first()

    if usr_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    new_pwd = hash_function_pwd(request.password)
    new_user = User(
            username=request.username,
            email=request.email,
            password_hash=new_pwd
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_token = create_token(new_user.id, request.email, request.username)
    return TokenResponse(access_token=new_token, token_type="bearer")

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    check_user = db.scalar(select(User).where(User.email == request.email))

    if not check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    verify_password = verify_pwd(request.password, check_user.password_hash)

    if not verify_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    new_token = create_token(check_user.id, request.email, check_user.username)
    return TokenResponse(access_token=new_token, token_type="bearer")

