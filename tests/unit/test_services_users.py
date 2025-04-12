import pytest
import unittest.mock
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.services.users import UserService
from src.repository.users import UserRepository
from src.schemas import UserCreate, UserResponse


@pytest.mark.asyncio
class TestUserService:
    async def test_create_user(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for create_user method
        mock_user = MagicMock(id=1)
        mock_repo.create_user = AsyncMock(return_value=mock_user)
        
        # Create user data
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        # Create service instance with repository mock
        service = UserService(mock_repo)
        
        # Call the tested method
        result = await service.create_user(user_data)
        
        # Check result
        assert result == mock_user
        # Check that repository method was called with correct parameters
        mock_repo.create_user.assert_called_once_with(user_data)
    
    async def test_get_user_by_email(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for get_user_by_email method
        mock_user = MagicMock(id=1)
        mock_repo.get_user_by_email = AsyncMock(return_value=mock_user)
        
        # Create service instance with repository mock
        service = UserService(mock_repo)
        
        # Call the tested method
        result = await service.get_user_by_email("test@example.com")
        
        # Check result
        assert result == mock_user
        # Check that repository method was called with correct parameters
        mock_repo.get_user_by_email.assert_called_once_with("test@example.com")
    
    async def test_get_user_by_username(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for get_user_by_username method
        mock_user = MagicMock(id=1)
        mock_repo.get_user_by_username = AsyncMock(return_value=mock_user)
        
        # Create service instance with repository mock
        service = UserService(mock_repo)
        
        # Call the tested method
        result = await service.get_user_by_username("testuser")
        
        # Check result
        assert result == mock_user
        # Check that repository method was called with correct parameters
        mock_repo.get_user_by_username.assert_called_once_with("testuser")
    
    async def test_get_users(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for get_users method
        mock_users = [MagicMock(id=1), MagicMock(id=2)]
        mock_repo.get_users = AsyncMock(return_value=mock_users)
        
        # Create service instance with repository mock
        service = UserService(mock_repo)
        
        # Call the tested method
        result = await service.get_users()
        
        # Check result
        assert result == mock_users
        # Check that repository method was called
        mock_repo.get_users.assert_called_once()
    
    async def test_get_user(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for get_user method
        mock_user = MagicMock(id=1)
        mock_repo.get_user = AsyncMock(return_value=mock_user)
        
        # Create service instance with repository mock
        service = UserService(mock_repo)
        
        # Call the tested method
        result = await service.get_user(1)
        
        # Check result
        assert result == mock_user
        # Check that repository method was called with correct parameters
        mock_repo.get_user.assert_called_once_with(1)
    
    async def test_confirmed_email(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for confirmed_email method
        mock_repo.confirmed_email = AsyncMock(return_value=True)
        
        # Create service instance with repository mock
        service = UserService(mock_repo)
        
        # Call the tested method
        await service.confirmed_email("test@example.com")
        
        # Check that repository method was called with correct parameters
        mock_repo.confirmed_email.assert_called_once_with("test@example.com")
    
    async def test_update_avatar_url(self):
        # Create mock for repository
        mock_repo = AsyncMock()
        # Specify return value for update_avatar_url method
        mock_user = MagicMock(id=1, avatar="https://example.com/avatar.jpg")
        mock_repo.update_avatar_url = AsyncMock(return_value=mock_user)
        
        # Create service instance with repository mock
        service = UserService(mock_repo)
        
        # Call the tested method
        result = await service.update_avatar_url("test@example.com", "https://example.com/avatar.jpg")
        
        # Check result
        assert result == mock_user
        # Check that repository method was called with correct parameters
        mock_repo.update_avatar_url.assert_called_once_with("test@example.com", "https://example.com/avatar.jpg") 