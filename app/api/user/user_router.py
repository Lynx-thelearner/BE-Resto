from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.user import user_service
from app.models.user.user_schema import UserResponse, UserCreate, UserUpdate, UserRegis
from orm_models import RoleEnum, User

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/profile", response_model=UserResponse)
def get_current_user_profile(current_user=Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.post("/", response_model=UserResponse)
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, request)

@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_user(db)

@router.get("/id/{id_user}", response_model=UserResponse)
def get_user_by_id(id_user:int, db: Session = Depends(get_db)):
    return user_service.get_user_by_id(db, id_user)

@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_username(username:str, db: Session = Depends(get_db)):
    
    user = user_service.get_user_by_username(db, username)
    
    # Jika service mengembalikan None, raise Error.
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User dengan username {username} tidak ditemukan")
        
    return user

@router.post("/register", response_model=UserResponse)
def register(user: UserRegis, db: Session = Depends(get_db)):
    return user_service.create_register(db=db, user=user)

@router.patch("/update-me", response_model=UserResponse)
def current_user_update(user_data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_service.update_me(db=db, current_user=current_user, user_data=user_data)

@router.patch("/{id_user}", response_model=UserResponse)
def update_user(id_user:int, user_data:UserUpdate, db: Session = Depends(get_db)):
    return user_service.update_user(db=db, id_user=id_user, user_data=user_data)
  
@router.delete("/{id_user}")
def delete_user(id_user:int, db: Session = Depends(get_db)):
    return user_service.delete_and_return_user(db=db, id_user=id_user)