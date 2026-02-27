from pydantic import BaseModel, ConfigDict
from typing import Optional
from decimal import Decimal
from app.models.kategori_menu.kategori_menu_schema import KategoriMenuResponse

class MenuCreate(BaseModel):
    kategori_id: int
    nama: str
    harga: Decimal
    current_stok: int
    is_tersedia: bool = True

class MenuUpdate(BaseModel):
    kategori_id: Optional[int] = None
    nama: Optional[str] = None
    harga: Optional[Decimal] = None
    current_stok: Optional[int] = None
    is_tersedia: Optional[bool] = None

class MenuResponse(BaseModel):
    id: int
    nama: str
    harga: Decimal
    current_stok: int
    is_tersedia: bool
    kategori: KategoriMenuResponse

    model_config = ConfigDict(from_attributes=True)
