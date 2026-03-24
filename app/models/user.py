from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=72)


class UserInDB(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    role: str = "user"
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: str
    created_at: Optional[datetime] = None