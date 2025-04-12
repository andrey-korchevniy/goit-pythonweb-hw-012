import pytest
from sqlalchemy import select
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import date, timedelta

from src.database.models import Contact
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate


@pytest.mark.asyncio
class TestContactRepository:
    async def test_get_contacts(self):
        # Создаем моки для объектов
        mock_session = AsyncMock()
        mock_contacts = [Contact(id=1), Contact(id=2)]
        
        # Настраиваем возвращаемое значение для метода execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_contacts
        mock_session.execute.return_value = mock_result
        
        # Создаем экземпляр репозитория
        repo = ContactRepository(mock_session)
        
        # Вызываем тестируемый метод
        result = await repo.get_contacts(0, 10, 1)
        
        # Проверяем результат
        assert result == mock_contacts
        # Проверяем, что метод execute был вызван
        mock_session.execute.assert_called_once()
    
    async def test_get_contact_by_id(self):
        # Создаем моки для объектов
        mock_session = AsyncMock()
        mock_contact = Contact(id=1)
        
        # Настраиваем возвращаемое значение для метода execute
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_session.execute.return_value = mock_result
        
        # Создаем экземпляр репозитория
        repo = ContactRepository(mock_session)
        
        # Вызываем тестируемый метод
        result = await repo.get_contact_by_id(1, 1)
        
        # Проверяем результат
        assert result == mock_contact
        # Проверяем, что метод execute был вызван
        mock_session.execute.assert_called_once()
    
    async def test_create_contact(self):
        # Создаем моки для объектов
        mock_session = AsyncMock()
        mock_contact = Contact(id=1)
        
        # Патчим модель Contact
        with patch('src.repository.contacts.Contact') as mock_contact_model:
            mock_contact_model.return_value = mock_contact
            
            # Создаем экземпляр репозитория
            repo = ContactRepository(mock_session)
            
            # Создаем данные контакта
            contact_data = ContactModel(
                name="Test",
                surname="Contact",
                email="test@example.com",
                phone="1234567890",
                birthday=date(1990, 1, 1)
            )
            
            # Вызываем тестируемый метод
            result = await repo.create_contact(contact_data, 1)
            
            # Проверяем результат
            assert result == mock_contact
            # Проверяем, что методы сессии были вызваны
            mock_session.add.assert_called_once_with(mock_contact)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_contact)
    
    async def test_update_contact(self):
        # Создаем моки для объектов
        mock_session = AsyncMock()
        mock_contact = Contact(id=1, name="Test")
        
        # Настраиваем возвращаемое значение для метода execute
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_session.execute.return_value = mock_result
        
        # Создаем экземпляр репозитория
        repo = ContactRepository(mock_session)
        
        # Создаем данные для обновления
        contact_update = ContactUpdate(name="Updated")
        
        # Вызываем тестируемый метод
        result = await repo.update_contact(1, contact_update, 1)
        
        # Проверяем результат
        assert result.name == "Updated"
        # Проверяем, что методы сессии были вызваны
        mock_session.commit.assert_called_once()
    
    async def test_delete_contact(self):
        # Создаем моки для объектов
        mock_session = AsyncMock()
        mock_contact = Contact(id=1)
        
        # Настраиваем возвращаемое значение для метода execute
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_session.execute.return_value = mock_result
        
        # Создаем экземпляр репозитория
        repo = ContactRepository(mock_session)
        
        # Вызываем тестируемый метод
        result = await repo.delete_contact(1, 1)
        
        # Проверяем результат
        assert result == mock_contact
        # Проверяем, что методы сессии были вызваны
        mock_session.delete.assert_called_once_with(mock_contact)
        mock_session.commit.assert_called_once()
    
    async def test_search_contacts(self):
        # Создаем моки для объектов
        mock_session = AsyncMock()
        mock_contacts = [Contact(id=1), Contact(id=2)]
        
        # Настраиваем возвращаемое значение для метода execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_contacts
        mock_session.execute.return_value = mock_result
        
        # Создаем экземпляр репозитория
        repo = ContactRepository(mock_session)
        
        # Вызываем тестируемый метод
        result = await repo.search_contacts("test", 1)
        
        # Проверяем результат
        assert result == mock_contacts
        # Проверяем, что метод execute был вызван
        mock_session.execute.assert_called_once()
    
    async def test_get_contacts_by_birthday(self):
        # Создаем моки для объектов
        mock_session = AsyncMock()
        mock_contacts = [Contact(id=1, birthday=date.today()), Contact(id=2, birthday=date.today() + timedelta(days=1))]
        
        # Настраиваем возвращаемое значение для метода execute
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_contacts
        mock_session.execute.return_value = mock_result
        
        # Создаем экземпляр репозитория
        repo = ContactRepository(mock_session)
        
        # Вызываем тестируемый метод
        result = await repo.get_contacts_by_birthday(7, 1)
        
        # Проверяем результат
        assert result == mock_contacts
        # Проверяем, что метод execute был вызван
        mock_session.execute.assert_called_once() 