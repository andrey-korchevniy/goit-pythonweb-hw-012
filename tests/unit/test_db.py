import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import contextlib
from sqlalchemy.exc import SQLAlchemyError

from src.database.db import get_db, DatabaseSessionManager


@pytest.mark.asyncio
async def test_get_db():
    """Тест функции get_db"""
    # Создаем мок для сессии
    mock_session = AsyncMock()
    
    # Создаем мок для менеджера контекста
    mock_context_manager = MagicMock()
    mock_context_manager.__aenter__ = AsyncMock(return_value=mock_session)
    mock_context_manager.__aexit__ = AsyncMock(return_value=None)
    
    # Создаем мок для sessionmanager
    mock_sessionmanager = MagicMock()
    mock_sessionmanager.session = MagicMock(return_value=mock_context_manager)
    
    # Патчим sessionmanager
    with patch("src.database.db.sessionmanager", mock_sessionmanager):
        # Получаем асинхронный генератор
        generator = get_db()
        
        # Получаем первое значение из генератора
        session = await anext(generator)
        
        # Проверяем, что возвращается наш мок
        assert session == mock_session
        
        try:
            # Попытка завершить генератор
            await anext(generator)
        except StopAsyncIteration:
            # Это ожидаемое поведение
            pass
        
        # Проверяем, что контекстный менеджер был использован
        mock_context_manager.__aenter__.assert_called_once()
        

@pytest.mark.asyncio
async def test_database_session_manager_init():
    """Тест инициализации менеджера сессии базы данных"""
    # Создаем моки для engine и session_maker
    mock_engine = MagicMock()
    mock_session_maker = MagicMock()
    
    # Патчим create_async_engine и async_sessionmaker
    with (
        patch("src.database.db.create_async_engine", return_value=mock_engine) as mock_create_engine,
        patch("src.database.db.async_sessionmaker", return_value=mock_session_maker) as mock_async_sessionmaker
    ):
        # Создаем экземпляр менеджера
        db_manager = DatabaseSessionManager("sqlite:///test.db")
        
        # Проверяем, что функции были вызваны с правильными параметрами
        mock_create_engine.assert_called_once_with("sqlite:///test.db")
        mock_async_sessionmaker.assert_called_once_with(
            autoflush=False, autocommit=False, bind=mock_engine
        )
        
        # Проверяем атрибуты объекта
        assert db_manager._engine == mock_engine
        assert db_manager._session_maker == mock_session_maker


@pytest.mark.asyncio
async def test_database_session_manager_session():
    """Тест метода session в DatabaseSessionManager"""
    # Создаем моки для session и session_maker
    mock_session = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session_maker = MagicMock(return_value=mock_session)
    
    # Создаем экземпляр класса с mock_session_maker
    db_manager = MagicMock()
    db_manager._session_maker = mock_session_maker
    
    # Получаем реальный метод session из класса
    session_method = DatabaseSessionManager.session
    
    # Нормальный сценарий - без исключений
    async with session_method(db_manager) as session:
        assert session == mock_session
    
    # Проверяем, что метод close был вызван
    mock_session.close.assert_called_once()
    # Проверяем, что метод rollback не был вызван
    mock_session.rollback.assert_not_called()
    
    # Сбрасываем моки
    mock_session.close.reset_mock()
    mock_session.rollback.reset_mock()
    
    # Сценарий с исключением SQLAlchemyError
    sql_error = SQLAlchemyError("Database error")
    try:
        async with session_method(db_manager):
            raise sql_error
    except SQLAlchemyError as e:
        assert e == sql_error
    
    # Проверяем, что методы rollback и close были вызваны
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_database_session_manager_not_initialized():
    """Тест вызова session с неинициализированным session_maker"""
    # Создаем экземпляр класса без session_maker
    db_manager = MagicMock()
    db_manager._session_maker = None
    
    # Получаем реальный метод session из класса
    session_method = DatabaseSessionManager.session
    
    # Проверяем, что вызывается исключение
    with pytest.raises(Exception) as excinfo:
        async with session_method(db_manager):
            pass
            
    # Проверяем сообщение в исключении
    assert "Database session is not initialized" in str(excinfo.value) 