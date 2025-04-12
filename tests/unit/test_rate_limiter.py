import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, HTTPException, status

from src.services.rate_limiter import RateLimiter


@pytest.fixture
def mock_redis():
    """Мок Redis для тестов"""
    redis = MagicMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    redis.incr = AsyncMock(return_value=1)
    return redis


def test_rate_limiter_init():
    """Тест инициализации RateLimiter"""
    limiter = RateLimiter(times=10, seconds=60)
    assert limiter.times == 10
    assert limiter.seconds == 60
    assert limiter.requests == {}


@pytest.mark.asyncio
async def test_rate_limiter_first_request():
    """Тест первого запроса к rate limiter"""
    limiter = RateLimiter(times=10, seconds=60)
    
    # Создаем мок запроса
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"
    request.url.path = "/api/test"
    
    # Вызываем метод
    result = await limiter(request)
    
    # Проверяем результат
    assert result is True
    assert len(limiter.requests["127.0.0.1:/api/test"]) == 1


@pytest.mark.asyncio
async def test_rate_limiter_multiple_requests():
    """Тест множественных запросов, но в пределах ограничения"""
    limiter = RateLimiter(times=10, seconds=60)
    
    # Создаем мок запроса
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"
    request.url.path = "/api/test"
    
    # Делаем несколько запросов
    for _ in range(5):
        result = await limiter(request)
        assert result is True
    
    # Проверяем, что все запросы были записаны
    assert len(limiter.requests["127.0.0.1:/api/test"]) == 5


@pytest.mark.asyncio
async def test_rate_limiter_endpoint_parameter():
    """Тест с указанным endpoint параметром"""
    limiter = RateLimiter(times=10, seconds=60)
    
    # Создаем мок запроса
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"
    request.url.path = "/api/original"
    
    # Вызываем с указанным endpoint
    result = await limiter(request, endpoint="/api/custom")
    
    # Проверяем результат
    assert result is True
    assert len(limiter.requests["127.0.0.1:/api/custom"]) == 1
    assert "127.0.0.1:/api/original" not in limiter.requests


@pytest.mark.asyncio
async def test_rate_limiter_limit_exceeded():
    """Тест превышения ограничения запросов"""
    limiter = RateLimiter(times=3, seconds=60)
    
    # Создаем мок запроса
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"
    request.url.path = "/api/test"
    
    # Делаем запросы до предела
    for _ in range(3):
        result = await limiter(request)
        assert result is True
    
    # Следующий запрос должен вызвать исключение
    with pytest.raises(HTTPException) as exc_info:
        await limiter(request)
    
    # Проверяем исключение
    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "Слишком много запросов" in exc_info.value.detail


@pytest.mark.asyncio
async def test_rate_limiter_separate_endpoints():
    """Тест ограничения для разных endpoint-ов"""
    limiter = RateLimiter(times=3, seconds=60)
    
    # Создаем моки запросов к разным endpoint-ам
    request1 = MagicMock(spec=Request)
    request1.client.host = "127.0.0.1"
    request1.url.path = "/api/endpoint1"
    
    request2 = MagicMock(spec=Request)
    request2.client.host = "127.0.0.1"
    request2.url.path = "/api/endpoint2"
    
    # Делаем запросы к разным endpoint-ам
    for _ in range(3):
        result1 = await limiter(request1)
        result2 = await limiter(request2)
        assert result1 is True
        assert result2 is True
    
    # Запрос к первому endpoint должен вызвать исключение
    with pytest.raises(HTTPException):
        await limiter(request1)
        
    # А ко второму также должен вызвать исключение
    with pytest.raises(HTTPException):
        await limiter(request2)


@pytest.mark.asyncio
async def test_rate_limiter_separate_ips():
    """Тест ограничения для разных IP адресов"""
    limiter = RateLimiter(times=3, seconds=60)
    
    # Создаем моки запросов с разных IP
    request1 = MagicMock(spec=Request)
    request1.client.host = "127.0.0.1"
    request1.url.path = "/api/test"
    
    request2 = MagicMock(spec=Request)
    request2.client.host = "192.168.1.1"
    request2.url.path = "/api/test"
    
    # Делаем запросы с разных IP
    for _ in range(3):
        result1 = await limiter(request1)
        result2 = await limiter(request2)
        assert result1 is True
        assert result2 is True
    
    # Запрос с первого IP должен вызвать исключение
    with pytest.raises(HTTPException):
        await limiter(request1)
    
    # А со второго также должен вызвать исключение
    with pytest.raises(HTTPException):
        await limiter(request2)


@pytest.mark.asyncio
async def test_rate_limiter_expired_timestamps():
    """Тест очистки устаревших timestamp-ов"""
    limiter = RateLimiter(times=3, seconds=1)  # 1 секунда для быстрых тестов
    
    # Создаем мок запроса
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"
    request.url.path = "/api/test"
    
    # Делаем 3 запроса
    for _ in range(3):
        result = await limiter(request)
        assert result is True
    
    # Подождем более 1 секунды
    time.sleep(1.1)
    
    # Теперь лимит должен быть сброшен и запрос должен пройти
    result = await limiter(request)
    assert result is True
    
    # Проверяем, что старые запросы были удалены
    assert len(limiter.requests["127.0.0.1:/api/test"]) == 1


async def test_rate_limit_first_request(mock_redis):
    """Тест обработки первого запроса без превышения лимита"""
    # Создаем RateLimiter
    limiter = RateLimiter(times=10, seconds=60)
    
    # Создаем запрос
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"
    
    # Патчим Redis
    with patch("src.services.rate_limiter.redis_client", mock_redis):
        # Вызываем тестируемую функцию
        await limiter(request)
        
        # Проверяем, что Redis был использован
        mock_redis.get.assert_called_once()
        mock_redis.incr.assert_called_once()
        mock_redis.set.assert_called_once()


async def test_rate_limit_exceeded(mock_redis):
    """Тест превышения лимита запросов"""
    # Создаем RateLimiter
    limiter = RateLimiter(times=10, seconds=60)
    
    # Создаем запрос
    request = MagicMock(spec=Request)
    request.client.host = "127.0.0.1"
    
    # Настраиваем Redis для возврата значения больше лимита
    mock_redis.get.return_value = b"5"  # Уже есть 5 запросов
    mock_redis.incr.return_value = 11  # 11-й запрос превышает лимит 10
    
    # Патчим Redis
    with patch("src.services.rate_limiter.redis_client", mock_redis):
        # Вызываем тестируемую функцию и ожидаем исключение
        with pytest.raises(HTTPException) as excinfo:
            await limiter(request)
        
        # Проверяем, что исключение имеет правильный статус код
        assert excinfo.value.status_code == 429


def test_rate_limit_decorator():
    """Тест декоратора rate_limit"""
    # Проверяем, что декоратор создает RateLimiter с правильными параметрами
    limiter = rate_limit(times=5, seconds=30)
    assert isinstance(limiter, RateLimiter)
    assert limiter.times == 5
    assert limiter.seconds == 30 