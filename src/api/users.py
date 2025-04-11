from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserResponse
from src.services.auth import get_current_user
from src.services.users import UserService
from src.services.rate_limiter import RateLimiter
from src.services.upload_file import UploadFileService
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])

rate_limiter = RateLimiter(times=10, seconds=60)

async def rate_limit(request: Request):
    return await rate_limiter(request, "/api/users/me")

@router.get("/me", response_model=UserResponse, dependencies=[Depends(rate_limit)])
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    upload_service = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    )
    
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 
                           detail="Поддерживаются только форматы изображений: jpeg, png, gif")
    
    avatar_url = upload_service.upload_file(file, current_user.username)
    
    user_service = UserService(db)
    user = await user_service.update_avatar_url(current_user.email, avatar_url)
    
    return user 