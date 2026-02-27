from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.payment import payment_service
from app.models.payment.payment_schema import PaymentCreate, PaymentResponse
from orm_models import RoleEnum

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)

@router.get("/", response_model=list[PaymentResponse])
def get_all_payments(db: Session = Depends(get_db)):
    return payment_service.get_all_payments(db)

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_by_id(payment_id: int, db: Session = Depends(get_db)):
    payment = payment_service.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pembayaran tidak ditemukan."
        )
    return payment

@router.get("/order/{order_id}", response_model=PaymentResponse)
def get_payment_by_order(order_id: int, db: Session = Depends(get_db)):
    payment = payment_service.get_payment_by_order(db, order_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pembayaran untuk order ini tidak ditemukan."
        )
    return payment

@router.post("/", response_model=PaymentResponse)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    return payment_service.create_payment(db, payload)

@router.delete("/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_service.delete_payment(db, payment_id)
