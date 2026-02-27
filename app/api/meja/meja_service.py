from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from app.models.meja.meja_schema import MejaCreate, MejaUpdate
from orm_models import Meja


#=================Getter=================================
def get_all_meja(db: Session) -> List[Meja]:
    return db.query(Meja).all()

def get_meja_by_id(db: Session, meja_id: int) -> Optional[Meja]:
    return db.query(Meja).filter(Meja.id == meja_id).first()

def get_meja_tersedia(db: Session) -> List[Meja]:
    return db.query(Meja).filter(Meja.is_tersedia == True).all()

#=====================Main Function=======================
def create_meja(db: Session, payload: MejaCreate):
    # Cek duplikasi nomor meja
    existing = db.query(Meja).filter(Meja.nomor_meja == payload.nomor_meja).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Meja dengan nomor '{payload.nomor_meja}' sudah ada."
        )

    new_meja = Meja(**payload.model_dump())

    db.add(new_meja)
    db.commit()
    db.refresh(new_meja)
    return new_meja

def update_meja(db: Session, meja_id: int, payload: MejaUpdate):
    meja = get_meja_by_id(db, meja_id)
    if not meja:
        raise HTTPException(status_code=404, detail="Meja tidak ditemukan.")

    update_data = payload.model_dump(exclude_unset=True)

    # Cek duplikasi nomor meja jika nomor_meja di-update
    if "nomor_meja" in update_data:
        existing = db.query(Meja).filter(Meja.nomor_meja == update_data["nomor_meja"]).first()
        if existing and existing.id != meja_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nomor meja '{update_data['nomor_meja']}' sudah digunakan oleh meja lain."
            )

    for key, value in update_data.items():
        setattr(meja, key, value)

    db.commit()
    db.refresh(meja)
    return meja

def delete_meja(db: Session, meja_id: int):
    meja = get_meja_by_id(db, meja_id)
    if not meja:
        raise HTTPException(status_code=404, detail="Meja tidak ditemukan.")

    nomor = meja.nomor_meja

    db.delete(meja)
    db.commit()
    return {"detail": f"Meja {nomor} berhasil dihapus."}
