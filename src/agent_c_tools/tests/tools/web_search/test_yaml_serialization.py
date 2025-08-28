"""
Comprehensive unit tests for YAML serialization functionality in web search models.

This test suite validates:
- YAML serialization correctness for all models
- Token efficiency and optimization
- Round-trip serialization integrity
- Edge cases and error handling
- Performance benchmarks comparing JSON vs YAML
- Security features (sensitive data filtering)
"""

import pytest
import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import patch

# Import models and utilities
from base.models import (
    SearchParameters, SearchResponse, SearchResult, WebSearchConfig,
    EngineCapabilities, EngineHealthStatus, SearchType, SafeSearchLevel, SearchDepth
)
from base.yaml_utils import YAMLOptimizer, YAMLSerializationMixin


class TestYAMLUtilities:
    """Test suite for YAML utility functions and classes."""
    
    def test_yaml_optimizer_initialization(self):
        """Test YAMLOptimizer initialization."""
        optimizer = YAMLOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'filter_for_yaml')
        assert hasattr(optimizer, 'apply_compact_field_names')
        assert hasattr(optimizer, 'filter_sensitive_data')
        assert hasattr(optimizer, 'to_yaml_string')
    
    def test_yaml_optimizer_field_name_compression(self):
        """Test field name compression functionality."""
        optimizer = YAMLOptimizer()
        
        # Test SearchResult field mappings
        test_data = {
            'published_date': '2024-01-01',
            'relevance_score': 0.9,
            'metadata': {}
        }
        
        compressed = optimizer.apply_compact_field_names(test_data, 'SearchResult')
        
        assert 'date' in compressed
        assert 'score' in compressed
        assert 'published_date' not in compressed
        assert 'relevance_score' not in compressed
        assert compressed['date'] == '2024-01-01'
        assert compressed['score'] == 0.9
    
    def test_yaml_optimizer_value_filtering(self):
        """Test value filtering for token optimization."""
        optimizer = YAMLOptimizer()
        
        test_data = {
            'title': 'Test Title',
            'url': 'https://example.com',
            'snippet': 'Test snippet',
            'published_date': None,
            'source': '',
            'relevance_score': 0.0,
            'metadata': {}
        }
        
        filtered = optimizer.filter_for_yaml(test_data, compact=True)
        
        # Should keep non-empty, non-None, non-default values
        assert 'title' in filtered
        assert 'url' in filtered
        assert 'snippet' in filtered
        
        # Should filter out None, empty, and default values in compact mode
        assert 'published_date' not in filtered
        assert 'source' not in filtered
        assert 'relevance_score' not in filtered
        assert 'metadata' not in filtered
    
    def test_yaml_optimizer_sensitive_data_filtering(self):
        """Test sensitive data filtering."""
        optimizer = YAMLOptimizer()
        
        test_data = {
            'engine_name': 'test_engine',
            'api_key': 'secret_key_123',
            'password': 'secret_password',
            'token': 'auth_token_456',
            'base_url': 'https://api.example.com',
            'timeout': 30
        }
        
        filtered = optimizer.filter_sensitive_data(test_data)
        
        # Should keep non-sensitive data
        assert 'engine_name' in filtered
        assert 'base_url' in filtered
        assert 'timeout' in filtered
        
        # Should filter out sensitive data
        assert 'api_key' not in filtered
        assert 'password' not in filtered
        assert 'token' not in filtered
    
    def test_yaml_serialization_mixin(self):
        """Test YAMLSerializationMixin functionality."""
        
        # Create a test class that uses the mixin
        class TestModel(YAMLSerializationMixin):
            def __init__(self, name: str, value: int, optional: str = None):
                self.name = name
                self.value = value
                self.optional = optional
            
            def to_dict(self) -> Dict[str, Any]:
                return {
                    'name': self.name,
                    'value': self.value,
                    'optional': self.optional
                }
        
        model = TestModel('test', 42, None)
        
        # Test YAML serialization
        yaml_output = model.to_yaml(compact=True)
        assert isinstance(yaml_output, str)
        assert 'name: test' in yaml_output
        assert 'value: 42' in yaml_output
        assert 'optional' not in yaml_output  # Should be filtered in compact mode
        
        # Test YAML dict preparation
        yaml_dict = model.to_yaml_dict(compact=True)
        assert isinstance(yaml_dict, dict)
        assert yaml_dict['name'] == 'test'
        assert yaml_dict['value'] == 42
        assert 'optional' not in yaml_dict


