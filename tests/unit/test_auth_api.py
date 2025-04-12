import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status, HTTPException, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.api.auth import (
    register, 
    login_for_access_token, 
    confirmed_email, 
    request_email, 
    read_users_me
)
from src.schemas import UserCreate, RequestEmail, UserResponse


@pytest.fixture
def mock_user_service():
    """Мок сервиса пользователей"""
    service = AsyncMock()
    service.get_user_by_email = AsyncMock(return_value=None)
    service.get_user_by_username = AsyncMock(return_value=None)
    service.create_user = AsyncMock()
    service.confirmed_email = AsyncMock()
    return service


@pytest.fixture
def mock_user():
    """Мок объекта пользователя для тестов"""
    return MagicMock(
        id=1, 
        email="test@example.com", 
        username="testuser", 
        confirmed=True,
        hashed_password="hashed_password123"
    )


@pytest.mark.asyncio
async def test_register_success(mock_user_service):
    """Тест успешной регистрации пользователя"""
    # Настраиваем моки
    body = UserCreate(username="testuser", email="test@example.com", password="password123")
    background_tasks = MagicMock(spec=BackgroundTasks)
    request = MagicMock(spec=Request)
    request.base_url = "http://test-server.com/"
    db = AsyncMock()
    
    # Патчим UserService для возврата нашего мока
    with patch("src.api.auth.UserService", return_value=mock_user_service):
        # Патчим функцию хеширования пароля
        with patch("src.api.auth.get_password_hash", return_value="hashed_password"):
            # Создаем мок созданного пользователя
            created_user = MagicMock(email="test@example.com", username="testuser")
            mock_user_service.create_user.return_value = created_user
            
            # Вызываем тестируемую функцию
            result = await register(body, background_tasks, request, db)
            
            # Проверяем результат
            assert result == created_user
            
            # Проверяем, что правильные методы вызваны
            mock_user_service.get_user_by_email.assert_called_once_with("test@example.com")
            mock_user_service.get_user_by_username.assert_called_once_with("testuser")
            mock_user_service.create_user.assert_called_once_with(body)
            background_tasks.add_task.assert_called_once()


@pytest.mark.asyncio
async def test_register_email_exists(mock_user_service, mock_user):
    """Тест регистрации с существующим email"""
    # Настраиваем моки
    body = UserCreate(username="testuser", email="test@example.com", password="password123")
    background_tasks = MagicMock(spec=BackgroundTasks)
    request = MagicMock(spec=Request)
    db = AsyncMock()
    
    # Устанавливаем, что пользователь с таким email уже существует
    mock_user_service.get_user_by_email.return_value = mock_user
    
    # Патчим UserService для возврата нашего мока
    with patch("src.api.auth.UserService", return_value=mock_user_service):
        # Вызываем тестируемую функцию и проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await register(body, background_tasks, request, db)
        
        # Проверяем исключение
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "email already exist" in exc_info.value.detail


@pytest.mark.asyncio
async def test_register_username_exists(mock_user_service, mock_user):
    """Тест регистрации с существующим именем пользователя"""
    # Настраиваем моки
    body = UserCreate(username="testuser", email="test@example.com", password="password123")
    background_tasks = MagicMock(spec=BackgroundTasks)
    request = MagicMock(spec=Request)
    db = AsyncMock()
    
    # Устанавливаем, что пользователя с таким email нет, но имя уже занято
    mock_user_service.get_user_by_email.return_value = None
    mock_user_service.get_user_by_username.return_value = mock_user
    
    # Патчим UserService для возврата нашего мока
    with patch("src.api.auth.UserService", return_value=mock_user_service):
        # Вызываем тестируемую функцию и проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await register(body, background_tasks, request, db)
        
        # Проверяем исключение
        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "name already exist" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_success(mock_user_service, mock_user):
    """Тест успешной авторизации"""
    # Настраиваем моки
    form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    form_data.username = "testuser"
    form_data.password = "password123"
    db = AsyncMock()
    
    # Устанавливаем, что пользователь существует и подтвержден
    mock_user_service.get_user_by_username.return_value = mock_user
    
    # Патчим нужные функции
    with patch("src.api.auth.UserService", return_value=mock_user_service), \
         patch("src.api.auth.verify_password", return_value=True), \
         patch("src.api.auth.create_access_token", return_value="test_token"):
        
        # Вызываем тестируемую функцию
        result = await login_for_access_token(form_data, db)
        
        # Проверяем результат
        assert result == {"access_token": "test_token", "token_type": "bearer"}


