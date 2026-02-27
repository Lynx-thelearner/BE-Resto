from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import require_role, get_current_user
from app.api.order import order_service
from app.models.order.order_schema import (
    OrderCreate, OrderResponse, OrderDetailResponse, OrderUpdate,
    OrderStatusHistoryResponse
)
from orm_models import RoleEnum, OrderStatusEnum

router = APIRouter(
    prefix="/order",
    tags=["Order"]
)

@router.get("/", response_model=list[OrderResponse])
def get_all_orders(db: Session = Depends(get_db)):
    return order_service.get_all_orders(db)

@router.get("/status/{order_status}", response_model=list[OrderResponse])
def get_orders_by_status(order_status: OrderStatusEnum, db: Session = Depends(get_db)):
    return order_service.get_orders_by_status(db, order_status)

@router.get("/meja/{meja_id}", response_model=list[OrderResponse])
def get_orders_by_meja(meja_id: int, db: Session = Depends(get_db)):
    return order_service.get_orders_by_meja(db, meja_id)

@router.get("/waiter/{waiter_id}", response_model=list[OrderResponse])
def get_orders_by_waiter(waiter_id: int, db: Session = Depends(get_db)):
    return order_service.get_orders_by_waiter(db, waiter_id)

@router.get("/{order_id}/history", response_model=list[OrderStatusHistoryResponse])
def get_order_status_history(order_id: int, db: Session = Depends(get_db)):
    return order_service.get_order_status_history(db, order_id)

@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order tidak ditemukan."
        )
    return order

@router.post("/", response_model=OrderDetailResponse)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    return order_service.create_order(db, payload)

@router.patch("/{order_id}", response_model=OrderDetailResponse)
def update_order(order_id: int, payload: OrderUpdate, db: Session = Depends(get_db)):
    return order_service.update_order(db, order_id, payload)

@router.delete("/{order_id}")
def delete_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.delete_order(db, order_id)
