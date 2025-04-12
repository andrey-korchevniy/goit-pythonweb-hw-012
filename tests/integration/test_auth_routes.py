import pytest
from datetime import date
import json
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from jose import jwt

from src.database.models import User
from src.services.auth import get_password_hash, create_access_token, create_email_token
from src.conf.config import settings

# Constants for JWT
JWT_SECRET = settings.JWT_SECRET
JWT_ALGORITHM = settings.JWT_ALGORITHM

@pytest.mark.asyncio
class TestAuthRoutes:
    async def test_register_user(self, client, async_session):
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        with patch("src.api.auth.send_email", new_callable=AsyncMock) as mock_send_email:
            mock_send_email.return_value = None
            
            # Act
            response = await client.post("/api/auth/register", json=user_data)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["user"]["email"] == user_data["email"]
            assert data["user"]["username"] == user_data["username"]
            assert "password" not in data["user"]
            
            # Verify the user was created in the database
            stmt = select(User).filter_by(email=user_data["email"])
            result = await async_session.execute(stmt)
            db_user = result.scalar_one_or_none()
            assert db_user is not None
            assert db_user.username == user_data["username"]
            assert not db_user.confirmed  # Email not confirmed yet
            
            # Verify email was sent
            mock_send_email.assert_called_once()
    
    async def test_login_user(self, client, async_session):
        # Arrange
        # Create a test user with a known password
        username = "testlogin"
        email = "testlogin@example.com"
        password = "password123"
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in the database
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=True)
        async_session.add(user)
        await async_session.commit()
        
        # Prepare login data
        login_data = {
            "username": email,
            "password": password
        }
        
        # Act
        response = await client.post("/api/auth/login", 
                                    data=login_data,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_wrong_password(self, client, async_session):
        # Arrange
        # Create a test user
        username = "wrongpasstest"
        email = "wrongpass@example.com"
        password = "correctpassword"
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in the database
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=True)
        async_session.add(user)
        await async_session.commit()
        
        # Prepare login data with wrong password
        login_data = {
            "username": email,
            "password": "wrongpassword"
        }
        
        # Act
        response = await client.post("/api/auth/login", 
                                    data=login_data,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Invalid email or password"
    
    async def test_login_email_not_confirmed(self, client, async_session):
        # Arrange
        # Create a test user with unconfirmed email
        username = "unconfirmed"
        email = "unconfirmed@example.com"
        password = "password123"
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in the database with confirmed=False
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=False)
        async_session.add(user)
        await async_session.commit()
        
        # Prepare login data
        login_data = {
            "username": email,
            "password": password
        }
        
        # Act
        response = await client.post("/api/auth/login", 
                                    data=login_data,
                                    headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Email not confirmed" in data["detail"]
        
    async def test_refresh_token(self, client, async_session):
        # Arrange
        # Create a test user
        username = "refreshtest"
        email = "refresh@example.com"
        password = "password123"
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in the database
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=True)
        async_session.add(user)
        await async_session.commit()
        
        # Create a valid access token
        access_token = await create_access_token({"sub": email})
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Act
        response = await client.get("/api/auth/refresh_token", headers=headers)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
    async def test_confirmed_email(self, client, async_session):
        # Arrange
        # Create a test user with unconfirmed email
        username = "confirmtest"
        email = "confirm@example.com"
        password = "password123"
        
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in the database with confirmed=False
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=False)
        async_session.add(user)
        await async_session.commit()
        
        # Create a token for email confirmation
        token = await create_email_token({"sub": email})
        
        # Act
        response = await client.get(f"/api/auth/confirmed_email/{token}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Email confirmed"
        
        # Verify user's email is now confirmed in the database
        stmt = select(User).filter_by(email=email)
        result = await async_session.execute(stmt)
        db_user = result.scalar_one_or_none()
        assert db_user.confirmed == True


def test_register_user_integration(test_client):
    """Test for user registration"""
    # Prepare data for request
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }
    
    # Mock email sending function
    with patch("src.api.auth.send_email") as mock_send_email:
        mock_send_email.return_value = None
        
        # Execute request
        response = test_client.post("/api/auth/register", json=user_data)
        
    # Check result
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data


def test_login_user_integration(test_client, async_session):
    """Test for user login with prior database record creation"""
    # Create user through event loop
    event_loop = asyncio.get_event_loop()
    
    # Username and password for test
    username = "testuser"
    email = "test@example.com"
    password = "testpassword"
    
    async def create_user():
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            confirmed=True
        )
        
        async_session.add(user)
        await async_session.commit()
    
    # Execute user creation
    event_loop.run_until_complete(create_user())
    
    # Prepare data for login
    login_data = {
        "username": email,
        "password": password
    }
    
    # Execute request
    response = test_client.post(
        "/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check result
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(test_client, async_session):
    """Test for login with incorrect password"""
    # Create user through event loop
    event_loop = asyncio.get_event_loop()
    
    # Username and password for test
    username = "testuser2"
    email = "test2@example.com"
    password = "correctpassword"
    
    async def create_user():
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            confirmed=True
        )
        
        async_session.add(user)
        await async_session.commit()
    
    # Execute user creation
    event_loop.run_until_complete(create_user())
    
    # Prepare data for login with incorrect password
    login_data = {
        "username": email,
        "password": "wrongpassword"
    }
    
    # Execute request
    response = test_client.post(
        "/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Check result
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Invalid email or password"


def test_get_current_user(test_client, async_session):
    """Test for getting current user"""
    # Create user through event loop
    event_loop = asyncio.get_event_loop()
    
    # Username for test
    username = "testuser3"
    email = "test3@example.com"
    
    async def create_user():
        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password="hashed_password",
            confirmed=True
        )
        
        async_session.add(user)
        await async_session.commit()
        
        # Create access token
        access_token = jwt.encode(
            {"sub": email, "exp": datetime.now() + timedelta(minutes=15)},
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )
        
        return access_token
    
    # Get access token
    access_token = event_loop.run_until_complete(create_user())
    
    # Execute request
    response = test_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Check result
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["username"] == username 