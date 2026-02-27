from pydantic import BaseModel, ConfigDict
from typing import Optional

class KategoriMenuCreate(BaseModel):
    nama: str

class KategoriMenuUpdate(BaseModel):
    nama: Optional[str] = None

class KategoriMenuResponse(BaseModel):
    id: int
    nama: str

    model_config = ConfigDict(from_attributes=True)
