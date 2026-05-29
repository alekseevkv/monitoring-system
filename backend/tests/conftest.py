import pytest

from src.repositories.check_result import CheckResultRepository
from src.repositories.incidents import IncidentRepository

@pytest.fixture
def mock_check_repo():
    from unittest.mock import AsyncMock
    return AsyncMock(spec=CheckResultRepository)

@pytest.fixture
def mock_incident_repo():
    from unittest.mock import AsyncMock
    return AsyncMock(spec=IncidentRepository)