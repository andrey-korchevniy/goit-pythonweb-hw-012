from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# User schemas
class UserBase(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=6, max_length=100)

class UserResponse(UserBase):
    id: int
    avatar: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    hashed_password: str
    
    model_config = ConfigDict(from_attributes=True)

# Email verification schema
class RequestEmail(BaseModel):
    email: EmailStr

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Contact schemas
class ContactBase(BaseModel):
    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(default=None, max_length=500)

class ContactModel(ContactBase):
    pass

class ContactUpdate(ContactBase):
    name: Optional[str] = Field(default=None, max_length=50)
    surname: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(default=None, max_length=500)

class ContactResponse(ContactBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True) 