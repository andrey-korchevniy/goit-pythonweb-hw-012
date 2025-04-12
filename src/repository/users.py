"""
Модуль репозиторію для управління користувачами в базі даних.

Цей модуль містить клас UserRepository, який надає 
методи для роботи з користувачами в базі даних.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserRole
from src.schemas import UserCreate

class UserRepository:
    """
    Репозиторій для управління користувачами в базі даних.
    
    Attributes:
        db: Асинхронна сесія SQLAlchemy для роботи з базою даних.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Ініціалізація репозиторію користувачів.
        
        Args:
            db: Асинхронна сесія SQLAlchemy.
        """
        self.db = db

    async def get_users(self) -> List[User]:
        """
        Отримання списку всіх користувачів.
        
        Returns:
            Список всіх користувачів.
        """
        stmt = select(User)
        users = await self.db.execute(stmt)
        return users.scalars().all()

    async def get_user(self, user_id: int) -> User | None:
        """
        Отримання користувача за його ідентифікатором.
        
        Args:
            user_id: Ідентифікатор користувача.
            
        Returns:
            Користувач із вказаним ідентифікатором або None, якщо користувача не знайдено.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Отримання користувача за його email.
        
        Args:
            email: Email користувача.
            
        Returns:
            Користувач із вказаним email або None, якщо користувача не знайдено.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Отримання користувача за його іменем користувача.
        
        Args:
            username: Ім'я користувача.
            
        Returns:
            Користувач із вказаним іменем або None, якщо користувача не знайдено.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Створення нового користувача.
        
        Args:
            user_data: Модель з даними для створення користувача.
            
        Returns:
            Створений користувач.
        """
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.password,
            role=user_data.role
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
        
    async def confirmed_email(self, email: str) -> None:
        """
        Підтвердження email користувача.
        
        Args:
            email: Email користувача для підтвердження.
            
        Returns:
            None
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()
        
    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Оновлення URL аватару користувача.
        
        Args:
            email: Email користувача.
            url: Новий URL аватару.
            
        Returns:
            Оновлений користувач.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user
        
    async def update_password(self, email: str, hashed_password: str) -> User:
        """
        Оновлення пароля користувача.
        
        Args:
            email: Email користувача.
            hashed_password: Новий хешований пароль.
            
        Returns:
            Оновлений користувач.
        """
        user = await self.get_user_by_email(email)
        user.hashed_password = hashed_password
        await self.db.commit()
        await self.db.refresh(user)
        return user 