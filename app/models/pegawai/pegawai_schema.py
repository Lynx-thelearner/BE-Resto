from pydantic import BaseModel, Field, EmailStr, StringConstraints, ConfigDict, field_validator
from typing import Optional, Annotated
from orm_models import JabatanEnum, ActiveEnum

class PegawaiCreate(BaseModel):
    nama: str
    jabatan: JabatanEnum
    status: ActiveEnum
    
class PegawaiUpdate(BaseModel):
    nama: Optional[str] = None
    jabatan: Optional[JabatanEnum] = None
    status: Optional[ActiveEnum] = None
    
class PegawaiResponse(PegawaiCreate):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)
        