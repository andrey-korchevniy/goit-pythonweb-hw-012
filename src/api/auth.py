"""
Модуль API для авторизації та автентифікації користувачів.

Цей модуль містить ендпоінти для реєстрації, авторизації, підтвердження email та керування 
обліковим записом користувача.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import UserCreate, UserResponse, Token, RequestEmail
from src.services.auth import get_current_user, get_password_hash, verify_password, create_access_token, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate, 
    background_tasks: BackgroundTasks, 
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    """
    Реєстрація нового користувача.
    
    Args:
        body: Дані для створення нового користувача.
        background_tasks: Об'єкт для фонових завдань.
        request: Об'єкт запиту для отримання базового URL.
        db: Сесія бази даних.
        
    Returns:
        Об'єкт зареєстрованого користувача.
        
    Raises:
        HTTPException: Якщо користувач з таким email або ім'ям вже існує.
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
    Автентифікація користувача та видача токена доступу.
    
    Args:
        form_data: Дані форми для входу (ім'я користувача і пароль).
        db: Сесія бази даних.
        
    Returns:
        Токен доступу для автентифікованого користувача.
        
    Raises:
        HTTPException: Якщо дані автентифікації неправильні або email не підтверджено.
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
    
    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Підтвердження email користувача за допомогою токена.
    
    Args:
        token: Токен для підтвердження email.
        db: Сесія бази даних.
        
    Returns:
        Повідомлення про успішне підтвердження email.
        
    Raises:
        HTTPException: Якщо токен недійсний або користувач не існує.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Помилка верифікації"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Your email is  confirmed"}

@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Запит на повторне надсилання листа для підтвердження email.
    
    Args:
        body: Дані запиту (email).
        background_tasks: Об'єкт для фонових завдань.
        request: Об'єкт запиту для отримання базового URL.
        db: Сесія бази даних.
        
    Returns:
        Повідомлення про надсилання листа.
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

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Отримання даних поточного автентифікованого користувача.
    
    Args:
        current_user: Об'єкт поточного користувача, отриманий з токена.
        
    Returns:
        Дані поточного користувача.
    """
    return current_user 