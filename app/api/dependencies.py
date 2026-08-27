# ============================================================
# app/api/dependencies.py
# Authentication dependency — protects endpoints by only allowing authenticated caller to call the endpoint
# ============================================================


from fastapi import Depends, HTTPException, status        
from fastapi.security import OAuth2PasswordBearer         
from sqlalchemy.orm import Session                         
from jose import JWTError                                  
from app.database import get_db                           
from app.models import User                               
from app.services.auth_service import decode_token         
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") # Dependency used for getting the token that is the main authentication mechanism

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    '''
    Receives a token from the auth/login endpoint and decode the token to check that it's valid.
    If the token is valid, it will be used by the user for calling all other endpoints that requires authentication
    '''

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