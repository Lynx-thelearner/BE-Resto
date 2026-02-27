from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import auth
from app.core.auth import create_access_token, oauth2_scheme
from app.core.deps import get_db
from fastapi.security import  OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.auth import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=auth.Token)
def login_endpoint(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth_service.login_user(db, form_data.username, form_data.password)

@router.post("/logout")
def logout_endpoint(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return auth_service.logout_user(db, token)

