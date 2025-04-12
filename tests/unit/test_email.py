import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi_mail import FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors

from src.services.email import send_email


@pytest.mark.asyncio
async def test_send_email_success():
    """Тест успешной отправки email"""
    # Создаем моки для модулей
    mock_message = MagicMock()
    mock_fast_mail = MagicMock()
    mock_fast_mail.send_message = AsyncMock()
    mock_token = "test_token"
    
    # Параметры для вызова функции
    email_to = "test@example.com"
    username = "testuser"
    host = "localhost:8000"
    
    # Патчим необходимые функции и классы
    with (
        patch("src.services.email.MessageSchema", return_value=mock_message) as mock_message_schema,
        patch("src.services.email.FastMail", return_value=mock_fast_mail) as mock_fastmail_class,
        patch("src.services.email.create_email_token", AsyncMock(return_value=mock_token)) as mock_create_token
    ):
        # Вызываем тестируемую функцию
        await send_email(email_to, username, host)
        
        # Проверяем, что create_email_token был вызван с правильными параметрами
        mock_create_token.assert_called_once_with({"sub": email_to})
        
        # Проверяем создание объекта MessageSchema с правильными параметрами
        mock_message_schema.assert_called_once()
        args, kwargs = mock_message_schema.call_args
        assert kwargs["recipients"] == [email_to]
        assert kwargs["subject"] == "Подтверждение электронной почты"
        assert kwargs["template_body"]["host"] == host
        assert kwargs["template_body"]["username"] == username
        assert kwargs["template_body"]["token"] == mock_token
        assert kwargs["subtype"] == MessageType.html
        
        # Проверяем, что FastMail был создан
        mock_fastmail_class.assert_called_once()
        
        # Проверяем, что метод send_message был вызван
        mock_fast_mail.send_message.assert_called_once_with(mock_message, template_name="verify_email.html")


@pytest.mark.asyncio
async def test_send_email_connection_error():
    """Тест обработки ошибки при отправке email"""
    # Создаем моки для модулей
    mock_message = MagicMock()
    mock_fast_mail = MagicMock()
    # Настраиваем отправку, чтобы вызвать исключение
    mock_fast_mail.send_message = AsyncMock(side_effect=ConnectionErrors("Connection failed"))
    mock_token = "test_token"
    
    # Параметры для вызова функции
    email_to = "test@example.com"
    username = "testuser"
    host = "localhost:8000"
    
    # Патчим необходимые функции, классы и print
    with (
        patch("src.services.email.MessageSchema", return_value=mock_message),
        patch("src.services.email.FastMail", return_value=mock_fast_mail),
        patch("src.services.email.create_email_token", AsyncMock(return_value=mock_token)),
        patch("builtins.print") as mock_print
    ):
        # Вызываем тестируемую функцию
        await send_email(email_to, username, host)
        
        # Проверяем вызов print с сообщением об ошибке
        mock_print.assert_called_once()
        args, _ = mock_print.call_args
        assert "Ошибка при отправке email" in args[0] 