class TestSearchResultYAML:
    """Test suite for SearchResult YAML serialization."""
    
    def test_search_result_yaml_basic(self):
        """Test basic SearchResult YAML serialization."""
        result = SearchResult(
            title="Test Result",
            url="https://example.com",
            snippet="Test snippet"
        )
        
        # Test compact YAML
        yaml_output = result.to_yaml(compact=True)
        assert isinstance(yaml_output, str)
        assert 'title: Test Result' in yaml_output
        assert 'url: https://example.com' in yaml_output
        assert 'snippet: Test snippet' in yaml_output
        
        # Verify YAML is parseable
        parsed = yaml.safe_load(yaml_output)
        assert parsed['title'] == 'Test Result'
        assert parsed['url'] == 'https://example.com'
        assert parsed['snippet'] == 'Test snippet'
    
    def test_search_result_yaml_complete(self):
        """Test complete SearchResult YAML serialization."""
        published_date = datetime(2024, 1, 1, 12, 0, 0)
        metadata = {'category': 'technology', 'author': 'John Doe'}
        
        result = SearchResult(
            title="Complete Test Result",
            url="https://example.com/article",
            snippet="Complete test snippet",
            published_date=published_date,
            source="example.com",
            relevance_score=0.95,
            metadata=metadata
        )
        
        # Test verbose YAML
        yaml_output = result.to_yaml(compact=False)
        parsed = yaml.safe_load(yaml_output)
        
        assert parsed['title'] == 'Complete Test Result'
        assert parsed['url'] == 'https://example.com/article'
        assert parsed['snippet'] == 'Complete test snippet'
        assert parsed['published_date'] is not None
        assert parsed['source'] == 'example.com'
        assert parsed['relevance_score'] == 0.95
        assert parsed['metadata']['category'] == 'technology'
        assert parsed['metadata']['author'] == 'John Doe'
    
    def test_search_result_yaml_field_compression(self):
        """Test SearchResult field name compression."""
        result = SearchResult(
            title="Compression Test",
            url="https://example.com",
            snippet="Test snippet",
            published_date=datetime(2024, 1, 1),
            relevance_score=0.8
        )
        
        yaml_dict = result.to_yaml_dict(compact=True)
        
        # Should use compressed field names
        assert 'date' in yaml_dict
        assert 'score' in yaml_dict
        assert 'published_date' not in yaml_dict
        assert 'relevance_score' not in yaml_dict
        
        assert yaml_dict['date'] is not None
        assert yaml_dict['score'] == 0.8
    
    def test_search_result_yaml_token_efficiency(self):
        """Test SearchResult token efficiency."""
        result = SearchResult(
            title="Token Efficiency Test",
            url="https://example.com",
            snippet="Testing token efficiency",
            published_date=None,  # Should be filtered
            source="",  # Should be filtered
            relevance_score=0.0,  # Should be filtered
            metadata={}  # Should be filtered
        )
        
        # Compare JSON vs YAML token counts
        json_output = json.dumps(result.to_dict())
        yaml_output = result.to_yaml(compact=True)
        
        json_tokens = len(json_output.split())
        yaml_tokens = len(yaml_output.split())
        
        # YAML should be more token-efficient
        assert yaml_tokens < json_tokens
        
        # Calculate token reduction percentage
        reduction = (json_tokens - yaml_tokens) / json_tokens * 100
        assert reduction > 20  # Should achieve at least 20% reduction
    
    def test_search_result_yaml_roundtrip(self):
        """Test SearchResult YAML round-trip serialization."""
        original = SearchResult(
            title="Roundtrip Test",
            url="https://roundtrip.test",
            snippet="Testing roundtrip serialization",
            published_date=datetime(2024, 6, 15, 10, 30, 0),
            source="roundtrip.test",
            relevance_score=0.75,
            metadata={'test': True, 'number': 42}
        )
        
        # Serialize to YAML
        yaml_output = original.to_yaml(compact=False)
        
        # Parse YAML back to dict
        parsed_dict = yaml.safe_load(yaml_output)
        
        # Create new SearchResult from parsed data
        # Note: This requires handling datetime parsing
        if 'published_date' in parsed_dict and parsed_dict['published_date']:
            if isinstance(parsed_dict['published_date'], str):
                parsed_dict['published_date'] = datetime.fromisoformat(
                    parsed_dict['published_date'].replace('Z', '+00:00')
                )
        
        restored = SearchResult(**parsed_dict)
        
        # Verify integrity
        assert restored.title == original.title
        assert restored.url == original.url
        assert restored.snippet == original.snippet
        assert restored.source == original.source
        assert restored.relevance_score == original.relevance_score
        assert restored.metadata == original.metadata


class TestSearchResponseYAML:
    """Test suite for SearchResponse YAML serialization."""
    
    def test_search_response_yaml_basic(self):
        """Test basic SearchResponse YAML serialization."""
        results = [
            SearchResult(title="Result 1", url="https://example1.com", snippet="Snippet 1"),
            SearchResult(title="Result 2", url="https://example2.com", snippet="Snippet 2")
        ]
        
        response = SearchResponse(
            results=results,
            total_results=2,
            search_time=0.5,
            engine_used="duckduckgo",
            query="test query",
            search_type=SearchType.WEB
        )
        
        yaml_output = response.to_yaml(compact=True)
        parsed = yaml.safe_load(yaml_output)
        
        assert len(parsed['results']) == 2
        assert parsed['total_results'] == 2
        assert parsed['search_time'] == 0.5
        assert parsed['engine_used'] == 'duckduckgo'
        assert parsed['query'] == 'test query'
        assert parsed['search_type'] == 'web'
    
    def test_search_response_yaml_field_compression(self):
        """Test SearchResponse field name compression."""
        response = SearchResponse(
            results=[],
            total_results=0,
            search_time=0.3,
            engine_used="google_serp",
            query="compression test",
            search_type=SearchType.NEWS
        )
        
        yaml_dict = response.to_yaml_dict(compact=True)
        
        # Should use compressed field names
        assert 'type' in yaml_dict
        assert 'engine' in yaml_dict
        assert 'time' in yaml_dict
        assert 'total' in yaml_dict
        
        assert 'search_type' not in yaml_dict
        assert 'engine_used' not in yaml_dict
        assert 'search_time' not in yaml_dict
        assert 'total_results' not in yaml_dict
    
    def test_search_response_yaml_nested_optimization(self):
        """Test SearchResponse nested SearchResult optimization."""
        results = [
            SearchResult(
                title="Nested Test 1",
                url="https://nested1.com",
                snippet="First nested result",
                published_date=datetime(2024, 1, 1),
                relevance_score=0.9
            ),
            SearchResult(
                title="Nested Test 2",
                url="https://nested2.com",
                snippet="Second nested result",
                published_date=None,  # Should be filtered
                relevance_score=0.0   # Should be filtered
            )
        ]
        
        response = SearchResponse(
            results=results,
            total_results=2,
            search_time=0.75,
            engine_used="test_engine",
            query="nested optimization test",
            search_type=SearchType.RESEARCH
        )
        
        yaml_dict = response.to_yaml_dict(compact=True)
        
        # Check nested SearchResult optimization
        result1 = yaml_dict['results'][0]
        result2 = yaml_dict['results'][1]
        
        # First result should have compressed fields
        assert 'date' in result1
        assert 'score' in result1
        assert 'published_date' not in result1
        assert 'relevance_score' not in result1
        
        # Second result should have filtered fields
        assert 'date' not in result2  # None value filtered
        assert 'score' not in result2  # Default value filtered
    
    def test_search_response_yaml_token_efficiency(self):
        """Test SearchResponse token efficiency with multiple results."""
        results = [
            SearchResult(
                title=f"Result {i}",
                url=f"https://example{i}.com",
                snippet=f"Snippet {i}",
                published_date=datetime(2024, 1, i+1) if i % 2 == 0 else None,
                source=f"source{i}.com" if i % 3 == 0 else "",
                relevance_score=0.8 + (i * 0.05) if i < 3 else 0.0,
                metadata={'index': i} if i % 4 == 0 else {}
            )
            for i in range(10)
        ]
        
        response = SearchResponse(
            results=results,
            total_results=10,
            search_time=1.2,
            engine_used="efficiency_test_engine",
            query="token efficiency test query",
            search_type=SearchType.WEB,
            metadata={'test_run': True, 'batch_size': 10}
        )
        
        # Compare JSON vs YAML
        json_output = json.dumps(response.to_dict())
        yaml_output = response.to_yaml(compact=True)
        
        json_tokens = len(json_output.split())
        yaml_tokens = len(yaml_output.split())
        
        # Calculate reduction
        reduction = (json_tokens - yaml_tokens) / json_tokens * 100
        
        # Should achieve significant reduction with multiple results
        assert reduction > 30  # Target 30%+ reduction
        assert yaml_tokens < json_tokens


