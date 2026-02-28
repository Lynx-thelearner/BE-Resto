from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional, Dict, Any
from app.models.pegawai.pegawai_schema import PegawaiCreate, PegawaiResponse, PegawaiUpdate
from orm_models import User, Pegawai, RoleEnum, JabatanEnum, ActiveEnum
from app.core.security import hash_password
from passlib.context import CryptContext

def get_all_pegawai(db: Session) -> List[Pegawai]:
    return db.query(Pegawai).order_by(Pegawai.id.asc()).all()

#=====================Main Function=======================
def create_pegawai(db: Session, payload: PegawaiCreate, user_id: int):
    #Buat ngecek id_user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan.")
    
    #Ngecek akun pegawai, cuma boleh ada 1
    existing_pegawai = db.query(Pegawai).filter(Pegawai.user_id == user_id).first()
    if existing_pegawai:
        raise HTTPException(status_code=400, detail="User ini sudah memiliki profil pegawai.")
    
    new_pegawai = payload.model_dump()
    new_pegawai["user_id"] = user_id
    pegawai = Pegawai(**new_pegawai)
    
    db.add(pegawai)
    db.commit()
    db.refresh(pegawai)
    
    return pegawai

def update_pegawai(db: Session, pegawai_id: int, payload: PegawaiUpdate):
    pegawai = db.query(Pegawai).filter(Pegawai.id == pegawai_id).first()
    if not pegawai:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan.")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(pegawai, key, value)
    
    db.commit()
    db.refresh(pegawai)
    return pegawai

def delete_pegawai(db: Session, pegawai_id: int):
    pegawai = db.query(Pegawai).filter(Pegawai.id == pegawai_id).first()
    if not pegawai:
        raise HTTPException(status_code=404, detail="Pegawai tidak ditemukan.")
    
    name = pegawai.nama
    
    db.delete(pegawai)
    db.commit()
    return {"detail": f"Pegawai {name} berhasil dihapus."}