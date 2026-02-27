from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.meja import meja_service
from app.models.meja.meja_schema import MejaCreate, MejaResponse, MejaUpdate
from orm_models import RoleEnum

router = APIRouter(
    prefix="/meja",
    tags=["Meja"]
)

@router.get("/", response_model=list[MejaResponse])
def get_all_meja(db: Session = Depends(get_db)):
    return meja_service.get_all_meja(db)

@router.get("/tersedia", response_model=list[MejaResponse])
def get_meja_tersedia(db: Session = Depends(get_db)):
    return meja_service.get_meja_tersedia(db)

@router.get("/{meja_id}", response_model=MejaResponse)
def get_meja_by_id(meja_id: int, db: Session = Depends(get_db)):
    meja = meja_service.get_meja_by_id(db, meja_id)
    if not meja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meja tidak ditemukan."
        )
    return meja

@router.post("/", response_model=MejaResponse)
def create_meja(payload: MejaCreate, db: Session = Depends(get_db)):
    return meja_service.create_meja(db, payload)

@router.patch("/{meja_id}", response_model=MejaResponse)
def update_meja(meja_id: int, payload: MejaUpdate, db: Session = Depends(get_db)):
    return meja_service.update_meja(db, meja_id, payload)

@router.delete("/{meja_id}")
def delete_meja(meja_id: int, db: Session = Depends(get_db)):
    return meja_service.delete_meja(db, meja_id)