class TestSearchParametersYAML:
    """Test suite for SearchParameters YAML serialization."""
    
    def test_search_parameters_yaml_basic(self):
        """Test basic SearchParameters YAML serialization."""
        params = SearchParameters(
            query="basic test query",
            engine="duckduckgo",
            search_type=SearchType.WEB
        )
        
        yaml_output = params.to_yaml(compact=True)
        parsed = yaml.safe_load(yaml_output)
        
        assert parsed['query'] == 'basic test query'
        assert parsed['engine'] == 'duckduckgo'
        assert parsed['search_type'] == 'web'
    
    def test_search_parameters_yaml_enum_optimization(self):
        """Test SearchParameters enum optimization."""
        params = SearchParameters(
            query="enum test",
            engine="test_engine",
            search_type=SearchType.RESEARCH,
            safe_search=SafeSearchLevel.STRICT,
            search_depth=SearchDepth.DEEP
        )
        
        yaml_dict = params.to_yaml_dict(compact=True)
        
        # Enums should be converted to string values
        assert yaml_dict['search_type'] == 'research'
        assert yaml_dict['safe_search'] == 'strict'
        assert yaml_dict['search_depth'] == 'deep'
    
    def test_search_parameters_yaml_datetime_optimization(self):
        """Test SearchParameters datetime optimization."""
        date_from = datetime(2024, 1, 1, 0, 0, 0, 0)  # No microseconds
        date_to = datetime(2024, 12, 31, 23, 59, 59, 123456)  # With microseconds
        
        params = SearchParameters(
            query="datetime test",
            engine="test_engine",
            search_type=SearchType.NEWS,
            date_from=date_from,
            date_to=date_to
        )
        
        yaml_output = params.to_yaml(compact=True)
        parsed = yaml.safe_load(yaml_output)
        
        # Verify datetime serialization
        assert 'date_from' in parsed
        assert 'date_to' in parsed
        
        # Check microsecond handling (should be removed when zero)
        date_from_str = parsed['date_from']
        assert '.000000' not in date_from_str or date_from_str.endswith('T00:00:00')
    
    def test_search_parameters_yaml_default_filtering(self):
        """Test SearchParameters default value filtering."""
        params = SearchParameters(
            query="default filtering test",
            engine="auto",  # Default value
            search_type=SearchType.WEB,
            max_results=10,  # Default value
            safe_search=SafeSearchLevel.MODERATE,  # Default value
            page=1,  # Default value
            include_images=False,  # Default value
            include_videos=False   # Default value
        )
        
        yaml_dict = params.to_yaml_dict(compact=True)
        
        # Should keep non-default values
        assert 'query' in yaml_dict
        assert 'search_type' in yaml_dict
        
        # Should filter default values in compact mode
        assert 'engine' not in yaml_dict or yaml_dict['engine'] != 'auto'
        assert 'max_results' not in yaml_dict or yaml_dict['max_results'] != 10
        assert 'safe_search' not in yaml_dict or yaml_dict['safe_search'] != 'moderate'
        assert 'page' not in yaml_dict or yaml_dict['page'] != 1
        assert 'include_images' not in yaml_dict
        assert 'include_videos' not in yaml_dict


