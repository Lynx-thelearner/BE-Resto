from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from orm_models import OrderStatusEnum, TipeOrder, JabatanEnum, ActiveEnum


# =================== Nested Models ===================
class MejaNested(BaseModel):
    id: int
    nomor_meja: str
    kapasitas: int

    model_config = ConfigDict(from_attributes=True)

class WaiterNested(BaseModel):
    id: int
    nama: str
    jabatan: JabatanEnum

    model_config = ConfigDict(from_attributes=True)

class MenuNested(BaseModel):
    id: int
    nama: str
    harga: Decimal

    model_config = ConfigDict(from_attributes=True)

# =================== Order Item ===================
class OrderItemCreate(BaseModel):
    menu_id: int
    jumlah: int
    catatan: Optional[str] = None

class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    menu_id: int
    jumlah: int
    harga_at_time: Decimal
    catatan: Optional[str] = None
    menu: Optional[MenuNested] = None

    model_config = ConfigDict(from_attributes=True)

# =================== Order ===================
class OrderCreate(BaseModel):
    meja_id: Optional[int] = None
    waiter_id: int
    tipe_order: TipeOrder
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    meja_id: Optional[int] = None
    tipe_order: Optional[TipeOrder] = None
    status: Optional[OrderStatusEnum] = None
    items: Optional[List[OrderItemCreate]] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatusEnum

class OrderResponse(BaseModel):
    id: int
    order_number: str
    meja_id: Optional[int] = None
    waiter_id: int
    tipe_order: TipeOrder
    status: OrderStatusEnum
    total_harga: Decimal
    created_at: datetime
    waktu_selesai: Optional[datetime] = None
    meja: Optional[MejaNested] = None
    waiter: Optional[WaiterNested] = None

    model_config = ConfigDict(from_attributes=True)

class OrderDetailResponse(OrderResponse):
    items: List[OrderItemResponse] = []
    payment: Optional["PaymentNested"] = None

# =================== Payment Nested ===================
class PaymentNested(BaseModel):
    id: int
    method: str
    amount: Decimal
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)

OrderDetailResponse.model_rebuild()

# =================== Order Status History ===================
class OrderStatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    status: OrderStatusEnum
    changed_at: datetime
    waiter_id: int

    model_config = ConfigDict(from_attributes=True)
