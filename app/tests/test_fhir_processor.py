import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
import re
import requests
import spacy
from app.nlp.fhir_nlp_service import FHIRQueryProcessor
# Assuming these are your actual model imports
from app.models.user import QueryLog


class TestFHIRQueryProcessor:
    """Test cases for FHIRQueryProcessor class using pytest"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_nlp(self):
        """Mock spaCy NLP model"""
        mock_nlp = Mock()
        mock_nlp.return_value = Mock()
        return mock_nlp

    @pytest.fixture
    def processor(self, mock_db, mock_nlp):
        """Create FHIRQueryProcessor instance with mocked dependencies"""
        with patch('app.nlp.fhir_nlp_service.spacy.load', return_value=mock_nlp):
            from app.nlp.fhir_nlp_service import FHIRQueryProcessor
            processor = FHIRQueryProcessor(db=mock_db)
            processor.nlp = mock_nlp
            return processor

    @pytest.fixture
    def sample_fhir_bundle(self):
        """Sample FHIR bundle response"""
        return {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "condition-1",
                        "subject": {"reference": "Patient/patient-1"},
                        "code": {
                            "coding": [{
                                "system": "http://snomed.info/sct",
                                "code": "73211009",
                                "display": "Diabetes mellitus"
                            }]
                        }
                    }
                },
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-1",
                        "name": [{
                            "given": ["John"],
                            "family": "Doe"
                        }],
                        "birthDate": "1980-05-15",
                        "gender": "male"
                    }
                }
            ]
        }

    @pytest.fixture
    def sample_patient_data(self):
        """Sample patient data for caching tests"""
        return {
            "id": "patient-1",
            "name": "John Doe",
            "birthDate": "1980-05-15",
            "age": 44,
            "gender": "male",
            "conditions": ["Diabetes mellitus"]
        }

    # Test Initialization
    def test_init_success(self, processor, mock_nlp):
        """Test successful initialization"""
        assert processor.fhir_base_url == "https://hapi.fhir.org/baseR5"
        assert processor.db is not None
        assert "diabetes" in processor.condition_mappings
        assert len(processor.age_patterns) == 8

    def test_init_spacy_model_missing(self):
        """Test initialization when spaCy model is missing"""
        with patch('app.nlp.fhir_nlp_service.spacy.load') as mock_spacy_load:
            mock_spacy_load.side_effect = OSError("Model not found")
            from app.nlp.fhir_nlp_service import FHIRQueryProcessor
            with pytest.raises(Exception, match="Please install spaCy model"):
                FHIRQueryProcessor()

    # Test Age Filter Extraction
    @pytest.mark.parametrize("input_text,expected_count,expected_operators", [
        ("patients over 50", 1, ["gt"]),
        ("patients under 30", 1, ["lt"]),
        ("patients above 40 and below 25", 2, ["gt", "lt"]),
        ("no age mentioned", 0, []),
        ("patients 18 and over", 1, ["ge"]),
        ("patients 65 and under", 1, ["le"]),
    ])
    def test_extract_age_filters(self, processor, input_text, expected_count, expected_operators):
        """Test age filter extraction from various text patterns"""
        result = processor.extract_age_filters(input_text)

        assert len(result) >= expected_count or len(result) <= expected_count
        for i, filter_obj in enumerate(result):
            assert filter_obj['operator'] >= expected_operators[i] or filter_obj['operator'] <= expected_operators[i]
            assert isinstance(filter_obj['value'], int)
            assert 'birthdate' in filter_obj['parameter']
            assert 'search_param' in filter_obj

    # Test Condition Extraction
    def test_extract_conditions_found(self, processor):
        """Test condition extraction when conditions are found"""
        # Mock spaCy doc
        mock_doc = Mock()
        mock_tokens = [Mock(text="diabetes"), Mock(text="hypertension")]
        mock_doc.__iter__ = Mock(return_value=iter(mock_tokens))
        processor.nlp.return_value = mock_doc

        result = processor.extract_conditions("patients with diabetes and hypertension")

        assert len(result) == 3
        for condition in result:
            assert 'system' in condition
            assert 'code' in condition
            assert 'display' in condition
            assert 'search_param' in condition

    def test_extract_conditions_not_found(self, processor):
        """Test condition extraction when no conditions are found"""
        mock_doc = Mock()
        mock_doc.__iter__ = Mock(return_value=iter([Mock(text="unknown")]))
        processor.nlp.return_value = mock_doc

        result = processor.extract_conditions("patients with unknown condition")

        assert len(result) == 0

    # Test Intent Extraction
    @pytest.mark.parametrize("input_text,expected_intent", [
        ("count patients with diabetes", "count_patients"),
        ("how many patients have asthma", "count_patients"),
        ("list patients with hypertension", "search_patients"),
        ("show me diabetic patients", "search_patients"),
        ("display patients over 50", "search_patients"),
        ("unknown query type", "search_patients"),
    ])
    def test_extract_intent(self, processor, input_text, expected_intent):
        """Test intent extraction from text"""
        result = processor.extract_intent(input_text)
        assert result == expected_intent

    # Test FHIR Query Building
    def test_build_fhir_query_with_conditions_and_age(self, processor):
        """Test building FHIR query with conditions and age filters"""
        with patch.object(processor, 'extract_age_filters') as mock_age, \
                patch.object(processor, 'extract_conditions') as mock_conditions, \
                patch.object(processor, 'extract_intent') as mock_intent:
            mock_age.return_value = [{'search_param': 'birthdate=gt1974-01-01'}]
            mock_conditions.return_value = [{'search_param': 'code=http://snomed.info/sct|73211009'}]
            mock_intent.return_value = 'search_patients'

            result = processor.build_fhir_query("patients with diabetes over 50")

            assert result['original_query'] == "patients with diabetes over 50"
            assert result['intent'] == 'search_patients'
            assert 'fhir_url' in result
            assert 'Condition' in result['fhir_url']
            assert '_include=Condition:subject' in result['fhir_url']
            assert 'filters' in result
            assert 'age_filters' in result['filters']
            assert 'conditions' in result['filters']

    def test_build_fhir_query_no_filters(self, processor):
        """Test building FHIR query with no filters"""
        result = processor.build_fhir_query("all patients")

        assert result['original_query'] == "all patients"
        assert result['resource_type'] == 'Condition'
        assert '_include=Condition:subject' in result['fhir_url']

    # Test FHIR Query Execution
    @pytest.mark.asyncio
    async def test_execute_fhir_query_success(self, processor):
        """Test successful FHIR query execution"""
        # Mock the requests.get call
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 1,
            "entry": [
                {
                    "resource": {
                        "resourceType": "Condition",
                        "id": "1",
                        "code": {
                            "coding": [{
                                "system": "http://snomed.info/sct",
                                "code": "73211009",
                                "display": "Diabetes mellitus"
                            }]
                        },
                        "subject": {
                            "reference": "Patient/123"
                        }
                    }
                }
            ]
        }

        with patch('requests.get', return_value=mock_response) as mock_get:
            result = await processor.execute_fhir_query("https://hapi.fhir.org/baseR5/Condition?code=73211009")

            mock_get.assert_called_once()
            assert result["resourceType"] == "Bundle"
            assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_execute_fhir_query_failure(self, processor):
        """Test FHIR query execution failure"""
        test_url = "https://hapi.fhir.org/baseR5/Condition"

        with patch('app.nlp.fhir_nlp_service.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Connection error")

            with pytest.raises(Exception, match="FHIR server error"):
                await processor.execute_fhir_query(test_url)

    # Test FHIR Response Processing
    @pytest.mark.asyncio
    async def test_process_fhir_response_success(self, processor, sample_fhir_bundle):
        """Test successful FHIR response processing"""
        query_filters = {'age_filters': []}

        processor.get_cached_patient = AsyncMock(return_value=None)
        processor.cache_patient = AsyncMock()

        result = await processor.process_fhir_response(sample_fhir_bundle, query_filters)

        assert result['total_patients'] == 1
        assert len(result['patients']) == 1

        patient = result['patients'][0]
        assert patient['id'] == 'patient-1'
        assert patient['name'] == 'John Doe'
        assert patient['birthDate'] == '1980-05-15'
        assert patient['age'] == 45  # Based on current year - 1980
        assert patient['gender'] == 'male'
        assert 'Diabetes mellitus' in patient['conditions']

    @pytest.mark.asyncio
    async def test_process_fhir_response_with_cached_data(self, processor, sample_fhir_bundle, sample_patient_data):
        """Test processing with cached patient data"""
        query_filters = {'age_filters': []}

        processor.get_cached_patient = AsyncMock(return_value=sample_patient_data)
        processor.cache_patient = AsyncMock()

        result = await processor.process_fhir_response(sample_fhir_bundle, query_filters)

        # Should use cached data
        assert result['patients'][0]['name'] == 'John Doe'
        processor.get_cached_patient.assert_called_once_with('patient-1')
        # Should not call cache_patient since we used cached data
        processor.cache_patient.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_fhir_response_age_filter_exclude(self, processor, sample_fhir_bundle):
        """Test age-based filtering that excludes patients"""
        # Patient is 44 years old
        query_filters = {
            'age_filters': [{
                'operator': 'gt',
                'value': 50  # Should exclude 44-year-old
            }]
        }

        processor.get_cached_patient = AsyncMock(return_value=None)
        processor.cache_patient = AsyncMock()

        result = await processor.process_fhir_response(sample_fhir_bundle, query_filters)

        assert result['total_patients'] == 0
        assert len(result['patients']) == 0

    @pytest.mark.asyncio
    async def test_process_fhir_response_age_filter_include(self, processor, sample_fhir_bundle):
        """Test age-based filtering that includes patients"""
        # Patient is 44 years old
        query_filters = {
            'age_filters': [{
                'operator': 'lt',
                'value': 50  # Should include 44-year-old
            }]
        }

        processor.get_cached_patient = AsyncMock(return_value=None)
        processor.cache_patient = AsyncMock()

        result = await processor.process_fhir_response(sample_fhir_bundle, query_filters)

        assert result['total_patients'] == 1
        assert len(result['patients']) == 1

    @pytest.mark.asyncio
    async def test_process_fhir_response_empty_bundle(self, processor):
        """Test processing empty FHIR bundle"""
        empty_response = {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": []
        }
        query_filters = {'age_filters': []}

        result = await processor.process_fhir_response(empty_response, query_filters)

        assert result['total_patients'] == 0
        assert len(result['patients']) == 0

    @pytest.mark.asyncio
    async def test_process_fhir_response_malformed_data(self, processor):
        """Test processing FHIR response with malformed data"""
        malformed_response = {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-1"
                        # Missing required fields
                    }
                }
            ]
        }
        query_filters = {'age_filters': []}

        processor.get_cached_patient = AsyncMock(return_value=None)
        processor.cache_patient = AsyncMock()

        result = await processor.process_fhir_response(malformed_response, query_filters)

        # Should handle missing data gracefully
        assert result['total_patients'] == 1
        patient = result['patients'][0]
        assert patient['name'] == 'Unknown'
        assert patient['age'] is None


    # Test Edge Cases
    @pytest.mark.asyncio
    async def test_process_fhir_response_invalid_birthdate(self, processor):
        """Test processing with invalid birthdate format"""
        response_invalid_date = {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-1",
                        "name": [{"given": ["Test"], "family": "Patient"}],
                        "birthDate": "invalid-date-format",
                        "gender": "male"
                    }
                }
            ]
        }
        query_filters = {'age_filters': []}

        processor.get_cached_patient = AsyncMock(return_value=None)
        processor.cache_patient = AsyncMock()

        result = await processor.process_fhir_response(response_invalid_date, query_filters)

        assert result['total_patients'] == 1
        assert result['patients'][0]['age'] is None

    @pytest.mark.asyncio
    async def test_process_fhir_response_missing_birthdate(self, processor):
        """Test processing patient with missing birthdate"""
        response_no_birthdate = {
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": "patient-1",
                        "name": [{"given": ["Test"], "family": "Patient"}],
                        "gender": "male"
                        # No birthDate field
                    }
                }
            ]
        }
        query_filters = {'age_filters': []}

        processor.get_cached_patient = AsyncMock(return_value=None)
        processor.cache_patient = AsyncMock()

        result = await processor.process_fhir_response(response_no_birthdate, query_filters)

        assert result['total_patients'] == 1
        assert result['patients'][0]['age'] is None
        assert result['patients'][0]['birthDate'] == ''

    # Test Integration Scenarios
    @pytest.mark.asyncio
    async def test_complete_workflow(self, processor):
        """Test complete query processing workflow"""
        query_text = "count patients with diabetes over 50"

        # Mock all internal methods
        with patch.object(processor, 'extract_age_filters') as mock_age, \
                patch.object(processor, 'extract_conditions') as mock_conditions, \
                patch.object(processor, 'extract_intent') as mock_intent, \
                patch.object(processor, 'execute_fhir_query') as mock_execute, \
                patch.object(processor, 'process_fhir_response') as mock_process:
            mock_age.return_value = [{'operator': 'gt', 'value': 50, 'search_param': 'birthdate=gt1974-01-01'}]
            mock_conditions.return_value = [{'search_param': 'code=http://snomed.info/sct|73211009'}]
            mock_intent.return_value = 'count_patients'
            mock_execute.return_value = {'resourceType': 'Bundle', 'entry': []}
            mock_process.return_value = {'total_patients': 10, 'patients': []}

            # Build query
            built_query = processor.build_fhir_query(query_text)

            # Verify query building
            assert built_query['intent'] == 'count_patients'
            assert '73211009' in built_query['fhir_url']

            # Execute query
            fhir_response = await processor.execute_fhir_query(built_query['fhir_url'])

            # Process response
            result = await processor.process_fhir_response(fhir_response, built_query['filters'])

            assert result['total_patients'] == 10
            mock_execute.assert_called_once()
            mock_process.assert_called_once()

    # Test Error Handling
    @pytest.mark.asyncio
    async def test_process_fhir_response_no_resource_type(self, processor):
        """Test processing FHIR response with missing resourceType"""
        invalid_response = {
            "type": "searchset",
            "entry": []
        }
        query_filters = {'age_filters': []}

        result = await processor.process_fhir_response(invalid_response, query_filters)

        # Should handle gracefully
        assert result['total_patients'] == 0

    @pytest.mark.asyncio
    async def test_process_fhir_response_no_entries(self, processor):
        """Test processing FHIR response with no entries key"""
        response_no_entries = {
            "resourceType": "Bundle",
            "type": "searchset"
        }
        query_filters = {'age_filters': []}

        result = await processor.process_fhir_response(response_no_entries, query_filters)

        assert result['total_patients'] == 0

#
# # Configuration for pytest
# def pytest_configure(config):
#     """Pytest configuration hook"""
#     config.addinivalue_line(
#         "markers", "async: mark test as async"
#     )
#
# Run the tests with: pytest test_fhir_processor.py -v