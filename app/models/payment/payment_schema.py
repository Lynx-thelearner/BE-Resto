from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import datetime
from orm_models import PaymentMethod


class PaymentCreate(BaseModel):
    order_id: int
    method: PaymentMethod
    amount: Decimal

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    method: PaymentMethod
    amount: Decimal
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)
