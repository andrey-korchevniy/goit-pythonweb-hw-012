import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate

@pytest.mark.asyncio
class TestContactRepository:
    async def test_get_contacts(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user", email="test@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        user_id = user.id
        
        # Create test contacts
        contacts_data = [
            {
                "name": "John", 
                "surname": "Doe", 
                "email": "john@example.com", 
                "phone": "1234567890", 
                "birthday": date(1990, 1, 1), 
                "user_id": user_id
            },
            {
                "name": "Jane", 
                "surname": "Smith", 
                "email": "jane@example.com", 
                "phone": "0987654321", 
                "birthday": date(1992, 5, 20), 
                "user_id": user_id
            }
        ]
        
        for contact_data in contacts_data:
            async_session.add(Contact(**contact_data))
        await async_session.commit()
        
        # Act
        contacts = await contact_repo.get_contacts(skip=0, limit=10, user_id=user_id)
        
        # Assert
        assert len(contacts) == 2
        assert contacts[0].name == "John"
        assert contacts[1].name == "Jane"
    
    async def test_get_contact_by_id(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user2", email="test2@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        user_id = user.id
        
        # Create a test contact
        contact_data = {
            "name": "Alice", 
            "surname": "Johnson", 
            "email": "alice@example.com", 
            "phone": "5556667777", 
            "birthday": date(1985, 3, 15), 
            "user_id": user_id
        }
        
        contact = Contact(**contact_data)
        async_session.add(contact)
        await async_session.commit()
        await async_session.refresh(contact)
        
        # Act
        result = await contact_repo.get_contact_by_id(contact.id, user_id)
        
        # Assert
        assert result is not None
        assert result.name == contact_data["name"]
        assert result.email == contact_data["email"]
    
    async def test_get_nonexistent_contact(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user3", email="test3@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        # Act
        result = await contact_repo.get_contact_by_id(999, user.id)
        
        # Assert
        assert result is None
    
    async def test_get_contacts_by_birthday(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user4", email="test4@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        user_id = user.id
        
        # Today and upcoming dates for testing
        today = date.today()
        tomorrow = today + timedelta(days=1)
        next_week = today + timedelta(days=7)
        month_later = today + timedelta(days=30)
        
        # Create birthday adjusted to current year
        def birthday_for(target_date):
            target_month = target_date.month
            target_day = target_date.day
            year = date.today().year
            if date.today() > date(year, target_month, target_day):
                year += 1
            return date(1990, target_month, target_day)  # Using 1990 as birth year
        
        # Create test contacts with specific birthdays
        contacts_data = [
            {
                "name": "Today", 
                "surname": "Birthday", 
                "email": "today@example.com", 
                "phone": "1111111111", 
                "birthday": birthday_for(today), 
                "user_id": user_id
            },
            {
                "name": "Tomorrow", 
                "surname": "Birthday", 
                "email": "tomorrow@example.com", 
                "phone": "2222222222", 
                "birthday": birthday_for(tomorrow), 
                "user_id": user_id
            },
            {
                "name": "NextWeek", 
                "surname": "Birthday", 
                "email": "nextweek@example.com", 
                "phone": "3333333333", 
                "birthday": birthday_for(next_week), 
                "user_id": user_id
            },
            {
                "name": "Later", 
                "surname": "Birthday", 
                "email": "later@example.com", 
                "phone": "4444444444", 
                "birthday": birthday_for(month_later), 
                "user_id": user_id
            }
        ]
        
        for contact_data in contacts_data:
            async_session.add(Contact(**contact_data))
        await async_session.commit()
        
        # Act - Get contacts with birthdays in the next 7 days
        upcoming_contacts = await contact_repo.get_contacts_by_birthday(days=7, user_id=user_id)
        
        # Assert
        # We should get 3 contacts (today, tomorrow, and one week from now)
        contact_emails = [contact.email for contact in upcoming_contacts]
        assert len(upcoming_contacts) == 3
        assert "today@example.com" in contact_emails
        assert "tomorrow@example.com" in contact_emails
        assert "nextweek@example.com" in contact_emails
        assert "later@example.com" not in contact_emails
    
    async def test_search_contacts(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user5", email="test5@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        user_id = user.id
        
        # Create test contacts for search
        contacts_data = [
            {
                "name": "Robert", 
                "surname": "Smith", 
                "email": "robert@example.com", 
                "phone": "1112223333", 
                "birthday": date(1980, 5, 15), 
                "user_id": user_id
            },
            {
                "name": "Maria", 
                "surname": "Rodriguez", 
                "email": "maria@example.com", 
                "phone": "4445556666", 
                "birthday": date(1992, 8, 20), 
                "user_id": user_id
            },
            {
                "name": "Steve", 
                "surname": "Robertson", 
                "email": "steve@example.com", 
                "phone": "7778889999", 
                "birthday": date(1975, 3, 10), 
                "user_id": user_id
            }
        ]
        
        for contact_data in contacts_data:
            async_session.add(Contact(**contact_data))
        await async_session.commit()
        
        # Act - Search by name
        name_results = await contact_repo.search_contacts("Rob", user_id)
        
        # Assert
        assert len(name_results) == 2  # Should match Robert and Robertson
        name_result_names = {contact.name for contact in name_results}
        assert "Robert" in name_result_names
        assert "Steve" in name_result_names
        
        # Act - Search by email
        email_results = await contact_repo.search_contacts("maria", user_id)
        
        # Assert
        assert len(email_results) == 1
        assert email_results[0].name == "Maria"
    
    async def test_create_contact(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user6", email="test6@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        user_id = user.id
        
        # Create contact data
        contact_data = ContactModel(
            name="New",
            surname="Contact",
            email="new@example.com",
            phone="9876543210",
            birthday=date(2000, 1, 1)
        )
        
        # Act
        contact = await contact_repo.create_contact(contact_data, user_id)
        
        # Assert
        assert contact.name == contact_data.name
        assert contact.surname == contact_data.surname
        assert contact.email == contact_data.email
        assert contact.phone == contact_data.phone
        assert contact.birthday == contact_data.birthday
        assert contact.user_id == user_id
        
        # Verify the contact was created in the database
        stmt = select(Contact).filter_by(email=contact_data.email)
        result = await async_session.execute(stmt)
        db_contact = result.scalar_one_or_none()
        assert db_contact is not None
        assert db_contact.name == contact_data.name
    
    async def test_update_contact(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user7", email="test7@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        user_id = user.id
        
        # Create a test contact
        contact_data = {
            "name": "Original", 
            "surname": "Name", 
            "email": "original@example.com", 
            "phone": "1234567890", 
            "birthday": date(1990, 1, 1), 
            "user_id": user_id
        }
        
        contact = Contact(**contact_data)
        async_session.add(contact)
        await async_session.commit()
        await async_session.refresh(contact)
        
        # Update data
        update_data = ContactUpdate(
            name="Updated",
            surname="Name",
            additional_data="Some additional information"
        )
        
        # Act
        updated_contact = await contact_repo.update_contact(contact.id, update_data, user_id)
        
        # Assert
        assert updated_contact is not None
        assert updated_contact.name == "Updated"
        assert updated_contact.surname == "Name"
        assert updated_contact.email == contact_data["email"]  # Unchanged
        assert updated_contact.additional_data == "Some additional information"
    
    async def test_delete_contact(self, async_session):
        # Arrange
        contact_repo = ContactRepository(async_session)
        
        # Create a test user
        user = User(username="test_user8", email="test8@example.com", hashed_password="password")
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        
        user_id = user.id
        
        # Create a test contact
        contact_data = {
            "name": "ToDelete", 
            "surname": "Contact", 
            "email": "delete@example.com", 
            "phone": "1231231231", 
            "birthday": date(1995, 5, 5), 
            "user_id": user_id
        }
        
        contact = Contact(**contact_data)
        async_session.add(contact)
        await async_session.commit()
        await async_session.refresh(contact)
        
        contact_id = contact.id
        
        # Act
        deleted_contact = await contact_repo.delete_contact(contact_id, user_id)
        
        # Assert
        assert deleted_contact is not None
        assert deleted_contact.name == contact_data["name"]
        
        # Verify the contact was deleted from the database
        stmt = select(Contact).filter_by(id=contact_id)
        result = await async_session.execute(stmt)
        db_contact = result.scalar_one_or_none()
        assert db_contact is None 