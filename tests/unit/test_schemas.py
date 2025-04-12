import pytest
from datetime import date
from pydantic import ValidationError

from src.schemas import (
    UserBase, UserCreate, UserResponse, 
    ContactModel, ContactUpdate, ContactResponse
)


def test_user_base():
    """Test UserBase model"""
    # Create correct object
    user = UserBase(
        username="testuser",
        email="test@example.com"
    )
    
    # Check attributes
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    
    # Check email validation
    with pytest.raises(ValidationError):
        UserBase(
            username="testuser",
            email="invalid-email"  # Invalid email
        )


def test_user_create():
    """Test UserCreate model"""
    # Create correct object
    user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Check attributes
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "password123"


def test_user_response():
    """Test UserResponse model"""
    # Create correct object
    user = UserResponse(
        id=1,
        username="testuser",
        email="test@example.com",
        avatar=None
    )
    
    # Check attributes
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.avatar is None


def test_contact_model():
    """Test ContactModel model"""
    # Create correct object
    birthday_date = date(1990, 1, 1)
    contact = ContactModel(
        name="John",
        surname="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=birthday_date
    )
    
    # Check attributes
    assert contact.name == "John"
    assert contact.surname == "Doe"
    assert contact.email == "john@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == birthday_date
    
    # Check email validation
    with pytest.raises(ValidationError):
        ContactModel(
            name="John",
            surname="Doe",
            email="invalid-email",  # Invalid email
            phone="1234567890",
            birthday=birthday_date
        )


def test_contact_update():
    """Test ContactUpdate model"""
    # Create correct object with partial data
    contact = ContactUpdate(name="John")
    
    # Check attributes
    assert contact.name == "John"
    assert contact.surname is None
    assert contact.email is None
    assert contact.phone is None
    assert contact.birthday is None
    assert contact.additional_data is None


def test_contact_response():
    """Test ContactResponse model"""
    # Create correct object
    birthday_date = date(1990, 1, 1)
    contact = ContactResponse(
        id=1,
        name="John",
        surname="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=birthday_date,
        additional_data="Some notes",
        user_id=1
    )
    
    # Check attributes
    assert contact.id == 1
    assert contact.name == "John"
    assert contact.surname == "Doe"
    assert contact.email == "john@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == birthday_date
    assert contact.additional_data == "Some notes"
    assert contact.user_id == 1 