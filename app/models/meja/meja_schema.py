from pydantic import BaseModel, ConfigDict
from typing import Optional

class MejaCreate(BaseModel):
    nomor_meja: str
    kapasitas: int
    is_tersedia: bool = True

class MejaUpdate(BaseModel):
    nomor_meja: Optional[str] = None
    kapasitas: Optional[int] = None
    is_tersedia: Optional[bool] = None

class MejaResponse(BaseModel):
    id: int
    nomor_meja: str
    kapasitas: int
    is_tersedia: bool

    model_config = ConfigDict(from_attributes=True)
