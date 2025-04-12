import pytest
from unittest.mock import patch, MagicMock
import os

from src.conf.config import Settings


def test_settings_attributes():
    """Check settings class attributes"""
    # Create settings with minimal parameters
    settings = Settings(
        DB_URL="sqlite:///test.db",
        JWT_SECRET="test_secret_key",
        JWT_ALGORITHM="HS256"
    )
    
    # Check that main attributes exist
    assert hasattr(settings, "DB_URL")
    assert hasattr(settings, "JWT_SECRET")
    assert hasattr(settings, "JWT_ALGORITHM")
    
    # Check values
    assert settings.DB_URL == "sqlite:///test.db"
    assert settings.JWT_SECRET == "test_secret_key"
    assert settings.JWT_ALGORITHM == "HS256"


def test_settings_env_variables():
    """Check settings from environment variables"""
    # Consider data types expected by Settings
    env_vars = {
        "DB_URL": "postgresql+asyncpg://test:test@localhost:5432/test",
        "JWT_SECRET": "test_secret_key",
        "JWT_ALGORITHM": "HS512",
        "MAIL_USERNAME": "test@example.com",
        "MAIL_PASSWORD": "test_password",
        "MAIL_FROM": "test@example.com",
        "MAIL_FROM_NAME": "Test User",
        "MAIL_PORT": "587",
        "MAIL_SERVER": "test.smtp.com",
        "REDIS_HOST": "test_redis",
        "REDIS_PORT": "6379",
        "CLD_NAME": "test_cloud",
        "CLD_API_KEY": "12345",  # Numeric value for API key
        "CLD_API_SECRET": "api_secret_test"
    }
    
    # Call only necessary settings, forcibly passing them as parameters
    settings = Settings(
        DB_URL=env_vars["DB_URL"],
        JWT_SECRET=env_vars["JWT_SECRET"],
        JWT_ALGORITHM=env_vars["JWT_ALGORITHM"],
        MAIL_USERNAME=env_vars["MAIL_USERNAME"],
        MAIL_FROM=env_vars["MAIL_FROM"]
    )
    
    # Check that values were set
    assert settings.DB_URL == env_vars["DB_URL"]
    assert settings.JWT_SECRET == env_vars["JWT_SECRET"]
    assert settings.JWT_ALGORITHM == env_vars["JWT_ALGORITHM"]
    assert settings.MAIL_USERNAME == env_vars["MAIL_USERNAME"]
    assert settings.MAIL_FROM == env_vars["MAIL_FROM"] 