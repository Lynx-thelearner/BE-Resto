from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.pegawai import pegawai_service
from app.models.pegawai.pegawai_schema import PegawaiCreate, PegawaiResponse, PegawaiUpdate
from orm_models import RoleEnum, User

router = APIRouter(
    prefix="/pegawai",
    tags=["Pegawai"]
)

@router.get("/", response_model=list[PegawaiResponse])
def get_all_pegawai(db: Session = Depends(get_db)):
    return pegawai_service.get_all_pegawai(db)

@router.post("/{user_id}", response_model=PegawaiResponse)
def create_pegawai(user_id: int, payload: PegawaiCreate, db: Session = Depends(get_db)):
    return pegawai_service.create_pegawai(db, payload, user_id)

@router.patch("/{pegawai_id}", response_model=PegawaiResponse)
def update_pegawai(pegawai_id: int, payload: PegawaiUpdate, db: Session = Depends(get_db)):
    return pegawai_service.update_pegawai(db, pegawai_id, payload)

@router.delete("/{pegawai_id}")
def delete_pegawai(pegawai_id: int, db: Session = Depends(get_db)):
    return pegawai_service.delete_pegawai(db, pegawai_id)