@pytest.mark.asyncio
async def test_login_user_not_found(mock_user_service):
    """Тест авторизации с несуществующим пользователем"""
    # Настраиваем моки
    form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    form_data.username = "nonexistent"
    form_data.password = "password123"
    db = AsyncMock()
    
    # Устанавливаем, что пользователь не существует
    mock_user_service.get_user_by_username.return_value = None
    
    # Патчим UserService для возврата нашего мока
    with patch("src.api.auth.UserService", return_value=mock_user_service):
        # Вызываем тестируемую функцию и проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await login_for_access_token(form_data, db)
        
        # Проверяем исключение
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Bad login or password" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_wrong_password(mock_user_service, mock_user):
    """Тест авторизации с неправильным паролем"""
    # Настраиваем моки
    form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    form_data.username = "testuser"
    form_data.password = "wrong_password"
    db = AsyncMock()
    
    # Устанавливаем, что пользователь существует
    mock_user_service.get_user_by_username.return_value = mock_user
    
    # Патчим нужные функции
    with patch("src.api.auth.UserService", return_value=mock_user_service), \
         patch("src.api.auth.verify_password", return_value=False):
        
        # Вызываем тестируемую функцию и проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await login_for_access_token(form_data, db)
        
        # Проверяем исключение
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Bad login or password" in exc_info.value.detail


@pytest.mark.asyncio
async def test_login_email_not_confirmed(mock_user_service):
    """Тест авторизации с неподтвержденным email"""
    # Настраиваем моки
    form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    form_data.username = "testuser"
    form_data.password = "password123"
    db = AsyncMock()
    
    # Создаем пользователя с неподтвержденным email
    unconfirmed_user = MagicMock(
        id=1, 
        email="test@example.com", 
        username="testuser", 
        confirmed=False,
        hashed_password="hashed_password123"
    )
    
    # Устанавливаем, что пользователь существует но не подтвержден
    mock_user_service.get_user_by_username.return_value = unconfirmed_user
    
    # Патчим нужные функции
    with patch("src.api.auth.UserService", return_value=mock_user_service), \
         patch("src.api.auth.verify_password", return_value=True):
        
        # Вызываем тестируемую функцию и проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await login_for_access_token(form_data, db)
        
        # Проверяем исключение
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Email is not confirmed" in exc_info.value.detail


@pytest.mark.asyncio
async def test_confirmed_email_success(mock_user_service, mock_user):
    """Тест успешного подтверждения email"""
    # Настраиваем моки
    token = "valid_token"
    db = AsyncMock()
    
    # Устанавливаем, что пользователь существует и не подтвержден
    unconfirmed_user = MagicMock(
        id=1, 
        email="test@example.com", 
        username="testuser", 
        confirmed=False
    )
    mock_user_service.get_user_by_email.return_value = unconfirmed_user
    
    # Патчим нужные функции
    with patch("src.api.auth.UserService", return_value=mock_user_service), \
         patch("src.api.auth.get_email_from_token", return_value="test@example.com"):
        
        # Вызываем тестируемую функцию
        result = await confirmed_email(token, db)
        
        # Проверяем результат
        assert result == {"message": "Your email is  confirmed"}
        
        # Проверяем, что правильные методы вызваны
        mock_user_service.confirmed_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_confirmed_email_already_confirmed(mock_user_service, mock_user):
    """Тест подтверждения уже подтвержденного email"""
    # Настраиваем моки
    token = "valid_token"
    db = AsyncMock()
    
    # Устанавливаем, что пользователь существует и уже подтвержден
    mock_user_service.get_user_by_email.return_value = mock_user  # mock_user.confirmed = True
    
    # Патчим нужные функции
    with patch("src.api.auth.UserService", return_value=mock_user_service), \
         patch("src.api.auth.get_email_from_token", return_value="test@example.com"):
        
        # Вызываем тестируемую функцию
        result = await confirmed_email(token, db)
        
        # Проверяем результат
        assert result == {"message": "Your email is already confirmed"}
        
        # Проверяем, что метод confirmed_email не вызывался
        mock_user_service.confirmed_email.assert_not_called()


