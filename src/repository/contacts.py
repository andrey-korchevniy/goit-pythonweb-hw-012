"""
Модуль репозиторію для управління контактами в базі даних.

Цей модуль містить клас ContactRepository, який надає 
методи для роботи з контактами в базі даних.
"""

from typing import List, Optional
from datetime import date, timedelta

from sqlalchemy import select, extract, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactModel, ContactUpdate

class ContactRepository:
    """
    Репозиторій для управління контактами в базі даних.
    
    Attributes:
        db: Асинхронна сесія SQLAlchemy для роботи з базою даних.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Ініціалізація репозиторію контактів.
        
        Args:
            session: Асинхронна сесія SQLAlchemy.
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user_id: int) -> List[Contact]:
        """
        Отримання списку контактів з пагінацією.
        
        Args:
            skip: Кількість контактів, які слід пропустити.
            limit: Максимальна кількість контактів для повернення.
            user_id: Ідентифікатор користувача, якому належать контакти.
            
        Returns:
            Список контактів.
        """
        stmt = select(Contact).filter_by(user_id=user_id).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user_id: int) -> Contact | None:
        """
        Отримання контакту за його ідентифікатором.
        
        Args:
            contact_id: Ідентифікатор контакту.
            user_id: Ідентифікатор користувача, якому належить контакт.
            
        Returns:
            Контакт із вказаним ідентифікатором або None, якщо контакт не знайдено.
        """
        stmt = select(Contact).filter_by(id=contact_id, user_id=user_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contacts_by_birthday(self, days: int = 7, user_id: int = None) -> List[Contact]:
        """
        Отримання списку контактів з днями народження у вказаному діапазоні днів.
        
        Args:
            days: Кількість днів для пошуку майбутніх днів народження (за замовчуванням 7).
            user_id: Ідентифікатор користувача (якщо None, шукаємо для всіх користувачів).
            
        Returns:
            Список контактів з майбутніми днями народження.
        """
        today = date.today()
        end_date = today + timedelta(days=days)
        
        base_query = select(Contact)
        
        if user_id is not None:
            base_query = base_query.filter(Contact.user_id == user_id)
        
        if today.month == 12 and end_date.month < 12:
            december_stmt = base_query.where(
                extract('month', Contact.birthday) == 12,
                extract('day', Contact.birthday) >= today.day,
                extract('day', Contact.birthday) <= 31
            )
            
            january_stmt = base_query.where(
                extract('month', Contact.birthday) == 1,
                extract('day', Contact.birthday) >= 1,
                extract('day', Contact.birthday) <= end_date.day
            )
            
            dec_result = await self.db.execute(december_stmt)
            jan_result = await self.db.execute(january_stmt)
            
            return list(dec_result.scalars().all()) + list(jan_result.scalars().all())
        else:
            if today.month == end_date.month:
                stmt = base_query.where(
                    extract('month', Contact.birthday) == today.month,
                    extract('day', Contact.birthday) >= today.day,
                    extract('day', Contact.birthday) <= end_date.day
                )
            else:
                stmt = base_query.where(
                    or_(
                        and_(
                            extract('month', Contact.birthday) == today.month,
                            extract('day', Contact.birthday) >= today.day
                        ),
                        and_(
                            extract('month', Contact.birthday) == end_date.month,
                            extract('day', Contact.birthday) <= end_date.day
                        )
                    )
                )
            
            result = await self.db.execute(stmt)
            return result.scalars().all()

    async def search_contacts(self, search_term: str, user_id: int) -> List[Contact]:
        """
        Пошук контактів за ім'ям, прізвищем або email.
        
        Args:
            search_term: Пошуковий запит.
            user_id: Ідентифікатор користувача, якому належать контакти.
            
        Returns:
            Список контактів, що відповідають пошуковому запиту.
        """
        search_pattern = f"%{search_term}%"
        stmt = select(Contact).filter_by(user_id=user_id).where(
            or_(
                Contact.name.ilike(search_pattern),
                Contact.surname.ilike(search_pattern),
                Contact.email.ilike(search_pattern)
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_contact(self, body: ContactModel, user_id: int) -> Contact:
        """
        Створення нового контакту.
        
        Args:
            body: Модель з даними контакту.
            user_id: Ідентифікатор користувача, якому буде належати контакт.
            
        Returns:
            Створений контакт.
        """
        contact_data = body.model_dump(exclude_unset=True)
        contact = Contact(**contact_data, user_id=user_id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate, user_id: int) -> Optional[Contact]:
        """
        Оновлення існуючого контакту.
        
        Args:
            contact_id: Ідентифікатор контакту для оновлення.
            body: Модель з новими даними контакту.
            user_id: Ідентифікатор користувача, якому належить контакт.
            
        Returns:
            Оновлений контакт або None, якщо контакт не знайдено.
        """
        contact = await self.get_contact_by_id(contact_id, user_id)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                if value is not None:
                    setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def delete_contact(self, contact_id: int, user_id: int) -> Optional[Contact]:
        """
        Видалення контакту.
        
        Args:
            contact_id: Ідентифікатор контакту для видалення.
            user_id: Ідентифікатор користувача, якому належить контакт.
            
        Returns:
            Видалений контакт або None, якщо контакт не знайдено.
        """
        contact = await self.get_contact_by_id(contact_id, user_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact 