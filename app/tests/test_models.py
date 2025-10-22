from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

# Assuming your main FastAPI app is in app/main.py
from app.main import app

class TestModels:
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture(scope="function")
    def test_create_user(self, client):
        response = client.post(
            "/auth/register",
            json={"email": "test1@example.com", "password": "testpassword", "username": "testuser"},
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test1@example.com"