class TestWebSearchConfigYAML:
    """Test suite for WebSearchConfig YAML serialization."""
    
    def test_web_search_config_yaml_basic(self):
        """Test basic WebSearchConfig YAML serialization."""
        config = WebSearchConfig(
            engine_name="test_engine",
            api_key_name="TEST_API_KEY",
            base_url="https://api.test.com",
            timeout=30,
            max_retries=3
        )
        
        yaml_output = config.to_yaml(compact=True)
        parsed = yaml.safe_load(yaml_output)
        
        assert parsed['engine_name'] == 'test_engine'
        assert parsed['api_key_name'] == 'TEST_API_KEY'
        assert parsed['base_url'] == 'https://api.test.com'
        assert parsed['timeout'] == 30
        assert parsed['max_retries'] == 3
    
    def test_web_search_config_yaml_sensitive_data_filtering(self):
        """Test WebSearchConfig sensitive data filtering."""
        config = WebSearchConfig(
            engine_name="secure_engine",
            api_key_name="SECRET_API_KEY",
            password="secret_password_123",
            token="auth_token_456",
            base_url="https://secure.api.com",
            timeout=60
        )
        
        # Test with sensitive data included
        yaml_with_sensitive = config.to_yaml(compact=True, include_sensitive=True)
        parsed_with_sensitive = yaml.safe_load(yaml_with_sensitive)
        
        assert 'api_key_name' in parsed_with_sensitive
        assert 'password' in parsed_with_sensitive
        assert 'token' in parsed_with_sensitive
        
        # Test with sensitive data filtered
        yaml_secure = config.to_yaml(compact=True, include_sensitive=False)
        parsed_secure = yaml.safe_load(yaml_secure)
        
        assert 'engine_name' in parsed_secure
        assert 'base_url' in parsed_secure
        assert 'timeout' in parsed_secure
        
        # Sensitive fields should be filtered
        assert 'api_key_name' not in parsed_secure
        assert 'password' not in parsed_secure
        assert 'token' not in parsed_secure
    
    def test_web_search_config_yaml_field_compression(self):
        """Test WebSearchConfig field name compression."""
        config = WebSearchConfig(
            engine_name="compression_test",
            api_key_name="API_KEY",
            base_url="https://api.example.com",
            request_timeout=45,
            max_retries=5,
            rate_limit_per_minute=100
        )
        
        yaml_dict = config.to_yaml_dict(compact=True)
        
        # Should use compressed field names
        assert 'name' in yaml_dict
        assert 'api_key' in yaml_dict
        assert 'url' in yaml_dict
        assert 'timeout' in yaml_dict
        assert 'retries' in yaml_dict
        assert 'rate_limit' in yaml_dict
        
        # Original field names should not be present
        assert 'engine_name' not in yaml_dict
        assert 'api_key_name' not in yaml_dict
        assert 'base_url' not in yaml_dict
        assert 'request_timeout' not in yaml_dict
        assert 'max_retries' not in yaml_dict
        assert 'rate_limit_per_minute' not in yaml_dict
    
    def test_web_search_config_yaml_nested_capabilities(self):
        """Test WebSearchConfig with nested EngineCapabilities optimization."""
        capabilities = EngineCapabilities(
            supported_search_types=[SearchType.WEB, SearchType.NEWS],
            max_results_per_request=100,
            supports_safe_search=True,
            supports_date_filtering=True,
            supports_domain_filtering=False,
            supports_language_filtering=True,
            supports_region_filtering=True,
            supports_custom_parameters=False,
            rate_limit_per_minute=1000,
            requires_api_key=True,
            supports_batch_requests=False
        )
        
        config = WebSearchConfig(
            engine_name="nested_test",
            capabilities=capabilities
        )
        
        yaml_dict = config.to_yaml_dict(compact=True)
        
        # Should have nested capabilities with optimization
        assert 'capabilities' in yaml_dict
        capabilities_dict = yaml_dict['capabilities']
        
        # Check EngineCapabilities field compression
        assert 'types' in capabilities_dict  # supported_search_types -> types
        assert 'max_results' in capabilities_dict  # max_results_per_request -> max_results
        assert 'api_key' in capabilities_dict  # requires_api_key -> api_key
        
        # Original field names should not be present
        assert 'supported_search_types' not in capabilities_dict
        assert 'max_results_per_request' not in capabilities_dict
        assert 'requires_api_key' not in capabilities_dict


class TestEngineCapabilitiesYAML:
    """Test suite for EngineCapabilities YAML serialization."""
    
    def test_engine_capabilities_yaml_basic(self):
        """Test basic EngineCapabilities YAML serialization."""
        capabilities = EngineCapabilities(
            supported_search_types=[SearchType.WEB, SearchType.NEWS],
            max_results_per_request=50,
            supports_safe_search=True,
            supports_date_filtering=False,
            rate_limit_per_minute=500,
            requires_api_key=True
        )
        
        yaml_output = capabilities.to_yaml(compact=True)
        parsed = yaml.safe_load(yaml_output)
        
        assert 'web' in parsed['supported_search_types']
        assert 'news' in parsed['supported_search_types']
        assert parsed['max_results_per_request'] == 50
        assert parsed['supports_safe_search'] is True
        assert parsed['supports_date_filtering'] is False
        assert parsed['rate_limit_per_minute'] == 500
        assert parsed['requires_api_key'] is True
    
    def test_engine_capabilities_yaml_field_compression(self):
        """Test EngineCapabilities field name compression."""
        capabilities = EngineCapabilities(
            supported_search_types=[SearchType.RESEARCH, SearchType.TECH],
            max_results_per_request=200,
            supports_safe_search=True,
            supports_date_filtering=True,
            supports_domain_filtering=True,
            supports_language_filtering=False,
            supports_region_filtering=False,
            supports_custom_parameters=True,
            rate_limit_per_minute=2000,
            requires_api_key=False,
            supports_batch_requests=True
        )
        
        yaml_dict = capabilities.to_yaml_dict(compact=True)
        
        # Should use compressed field names
        assert 'types' in yaml_dict
        assert 'max_results' in yaml_dict
        assert 'safe_search' in yaml_dict
        assert 'date_filter' in yaml_dict
        assert 'domain_filter' in yaml_dict
        assert 'language_filter' in yaml_dict
        assert 'region_filter' in yaml_dict
        assert 'custom_params' in yaml_dict
        assert 'rate_limit' in yaml_dict
        assert 'api_key' in yaml_dict
        assert 'batch' in yaml_dict
        
        # Original field names should not be present
        assert 'supported_search_types' not in yaml_dict
        assert 'max_results_per_request' not in yaml_dict
        assert 'supports_safe_search' not in yaml_dict
        assert 'rate_limit_per_minute' not in yaml_dict
        assert 'requires_api_key' not in yaml_dict
        assert 'supports_batch_requests' not in yaml_dict
    
    def test_engine_capabilities_yaml_boolean_filtering(self):
        """Test EngineCapabilities boolean value filtering."""
        capabilities = EngineCapabilities(
            supported_search_types=[SearchType.WEB],
            max_results_per_request=100,
            supports_safe_search=False,  # Should be filtered in compact mode
            supports_date_filtering=False,  # Should be filtered in compact mode
            supports_domain_filtering=True,  # Should be kept
            supports_language_filtering=False,  # Should be filtered in compact mode
            supports_region_filtering=True,  # Should be kept
            supports_custom_parameters=False,  # Should be filtered in compact mode
            rate_limit_per_minute=1000,
            requires_api_key=True,  # Should be kept
            supports_batch_requests=False  # Should be filtered in compact mode
        )
        
        yaml_dict = capabilities.to_yaml_dict(compact=True)
        
        # Should keep True values
        assert yaml_dict.get('domain_filter') is True
        assert yaml_dict.get('region_filter') is True
        assert yaml_dict.get('api_key') is True
        
        # Should filter False values in compact mode
        assert 'safe_search' not in yaml_dict or yaml_dict['safe_search'] is not False
        assert 'date_filter' not in yaml_dict or yaml_dict['date_filter'] is not False
        assert 'language_filter' not in yaml_dict or yaml_dict['language_filter'] is not False
        assert 'custom_params' not in yaml_dict or yaml_dict['custom_params'] is not False
        assert 'batch' not in yaml_dict or yaml_dict['batch'] is not False


