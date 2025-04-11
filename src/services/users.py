from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.users import UserRepository
from src.schemas import UserCreate

class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, user_data: UserCreate):
        return await self.repository.create_user(user_data)

    async def get_user_by_email(self, email: str):
        return await self.repository.get_user_by_email(email)

    async def get_user_by_username(self, username: str):
        return await self.repository.get_user_by_username(username)

    async def get_users(self):
        return await self.repository.get_users()

    async def get_user(self, user_id: int):
        return await self.repository.get_user(user_id)
        
    async def confirmed_email(self, email: str):
        return await self.repository.confirmed_email(email)
        
    async def update_avatar_url(self, email: str, url: str):
        return await self.repository.update_avatar_url(email, url) 