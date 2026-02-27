from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.kategori_menu.kategori_menu_schema import KategoriMenuCreate, KategoriMenuUpdate
from orm_models import KategoriMenu


#=================Getter=================================
def get_all_kategori(db: Session) -> List[KategoriMenu]:
    return db.query(KategoriMenu).all()

def get_kategori_by_id(db: Session, kategori_id: int) -> Optional[KategoriMenu]:
    return db.query(KategoriMenu).filter(KategoriMenu.id == kategori_id).first()

#=====================Main Function=======================
def create_kategori(db: Session, payload: KategoriMenuCreate):
    # Cek duplikasi nama kategori
    existing = db.query(KategoriMenu).filter(KategoriMenu.nama == payload.nama).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Kategori '{payload.nama}' sudah ada."
        )

    new_kategori = KategoriMenu(**payload.model_dump())

    db.add(new_kategori)
    db.commit()
    db.refresh(new_kategori)
    return new_kategori

def update_kategori(db: Session, kategori_id: int, payload: KategoriMenuUpdate):
    kategori = get_kategori_by_id(db, kategori_id)
    if not kategori:
        raise HTTPException(status_code=404, detail="Kategori menu tidak ditemukan.")

    update_data = payload.model_dump(exclude_unset=True)

    # Cek duplikasi nama jika nama di-update
    if "nama" in update_data:
        existing = db.query(KategoriMenu).filter(KategoriMenu.nama == update_data["nama"]).first()
        if existing and existing.id != kategori_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Kategori '{update_data['nama']}' sudah digunakan."
            )

    for key, value in update_data.items():
        setattr(kategori, key, value)

    db.commit()
    db.refresh(kategori)
    return kategori

def delete_kategori(db: Session, kategori_id: int):
    kategori = get_kategori_by_id(db, kategori_id)
    if not kategori:
        raise HTTPException(status_code=404, detail="Kategori menu tidak ditemukan.")

    nama = kategori.nama

    db.delete(kategori)
    db.commit()
    return {"detail": f"Kategori '{nama}' berhasil dihapus."}
