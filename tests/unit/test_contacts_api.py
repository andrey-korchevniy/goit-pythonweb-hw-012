import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

from fastapi import status, HTTPException

from src.api.contacts import read_contacts, read_contact, create_contact, update_contact, delete_contact, search_contacts, upcoming_birthdays
from src.schemas import ContactModel, ContactResponse, ContactUpdate


@pytest.fixture
def mock_user():
    """Мок пользователя для тестов"""
    return MagicMock(id=1, email="test@example.com")


@pytest.fixture
def mock_contact_service():
    """Мок сервиса контактов"""
    service = MagicMock()
    service.get_contacts = AsyncMock()
    service.get_contact = AsyncMock()
    service.create_contact = AsyncMock()
    service.update_contact = AsyncMock()
    service.delete_contact = AsyncMock()
    service.search_contacts = AsyncMock()
    service.get_contacts_by_birthday = AsyncMock()
    return service


@pytest.fixture
def mock_contact():
    """Мок контакта для тестов"""
    return MagicMock(
        id=1,
        name="John",
        surname="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1),
        user_id=1
    )


@pytest.mark.asyncio
async def test_read_contacts(mock_user, mock_contact_service):
    """Тест получения списка контактов"""
    # Настройка мока сервиса
    mock_contacts = [MagicMock(), MagicMock()]
    mock_contact_service.get_contacts.return_value = mock_contacts
    
    # Вызываем тестируемую функцию
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        result = await read_contacts(0, 100, None, mock_user)
    
    # Проверяем результат
    assert result == mock_contacts
    mock_contact_service.get_contacts.assert_called_once_with(0, 100, mock_user.id)


@pytest.mark.asyncio
async def test_search_contacts(mock_user, mock_contact_service):
    """Тест поиска контактов"""
    # Настройка мока сервиса
    mock_contacts = [MagicMock(), MagicMock()]
    mock_contact_service.search_contacts.return_value = mock_contacts
    
    # Вызываем тестируемую функцию
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        result = await search_contacts("John", None, mock_user)
    
    # Проверяем результат
    assert result == mock_contacts
    mock_contact_service.search_contacts.assert_called_once_with("John", mock_user.id)


@pytest.mark.asyncio
async def test_upcoming_birthdays(mock_user, mock_contact_service):
    """Тест получения предстоящих дней рождения"""
    # Настройка мока сервиса
    mock_contacts = [MagicMock(), MagicMock()]
    mock_contact_service.get_contacts_by_birthday.return_value = mock_contacts
    
    # Вызываем тестируемую функцию
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        result = await upcoming_birthdays(7, None, mock_user)
    
    # Проверяем результат
    assert result == mock_contacts
    mock_contact_service.get_contacts_by_birthday.assert_called_once_with(7, mock_user.id)


@pytest.mark.asyncio
async def test_read_contact_found(mock_user, mock_contact_service, mock_contact):
    """Тест получения контакта по ID, когда контакт существует"""
    # Настройка мока сервиса
    mock_contact_service.get_contact.return_value = mock_contact
    
    # Вызываем тестируемую функцию
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        result = await read_contact(1, None, mock_user)
    
    # Проверяем результат
    assert result == mock_contact
    mock_contact_service.get_contact.assert_called_once_with(1, mock_user.id)


@pytest.mark.asyncio
async def test_read_contact_not_found(mock_user, mock_contact_service):
    """Тест получения несуществующего контакта по ID"""
    # Настройка мока сервиса
    mock_contact_service.get_contact.return_value = None
    
    # Вызываем тестируемую функцию и ожидаем исключение
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        with pytest.raises(HTTPException) as exc_info:
            await read_contact(999, None, mock_user)
    
    # Проверяем исключение
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Contact not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_contact(mock_user, mock_contact_service, mock_contact):
    """Тест создания нового контакта"""
    # Настройка мока сервиса
    mock_contact_service.create_contact.return_value = mock_contact
    
    # Создаем данные для контакта
    contact_data = ContactModel(
        name="John",
        surname="Doe",
        email="john@example.com",
        phone="1234567890",
        birthday=date(1990, 1, 1)
    )
    
    # Вызываем тестируемую функцию
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        result = await create_contact(contact_data, None, mock_user)
    
    # Проверяем результат
    assert result == mock_contact
    mock_contact_service.create_contact.assert_called_once_with(contact_data, mock_user.id)


@pytest.mark.asyncio
async def test_update_contact_found(mock_user, mock_contact_service, mock_contact):
    """Тест обновления существующего контакта"""
    # Настройка мока сервиса
    mock_contact_service.update_contact.return_value = mock_contact
    
    # Создаем данные для обновления
    update_data = ContactUpdate(
        name="John Updated",
        surname="Doe Updated"
    )
    
    # Вызываем тестируемую функцию
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        result = await update_contact(update_data, 1, None, mock_user)
    
    # Проверяем результат
    assert result == mock_contact
    mock_contact_service.update_contact.assert_called_once_with(1, update_data, mock_user.id)


@pytest.mark.asyncio
async def test_update_contact_not_found(mock_user, mock_contact_service):
    """Тест обновления несуществующего контакта"""
    # Настройка мока сервиса
    mock_contact_service.update_contact.return_value = None
    
    # Создаем данные для обновления
    update_data = ContactUpdate(
        name="John Updated",
        surname="Doe Updated"
    )
    
    # Вызываем тестируемую функцию и ожидаем исключение
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        with pytest.raises(HTTPException) as exc_info:
            await update_contact(update_data, 999, None, mock_user)
    
    # Проверяем исключение
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Contact not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_delete_contact_found(mock_user, mock_contact_service, mock_contact):
    """Тест удаления существующего контакта"""
    # Настройка мока сервиса
    mock_contact_service.delete_contact.return_value = mock_contact
    
    # Вызываем тестируемую функцию
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        result = await delete_contact(1, None, mock_user)
    
    # Проверяем результат
    assert result == mock_contact
    mock_contact_service.delete_contact.assert_called_once_with(1, mock_user.id)


@pytest.mark.asyncio
async def test_delete_contact_not_found(mock_user, mock_contact_service):
    """Тест удаления несуществующего контакта"""
    # Настройка мока сервиса
    mock_contact_service.delete_contact.return_value = None
    
    # Вызываем тестируемую функцию и ожидаем исключение
    with patch("src.api.contacts.ContactService", return_value=mock_contact_service):
        with pytest.raises(HTTPException) as exc_info:
            await delete_contact(999, None, mock_user)
    
    # Проверяем исключение
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Contact not found" in exc_info.value.detail