from unittest.mock import AsyncMock

import pytest

from src.repositories.check_result import CheckResultRepository
from src.repositories.incidents import IncidentRepository

@pytest.fixture
def mock_check_repo():
    return AsyncMock(spec=CheckResultRepository)

@pytest.fixture
def mock_incident_repo():
    return AsyncMock(spec=IncidentRepository)