from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.menu.menu_schema import MenuCreate, MenuUpdate
from orm_models import Menu, KategoriMenu


#=================Getter=================================
def get_all_menu(db: Session) -> List[Menu]:
    return db.query(Menu).options(joinedload(Menu.kategori)).all()

def get_menu_by_id(db: Session, menu_id: int) -> Optional[Menu]:
    return db.query(Menu).options(joinedload(Menu.kategori)).filter(Menu.id == menu_id).first()

def get_menu_tersedia(db: Session) -> List[Menu]:
    return db.query(Menu).options(joinedload(Menu.kategori)).filter(Menu.is_tersedia == True).all()

def get_menu_by_kategori(db: Session, kategori_id: int) -> List[Menu]:
    return db.query(Menu).options(joinedload(Menu.kategori)).filter(Menu.kategori_id == kategori_id).all()

#=====================Main Function=======================
def create_menu(db: Session, payload: MenuCreate):
    # Cek apakah kategori ada
    kategori = db.query(KategoriMenu).filter(KategoriMenu.id == payload.kategori_id).first()
    if not kategori:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kategori menu tidak ditemukan."
        )

    # Cek duplikasi nama menu
    existing = db.query(Menu).filter(Menu.nama == payload.nama).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Menu '{payload.nama}' sudah ada."
        )

    new_menu = Menu(**payload.model_dump())

    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)
    return new_menu

def update_menu(db: Session, menu_id: int, payload: MenuUpdate):
    menu = get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan.")

    update_data = payload.model_dump(exclude_unset=True)

    # Cek apakah kategori ada jika kategori_id di-update
    if "kategori_id" in update_data:
        kategori = db.query(KategoriMenu).filter(KategoriMenu.id == update_data["kategori_id"]).first()
        if not kategori:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kategori menu tidak ditemukan."
            )

    # Cek duplikasi nama jika nama di-update
    if "nama" in update_data:
        existing = db.query(Menu).filter(Menu.nama == update_data["nama"]).first()
        if existing and existing.id != menu_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Menu '{update_data['nama']}' sudah digunakan oleh menu lain."
            )

    for key, value in update_data.items():
        setattr(menu, key, value)

    db.commit()
    db.refresh(menu)
    return menu

def delete_menu(db: Session, menu_id: int):
    menu = get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan.")

    nama = menu.nama

    db.delete(menu)
    db.commit()
    return {"detail": f"Menu '{nama}' berhasil dihapus."}
