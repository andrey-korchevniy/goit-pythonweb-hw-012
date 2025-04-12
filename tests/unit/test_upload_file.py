import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import UploadFile

from src.services.upload_file import UploadFileService


def test_upload_file_service_init():
    """Test initialization of file upload service"""
    # Create service with test settings
    service = UploadFileService(
        cloud_name="test_cloud",
        api_key="test_key",
        api_secret="test_secret"
    )
    
    # Check attributes
    assert service.cloud_name == "test_cloud"
    assert service.api_key == "test_key"
    assert service.api_secret == "test_secret"


def test_upload_file():
    """Test file upload function"""
    # Create mock for Cloudinary
    mock_cloudinary_uploader = MagicMock()
    mock_cloudinary_uploader.upload = MagicMock(return_value={"version": "1234"})
    
    mock_cloudinary_image = MagicMock()
    mock_cloudinary_image.build_url = MagicMock(return_value="https://example.com/image.jpg")
    
    mock_cloudinary = MagicMock()
    mock_cloudinary.uploader = mock_cloudinary_uploader
    mock_cloudinary.CloudinaryImage = MagicMock(return_value=mock_cloudinary_image)
    
    # Create file upload service
    service = UploadFileService(
        cloud_name="test_cloud",
        api_key="test_key",
        api_secret="test_secret"
    )
    
    # Create mock for file
    mock_file = MagicMock(spec=UploadFile)
    mock_file.file = MagicMock()
    mock_file.filename = "test.jpg"
    
    # Patch Cloudinary module
    with (
        patch("src.services.upload_file.cloudinary", mock_cloudinary),
        patch("src.services.upload_file.cloudinary.uploader", mock_cloudinary_uploader),
        patch("src.services.upload_file.cloudinary.CloudinaryImage", lambda _: mock_cloudinary_image)
    ):
        # Call the tested function
        result = service.upload_file(mock_file, "test_user")
        
        # Check result
        assert result == "https://example.com/image.jpg"
        
        # Check that Cloudinary.uploader.upload was called with correct parameters
        mock_cloudinary_uploader.upload.assert_called_once()
        args, kwargs = mock_cloudinary_uploader.upload.call_args
        assert args[0] == mock_file.file
        assert kwargs["public_id"] == "ContactsApp/test_user"
        assert kwargs["overwrite"] is True 