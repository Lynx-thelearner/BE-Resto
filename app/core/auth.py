from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import os
from orm_models import RoleEnum, User
from app.core.deps import get_db

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/auth/login")

class TokenData(BaseModel):
    id_user: int
    role: RoleEnum 

class Token(BaseModel):
    """Response ketika login sukses"""
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Isi token setelah di-decode"""
    sub: Optional[str] = None   # pegawai_id 
    role: Optional[str] = None  # anggota/petugas
    exp: Optional[int] = None   # expiry time
    
def create_access_token(subject: str, claims: Dict | None = None, expires_delta: Optional[timedelta] = None):
    to_encode = {"sub": subject}
    
    if claims:
        to_encode.update(claims)
        
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        #Decode token
        payload_dict = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 1. Validate structure using Pydantic
        token_payload = TokenPayload(**payload_dict)
        
        if token_payload.sub is None or token_payload.role is None:
            raise credentials_exception
            
        # 2. Safely convert Enum (Handle ValueError)
        try:
            user_role = RoleEnum(token_payload.role)
        except ValueError:
            raise credentials_exception # Token role doesn't match Server role
            
        return TokenData(id_user=int(token_payload.sub), role=user_role)
        
    except (JWTError, ValidationError):
        raise credentials_exception
    
def get_current_user(db: Session = Depends(get_db), token_data: TokenData = Depends(verify_token)):
    user = db.query(User).filter(User.id == token_data.id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def require_role(*allowed_roles: RoleEnum):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource."
            )
        return current_user
    return dependency