from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.menu import menu_service
from app.models.menu.menu_schema import MenuCreate, MenuResponse, MenuUpdate
from orm_models import RoleEnum

router = APIRouter(
    prefix="/menu",
    tags=["Menu"]
)

@router.get("/", response_model=list[MenuResponse])
def get_all_menu(db: Session = Depends(get_db)):
    return menu_service.get_all_menu(db)

@router.get("/tersedia", response_model=list[MenuResponse])
def get_menu_tersedia(db: Session = Depends(get_db)):
    return menu_service.get_menu_tersedia(db)

@router.get("/kategori/{kategori_id}", response_model=list[MenuResponse])
def get_menu_by_kategori(kategori_id: int, db: Session = Depends(get_db)):
    return menu_service.get_menu_by_kategori(db, kategori_id)

@router.get("/{menu_id}", response_model=MenuResponse)
def get_menu_by_id(menu_id: int, db: Session = Depends(get_db)):
    menu = menu_service.get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu tidak ditemukan."
        )
    return menu

@router.post("/", response_model=MenuResponse)
def create_menu(payload: MenuCreate, db: Session = Depends(get_db)):
    return menu_service.create_menu(db, payload)

@router.patch("/{menu_id}", response_model=MenuResponse)
def update_menu(menu_id: int, payload: MenuUpdate, db: Session = Depends(get_db)):
    return menu_service.update_menu(db, menu_id, payload)

@router.delete("/{menu_id}")
def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    return menu_service.delete_menu(db, menu_id)
