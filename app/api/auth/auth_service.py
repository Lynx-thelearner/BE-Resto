from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import verify_password
from orm_models import User
from app.core.auth import create_access_token, Token

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Check credentials and return User object if valid, else None.
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
        
    if not verify_password(password, user.password):
        return None
        
    return user


def login_user(db: Session, username: str, password: str) -> Token:
    """
    Orchestrates the login process.
    """
    # 1. Authenticate
    user = authenticate_user(db, username, password)
    
    # 2. Handle failure (The Router/Service layer decides the specific error)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create Token
    access_token = create_access_token(
        subject=str(user.id), 
        claims={
            "username": user.username,
            "role": user.role.value
        }
    )

    return Token(access_token=access_token, token_type="bearer")