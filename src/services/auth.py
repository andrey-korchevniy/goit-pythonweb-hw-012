from datetime import datetime, timedelta
from datetime import timezone as tz
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import UserRole
from src.repository.users import UserRepository
from src.schemas import TokenData, UserResponse
from src.services.redis import get_cached_user, cache_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def create_access_token(data: dict, expires_delta: Optional[float] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(tz.UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(tz.UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def create_email_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz.UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(tz.UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def create_reset_password_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(tz.UTC) + timedelta(hours=1)
    to_encode.update({"iat": datetime.now(tz.UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload["sub"]
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email confirmation",
        )

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Failed to verify credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Try to get user from cache
    cached_user = await get_cached_user(token_data.username)
    
    if cached_user:
        user = UserResponse(**cached_user)
        return user
    
    # If user is not in cache, get from database
    user_repository = UserRepository(db)
    user = await user_repository.get_user_by_username(token_data.username)
    
    if user is None:
        raise credentials_exception
    
    # Cache user for subsequent requests
    await cache_user(user)
    
    return user

async def get_admin_user(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator rights are required to perform this operation"
        )
    return current_user