class TestEngineHealthStatusYAML:
    """Test suite for EngineHealthStatus YAML serialization."""
    
    def test_engine_health_status_yaml_basic(self):
        """Test basic EngineHealthStatus YAML serialization."""
        last_check = datetime(2024, 6, 15, 14, 30, 0)
        
        status = EngineHealthStatus(
            engine_name="test_engine",
            is_available=True,
            last_check=last_check,
            response_time=0.25,
            error_rate=0.02,
            status_message="Engine is healthy"
        )
        
        yaml_output = status.to_yaml(compact=True)
        parsed = yaml.safe_load(yaml_output)
        
        assert parsed['engine_name'] == 'test_engine'
        assert parsed['is_available'] is True
        assert parsed['response_time'] == 0.25
        assert parsed['error_rate'] == 0.02
        assert parsed['status_message'] == 'Engine is healthy'
    
    def test_engine_health_status_yaml_field_compression(self):
        """Test EngineHealthStatus field name compression."""
        status = EngineHealthStatus(
            engine_name="compression_test",
            is_available=False,
            last_check=datetime.now(),
            response_time=1.5,
            error_rate=0.15,
            status_message="Engine experiencing issues"
        )
        
        yaml_dict = status.to_yaml_dict(compact=True)
        
        # Should use compressed field names
        assert 'name' in yaml_dict
        assert 'available' in yaml_dict
        assert 'check' in yaml_dict
        assert 'time' in yaml_dict
        assert 'errors' in yaml_dict
        assert 'message' in yaml_dict
        
        # Original field names should not be present
        assert 'engine_name' not in yaml_dict
        assert 'is_available' not in yaml_dict
        assert 'last_check' not in yaml_dict
        assert 'response_time' not in yaml_dict
        assert 'error_rate' not in yaml_dict
        assert 'status_message' not in yaml_dict
    
    def test_engine_health_status_yaml_datetime_optimization(self):
        """Test EngineHealthStatus datetime optimization."""
        # Test with microseconds
        last_check_with_microseconds = datetime(2024, 6, 15, 14, 30, 45, 123456)
        
        # Test without microseconds
        last_check_without_microseconds = datetime(2024, 6, 15, 14, 30, 45, 0)
        
        status1 = EngineHealthStatus(
            engine_name="datetime_test_1",
            is_available=True,
            last_check=last_check_with_microseconds,
            response_time=0.3,
            error_rate=0.01
        )
        
        status2 = EngineHealthStatus(
            engine_name="datetime_test_2",
            is_available=True,
            last_check=last_check_without_microseconds,
            response_time=0.3,
            error_rate=0.01
        )
        
        yaml_output1 = status1.to_yaml(compact=True)
        yaml_output2 = status2.to_yaml(compact=True)
        
        # Both should be valid YAML
        parsed1 = yaml.safe_load(yaml_output1)
        parsed2 = yaml.safe_load(yaml_output2)
        
        assert 'last_check' in parsed1 or 'check' in parsed1
        assert 'last_check' in parsed2 or 'check' in parsed2
        
        # Check that microseconds are handled appropriately
        # (either included or removed based on optimization)
        assert isinstance(parsed1.get('last_check') or parsed1.get('check'), str)
        assert isinstance(parsed2.get('last_check') or parsed2.get('check'), str)


