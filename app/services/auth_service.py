# ============================================================
# app/services/auth_service.py
# This file contains the core authentication logic. 
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timedelta, timezone  
from jose import jwt, JWTError                        
from passlib.context import CryptContext              
from app.config import (                              
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_EXPIRATION_MINUTES
)

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_function_pwd(password):
    """
    Takes in a plain password and hash the user inputted password

    Param:
    password(str): user password

    Returns:
    a hashed password
    
    """
    hash_pwd = PWD_CONTEXT.hash(password)
    return hash_pwd


def verify_pwd(plain_pwd, hash_pwd):
    """
    Takes in a plain password, then hash the password and compare 
    the hash passwod with the user recorded hashed password in the database
    Used for login password verification

    Params:
    plain_pwd(str): regular password
    hash_pwd(str): hashed password

    Return:
    True if the password match and false otherwise
    """

    verify = PWD_CONTEXT.verify(plain_pwd, hash_pwd)
    return verify # Could return true or false


def create_token(user_id, email, username):
    """
    Create the JWT Token for user authentication for most endpoints throughout the app
   
    Param:
    user_id(int)
    email(str)
    username(str)


    Return: the JWT Token
    """
    payload = {
        "id": user_id,
        "email": email,
        "username": username,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)

    }

    encoded_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded_token


def decode_token(token):
    """
    Decode the JWT Token
    
    Param: JWT token

    Return: decoded information or None for JWT Error
    """
    try:
        decoded_token = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except JWTError:
        return None
    

    
    
    
     









