from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base
from sqlalchemy.orm.session import close_all_sessions
from sqlalchemy_utils import create_database, drop_database, database_exists
import pytest

# Assuming your main FastAPI app is in app/main.py
from app.main import app

DATABASE_URL = "postgresql+asyncpg://postgres:ma3str0@localhost:5432/testhcheck"
class TestModels:
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)

    # @pytest.fixture(scope="function")
    # def test_create_user(self, client):
    #     response = client.post(
    #         "/auth/register",
    #         json={"email": "test1@example.com", "password": "testpassword", "username": "testuser"},
    #     )
    #     assert response.status_code == 201

    def setUpClass(self):
        print('\n\n.................................')
        print('....... Testing Functions .......')
        print('.........  Patient Class  .........')
        print('.................................\n\n')

    def setUp(self, mock_db) -> None:
        """initializes new patient for testing"""
        self.app = app.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        """Test successful health check with database connected"""
        with patch('app.main.get_session', return_value=mock_db), \
            patch('app.models.test_db_connection', AsyncMock(return_value=True)):
            stmt = select(UserModel).all()
            result = db.execute(stmt)
            return result.scalar_one_or_none()

        # db_session.create_all()

    def tearDown(self) -> None:
        db_session.remove()
        db_session.drop_all()
        self.app_context.pop()