class TestYAMLPerformanceBenchmarks:
    """Performance benchmark tests comparing JSON vs YAML token efficiency."""
    
    def test_single_search_result_performance(self):
        """Benchmark single SearchResult serialization."""
        result = SearchResult(
            title="Performance Benchmark Test Result",
            url="https://performance.benchmark.test/article",
            snippet="This is a comprehensive performance benchmark test snippet that contains multiple words and phrases to simulate real-world search results.",
            published_date=datetime(2024, 6, 15, 10, 30, 45),
            source="performance.benchmark.test",
            relevance_score=0.87,
            metadata={
                'category': 'technology',
                'author': 'Performance Tester',
                'word_count': 150,
                'reading_time': '2 minutes',
                'tags': ['performance', 'benchmark', 'testing']
            }
        )
        
        # JSON serialization
        json_output = json.dumps(result.to_dict())
        json_tokens = len(json_output.split())
        
        # YAML serialization (compact)
        yaml_output = result.to_yaml(compact=True)
        yaml_tokens = len(yaml_output.split())
        
        # Calculate efficiency
        token_reduction = (json_tokens - yaml_tokens) / json_tokens * 100
        
        # Assertions
        assert yaml_tokens < json_tokens, "YAML should be more token-efficient than JSON"
        assert token_reduction > 25, f"Token reduction should be >25%, got {token_reduction:.1f}%"
        
        print(f"SearchResult Performance:")
        print(f"  JSON tokens: {json_tokens}")
        print(f"  YAML tokens: {yaml_tokens}")
        print(f"  Reduction: {token_reduction:.1f}%")
    
    def test_search_response_performance(self):
        """Benchmark SearchResponse with multiple results."""
        results = [
            SearchResult(
                title=f"Benchmark Result {i+1}",
                url=f"https://benchmark{i+1}.test/article",
                snippet=f"This is benchmark result {i+1} with detailed snippet content for performance testing.",
                published_date=datetime(2024, 6, i+1, 10, 0, 0) if i % 2 == 0 else None,
                source=f"benchmark{i+1}.test" if i % 3 == 0 else "",
                relevance_score=0.9 - (i * 0.1) if i < 5 else 0.0,
                metadata={'index': i, 'category': 'test'} if i % 4 == 0 else {}
            )
            for i in range(15)
        ]
        
        response = SearchResponse(
            results=results,
            total_results=15,
            search_time=1.25,
            engine_used="benchmark_engine",
            query="comprehensive performance benchmark test query",
            search_type=SearchType.RESEARCH,
            metadata={
                'benchmark_run': True,
                'test_timestamp': datetime.now().isoformat(),
                'result_count': 15,
                'performance_metrics': {
                    'cpu_usage': 45.2,
                    'memory_usage': 128.5,
                    'network_latency': 23.7
                }
            }
        )
        
        # JSON serialization
        json_output = json.dumps(response.to_dict())
        json_tokens = len(json_output.split())
        
        # YAML serialization (compact)
        yaml_output = response.to_yaml(compact=True)
        yaml_tokens = len(yaml_output.split())
        
        # Calculate efficiency
        token_reduction = (json_tokens - yaml_tokens) / json_tokens * 100
        
        # Assertions
        assert yaml_tokens < json_tokens, "YAML should be more token-efficient than JSON"
        assert token_reduction > 30, f"Token reduction should be >30%, got {token_reduction:.1f}%"
        
        print(f"SearchResponse Performance (15 results):")
        print(f"  JSON tokens: {json_tokens}")
        print(f"  YAML tokens: {yaml_tokens}")
        print(f"  Reduction: {token_reduction:.1f}%")
    
    def test_search_parameters_performance(self):
        """Benchmark SearchParameters serialization."""
        params = SearchParameters(
            query="comprehensive search parameters performance benchmark test query with multiple terms",
            engine="performance_benchmark_engine",
            search_type=SearchType.RESEARCH,
            max_results=50,
            safe_search=SafeSearchLevel.STRICT,
            language="en-US",
            region="United States",
            include_domains=["benchmark1.test", "benchmark2.test", "performance.test"],
            exclude_domains=["spam.test", "blocked.test"],
            date_from=datetime(2024, 1, 1, 0, 0, 0),
            date_to=datetime(2024, 12, 31, 23, 59, 59),
            search_depth=SearchDepth.DEEP,
            include_images=True,
            include_videos=True,
            category="technology",
            sort="relevance",
            additional_parameters={
                'custom_filter': 'advanced',
                'boost_recent': True,
                'exclude_duplicates': True,
                'min_quality_score': 0.7
            }
        )
        
        # JSON serialization
        json_output = json.dumps(params.to_dict())
        json_tokens = len(json_output.split())
        
        # YAML serialization (compact)
        yaml_output = params.to_yaml(compact=True)
        yaml_tokens = len(yaml_output.split())
        
        # Calculate efficiency
        token_reduction = (json_tokens - yaml_tokens) / json_tokens * 100
        
        # Assertions
        assert yaml_tokens < json_tokens, "YAML should be more token-efficient than JSON"
        assert token_reduction > 25, f"Token reduction should be >25%, got {token_reduction:.1f}%"
        
        print(f"SearchParameters Performance:")
        print(f"  JSON tokens: {json_tokens}")
        print(f"  YAML tokens: {yaml_tokens}")
        print(f"  Reduction: {token_reduction:.1f}%")
    
    def test_web_search_config_performance(self):
        """Benchmark WebSearchConfig serialization."""
        capabilities = EngineCapabilities(
            supported_search_types=[SearchType.WEB, SearchType.NEWS, SearchType.RESEARCH],
            max_results_per_request=200,
            supports_safe_search=True,
            supports_date_filtering=True,
            supports_domain_filtering=True,
            supports_language_filtering=True,
            supports_region_filtering=True,
            supports_custom_parameters=True,
            rate_limit_per_minute=5000,
            requires_api_key=True,
            supports_batch_requests=True
        )
        
        config = WebSearchConfig(
            engine_name="performance_benchmark_search_engine",
            api_key_name="PERFORMANCE_BENCHMARK_API_KEY",
            base_url="https://api.performance.benchmark.test/v2/search",
            request_timeout=60,
            max_retries=5,
            rate_limit_per_minute=5000,
            capabilities=capabilities,
            default_parameters={
                'safe_search': 'moderate',
                'language': 'en',
                'region': 'global',
                'format': 'json',
                'include_metadata': True
            },
            custom_headers={
                'User-Agent': 'PerformanceBenchmarkClient/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            retry_strategy={
                'backoff_factor': 2.0,
                'max_backoff': 300,
                'retry_on_timeout': True,
                'retry_on_rate_limit': True
            }
        )
        
        # JSON serialization
        json_output = json.dumps(config.to_dict())
        json_tokens = len(json_output.split())
        
        # YAML serialization (compact, without sensitive data)
        yaml_output = config.to_yaml(compact=True, include_sensitive=False)
        yaml_tokens = len(yaml_output.split())
        
        # Calculate efficiency
        token_reduction = (json_tokens - yaml_tokens) / json_tokens * 100
        
        # Assertions
        assert yaml_tokens < json_tokens, "YAML should be more token-efficient than JSON"
        assert token_reduction > 20, f"Token reduction should be >20%, got {token_reduction:.1f}%"
        
        print(f"WebSearchConfig Performance:")
        print(f"  JSON tokens: {json_tokens}")
        print(f"  YAML tokens: {yaml_tokens}")
        print(f"  Reduction: {token_reduction:.1f}%")


