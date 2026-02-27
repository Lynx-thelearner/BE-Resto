from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date

from app.models.stok_harian.stok_harian_schema import StokHarianCreate, StokHarianUpdate
from orm_models import UpdateStokHarian, Menu, Pegawai


#=================Getter=================================
def get_all_stok_harian(db: Session) -> List[UpdateStokHarian]:
    return db.query(UpdateStokHarian).all()

def get_stok_harian_by_id(db: Session, stok_id: int) -> Optional[UpdateStokHarian]:
    return db.query(UpdateStokHarian).filter(UpdateStokHarian.id == stok_id).first()

def get_stok_by_tanggal(db: Session, tanggal: date) -> List[UpdateStokHarian]:
    return db.query(UpdateStokHarian).filter(UpdateStokHarian.tanggal == tanggal).all()

def get_stok_by_menu(db: Session, menu_id: int) -> List[UpdateStokHarian]:
    return db.query(UpdateStokHarian).filter(UpdateStokHarian.menu_id == menu_id).all()


#=====================Main Function=======================
def create_stok_harian(db: Session, payload: StokHarianCreate):
    # Validasi menu
    menu = db.query(Menu).filter(Menu.id == payload.menu_id).first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu tidak ditemukan.")

    # Validasi pegawai
    pegawai = db.query(Pegawai).filter(Pegawai.id == payload.id_pegawai).first()
    if not pegawai:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan.")

    # Cek duplikasi (1 menu per hari)
    existing = db.query(UpdateStokHarian).filter(
        UpdateStokHarian.tanggal == payload.tanggal,
        UpdateStokHarian.menu_id == payload.menu_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Stok harian untuk menu ini pada tanggal {payload.tanggal} sudah ada. Gunakan update."
        )

    new_stok = UpdateStokHarian(**payload.model_dump())

    # Update current_stok di tabel menu
    menu.current_stok = payload.stok

    db.add(new_stok)
    db.commit()
    db.refresh(new_stok)

    return new_stok


def update_stok_harian(db: Session, stok_id: int, payload: StokHarianUpdate):
    stok = get_stok_harian_by_id(db, stok_id)
    if not stok:
        raise HTTPException(status_code=404, detail="Data stok harian tidak ditemukan.")

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(stok, key, value)

    # Jika stok diupdate, sync ke current_stok menu
    if "stok" in update_data:
        menu = db.query(Menu).filter(Menu.id == stok.menu_id).first()
        if menu:
            menu.current_stok = update_data["stok"]

    db.commit()
    db.refresh(stok)
    return stok


def delete_stok_harian(db: Session, stok_id: int):
    stok = get_stok_harian_by_id(db, stok_id)
    if not stok:
        raise HTTPException(status_code=404, detail="Data stok harian tidak ditemukan.")

    stok_ref = stok.id

    db.delete(stok)
    db.commit()

    return {"detail": f"Data stok harian ID {stok_ref} berhasil dihapus."}
