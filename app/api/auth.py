# ============================================================
# app/api/auth.py
# API Endpoint for authentication
# Include enpoints for handling user login and registration
# ============================================================


import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, HTTPException, status  
from pydantic import BaseModel, EmailStr                       
from datetime import datetime
from sqlalchemy.orm import Session                              
from app.database import get_db                                
from app.models import User                                     
from app.services.auth_service import (                         
    hash_function_pwd,
    verify_pwd,
    create_token
)
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    """Request body for validating user input when registering a new account"""
    email: EmailStr
    username: str
    password: str

class LoginRequest(BaseModel):
    """Request body for validating user input when logging in to an existing account"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response model that validates the token that is given to a user after a successful login"""
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Check if an account is already registered and create a new account for new user
    """
    usr_exists = db.query(User).filter(User.email == request.email).first()

    if usr_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    
    new_pwd = hash_function_pwd(request.password)
    new_user = User(
            username=request.username,
            email=request.email,
            password_hash=new_pwd
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    '''
    Handles the logic for existing user login
    '''
    check_user = db.scalar(select(User).where(User.email == request.email))

    if not check_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Credentials")
    
    verify_password = verify_pwd(request.password, check_user.password_hash)

    if not verify_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Credentials")
    
    new_token = create_token(check_user.id, request.email, check_user.username)
    return TokenResponse(access_token=new_token, token_type="bearer")

@router.post("/token", response_model=TokenResponse)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_pwd(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user.id, user.email, user.username)
    return TokenResponse(access_token=token, token_type="bearer")