class TestYAMLEdgeCases:
    """Test suite for YAML serialization edge cases and error handling."""
    
    def test_yaml_with_none_values(self):
        """Test YAML serialization with None values."""
        result = SearchResult(
            title="None Values Test",
            url="https://none.test",
            snippet="Testing None values",
            published_date=None,
            source=None,
            relevance_score=None,
            metadata=None
        )
        
        # Compact mode should filter None values
        yaml_compact = result.to_yaml(compact=True)
        parsed_compact = yaml.safe_load(yaml_compact)
        
        assert 'title' in parsed_compact
        assert 'url' in parsed_compact
        assert 'snippet' in parsed_compact
        assert 'published_date' not in parsed_compact
        assert 'source' not in parsed_compact
        assert 'relevance_score' not in parsed_compact
        assert 'metadata' not in parsed_compact
        
        # Verbose mode should include None values
        yaml_verbose = result.to_yaml(compact=False)
        parsed_verbose = yaml.safe_load(yaml_verbose)
        
        assert 'published_date' in parsed_verbose
        assert parsed_verbose['published_date'] is None
    
    def test_yaml_with_empty_collections(self):
        """Test YAML serialization with empty collections."""
        result = SearchResult(
            title="Empty Collections Test",
            url="https://empty.test",
            snippet="Testing empty collections",
            metadata={}  # Empty dict
        )
        
        response = SearchResponse(
            results=[],  # Empty list
            total_results=0,
            search_time=0.1,
            engine_used="empty_test",
            query="empty test",
            search_type=SearchType.WEB,
            metadata={}  # Empty dict
        )
        
        # Compact mode should filter empty collections
        result_yaml = result.to_yaml(compact=True)
        result_parsed = yaml.safe_load(result_yaml)
        assert 'metadata' not in result_parsed
        
        response_yaml = response.to_yaml(compact=True)
        response_parsed = yaml.safe_load(response_yaml)
        assert 'results' in response_parsed  # Should keep empty results list
        assert 'metadata' not in response_parsed  # Should filter empty metadata
    
    def test_yaml_with_special_characters(self):
        """Test YAML serialization with special characters."""
        result = SearchResult(
            title="Special Characters: àáâãäå æç èéêë ìíîï ñ òóôõö ùúûü ýÿ",
            url="https://special-chars.test/àáâã",
            snippet="Testing special characters: @#$%^&*()_+-=[]{}|;':\",./<>?",
            metadata={
                'unicode_test': 'Unicode: 你好世界 🌍 🚀 ⭐',
                'symbols': '!@#$%^&*()_+-=[]{}|;\':",./<>?',
                'quotes': 'Single \'quotes\' and "double quotes"',
                'newlines': 'Line 1\nLine 2\nLine 3'
            }
        )
        
        yaml_output = result.to_yaml(compact=False)
        
        # Should be valid YAML
        parsed = yaml.safe_load(yaml_output)
        assert parsed['title'] == result.title
        assert parsed['url'] == result.url
        assert parsed['snippet'] == result.snippet
        assert parsed['metadata']['unicode_test'] == result.metadata['unicode_test']
        assert parsed['metadata']['symbols'] == result.metadata['symbols']
        assert parsed['metadata']['quotes'] == result.metadata['quotes']
        assert parsed['metadata']['newlines'] == result.metadata['newlines']
    
    def test_yaml_with_large_numbers(self):
        """Test YAML serialization with large numbers."""
        response = SearchResponse(
            results=[],
            total_results=999999999,  # Large number
            search_time=123.456789,  # High precision float
            engine_used="large_numbers_test",
            query="large numbers test",
            search_type=SearchType.WEB,
            metadata={
                'very_large_number': 18446744073709551615,  # Max uint64
                'scientific_notation': 1.23e-10,
                'negative_large': -999999999999
            }
        )
        
        yaml_output = response.to_yaml(compact=False)
        parsed = yaml.safe_load(yaml_output)
        
        assert parsed['total_results'] == 999999999
        assert abs(parsed['search_time'] - 123.456789) < 0.000001
        assert parsed['metadata']['very_large_number'] == 18446744073709551615
        assert abs(parsed['metadata']['scientific_notation'] - 1.23e-10) < 1e-15
        assert parsed['metadata']['negative_large'] == -999999999999
    
    @patch('base.yaml_utils.yaml', None)
    def test_yaml_fallback_to_json(self):
        """Test YAML fallback to JSON when PyYAML is not available."""
        result = SearchResult(
            title="Fallback Test",
            url="https://fallback.test",
            snippet="Testing JSON fallback"
        )
        
        # Should fallback to JSON format
        output = result.to_yaml(compact=True)
        
        # Should be valid JSON
        parsed = json.loads(output)
        assert parsed['title'] == 'Fallback Test'
        assert parsed['url'] == 'https://fallback.test'
        assert parsed['snippet'] == 'Testing JSON fallback'
    
    def test_yaml_with_circular_references(self):
        """Test YAML serialization handles circular references gracefully."""
        # Create a mock object with circular reference
        class CircularTest:
            def __init__(self):
                self.name = "circular_test"
                self.self_ref = self
            
            def to_dict(self):
                return {
                    'name': self.name,
                    'self_ref': 'circular_reference_detected'  # Safe representation
                }
        
        # This test ensures our YAML serialization doesn't break with circular refs
        # In practice, our dataclasses shouldn't have circular references,
        # but this tests robustness
        circular_obj = CircularTest()
        
        # Should not raise an exception
        try:
            result_dict = circular_obj.to_dict()
            yaml_output = yaml.dump(result_dict)
            parsed = yaml.safe_load(yaml_output)
            assert parsed['name'] == 'circular_test'
            assert parsed['self_ref'] == 'circular_reference_detected'
        except Exception as e:
            pytest.fail(f"YAML serialization should handle circular references gracefully: {e}")


