"""
Модуль схем для валідації даних.

Цей модуль містить класи Pydantic для валідації та серіалізації даних в API.
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# User schemas
class UserBase(BaseModel):
    """
    Базова модель користувача.
    
    Attributes:
        username: Ім'я користувача.
        email: Email користувача.
    """
    username: str = Field(min_length=2, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    """
    Модель для створення користувача.
    
    Attributes:
        password: Пароль користувача.
    """
    password: str = Field(min_length=6, max_length=100)

class UserResponse(UserBase):
    """
    Модель для відповіді API з даними користувача.
    
    Attributes:
        id: Ідентифікатор користувача.
        avatar: URL аватару користувача.
    """
    id: int
    avatar: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    """
    Модель користувача для зберігання в базі даних.
    
    Attributes:
        hashed_password: Хешований пароль користувача.
    """
    hashed_password: str
    
    model_config = ConfigDict(from_attributes=True)

# Email verification schema
class RequestEmail(BaseModel):
    """
    Модель для запиту верифікації email.
    
    Attributes:
        email: Email для верифікації.
    """
    email: EmailStr

# Token schemas
class Token(BaseModel):
    """
    Модель токену автентифікації.
    
    Attributes:
        access_token: Токен доступу.
        token_type: Тип токену.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Дані, що містяться в токені.
    
    Attributes:
        username: Ім'я користувача.
    """
    username: Optional[str] = None

# Contact schemas
class ContactBase(BaseModel):
    """
    Базова модель контакту.
    
    Attributes:
        name: Ім'я контакту.
        surname: Прізвище контакту.
        email: Email контакту.
        phone: Телефон контакту.
        birthday: Дата народження контакту.
        additional_data: Додаткова інформація про контакт.
    """
    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date
    additional_data: Optional[str] = Field(default=None, max_length=500)

class ContactModel(ContactBase):
    """
    Модель для створення контакту.
    """
    pass

class ContactUpdate(ContactBase):
    """
    Модель для оновлення контакту.
    
    Всі поля є необов'язковими для дозволу часткового оновлення.
    """
    name: Optional[str] = Field(default=None, max_length=50)
    surname: Optional[str] = Field(default=None, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(default=None, max_length=500)

class ContactResponse(ContactBase):
    """
    Модель для відповіді API з даними контакту.
    
    Attributes:
        id: Ідентифікатор контакту.
        user_id: Ідентифікатор користувача, якому належить контакт.
    """
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True) 