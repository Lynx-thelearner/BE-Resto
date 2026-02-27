from pydantic import BaseModel, Field, EmailStr, StringConstraints, ConfigDict, field_validator
from typing import Optional, Annotated
from orm_models import RoleEnum

class UserBase(BaseModel):
    username: str = Field(..., description="Unique username for the user")
    email: EmailStr = Field(..., description="User Email")
    role: RoleEnum = Field(RoleEnum.user, description="Role of the user")
    
class UserCreate(UserBase):
    password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=72)
    ] = Field(..., description="Password for the user account")
    
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the user")
    username: Optional[str] = Field(None, description="Unique username for the user")
    email: Optional[EmailStr] = Field(None, description="User Email")
    role: Optional[RoleEnum] = Field(None, description="Role of the user")
    
    password: Optional[
        Annotated[
            str,
            StringConstraints(min_length=8, max_length=72)
        ]
    ] = Field(None, description="Password for the user account")
    
class UserRegis(BaseModel):
    name: str = Field(..., description="Full name of the user")
    username: str = Field(..., description="Unique username for the user")
    email: EmailStr = Field(..., description="User Email")
    
    password: Annotated[
        str,
        StringConstraints(min_length=8, max_length=72)
    ] = Field(..., description="Password for the user account")
    
class UserResponse(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)