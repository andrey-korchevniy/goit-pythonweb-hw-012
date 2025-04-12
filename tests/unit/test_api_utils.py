import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from sqlalchemy.sql.elements import TextClause

from src.api.utils import healthchecker


@pytest.mark.asyncio
async def test_healthchecker_success():
    """Test for successful API health check"""
    # Create mock for database
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = 1
    mock_db.execute.return_value = mock_result
    
    # Call healthchecker function
    response = await healthchecker(mock_db)
    
    # Check result
    assert response == {"message": "API is up and running!"}
    mock_db.execute.assert_called_once()
    # Check that execute argument contains SQL query (without checking specific type)
    assert mock_db.execute.call_args is not None
    assert mock_db.execute.call_args[0] is not None


@pytest.mark.asyncio
async def test_healthchecker_db_not_configured():
    """Test for health check with incorrect database configuration"""
    # Create mock for database
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result
    
    # For tracking console messages
    with patch("builtins.print") as mock_print:
        # Call healthchecker function and check exception
        with pytest.raises(HTTPException) as excinfo:
            await healthchecker(mock_db)
        
        # Check exception
        assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        # Check error details considering actual implementation
        assert "Error connecting to the database" in excinfo.value.detail
        # Check that expected message was printed to console
        mock_print.assert_called_once()


@pytest.mark.asyncio
async def test_healthchecker_db_error():
    """Test for health check with database connection error"""
    # Create mock for database
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("Connection error")
    
    # Call healthchecker function and check exception
    with pytest.raises(HTTPException) as excinfo:
        await healthchecker(mock_db)
    
    # Check exception
    assert excinfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error connecting to the database" in excinfo.value.detail 