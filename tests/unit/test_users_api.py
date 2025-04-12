import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile, File

from src.api.users import router


@pytest.fixture
def mock_user():
    """Mock user for tests"""
    return MagicMock(id=1, email="test@example.com")


@pytest.fixture
def mock_user_service():
    """Mock user service"""
    service = MagicMock()
    service.update_avatar_url = AsyncMock()
    return service


def test_upload_avatar(monkeypatch, mock_user, mock_user_service):
    """Test uploading user avatar"""
    # Create a mock for the file
    file = MagicMock(spec=UploadFile)
    
    # Mock for file upload service
    mock_upload_file = AsyncMock(return_value="https://example.com/avatar.jpg")
    monkeypatch.setattr("src.api.users.upload_file", mock_upload_file)
    
    # Mock for user service
    updated_user = MagicMock(avatar="https://example.com/avatar.jpg")
    mock_user_service.update_avatar_url.return_value = updated_user
    
    # Override dependencies
    monkeypatch.setattr("src.api.users.get_user_service", lambda: mock_user_service)
    
    # Call the tested function through a coroutine
    import asyncio
    result = asyncio.run(router.dependency_overrides[{}]["upload_avatar"](file, mock_user))
    
    # Check the result
    assert result == updated_user
    mock_upload_file.assert_called_once_with(file)
    mock_user_service.update_avatar_url.assert_called_once_with(
        mock_user.email, "https://example.com/avatar.jpg"
    ) 