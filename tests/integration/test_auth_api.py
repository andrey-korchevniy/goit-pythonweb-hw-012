import pytest
import asyncio
from unittest.mock import patch, MagicMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.services.auth import get_password_hash, create_access_token, create_email_token


def test_register_user(test_client, async_session):
    # Prepare data for registration
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    }
    
    # Create mock for email sending function
    with patch("src.api.auth.send_email") as mock_send_email:
        # Set the mock to not perform actual sending
        mock_send_email.return_value = None
        
        # Execute registration request
        response = test_client.post("/api/auth/register", json=user_data)
        
        # Check result
        assert response.status_code == 201
        data = response.json()
        # Check data in API response (assuming API returns user)
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "password" not in data
        
        # Check that user is created in database
        event_loop = asyncio.get_event_loop()
        
        async def verify_user():
            stmt = select(User).filter_by(email=user_data["email"])
            result = await async_session.execute(stmt)
            db_user = result.scalar_one_or_none()
            return db_user
            
        db_user = event_loop.run_until_complete(verify_user())
        assert db_user is not None
        assert db_user.username == user_data["username"]
        assert not db_user.confirmed  # Email not confirmed
        
        # Check that email sending function was called
        mock_send_email.assert_called_once()


def test_login_user(test_client, async_session):
    # Create user
    event_loop = asyncio.get_event_loop()
    
    # Username, email and password for test user
    username = "testlogin"
    email = "testlogin@example.com"
    password = "password123"
    
    async def create_user():
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in database
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=True)
        async_session.add(user)
        await async_session.commit()
    
    event_loop.run_until_complete(create_user())
    
    # Prepare data for login
    login_data = {
        "username": email,
        "password": password
    }
    
    # Execute login request
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


def test_login_wrong_password(test_client, async_session):
    # Create user
    event_loop = asyncio.get_event_loop()
    
    # Username, email and password for test user
    username = "wrongpasstest"
    email = "wrongpass@example.com"
    password = "correctpassword"
    
    async def create_user():
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in database
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=True)
        async_session.add(user)
        await async_session.commit()
    
    event_loop.run_until_complete(create_user())
    
    # Prepare data for login with incorrect password
    login_data = {
        "username": email,
        "password": "wrongpassword"
    }
    
    # Execute login request
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


def test_confirmed_email(test_client, async_session):
    # Create user with unconfirmed email
    event_loop = asyncio.get_event_loop()
    
    # Username, email and password for test user
    username = "confirmtest"
    email = "confirm@example.com"
    password = "password123"
    
    async def create_user_and_token():
        # Hash the password
        hashed_password = get_password_hash(password)
        
        # Create user in database with confirmed=False
        user = User(username=username, email=email, hashed_password=hashed_password, confirmed=False)
        async_session.add(user)
        await async_session.commit()
        
        # Create token for email confirmation
        token = await create_email_token({"sub": email})
        return token
    
    token = event_loop.run_until_complete(create_user_and_token())
    
    # Execute email confirmation request
    response = test_client.get(f"/api/auth/confirmed_email/{token}")
    
    # Check result
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Email confirmed"
    
    # Check that user's email is confirmed in database
    async def verify_confirmed():
        stmt = select(User).filter_by(email=email)
        result = await async_session.execute(stmt)
        db_user = result.scalar_one_or_none()
        return db_user.confirmed
        
    assert event_loop.run_until_complete(verify_confirmed()) is True 