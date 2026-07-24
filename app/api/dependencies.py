# ============================================================
# app/api/dependencies.py
# Authentication dependency — protects endpoints
# get_current_user() extracts the JWT token, verifies it,
# and returns the logged-in user
# ============================================================


from fastapi import Depends, HTTPException, status        # dependency injection and errors
from fastapi.security import OAuth2PasswordBearer          # extracts token from header
from sqlalchemy.orm import Session                         # database session type
from jose import JWTError                                  # JWT error handling
from app.database import get_db                            # database dependency
from app.models import User                                # User table model
from app.services.auth_service import decode_token         # your decode function from file 1
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )


    decoded_token = decode_token(token)

    if decoded_token is None:
        raise credentials_exception
    
    usr_id = decoded_token.get("id")

    if usr_id is None:
       raise credentials_exception
    
    
    query_usr = db.scalar(select(User).where(User.id == usr_id))

    if not query_usr:
        raise credentials_exception
    
    return query_usr # Returns a User object