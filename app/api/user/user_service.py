from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from app.models.user.user_schema import UserCreate, UserRegis, UserUpdate
from orm_models import User, Pegawai, RoleEnum, JabatanEnum, ActiveEnum
from app.core.security import hash_password
from passlib.context import CryptContext


#=================Getter=================================
def get_all_user(db: Session) -> List[User]:
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

#=====================Main Function=======================
def create_user(db: Session, user_data: UserCreate):
    #Buat ngecek duplikasi username dan email
    if get_user_by_username(db, username=user_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username sudah digunakan")
    if get_user_by_email(db, email=user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email sudah digunakan")
        
    new_user = user_data.model_dump()
    new_user['password'] = hash_password(user_data.password)
    
    user = User(**new_user)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_register(db: Session, user_data: UserRegis):
    #Buat ngecek duplikasi username dan email
    if get_user_by_username(db, username=user_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Username sudah digunakan")
    if get_user_by_email(db, email=user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email sudah digunakan")
        
    new_user_data = user_data.model_dump()
    new_user_data['password'] = hash_password(user_data.password)
    new_user_data['role'] = RoleEnum.user
    
    new_user = User(**new_user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def update_user(db: Session, id_user:int, user_data:UserUpdate) -> User | None:
    user = get_user_by_id(db, id_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Pengguna tidak ditemukan")
        
    update_data = user_data.model_dump(exclude_unset=True)
    
    #Cek duplikat username    
    if "username" in update_data:
        new_username = update_data["username"]
        
        existing_user = get_user_by_username(db, new_username)
        
        if existing_user and existing_user.id != id_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"username {new_username} sudah digunakan oleh pengguna lain"
            )
            
    if "email" in update_data:
        new_email = update_data["email"]
        
        existing_user = get_user_by_email(db, new_email)
        
        if existing_user and existing_user.id != id_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {new_email} sudah digunakan oleh pengguna lain"
            )
            
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])
        
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.commit()
    db.refresh(user)
    return user

def update_me(db: Session, current_user: User, user_data:UserUpdate) -> User:
            
    update_data = user_data.model_dump(exclude_unset=True)
    
    #Cek duplikat username    
    if "username" in update_data:
        new_username = update_data["username"]
        
        existing_user = get_user_by_username(db, new_username)
        
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"username {new_username} sudah digunakan oleh pengguna lain"
            )
            
    if "email" in update_data:
        new_email = update_data["email"]
        
        existing_user = get_user_by_email(db, new_email)
        
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {new_email} sudah digunakan oleh pengguna lain"
            )

    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user

def delete_and_return_user(db: Session, id_user: int) -> Dict[str, str]:
    user = db.query(User).filter(User.id == id_user).first() 
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan"
        )
        
    # Ambil username sebelum delete
    username = user.username
    
    db.delete(user)
    db.commit()
    
    # Return dictionary aman
    return {"status": "success", "message": f"User {username} deleted"}
    