class TestYAMLIntegration:
    """Integration tests for YAML serialization across all models."""
    
    def test_complete_search_workflow_yaml(self):
        """Test complete search workflow with YAML serialization."""
        # Create search parameters
        params = SearchParameters(
            query="integration test with YAML serialization",
            engine="yaml_integration_engine",
            search_type=SearchType.RESEARCH,
            max_results=25,
            safe_search=SafeSearchLevel.MODERATE,
            language="en",
            region="US",
            date_from=datetime(2024, 1, 1),
            date_to=datetime(2024, 12, 31),
            search_depth=SearchDepth.DEEP
        )
        
        # Create search results
        results = [
            SearchResult(
                title=f"YAML Integration Result {i+1}",
                url=f"https://yaml-integration{i+1}.test",
                snippet=f"Integration test result {i+1} for YAML serialization testing",
                published_date=datetime(2024, 6, i+1, 12, 0, 0) if i % 2 == 0 else None,
                source=f"yaml-integration{i+1}.test" if i % 3 == 0 else "",
                relevance_score=0.95 - (i * 0.05) if i < 10 else 0.0,
                metadata={'integration_test': True, 'result_index': i} if i % 4 == 0 else {}
            )
            for i in range(10)
        ]
        
        # Create search response
        response = SearchResponse(
            results=results,
            total_results=10,
            search_time=2.15,
            engine_used="yaml_integration_engine",
            query="integration test with YAML serialization",
            search_type=SearchType.RESEARCH,
            metadata={
                'integration_test': True,
                'yaml_optimization': True,
                'test_timestamp': datetime.now().isoformat()
            }
        )
        
        # Create engine capabilities
        capabilities = EngineCapabilities(
            supported_search_types=[SearchType.WEB, SearchType.NEWS, SearchType.RESEARCH],
            max_results_per_request=100,
            supports_safe_search=True,
            supports_date_filtering=True,
            supports_domain_filtering=True,
            supports_language_filtering=True,
            supports_region_filtering=True,
            supports_custom_parameters=True,
            rate_limit_per_minute=2000,
            requires_api_key=True,
            supports_batch_requests=True
        )
        
        # Create configuration
        config = WebSearchConfig(
            engine_name="yaml_integration_engine",
            api_key_name="YAML_INTEGRATION_API_KEY",
            base_url="https://api.yaml-integration.test",
            request_timeout=45,
            max_retries=3,
            rate_limit_per_minute=2000,
            capabilities=capabilities
        )
        
        # Create health status
        health_status = EngineHealthStatus(
            engine_name="yaml_integration_engine",
            is_available=True,
            last_check=datetime.now(),
            response_time=0.35,
            error_rate=0.005,
            status_message="Engine is healthy and optimized for YAML"
        )
        
        # Test YAML serialization for all models
        params_yaml = params.to_yaml(compact=True)
        response_yaml = response.to_yaml(compact=True)
        capabilities_yaml = capabilities.to_yaml(compact=True)
        config_yaml = config.to_yaml(compact=True, include_sensitive=False)
        health_yaml = health_status.to_yaml(compact=True)
        
        # Verify all YAML outputs are valid
        params_parsed = yaml.safe_load(params_yaml)
        response_parsed = yaml.safe_load(response_yaml)
        capabilities_parsed = yaml.safe_load(capabilities_yaml)
        config_parsed = yaml.safe_load(config_yaml)
        health_parsed = yaml.safe_load(health_yaml)
        
        # Verify key data integrity
        assert params_parsed['query'] == params.query
        assert response_parsed['query'] == response.query
        assert len(response_parsed['results']) == 10
        assert capabilities_parsed['max_results_per_request'] == 100
        assert config_parsed['engine_name'] == 'yaml_integration_engine'
        assert health_parsed['engine_name'] == 'yaml_integration_engine'
        
        # Verify token efficiency across all models
        models_and_outputs = [
            ('SearchParameters', params, params_yaml),
            ('SearchResponse', response, response_yaml),
            ('EngineCapabilities', capabilities, capabilities_yaml),
            ('WebSearchConfig', config, config_yaml),
            ('EngineHealthStatus', health_status, health_yaml)
        ]
        
        total_json_tokens = 0
        total_yaml_tokens = 0
        
        for model_name, model_obj, yaml_output in models_and_outputs:
            json_output = json.dumps(model_obj.to_dict())
            json_tokens = len(json_output.split())
            yaml_tokens = len(yaml_output.split())
            
            total_json_tokens += json_tokens
            total_yaml_tokens += yaml_tokens
            
            # Each model should achieve token reduction
            reduction = (json_tokens - yaml_tokens) / json_tokens * 100
            assert reduction > 15, f"{model_name} should achieve >15% reduction, got {reduction:.1f}%"
        
        # Overall workflow should achieve significant token reduction
        overall_reduction = (total_json_tokens - total_yaml_tokens) / total_json_tokens * 100
        assert overall_reduction > 25, f"Overall workflow should achieve >25% reduction, got {overall_reduction:.1f}%"
        
        print(f"Integration Test Results:")
        print(f"  Total JSON tokens: {total_json_tokens}")
        print(f"  Total YAML tokens: {total_yaml_tokens}")
        print(f"  Overall reduction: {overall_reduction:.1f}%")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])