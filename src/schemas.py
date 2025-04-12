"""
Data validation schemas module.

This module contains Pydantic classes for data validation and serialization in the API.
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.database.models import UserRole

# User schemas
class UserBase(BaseModel):
    """
    Base user model.
    
    Attributes:
        username: User's username.
        email: User's email.
    """
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """
    Model for user creation.
    
    Attributes:
        password: User's password.
    """
    password: str = Field(min_length=6, max_length=100)
    role: UserRole = Field(default=UserRole.USER)

class UserResponse(UserBase):
    """
    Model for API response with user data.
    
    Attributes:
        id: User ID.
        avatar: User's avatar URL.
    """
    id: int
    avatar: Optional[str] = None
    role: UserRole
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    """
    User model for database storage.
    
    Attributes:
        hashed_password: User's hashed password.
    """
    hashed_password: str
    
    model_config = ConfigDict(from_attributes=True)

# Email verification schema
class RequestEmail(BaseModel):
    """
    Model for email verification request.
    
    Attributes:
        email: Email for verification.
    """
    email: EmailStr

# Password reset schemas
class RequestPasswordReset(BaseModel):
    """
    Model for password reset request.
    
    Attributes:
        email: User's email for password reset.
    """
    email: EmailStr

class ResetPassword(BaseModel):
    """
    Model for password reset using a token.
    
    Attributes:
        token: Password reset token.
        password: User's new password.
    """
    token: str
    password: str = Field(min_length=6, max_length=100)

# Token schemas
class Token(BaseModel):
    """
    Authentication token model.
    
    Attributes:
        access_token: Access token.
        token_type: Token type.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Data contained in the token.
    
    Attributes:
        username: Username.
    """
    username: Optional[str] = None

# Contact schemas
class ContactBase(BaseModel):
    """
    Base contact model.
    
    Attributes:
        name: Contact's first name.
        surname: Contact's last name.
        email: Contact's email.
        phone: Contact's phone number.
        birthday: Contact's birth date.
        additional_data: Additional information about the contact.
    """
    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(default=None, max_length=500)

class ContactModel(ContactBase):
    """
    Model for contact creation.
    """
    pass

class ContactUpdate(ContactBase):
    """
    Model for contact update.
    
    All fields are optional to allow partial updates.
    """
    name: Optional[str] = Field(default=None, max_length=50)
    surname: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(default=None, max_length=500)

class ContactResponse(ContactBase):
    """
    Model for API response with contact data.
    
    Attributes:
        id: Contact ID.
        user_id: ID of the user who owns the contact.
    """
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True) 