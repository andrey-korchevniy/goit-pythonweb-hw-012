import pytest
from unittest.mock import patch
from fastapi import HTTPException
from jose import JWTError

from src.services.auth import (
    get_password_hash, verify_password, get_email_from_token
)


def test_get_password_hash():
    """Тест создания хеша пароля"""
    password = "testpassword"
    hashed = get_password_hash(password)
    
    # Проверяем, что результат не пустой и отличается от исходного пароля
    assert hashed is not None
    assert hashed != password
    
    # Хеш должен выглядеть как bcrypt-хеш
    assert hashed.startswith('$2')


def test_verify_password():
    """Тест проверки пароля"""
    password = "testpassword"
    hashed = get_password_hash(password)
    
    # Проверяем, что правильный пароль проходит проверку
    assert verify_password(password, hashed) is True
    
    # Проверяем, что неправильный пароль не проходит проверку
    assert verify_password("wrongpassword", hashed) is False


@pytest.mark.asyncio
async def test_get_email_from_token_valid():
    """Тест получения email из валидного токена"""
    # Мокируем jwt.decode для возврата правильного payload
    with patch("src.services.auth.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "test@example.com"}
        
        # Вызываем функцию
        email = await get_email_from_token("valid_token")
        
        # Проверяем результат
        assert email == "test@example.com"
        mock_decode.assert_called_once()


@pytest.mark.asyncio
async def test_get_email_from_token_invalid():
    """Тест получения email из невалидного токена"""
    # Мокируем jwt.decode для генерации исключения JWTError
    with patch("src.services.auth.jwt.decode", side_effect=JWTError("JWT Error")):
        # Проверяем, что функция вызывает HTTPException
        with pytest.raises(HTTPException) as excinfo:
            await get_email_from_token("invalid_token")
        
        # Проверяем статус код исключения
        assert excinfo.value.status_code == 422 