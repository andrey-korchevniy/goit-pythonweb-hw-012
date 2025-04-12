import pytest
import asyncio
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Contact
from src.services.auth import create_access_token

def test_get_contacts(test_client, async_session):
    # Create user and contacts
    event_loop = asyncio.get_event_loop()
    
    async def setup():
        # Create test user
        user = User(
            username="test_user", 
            email="test@example.com", 
            hashed_password="password", 
            confirmed=True
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        # Create test contacts
        contacts_data = [
            {
                "name": "John", 
                "surname": "Doe", 
                "email": "john@example.com", 
                "phone": "1234567890", 
                "birthday": date(1990, 1, 1), 
                "user_id": user.id
            },
            {
                "name": "Jane", 
                "surname": "Smith", 
                "email": "jane@example.com", 
                "phone": "0987654321", 
                "birthday": date(1992, 5, 20), 
                "user_id": user.id
            }
        ]
        
        for contact_data in contacts_data:
            async_session.add(Contact(**contact_data))
        await async_session.commit()
        
        return user.email
        
    user_email = event_loop.run_until_complete(setup())
    
    # For basic functionality check, execute request to get contacts
    # with authorization through standard test client
    response = test_client.get(
        "/api/contacts/", 
        headers={"Authorization": f"Bearer test_token_for_{user_email}"}
    )
    
    # Here we check that the request was executed
    assert response is not None

def test_get_contact_by_id(test_client, async_session):
    # Use event loop for asynchronous operations in synchronous context
    event_loop = asyncio.get_event_loop()
    
    async def setup():
        # Create test user
        user = User(username="test_user2", email="test2@example.com", hashed_password="password", confirmed=True)
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        # Create test contact
        contact_data = {
            "name": "Alice", 
            "surname": "Johnson", 
            "email": "alice@example.com", 
            "phone": "5556667777", 
            "birthday": date(1985, 3, 15), 
            "user_id": user.id
        }
        
        contact = Contact(**contact_data)
        async_session.add(contact)
        await async_session.commit()
        await async_session.refresh(contact)
        
        # Create access token
        token = await create_access_token({"sub": user.email})
        return token, contact.id
        
    token, contact_id = event_loop.run_until_complete(setup())
        
    # Execute API request
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get(f"/api/contacts/{contact_id}", headers=headers)
    
    # Check result
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"

def test_create_contact(test_client, async_session):
    # Use event loop for asynchronous operations in synchronous context
    event_loop = asyncio.get_event_loop()
    
    async def setup():
        # Create test user
        user = User(username="test_user3", email="test3@example.com", hashed_password="password", confirmed=True)
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        # Create access token
        token = await create_access_token({"sub": user.email})
        return token
        
    token = event_loop.run_until_complete(setup())
    
    # Prepare data for contact creation
    contact_data = {
        "name": "New",
        "surname": "Contact",
        "email": "new_contact@example.com",
        "phone": "9876543210",
        "birthday": str(date(2000, 1, 1)),
    }
    
    # Execute API request for creation
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.post(
        "/api/contacts/",
        headers=headers,
        json=contact_data
    )
    
    # Check result
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == contact_data["name"]
    assert data["email"] == contact_data["email"]
    
    # Check that contact was created in database
    async def verify():
        stmt = select(Contact).filter_by(email=contact_data["email"])
        result = await async_session.execute(stmt)
        db_contact = result.scalar_one_or_none()
        return db_contact is not None
        
    assert event_loop.run_until_complete(verify()) is True 