from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class StokHarianCreate(BaseModel):
    tanggal: date
    menu_id: int
    stok: int
    id_pegawai: int

class StokHarianUpdate(BaseModel):
    stok: Optional[int] = None

class StokHarianResponse(BaseModel):
    id: int
    tanggal: date
    menu_id: int
    stok: int
    id_pegawai: int

    model_config = ConfigDict(from_attributes=True)
