import pytest
from datetime import date

from src.database.models import User, Contact


def test_user_attributes():
    """Тест атрибутов модели User"""
    # Создаем экземпляр модели User
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        confirmed=True
    )
    
    # Проверяем атрибуты
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"
    assert user.confirmed is True
    assert user.avatar is None


def test_contact_attributes():
    """Тест атрибутов модели Contact"""
    # Создаем экземпляр модели Contact
    birthday_date = date(1990, 1, 1)
    contact = Contact(
        name="John",
        surname="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=birthday_date,
        additional_data="Some notes",
        user_id=1
    )
    
    # Проверяем атрибуты
    assert contact.name == "John"
    assert contact.surname == "Doe"
    assert contact.email == "john@example.com"
    assert contact.phone == "1234567890"
    assert contact.birthday == birthday_date
    assert contact.additional_data == "Some notes"
    assert contact.user_id == 1 