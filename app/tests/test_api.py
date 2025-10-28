import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from .conftest import async_client

# Assuming your main FastAPI app is in app/main.py
from app.main import app
from app.nlp.fhir_nlp_service import FHIRQueryProcessor


class TestRoutes:
    """Test cases for FastAPI routes"""

    @pytest.fixture
    def async_client(self):
        """Create test async_client"""
        return TestClient(app)

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def sample_query_data(self):
        """Sample query data for POST /query"""
        return {
            "query": "patients with diabetes over 50"
        }

    @pytest.fixture
    def sample_fhir_query(self):
        """Sample FHIR query response"""
        return {
            "original_query": "patients with diabetes over 50",
            "intent": "search_patients",
            "fhir_url": "https://hapi.fhir.org/baseR5/Condition?code=http://snomed.info/sct|73211009&_include=Condition:subject&_include=Condition:patient",
            "resource_type": "Condition",
            "filters": {
                "age_filters": [{"operator": "gt", "value": 50}],
                "conditions": [{"system": "http://snomed.info/sct", "code": "73211009"}]
            },
            "search_parameters": ["code=http://snomed.info/sct|73211009"]
        }

    @pytest.fixture
    def sample_fhir_response(self):
        """Sample FHIR API response"""
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-1",
                        "name": [{"given": ["John"], "family": "Doe"}],
                        "birthDate": "1970-05-15",
                        "gender": "male"
                    }
                }
            ]
        }

    @pytest.fixture
    def sample_processed_results(self):
        """Sample processed results"""
        return {
            "total_patients": 1,
            "patients": [
                {
                    "id": "patient-1",
                    "name": "John Doe",
                    "birthDate": "1970-05-15",
                    "age": 54,
                    "gender": "male",
                    "conditions": ["Diabetes mellitus"]
                }
            ],
            "raw_fhir_response": {"resourceType": "Bundle"}
        }

    # Test POST /query
    @pytest.mark.asyncio
    async def test_process_query_success(self, async_client, mock_db, sample_query_data,
                                         sample_fhir_query, sample_fhir_response,
                                         sample_processed_results):
        """Test successful query processing"""
        # Mock the dependencies
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.nlp.fhir_nlp_service.FHIRQueryProcessor') as MockProcessor:
            # Setup mocks
            mock_processor_instance = AsyncMock()
            MockProcessor.return_value = mock_processor_instance

            mock_processor_instance.build_fhir_query.return_value = sample_fhir_query
            mock_processor_instance.execute_fhir_query.return_value = sample_fhir_response
            mock_processor_instance.process_fhir_response.return_value = sample_processed_results

            # mock_current_user.id = "user-123"

            # Mock datetime for execution time calculation
            mock_now = Mock()
            # mock_datetime.now.return_value = mock_now
            # mock_now.__sub__ = Mock(return_value=Mock(total_seconds=Mock(return_value=1.5)))

            # Make request
            response = async_client.post("/query", json=sample_query_data)

            # Assertions
            assert response.status_code == 200

            response_data = response.json()
            assert response_data["original_query"] == sample_query_data["query"]
            assert response_data["fhir_query"] == sample_fhir_query
            assert response_data["processed_results"] == sample_processed_results
            assert "execution_time" in response_data

            # Verify processor methods were called
            mock_processor_instance.build_fhir_query.assert_called_once_with(sample_query_data['query'])
            mock_processor_instance.execute_fhir_query.assert_called_once_with(sample_fhir_query['fhir_url'])
            mock_processor_instance.process_fhir_response.assert_called_once_with(
                sample_fhir_response, sample_fhir_query['filters']
            )
            mock_processor_instance.log_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_query_missing_query_field(self, async_client):
        """Test query processing with missing query field"""
        response = async_client.post("/query", json={})

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_process_query_empty_query(self, async_client):
        """Test query processing with empty query"""
        response = async_client.post("/query", json={"query": ""})

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_process_query_fhir_server_error(self, async_client, mock_db, sample_query_data):
        """Test query processing when FHIR server fails"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.nlp.fhir_nlp_service.FHIRQueryProcessor') as MockProcessor:
            mock_processor_instance = AsyncMock()
            MockProcessor.return_value = mock_processor_instance

            # Simulate FHIR server error
            mock_processor_instance.build_fhir_query.return_value = {"fhir_url": "test"}
            mock_processor_instance.execute_fhir_query.side_effect = Exception("FHIR server unavailable")

            response = async_client.post("/query", json=sample_query_data)

            assert response.status_code == 500
            assert "FHIR server unavailable" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_process_query_processor_error(self, async_client, mock_db, sample_query_data):
        """Test query processing when processor fails"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.nlp.fhir_nlp_service.FHIRQueryProcessor') as MockProcessor:
            mock_processor_instance = AsyncMock()
            MockProcessor.return_value = mock_processor_instance

            # Simulate processor error
            mock_processor_instance.build_fhir_query.side_effect = Exception("Processor error")

            response = async_client.post("/query", json=sample_query_data)

            assert response.status_code == 500
            assert "Processor error" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_process_query_logging_error(self, async_client, mock_db, sample_query_data,
                                               sample_fhir_query, sample_fhir_response,
                                               sample_processed_results):
        """Test query processing when logging fails but main request succeeds"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.nlp.fhir_nlp_service.FHIRQueryProcessor') as MockProcessor:
            mock_processor_instance = AsyncMock()
            MockProcessor.return_value = mock_processor_instance

            mock_processor_instance.build_fhir_query.return_value = sample_fhir_query
            mock_processor_instance.execute_fhir_query.return_value = sample_fhir_response
            mock_processor_instance.process_fhir_response.return_value = sample_processed_results
            mock_processor_instance.log_query.side_effect = Exception("Logging failed")

            mock_current_user.id = "user-123"

            mock_now = Mock()
            mock_datetime.now.return_value = mock_now
            mock_now.__sub__ = Mock(return_value=Mock(total_seconds=Mock(return_value=1.5)))

            # Should still return 200 even if logging fails
            response = async_client.post("/query", json=sample_query_data)

            assert response.status_code == 200
            # Logging error should be handled gracefully

    # Test GET /suggestions
    def test_get_suggestions_success(self, async_client):
        """Test successful suggestions retrieval"""
        response = async_client.get("/suggestions")

        assert response.status_code == 200

        response_data = response.json()
        assert "suggestions" in response_data
        assert isinstance(response_data["suggestions"], list)
        assert len(response_data["suggestions"]) > 0

        # Verify some expected suggestions are present
        suggestions = response_data["suggestions"]
        assert any("diabetic" in suggestion.lower() for suggestion in suggestions)
        assert any("asthma" in suggestion.lower() for suggestion in suggestions)
        assert any("hypertension" in suggestion.lower() for suggestion in suggestions)

    def test_get_suggestions_content(self, async_client):
        """Test suggestions content"""
        response = async_client.get("/suggestions")
        response_data = response.json()

        suggestions = response_data["suggestions"]

        # Check that suggestions are non-empty strings
        for suggestion in suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion.strip()) > 0

    # Test GET /health
    @pytest.mark.asyncio
    async def test_health_check_success(self, async_client, mock_db):
        """Test successful health check with database connected"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.database.db_engine.test_db_connection', AsyncMock(return_value=True)):

            response = async_client.get("/health")

            assert response.status_code == 200

            response_data = response.json()
            assert response_data["status"] == "healthy"
            assert response_data["database"] == "connected"
            assert "timestamp" in response_data

            # Verify timestamp is in ISO format
            try:
                datetime.fromisoformat(response_data["timestamp"].replace('Z', '+00:00'))
            except ValueError:
                pytest.fail("Timestamp is not in valid ISO format")

    @pytest.mark.asyncio
    async def test_health_check_database_disconnected(self, async_client, mock_db):
        """Test health check when database is disconnected"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.database.db_engine.test_db_connection', AsyncMock(return_value=False)):
            response = async_client.get("/health")

            assert response.status_code == 200

            response_data = response.json()
            assert response_data["status"] == "healthy"  # App is still healthy
            assert response_data["database"] == "disconnected"
            assert "timestamp" in response_data

    @pytest.mark.asyncio
    async def test_health_check_database_error(self, async_client, mock_db):
        """Test health check when database check raises an error"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.database.db_engine.test_db_connection', AsyncMock(side_effect=Exception("DB error"))):
            response = async_client.get("/health")

            # Should handle database errors gracefully
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["database"] == "disconnected"

    # Test Authentication/Authorization (if applicable)
    @pytest.mark.asyncio
    async def test_process_query_unauthorized(self, async_client, sample_query_data):
        """Test query processing without authentication"""
        # This test depends on how your auth is set up
        # If authentication is required and not provided, it should return 401
        pass

    # Test Performance
    @pytest.mark.asyncio
    async def test_process_query_performance(self, async_client, mock_db, sample_query_data,
                                             sample_fhir_query, sample_fhir_response,
                                             sample_processed_results):
        """Test query processing performance timing"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.nlp.fhir_nlp_service.FHIRQueryProcessor') as MockProcessor, \
                patch(datetime) as mock_datetime, \
                patch('app.main.current_user') as mock_current_user:
            mock_processor_instance = AsyncMock()
            MockProcessor.return_value = mock_processor_instance

            mock_processor_instance.build_fhir_query.return_value = sample_fhir_query
            mock_processor_instance.execute_fhir_query.return_value = sample_fhir_response
            mock_processor_instance.process_fhir_response.return_value = sample_processed_results

            mock_current_user.id = "user-123"

            # Mock start and end times to simulate 2 seconds execution
            mock_start = datetime(2024, 1, 1, 10, 0, 0)
            mock_end = datetime(2024, 1, 1, 10, 0, 2)  # 2 seconds later

            mock_datetime.now.side_effect = [mock_start, mock_end]

            response = async_client.post("/query", json=sample_query_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["execution_time"] == 2000  # 2 seconds in milliseconds

    # Test Edge Cases
    @pytest.mark.asyncio
    async def test_process_query_special_characters(self, async_client, mock_db):
        """Test query processing with special characters in query"""
        special_queries = [
            {"query": "patients with diabetes & hypertension"},
            {"query": "patients over 50; DROP TABLE patients;"},
            {"query": "patients with <script>alert('xss')</script>"},
            {"query": "patients with unicode: ñáéíóú"},
        ]

        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.nlp.fhir_nlp_service.FHIRQueryProcessor') as MockProcessor, \
                patch(datetime) as mock_datetime, \
                patch('app.main.current_user') as mock_current_user:
            mock_processor_instance = AsyncMock()
            MockProcessor.return_value = mock_processor_instance

            mock_processor_instance.build_fhir_query.return_value = {"fhir_url": "test"}
            mock_processor_instance.execute_fhir_query.return_value = {"test": "response"}
            mock_processor_instance.process_fhir_response.return_value = {"total_patients": 0, "patients": []}

            mock_current_user.id = "user-123"

            mock_now = Mock()
            mock_datetime.now.return_value = mock_now
            mock_now.__sub__ = Mock(return_value=Mock(total_seconds=Mock(return_value=1.0)))

            for query_data in special_queries:
                response = async_client.post("/query", json=query_data)
                assert response.status_code == 200
                assert response.json()["original_query"] == query_data["query"]

    @pytest.mark.asyncio
    async def test_process_query_large_response(self, async_client, mock_db, sample_query_data):
        """Test processing of large FHIR responses"""
        with patch('app.database.db_engine.get_session', return_value=mock_db), \
                patch('app.nlp.fhir_nlp_service.FHIRQueryProcessor') as MockProcessor, \
                patch(datetime) as mock_datetime, \
                patch('app.main.current_user') as mock_current_user:
            mock_processor_instance = AsyncMock()
            MockProcessor.return_value = mock_processor_instance

            # Create a large response
            large_fhir_response = {
                "resourceType": "Bundle",
                "type": "searchset",
                "entry": [{"resource": {"resourceType": "Patient", "id": f"patient-{i}"}}
                          for i in range(1000)]
            }

            large_processed_results = {
                "total_patients": 1000,
                "patients": [{"id": f"patient-{i}", "name": f"Patient {i}"}
                             for i in range(1000)],
                "raw_fhir_response": large_fhir_response
            }

            mock_processor_instance.build_fhir_query.return_value = {"fhir_url": "test", "filters": {}}
            mock_processor_instance.execute_fhir_query.return_value = large_fhir_response
            mock_processor_instance.process_fhir_response.return_value = large_processed_results

            mock_current_user.id = "user-123"

            mock_now = Mock()
            mock_datetime.now.return_value = mock_now
            mock_now.__sub__ = Mock(return_value=Mock(total_seconds=Mock(return_value=1.0)))

            response = async_client.post("/query", json=sample_query_data)

            assert response.status_code == 200
            response_data = response.json()
            assert response_data["processed_results"]["total_patients"] == 1000
            assert len(response_data["processed_results"]["patients"]) == 1000


# Test configuration
@pytest.fixture(autouse=True)
def no_sleep():
    """Prevent sleep in tests"""
    with patch('asyncio.sleep', return_value=None):
        yield


# Run the tests with different markers
@pytest.mark.fast
class TestFastRoutes:
    """Fast-running route tests"""

    def test_suggestions_fast(self, async_client):
        """Quick test for suggestions"""
        response = async_client.get("/suggestions")
        assert response.status_code == 200


@pytest.mark.integration
class TestIntegrationRoutes:
    """Integration tests for routes"""

    @pytest.mark.asyncio
    async def test_full_integration(self, async_client):
        """Test full integration workflow"""
        # This would be for tests that hit real endpoints
        # Use sparingly and mark as integration
        pass

@pytest.mark.asyncio
async def test_register_user_success(self, async_client):
    payload = {
        "email": "john@example.com",
        "username": "john",
        "password": "secret123",
    }
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert "hashed_password" not in data
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_email(self, async_client):
    payload = {
        "email": "dup@example.com",
        "username": "dupuser",
        "password": "secret123",
    }
    res1 = await async_client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = await async_client.post("/auth/register", json=payload)
    assert res2.status_code == 400
    assert "Email already registered" in res2.text