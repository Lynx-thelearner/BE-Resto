from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.kategori_menu import kategori_menu_service
from app.models.kategori_menu.kategori_menu_schema import KategoriMenuCreate, KategoriMenuResponse, KategoriMenuUpdate
from orm_models import RoleEnum

router = APIRouter(
    prefix="/kategori-menu",
    tags=["Kategori Menu"]
)

@router.get("/", response_model=list[KategoriMenuResponse])
def get_all_kategori(db: Session = Depends(get_db)):
    return kategori_menu_service.get_all_kategori(db)

@router.get("/{kategori_id}", response_model=KategoriMenuResponse)
def get_kategori_by_id(kategori_id: int, db: Session = Depends(get_db)):
    kategori = kategori_menu_service.get_kategori_by_id(db, kategori_id)
    if not kategori:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategori menu tidak ditemukan."
        )
    return kategori

@router.post("/", response_model=KategoriMenuResponse)
def create_kategori(payload: KategoriMenuCreate, db: Session = Depends(get_db)):
    return kategori_menu_service.create_kategori(db, payload)

@router.patch("/{kategori_id}", response_model=KategoriMenuResponse)
def update_kategori(kategori_id: int, payload: KategoriMenuUpdate, db: Session = Depends(get_db)):
    return kategori_menu_service.update_kategori(db, kategori_id, payload)

@router.delete("/{kategori_id}")
def delete_kategori(kategori_id: int, db: Session = Depends(get_db)):
    return kategori_menu_service.delete_kategori(db, kategori_id)
