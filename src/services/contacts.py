from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def get_contacts(self, skip: int, limit: int, user_id: int) -> List:
        return await self.repository.get_contacts(skip, limit, user_id)

    async def get_contact(self, contact_id: int, user_id: int):
        return await self.repository.get_contact_by_id(contact_id, user_id)

    async def create_contact(self, body: ContactModel, user_id: int):
        return await self.repository.create_contact(body, user_id)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user_id: int):
        return await self.repository.update_contact(contact_id, body, user_id)

    async def delete_contact(self, contact_id: int, user_id: int):
        return await self.repository.delete_contact(contact_id, user_id)

    async def search_contacts(self, search_term: str, user_id: int):
        return await self.repository.search_contacts(search_term, user_id)

    async def get_contacts_by_birthday(self, days: int = 7, user_id: int = None):
        return await self.repository.get_contacts_by_birthday(days, user_id) 