import pytest

from src.repositories.check_result import CheckResultRepository

@pytest.fixture
def mock_check_repo():
    from unittest.mock import AsyncMock
    return AsyncMock(spec=CheckResultRepository)