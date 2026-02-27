from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.stok_harian import stok_harian_service
from app.models.stok_harian.stok_harian_schema import StokHarianCreate, StokHarianResponse, StokHarianUpdate
from orm_models import RoleEnum

router = APIRouter(
    prefix="/stok-harian",
    tags=["Stok Harian"]
)

@router.get("/", response_model=list[StokHarianResponse])
def get_all_stok_harian(db: Session = Depends(get_db)):
    return stok_harian_service.get_all_stok_harian(db)

@router.get("/tanggal/{tanggal}", response_model=list[StokHarianResponse])
def get_stok_by_tanggal(tanggal: date, db: Session = Depends(get_db)):
    return stok_harian_service.get_stok_by_tanggal(db, tanggal)

@router.get("/menu/{menu_id}", response_model=list[StokHarianResponse])
def get_stok_by_menu(menu_id: int, db: Session = Depends(get_db)):
    return stok_harian_service.get_stok_by_menu(db, menu_id)

@router.get("/{stok_id}", response_model=StokHarianResponse)
def get_stok_harian_by_id(stok_id: int, db: Session = Depends(get_db)):
    stok = stok_harian_service.get_stok_harian_by_id(db, stok_id)
    if not stok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data stok harian tidak ditemukan."
        )
    return stok

@router.post("/", response_model=StokHarianResponse)
def create_stok_harian(payload: StokHarianCreate, db: Session = Depends(get_db)):
    return stok_harian_service.create_stok_harian(db, payload)

@router.patch("/{stok_id}", response_model=StokHarianResponse)
def update_stok_harian(stok_id: int, payload: StokHarianUpdate, db: Session = Depends(get_db)):
    return stok_harian_service.update_stok_harian(db, stok_id, payload)

@router.delete("/{stok_id}")
def delete_stok_harian(stok_id: int, db: Session = Depends(get_db)):
    return stok_harian_service.delete_stok_harian(db, stok_id)
