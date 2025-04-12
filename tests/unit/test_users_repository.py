import pytest
from datetime import datetime
import unittest.mock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate

@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_users(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        users_data = [
            {"username": "test1", "email": "test1@example.com", "hashed_password": "password1"},
            {"username": "test2", "email": "test2@example.com", "hashed_password": "password2"}
        ]
        for user_data in users_data:
            async_session.add(User(**user_data))
        await async_session.commit()
        
        # Act
        users = await user_repo.get_users()
        
        # Assert
        assert len(users) == 2
        assert users[0].username == "test1"
        assert users[1].username == "test2"
    
    async def test_get_user(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        user_data = {"username": "test_user", "email": "test@example.com", "hashed_password": "password"}
        user = User(**user_data)
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        # Act
        result = await user_repo.get_user(user.id)
        
        # Assert
        assert result is not None
        assert result.username == user_data["username"]
        assert result.email == user_data["email"]
    
    async def test_get_nonexistent_user(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        
        # Act
        result = await user_repo.get_user(999)
        
        # Assert
        assert result is None
    
    async def test_get_user_by_email(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        email = "unique@example.com"
        user_data = {"username": "unique_user", "email": email, "hashed_password": "password"}
        user = User(**user_data)
        async_session.add(user)
        await async_session.commit()
        
        # Act
        result = await user_repo.get_user_by_email(email)
        
        # Assert
        assert result is not None
        assert result.email == email
        assert result.username == user_data["username"]
    
    async def test_get_user_by_username(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        username = "special_username"
        user_data = {"username": username, "email": "special@example.com", "hashed_password": "password"}
        user = User(**user_data)
        async_session.add(user)
        await async_session.commit()
        
        # Act
        result = await user_repo.get_user_by_username(username)
        
        # Assert
        assert result is not None
        assert result.username == username
        assert result.email == user_data["email"]
    
    async def test_create_user(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        user_data = UserCreate(
            username="new_user",
            email="new@example.com",
            password="securepassword"
        )
        
        # Act
        user = await user_repo.create_user(user_data)
        
        # Assert
        assert user.username == user_data.username
        assert user.email == user_data.email
        assert user.hashed_password == user_data.password  # In the test, password is not hashed
        
        # Check that the user is actually created in the database
        stmt = select(User).filter_by(email=user_data.email)
        result = await async_session.execute(stmt)
        db_user = result.scalar_one_or_none()
        assert db_user is not None
        assert db_user.username == user_data.username
    
    async def test_confirmed_email(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        email = "confirm@example.com"
        user_data = {"username": "confirm_user", "email": email, "hashed_password": "password", "confirmed": False}
        user = User(**user_data)
        async_session.add(user)
        await async_session.commit()
        
        # Act
        await user_repo.confirmed_email(email)
        
        # Assert
        stmt = select(User).filter_by(email=email)
        result = await async_session.execute(stmt)
        updated_user = result.scalar_one_or_none()
        assert updated_user.confirmed is True
    
    async def test_update_avatar_url(self, async_session):
        # Arrange
        user_repo = UserRepository(async_session)
        email = "avatar@example.com"
        user_data = {"username": "avatar_user", "email": email, "hashed_password": "password"}
        user = User(**user_data)
        async_session.add(user)
        await async_session.commit()
        
        new_avatar_url = "https://example.com/avatar.jpg"
        
        # Act
        updated_user = await user_repo.update_avatar_url(email, new_avatar_url)
        
        # Assert
        assert updated_user.avatar == new_avatar_url
        
        # Check that URL is actually updated in the database
        stmt = select(User).filter_by(email=email)
        result = await async_session.execute(stmt)
        db_user = result.scalar_one_or_none()
        assert db_user.avatar == new_avatar_url 