@pytest.mark.asyncio
async def test_confirmed_email_user_not_found(mock_user_service):
    """Тест подтверждения email для несуществующего пользователя"""
    # Настраиваем моки
    token = "valid_token"
    db = AsyncMock()
    
    # Устанавливаем, что пользователь не существует
    mock_user_service.get_user_by_email.return_value = None
    
    # Патчим нужные функции
    with patch("src.api.auth.UserService", return_value=mock_user_service), \
         patch("src.api.auth.get_email_from_token", return_value="nonexistent@example.com"):
        
        # Вызываем тестируемую функцию и проверяем, что вызывается исключение
        with pytest.raises(HTTPException) as exc_info:
            await confirmed_email(token, db)
        
        # Проверяем исключение
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "верифікації" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_email_unconfirmed(mock_user_service):
    """Тест запроса повторного письма для неподтвержденного email"""
    # Настраиваем моки
    body = RequestEmail(email="test@example.com")
    background_tasks = MagicMock(spec=BackgroundTasks)
    request = MagicMock(spec=Request)
    request.base_url = "http://test-server.com/"
    db = AsyncMock()
    
    # Создаем пользователя с неподтвержденным email
    unconfirmed_user = MagicMock(
        id=1, 
        email="test@example.com", 
        username="testuser", 
        confirmed=False
    )
    
    # Устанавливаем, что пользователь существует но не подтвержден
    mock_user_service.get_user_by_email.return_value = unconfirmed_user
    
    # Патчим UserService для возврата нашего мока
    with patch("src.api.auth.UserService", return_value=mock_user_service):
        # Вызываем тестируемую функцию
        result = await request_email(body, background_tasks, request, db)
        
        # Проверяем результат
        assert result == {"message": "Check your email for confirmation"}
        
        # Проверяем, что задача добавлена в фоновые задачи
        background_tasks.add_task.assert_called_once()


@pytest.mark.asyncio
async def test_request_email_already_confirmed(mock_user_service, mock_user):
    """Тест запроса повторного письма для уже подтвержденного email"""
    # Настраиваем моки
    body = RequestEmail(email="test@example.com")
    background_tasks = MagicMock(spec=BackgroundTasks)
    request = MagicMock(spec=Request)
    db = AsyncMock()
    
    # Устанавливаем, что пользователь существует и уже подтвержден
    mock_user_service.get_user_by_email.return_value = mock_user  # mock_user.confirmed = True
    
    # Патчим UserService для возврата нашего мока
    with patch("src.api.auth.UserService", return_value=mock_user_service):
        # Вызываем тестируемую функцию
        result = await request_email(body, background_tasks, request, db)
        
        # Проверяем результат
        assert result == {"message": "Your email is already confirmed"}
        
        # Проверяем, что задача НЕ добавлена в фоновые задачи
        background_tasks.add_task.assert_not_called()


@pytest.mark.asyncio
async def test_request_email_user_not_found(mock_user_service):
    """Тест запроса повторного письма для несуществующего пользователя"""
    # Настраиваем моки
    body = RequestEmail(email="nonexistent@example.com")
    background_tasks = MagicMock(spec=BackgroundTasks)
    request = MagicMock(spec=Request)
    db = AsyncMock()
    
    # Устанавливаем, что пользователь не существует
    mock_user_service.get_user_by_email.return_value = None
    
    # Патчим UserService для возврата нашего мока
    with patch("src.api.auth.UserService", return_value=mock_user_service):
        # Вызываем тестируемую функцию
        result = await request_email(body, background_tasks, request, db)
        
        # Проверяем результат
        assert result == {"message": "Check your email for confirmation"}
        
        # Проверяем, что задача НЕ добавлена в фоновые задачи
        background_tasks.add_task.assert_not_called()


def test_read_users_me(mock_user):
    """Тест endpoint /me для получения информации о текущем пользователе"""
    # Преобразуем в UserResponse
    user_response = UserResponse.model_validate(mock_user)
    
    # Проверяем, что функция возвращает пользователя
    assert read_users_me(user_response) == user_response 