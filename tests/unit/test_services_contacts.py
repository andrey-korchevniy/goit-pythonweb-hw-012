import pytest
import unittest.mock
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.contacts import ContactService
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate


@pytest.mark.asyncio
class TestContactsService:
    async def test_get_contacts(self):
        # Create mock for contacts repository
        mock_repo = AsyncMock()
        # Specify return value for get_contacts method
        mock_contacts = [MagicMock(id=1), MagicMock(id=2)]
        mock_repo.get_contacts = AsyncMock(return_value=mock_contacts)
        
        # Create service instance with repository mock
        service = ContactService(mock_repo)
        
        # Call the tested method
        result = await service.get_contacts(0, 10, 1)
        
        # Check that the result matches expected
        assert result == mock_contacts
        # Check that repository method was called with correct parameters
        mock_repo.get_contacts.assert_called_once_with(0, 10, 1)
    
    async def test_get_contact(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for get_contact_by_id method
        mock_contact = MagicMock(id=1)
        mock_repo.get_contact_by_id = AsyncMock(return_value=mock_contact)
        
        # Create service instance with repository mock
        service = ContactService(mock_repo)
        
        # Call the tested method
        result = await service.get_contact(1, 1)
        
        # Check result
        assert result == mock_contact
        # Check that repository method was called with correct parameters
        mock_repo.get_contact_by_id.assert_called_once_with(1, 1)
    
    async def test_create_contact(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for create_contact method
        mock_contact = MagicMock(id=1)
        mock_repo.create_contact = AsyncMock(return_value=mock_contact)
        
        # Create data for contact creation
        contact_data = ContactModel(
            name="Test",
            surname="Contact",
            email="test@example.com",
            phone="1234567890",
            birthday=date(1990, 1, 1)
        )
        
        # Create service instance with repository mock
        service = ContactService(mock_repo)
        
        # Call the tested method
        result = await service.create_contact(contact_data, 1)
        
        # Check result
        assert result == mock_contact
        # Check that repository method was called with correct parameters
        mock_repo.create_contact.assert_called_once_with(contact_data, 1)
    
    async def test_update_contact(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for update_contact method
        mock_contact = MagicMock(id=1)
        mock_repo.update_contact = AsyncMock(return_value=mock_contact)
        
        # Create data for contact update
        contact_update = ContactUpdate(name="Updated")
        
        # Create service instance with repository mock
        service = ContactService(mock_repo)
        
        # Call the tested method
        result = await service.update_contact(1, contact_update, 1)
        
        # Check result
        assert result == mock_contact
        # Check that repository method was called with correct parameters
        mock_repo.update_contact.assert_called_once_with(1, contact_update, 1)
    
    async def test_delete_contact(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for delete_contact method
        mock_contact = MagicMock(id=1)
        mock_repo.delete_contact = AsyncMock(return_value=mock_contact)
        
        # Create service instance with repository mock
        service = ContactService(mock_repo)
        
        # Call the tested method
        result = await service.delete_contact(1, 1)
        
        # Check result
        assert result == mock_contact
        # Check that repository method was called with correct parameters
        mock_repo.delete_contact.assert_called_once_with(1, 1)
    
    async def test_search_contacts(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for search_contacts method
        mock_contacts = [MagicMock(id=1), MagicMock(id=2)]
        mock_repo.search_contacts = AsyncMock(return_value=mock_contacts)
        
        # Create service instance with repository mock
        service = ContactService(mock_repo)
        
        # Call the tested method
        result = await service.search_contacts("test", 1)
        
        # Check result
        assert result == mock_contacts
        # Check that repository method was called with correct parameters
        mock_repo.search_contacts.assert_called_once_with("test", 1)
    
    async def test_get_contacts_by_birthday(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for get_contacts_by_birthday method
        mock_contacts = [MagicMock(id=1), MagicMock(id=2)]
        mock_repo.get_contacts_by_birthday = AsyncMock(return_value=mock_contacts)
        
        # Create service instance with repository mock
        service = ContactService(mock_repo)
        
        # Call the tested method
        result = await service.get_contacts_by_birthday(7, 1)
        
        # Check result
        assert result == mock_contacts
        # Check that repository method was called with correct parameters
        mock_repo.get_contacts_by_birthday.assert_called_once_with(7, 1) 