from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timezone

from app.models.payment.payment_schema import PaymentCreate
from orm_models import Payment, Orders, OrderStatusEnum, Meja


#=================Getter=================================
def get_all_payments(db: Session) -> List[Payment]:
    return db.query(Payment).all()

def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.id == payment_id).first()

def get_payment_by_order(db: Session, order_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.order_id == order_id).first()


#=====================Main Function=======================
def create_payment(db: Session, payload: PaymentCreate):
    # Validasi order
    order = db.query(Orders).filter(Orders.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan.")

    # Cek apakah order sudah selesai
    if order.status != OrderStatusEnum.selesai:
        raise HTTPException(
            status_code=400,
            detail=f"Pembayaran hanya bisa dilakukan untuk order dengan status 'selesai'. Status saat ini: '{order.status.value}'."
        )

    # Cek apakah sudah ada pembayaran untuk order ini
    existing_payment = get_payment_by_order(db, payload.order_id)
    if existing_payment:
        raise HTTPException(status_code=400, detail="Order ini sudah memiliki pembayaran.")

    # Validasi jumlah pembayaran
    if payload.amount < order.total_harga:
        raise HTTPException(
            status_code=400,
            detail=f"Jumlah pembayaran (Rp {payload.amount}) kurang dari total harga (Rp {order.total_harga})."
        )

    new_payment = Payment(**payload.model_dump())

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return new_payment


def delete_payment(db: Session, payment_id: int):
    payment = get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Pembayaran tidak ditemukan.")

    payment_id_ref = payment.id

    db.delete(payment)
    db.commit()

    return {"detail": f"Pembayaran dengan ID {payment_id_ref} berhasil dihapus."}
