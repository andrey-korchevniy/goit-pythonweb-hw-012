import pytest
from sqlalchemy import select
from unittest.mock import MagicMock, AsyncMock, patch

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_users(self):
        # Create mocks for objects
        mock_session = AsyncMock()
        mock_users = [User(id=1), User(id=2)]
        
        # Set up return value for execute method
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_users
        mock_session.execute.return_value = mock_result
        
        # Create repository instance
        repo = UserRepository(mock_session)
        
        # Call the tested method
        result = await repo.get_users()
        
        # Check the result
        assert result == mock_users
        # Check that execute method was called
        mock_session.execute.assert_called_once()
    
    async def test_get_user(self):
        # Create mocks for objects
        mock_session = AsyncMock()
        mock_user = User(id=1)
        
        # Set up return value for execute method
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Create repository instance
        repo = UserRepository(mock_session)
        
        # Call the tested method
        result = await repo.get_user(1)
        
        # Check the result
        assert result == mock_user
        # Check that execute method was called
        mock_session.execute.assert_called_once()
    
    async def test_get_user_by_email(self):
        # Create mocks for objects
        mock_session = AsyncMock()
        mock_user = User(id=1, email="test@example.com")
        
        # Set up return value for execute method
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Create repository instance
        repo = UserRepository(mock_session)
        
        # Call the tested method
        result = await repo.get_user_by_email("test@example.com")
        
        # Check the result
        assert result == mock_user
        # Check that execute method was called
        mock_session.execute.assert_called_once()
    
    async def test_create_user(self):
        # Create mocks for objects
        mock_session = AsyncMock()
        mock_user = User(id=1, username="testuser", email="test@example.com")
        
        # Patch User model
        with patch('src.repository.users.User') as mock_user_model:
            mock_user_model.return_value = mock_user
            
            # Create repository instance
            repo = UserRepository(mock_session)
            
            # Create user data
            user_data = UserCreate(username="testuser", email="test@example.com", password="password123")
            
            # Call the tested method
            result = await repo.create_user(user_data)
            
            # Check the result
            assert result == mock_user
            # Check that session methods were called
            mock_session.add.assert_called_once_with(mock_user)
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once_with(mock_user)
    
    async def test_update_avatar_url(self):
        # Create mocks for objects
        mock_session = AsyncMock()
        mock_user = User(id=1, email="test@example.com")
        
        # Set up return value for execute method
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Create repository instance
        repo = UserRepository(mock_session)
        
        # Call the tested method
        avatar_url = "https://example.com/avatar.jpg"
        result = await repo.update_avatar_url("test@example.com", avatar_url)
        
        # Check the result
        assert result == mock_user
        assert mock_user.avatar == avatar_url
        # Check that session methods were called
        mock_session.commit.assert_called_once()
    
    async def test_confirmed_email(self):
        # Create mocks for objects
        mock_session = AsyncMock()
        mock_user = User(id=1, email="test@example.com", confirmed=False)
        
        # Set up return value for execute method
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result
        
        # Create repository instance
        repo = UserRepository(mock_session)
        
        # Call the tested method
        result = await repo.confirmed_email("test@example.com")
        
        # Check the result
        assert mock_user.confirmed == True
        # Check that session methods were called
        mock_session.commit.assert_called_once() 