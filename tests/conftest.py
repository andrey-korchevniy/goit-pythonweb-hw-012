import asyncio
import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from src.database.models import Base
from src.database.db import get_db
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    poolclass=NullPool,
)

# Dependency override
async def override_get_db():
    async with AsyncSession(engine) as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Global event loop for all tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def test_app():
    """Test app FastAPI"""
    return app

@pytest.fixture(scope="function")
def test_client():
    """test API client"""
    with TestClient(app) as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def async_session():
    # Create the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Run the tests
    async with AsyncSession(engine) as session:
        yield session
    
    # Drop the database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client():
    base_url = "http://test"
    async with AsyncClient(base_url=base_url) as ac:
        yield ac 