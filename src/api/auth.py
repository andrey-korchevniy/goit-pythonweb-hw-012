"""
API module for user authorization and authentication.

This module contains endpoints for registration, authentication, email confirmation,
and user account management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import UserCreate, UserResponse, Token, RequestEmail, RequestPasswordReset, ResetPassword
from src.services.auth import get_current_user, get_password_hash, verify_password, create_access_token, get_email_from_token, get_admin_user
from src.services.users import UserService
from src.services.email import send_email, send_reset_password_email
from src.services.redis import cache_user, invalidate_user_cache

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate, 
    background_tasks: BackgroundTasks, 
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        body: Data for creating a new user.
        background_tasks: Object for background tasks.
        request: Request object for getting the base URL.
        db: Database session.
        
    Returns:
        The registered user object.
        
    Raises:
        HTTPException: If a user with the same email or username already exists.
    """
    user_service = UserService(db)
    
    existing_user = await user_service.get_user_by_email(body.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="A user with the email already exist"
        )
    
    username_exists = await user_service.get_user_by_username(body.username)
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with the name already exist"
        )
    
    hashed_password = get_password_hash(body.password)
    body.password = hashed_password
    
    new_user = await user_service.create_user(body)
    
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, str(request.base_url)
    )
    
    return new_user

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and issue an access token.
    
    Args:
        form_data: Form data for login (username and password).
        db: Database session.
        
    Returns:
        Access token for the authenticated user.
        
    Raises:
        HTTPException: If authentication data is incorrect or email is not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email is not confirmed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Cache user in Redis
    await cache_user(user)
    
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm user's email using a token.
    
    Args:
        token: Token for email confirmation.
        db: Database session.
        
    Returns:
        Message about successful email confirmation.
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    
    await user_service.confirmed_email(email)
    
    # Invalidate user cache as their status has changed
    await invalidate_user_cache(user.username)
    
    return {"message": "Your email is  confirmed"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request for resending the email confirmation letter.
    
    Args:
        body: Request data (email).
        background_tasks: Object for background tasks.
        request: Request object for getting the base URL.
        db: Database session.
        
    Returns:
        Message about sending the letter.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and user.confirmed:
        return {"message": "Your email is already confirmed"}
    
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    
    return {"message": "Check your email for confirmation"}

@router.post("/request-password-reset")
async def request_password_reset(
    body: RequestPasswordReset,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request for password reset.
    
    Args:
        body: Request data (email).
        background_tasks: Object for background tasks.
        request: Request object for getting the base URL.
        db: Database session.
        
    Returns:
        Message about sending the password reset letter.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    
    if user:
        if not user.confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not confirmed. Please confirm your email first."
            )
        
        background_tasks.add_task(
            send_reset_password_email, user.email, user.username, str(request.base_url)
        )
    
    return {"message": "If your email is registered in the system, you will receive instructions for password reset"}

@router.post("/reset-password")
async def reset_password(
    body: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using a token.
    
    Args:
        body: Data for password reset (token, new password).
        db: Database session.
        
    Returns:
        Message about successful password reset.
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist.
    """
    try:
        email = await get_email_from_token(body.token)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token for password reset"
        )
    
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
    
    await user_service.update_password(email, body.password)
    
    # Invalidate user cache as their password has changed
    await invalidate_user_cache(user.username)
    
    return {"message": "Password successfully changed"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user's data.
    
    Args:
        current_user: Current user object obtained from the token.
        
    Returns:
        Current user's data.
    """
    return current_user 