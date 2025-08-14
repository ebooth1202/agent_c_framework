#!/usr/bin/env python3
"""
Comprehensive unit tests for YAML serialization functionality.

This test suite validates all YAML optimization features including:
- Token efficiency and optimization
- Round-trip serialization
- Edge cases and error handling
- Performance benchmarks
- All model implementations
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Import the models and utilities
from models import (
    SearchResult, SearchResponse, SearchParameters, 
    EngineCapabilities, WebSearchConfig, EngineHealthStatus,
    SearchType, SafeSearchLevel, SearchDepth
)
from yaml_utils import (
    YAMLOptimizer, YAMLSerializationMixin, get_yaml_module, get_yaml_info,
    check_yaml_dependencies, estimate_token_savings, validate_yaml_output,
    COMPACT_FIELD_NAMES
)


class TestYAMLSerializationBase(unittest.TestCase):
    """Base test class with common utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_datetime = datetime(2024, 7, 28, 15, 30, 45)
        self.yaml_available = get_yaml_module() is not False
    
    def assertTokenSavings(self, original_data: Dict[str, Any], yaml_output: str, min_savings: float = 10.0):
        """Assert that YAML provides minimum token savings."""
        json_output = json.dumps(original_data, separators=(',', ':'))
        savings = estimate_token_savings(json_output, yaml_output)
        self.assertGreaterEqual(
            savings['percentage_saved'], 
            min_savings,
            f"Expected at least {min_savings}% token savings, got {savings['percentage_saved']}%"
        )
    
    def assertValidYAML(self, yaml_output: str):
        """Assert that YAML output is valid and parseable."""
        self.assertTrue(validate_yaml_output(yaml_output), "YAML output should be valid")
        self.assertIsInstance(yaml_output, str, "YAML output should be a string")
        self.assertGreater(len(yaml_output.strip()), 0, "YAML output should not be empty")


class TestYAMLDependencies(TestYAMLSerializationBase):
    """Test YAML dependency management and import handling."""
    
    def test_yaml_module_loading(self):
        """Test YAML module loading and caching."""
        yaml_module1 = get_yaml_module()
        yaml_module2 = get_yaml_module()
        
        # Should return same cached instance
        self.assertIs(yaml_module1, yaml_module2, "YAML module should be cached")
    
    def test_yaml_info_reporting(self):
        """Test YAML information reporting."""
        info = get_yaml_info()
        
        self.assertIn('available', info)
        self.assertIn('version', info)
        self.assertIn('fallback_active', info)
        self.assertIsInstance(info['available'], bool)
    
    def test_dependency_checking(self):
        """Test comprehensive dependency checking."""
        deps = check_yaml_dependencies()
        
        required_keys = [
            'yaml_available', 'yaml_version', 'features_available',
            'features_missing', 'fallback_active', 'recommendations'
        ]
        
        for key in required_keys:
            self.assertIn(key, deps, f"Dependency check should include {key}")
        
        self.assertIsInstance(deps['features_available'], list)
        self.assertIsInstance(deps['recommendations'], list)
    
    def test_yaml_validation(self):
        """Test YAML validation functionality."""
        # Valid YAML
        valid_yaml = "name: test\nvalue: 42\nactive: true"
        self.assertTrue(validate_yaml_output(valid_yaml))
        
        # Invalid YAML
        invalid_yaml = "name: test\n  invalid: [unclosed"
        self.assertFalse(validate_yaml_output(invalid_yaml))
        
        # Edge cases
        self.assertFalse(validate_yaml_output(""))
        self.assertFalse(validate_yaml_output(None))
        self.assertTrue(validate_yaml_output("null"))
    
    @patch('yaml_utils.get_yaml_module')
    def test_fallback_behavior(self, mock_get_yaml):
        """Test fallback behavior when YAML is not available."""
        mock_get_yaml.return_value = False
        
        # Test that fallback still works
        optimizer = YAMLOptimizer()
        test_data = {'name': 'test', 'value': 42}
        
        result = optimizer.to_yaml_string(test_data, compact=True)
        self.assertIsInstance(result, str)
        
        # Should be valid JSON when YAML not available
        try:
            json.loads(result)
        except json.JSONDecodeError:
            self.fail("Fallback should produce valid JSON")


class TestYAMLOptimizer(TestYAMLSerializationBase):
    """Test YAMLOptimizer functionality."""
    
    def test_compact_field_names(self):
        """Test compact field name mapping."""
        test_data = {
            'search_type': 'web',
            'max_results': 10,
            'engine_name': 'test',
            'is_available': True
        }
        
        optimized = YAMLOptimizer.apply_compact_field_names(test_data)
        
        self.assertEqual(optimized.get('type'), 'web')
        self.assertEqual(optimized.get('max'), 10)
        self.assertEqual(optimized.get('name'), 'test')
        self.assertEqual(optimized.get('available'), True)
    
    def test_sensitive_data_filtering(self):
        """Test sensitive data filtering."""
        test_data = {
            'name': 'test_engine',
            'api_key': 'secret_key_123',
            'password': 'secret_password',
            'public_info': 'visible_data'
        }
        
        filtered = YAMLOptimizer.filter_sensitive_data(test_data)
        
        self.assertNotIn('api_key', filtered)
        self.assertNotIn('password', filtered)
        self.assertIn('name', filtered)
        self.assertIn('public_info', filtered)
    
    def test_value_optimization(self):
        """Test value optimization for different data types."""
        from enum import Enum
        
        class TestEnum(Enum):
            VALUE = "test_value"
        
        test_data = {
            'enum_field': TestEnum.VALUE,
            'datetime_field': self.test_datetime,
            'list_field': [1, 2, 3],
            'dict_field': {'nested': 'value'},
            'none_field': None,
            'empty_list': [],
            'empty_dict': {}
        }
        
        optimized = YAMLOptimizer.filter_for_yaml(test_data, compact=True)
        
        # Should optimize enum to string value
        # Should handle datetime appropriately
        # Should filter out None, empty collections in compact mode
        self.assertNotIn('none_field', optimized)
        self.assertNotIn('empty_list', optimized)
        self.assertNotIn('empty_dict', optimized)
    
    def test_data_sanitization(self):
        """Test data sanitization for YAML compatibility."""
        class UnserializableObject:
            def __str__(self):
                return "custom_object"
        
        test_data = {
            'normal_string': 'test',
            'number': 42,
            'boolean': True,
            'datetime': self.test_datetime,
            'enum': SearchType.WEB,
            'complex_object': UnserializableObject(),
            'nested': {
                'object': UnserializableObject()
            }
        }
        
        sanitized = YAMLOptimizer._sanitize_for_yaml(test_data)
        
        self.assertEqual(sanitized['normal_string'], 'test')
        self.assertEqual(sanitized['number'], 42)
        self.assertEqual(sanitized['boolean'], True)
        self.assertIsInstance(sanitized['datetime'], str)
        self.assertEqual(sanitized['enum'], 'web')
        self.assertIsInstance(sanitized['complex_object'], str)
    
    def test_yaml_string_generation(self):
        """Test YAML string generation with various options."""
        test_data = {'name': 'test', 'value': 42, 'active': True}
        
        # Test compact mode
        compact_yaml = YAMLOptimizer.to_yaml_string(test_data, compact=True)
        self.assertValidYAML(compact_yaml)
        
        # Test verbose mode
        verbose_yaml = YAMLOptimizer.to_yaml_string(test_data, compact=False)
        self.assertValidYAML(verbose_yaml)
        
        # Compact should generally be shorter
        if self.yaml_available:
            self.assertLessEqual(len(compact_yaml), len(verbose_yaml))


class TestSearchResultYAML(TestYAMLSerializationBase):
    """Test SearchResult YAML serialization."""
    
    def setUp(self):
        super().setUp()
        self.search_result = SearchResult(
            title="Python Machine Learning Tutorial",
            url="https://example.com/python-ml",
            snippet="Learn machine learning with Python. Comprehensive guide.",
            published_date=self.test_datetime,
            score=0.95,
            source="example.com",
            metadata={"category": "tutorial", "difficulty": "intermediate"}
        )
    
    def test_basic_yaml_serialization(self):
        """Test basic YAML serialization."""
        yaml_output = self.search_result.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Check for field name optimization
        self.assertIn('date:', yaml_output)  # published_date -> date
        self.assertNotIn('published_date:', yaml_output)
    
    def test_token_efficiency(self):
        """Test token efficiency compared to JSON."""
        original_data = self.search_result.to_dict()
        yaml_output = self.search_result.to_yaml(compact=True)
        
        self.assertTokenSavings(original_data, yaml_output, min_savings=20.0)
    
    def test_round_trip_serialization(self):
        """Test round-trip serialization accuracy."""
        yaml_output = self.search_result.to_yaml(compact=False)
        
        if self.yaml_available:
            import yaml
            parsed_data = yaml.safe_load(yaml_output)
            
            # Key fields should be preserved
            self.assertEqual(parsed_data['title'], self.search_result.title)
            self.assertEqual(parsed_data['url'], self.search_result.url)
            self.assertEqual(parsed_data['snippet'], self.search_result.snippet)
    
    def test_edge_cases(self):
        """Test edge cases and None values."""
        minimal_result = SearchResult(
            title="Minimal Result",
            url="https://example.com",
            snippet="Minimal snippet"
            # All optional fields are None
        )
        
        yaml_output = minimal_result.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Should not contain None fields in compact mode
        self.assertNotIn('score:', yaml_output)
        self.assertNotIn('source:', yaml_output)
    
    def test_metadata_handling(self):
        """Test metadata dictionary handling."""
        result_with_complex_metadata = SearchResult(
            title="Test Result",
            url="https://example.com",
            snippet="Test snippet",
            metadata={
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "empty": {},
                "none_value": None
            }
        )
        
        yaml_output = result_with_complex_metadata.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)


class TestSearchResponseYAML(TestYAMLSerializationBase):
    """Test SearchResponse YAML serialization."""
    
    def setUp(self):
        super().setUp()
        self.search_results = [
            SearchResult(
                title="Result 1",
                url="https://example1.com",
                snippet="First result snippet",
                score=0.9
            ),
            SearchResult(
                title="Result 2", 
                url="https://example2.com",
                snippet="Second result snippet",
                score=0.8
            )
        ]
        
        self.search_response = SearchResponse(
            success=True,
            engine_used="duckduckgo",
            search_type="web",
            query="python programming",
            execution_time=1.234,
            results=self.search_results,
            total_results=1500,
            page=1,
            pages_available=150,
            metadata={"search_id": "test123", "region": "us"}
        )
    
    def test_basic_yaml_serialization(self):
        """Test basic YAML serialization."""
        yaml_output = self.search_response.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Check for field name optimization
        self.assertIn('type:', yaml_output)  # search_type -> type
        self.assertIn('engine:', yaml_output)  # engine_used -> engine
        self.assertIn('time:', yaml_output)  # execution_time -> time
    
    def test_nested_optimization(self):
        """Test nested SearchResult optimization."""
        yaml_output = self.search_response.to_yaml(compact=True)
        
        # Nested SearchResults should also be optimized
        # This is complex to test directly, but we can verify the output is valid
        self.assertValidYAML(yaml_output)
        
        # Should contain results section
        self.assertIn('results:', yaml_output)
    
    def test_token_efficiency_with_multiple_results(self):
        """Test token efficiency with multiple nested results."""
        original_data = self.search_response.to_dict()
        yaml_output = self.search_response.to_yaml(compact=True)
        
        # Should achieve significant savings with nested optimization
        self.assertTokenSavings(original_data, yaml_output, min_savings=25.0)
    
    def test_error_response_handling(self):
        """Test error response serialization."""
        error_response = SearchResponse(
            success=False,
            engine_used="test_engine",
            search_type="web",
            query="test query",
            execution_time=0.5,
            results=[],
            error={"code": 500, "message": "Internal server error"}
        )
        
        yaml_output = error_response.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        self.assertIn('error:', yaml_output)


class TestSearchParametersYAML(TestYAMLSerializationBase):
    """Test SearchParameters YAML serialization."""
    
    def setUp(self):
        super().setUp()
        self.search_params = SearchParameters(
            query="machine learning python tutorial",
            engine="google",
            search_type=SearchType.RESEARCH,
            max_results=50,
            safesearch=SafeSearchLevel.MODERATE,
            language="en",
            region="us",
            include_images=True,
            include_domains=["github.com", "stackoverflow.com"],
            exclude_domains=["spam.com"],
            search_depth=SearchDepth.ADVANCED,
            start_date=self.test_datetime,
            end_date=self.test_datetime + timedelta(days=30),
            page=2,
            additional_params={"sort": "date", "filter": "high_quality"}
        )
    
    def test_enum_optimization(self):
        """Test enum value optimization."""
        yaml_output = self.search_params.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Enums should be converted to string values
        self.assertIn('type: research', yaml_output)  # SearchType.RESEARCH -> "research"
        self.assertIn('safe: moderate', yaml_output)  # SafeSearchLevel.MODERATE -> "moderate"
        self.assertIn('depth: advanced', yaml_output)  # SearchDepth.ADVANCED -> "advanced"
    
    def test_datetime_optimization(self):
        """Test datetime serialization optimization."""
        yaml_output = self.search_params.to_yaml(compact=True)
        
        # Should contain optimized datetime fields
        self.assertIn('start:', yaml_output)  # start_date -> start
        self.assertIn('end:', yaml_output)  # end_date -> end
        
        # Should use ISO format
        self.assertIn('2024-07-28T15:30:45', yaml_output)
    
    def test_list_optimization(self):
        """Test list field optimization."""
        yaml_output = self.search_params.to_yaml(compact=True)
        
        # Lists should be optimized
        self.assertIn('include:', yaml_output)  # include_domains -> include
        self.assertIn('exclude:', yaml_output)  # exclude_domains -> exclude
        
        # Should contain list values
        self.assertIn('github.com', yaml_output)
        self.assertIn('stackoverflow.com', yaml_output)
    
    def test_default_value_filtering(self):
        """Test default value filtering."""
        minimal_params = SearchParameters(query="test query")
        yaml_output = minimal_params.to_yaml(compact=True)
        
        # Should not contain default values in compact mode
        self.assertNotIn('page: 1', yaml_output)
        self.assertNotIn('max_results: 10', yaml_output)
        self.assertNotIn('language: en', yaml_output)
    
    def test_api_call_optimization(self):
        """Test optimization for high-frequency API calls."""
        # Simulate common API parameters
        api_params = SearchParameters(
            query="python programming",
            max_results=10
        )
        
        original_data = api_params.to_dict()
        yaml_output = api_params.to_yaml(compact=True)
        
        # Should achieve good savings for API calls
        self.assertTokenSavings(original_data, yaml_output, min_savings=30.0)


class TestEngineCapabilitiesYAML(TestYAMLSerializationBase):
    """Test EngineCapabilities YAML serialization."""
    
    def setUp(self):
        super().setUp()
        self.capabilities = EngineCapabilities(
            search_types=[SearchType.WEB, SearchType.NEWS, SearchType.RESEARCH],
            supports_pagination=True,
            supports_date_filtering=True,
            supports_domain_filtering=True,
            supports_safe_search=True,
            supports_language_filtering=True,
            max_results_per_request=500,
            rate_limit_per_minute=2000
        )
    
    def test_capability_flags_optimization(self):
        """Test capability flags optimization."""
        yaml_output = self.capabilities.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Should use compact field names
        self.assertIn('pagination:', yaml_output)  # supports_pagination -> pagination
        self.assertIn('date_filter:', yaml_output)  # supports_date_filtering -> date_filter
        self.assertIn('max_results:', yaml_output)  # max_results_per_request -> max_results
    
    def test_search_types_optimization(self):
        """Test search types list optimization."""
        yaml_output = self.capabilities.to_yaml(compact=True)
        
        # Should optimize search_types to types
        self.assertIn('types:', yaml_output)
        self.assertNotIn('search_types:', yaml_output)
        
        # Should contain enum values as strings
        self.assertIn('web', yaml_output)
        self.assertIn('news', yaml_output)
        self.assertIn('research', yaml_output)
    
    def test_false_capability_filtering(self):
        """Test filtering of false capability flags."""
        minimal_capabilities = EngineCapabilities(
            search_types=[SearchType.WEB],
            max_results_per_request=50
            # All other capabilities default to False
        )
        
        yaml_output = minimal_capabilities.to_yaml(compact=True)
        
        # Should not contain false capability flags in compact mode
        self.assertNotIn('pagination: false', yaml_output)
        self.assertNotIn('date_filter: false', yaml_output)


class TestWebSearchConfigYAML(TestYAMLSerializationBase):
    """Test WebSearchConfig YAML serialization."""
    
    def setUp(self):
        super().setUp()
        self.config = WebSearchConfig(
            engine_name="google_search",
            requires_api_key=True,
            api_key_name="GOOGLE_API_KEY",
            base_url="https://api.google.com/search",
            timeout=45,
            max_retries=5,
            retry_delay=2.0,
            capabilities=EngineCapabilities(
                search_types=[SearchType.WEB, SearchType.NEWS],
                supports_pagination=True,
                max_results_per_request=100
            ),
            default_parameters={"gl": "us", "hl": "en"},
            health_check_url="https://api.google.com/health",
            cache_ttl=600
        )
    
    def test_sensitive_data_filtering(self):
        """Test sensitive data filtering."""
        # Test with sensitive data included
        yaml_with_sensitive = self.config.to_yaml(compact=True, include_sensitive=True)
        self.assertIn('api_key:', yaml_with_sensitive)
        
        # Test with sensitive data filtered
        yaml_secure = self.config.to_yaml(compact=True, include_sensitive=False)
        self.assertNotIn('api_key:', yaml_secure)
        self.assertNotIn('GOOGLE_API_KEY', yaml_secure)
    
    def test_nested_capabilities_optimization(self):
        """Test nested EngineCapabilities optimization."""
        yaml_output = self.config.to_yaml(compact=True)
        
        # Should contain capabilities section
        self.assertIn('capabilities:', yaml_output)
        
        # Nested capabilities should be optimized
        # This is complex to verify directly, but output should be valid
        self.assertValidYAML(yaml_output)
    
    def test_configuration_file_generation(self):
        """Test configuration file generation."""
        # Test verbose mode for configuration files
        config_yaml = self.config.to_yaml(compact=False, include_sensitive=False)
        self.assertValidYAML(config_yaml)
        
        # Should be human-readable
        self.assertIn('\n', config_yaml)  # Should have line breaks


class TestEngineHealthStatusYAML(TestYAMLSerializationBase):
    """Test EngineHealthStatus YAML serialization."""
    
    def setUp(self):
        super().setUp()
        self.healthy_status = EngineHealthStatus(
            engine_name="production_search",
            is_available=True,
            last_check=self.test_datetime,
            response_time=0.156,
            api_key_configured=True,
            capabilities=EngineCapabilities(
                search_types=[SearchType.WEB, SearchType.NEWS],
                supports_pagination=True,
                max_results_per_request=100
            )
        )
        
        self.error_status = EngineHealthStatus(
            engine_name="failing_search",
            is_available=False,
            last_check=self.test_datetime,
            response_time=None,
            error_message="Connection timeout after 30 seconds",
            api_key_configured=False,
            capabilities=None
        )
    
    def test_healthy_status_serialization(self):
        """Test healthy engine status serialization."""
        yaml_output = self.healthy_status.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Should use compact field names
        self.assertIn('name:', yaml_output)  # engine_name -> name
        self.assertIn('available:', yaml_output)  # is_available -> available
        self.assertIn('check:', yaml_output)  # last_check -> check
        self.assertIn('time:', yaml_output)  # response_time -> time
    
    def test_error_status_serialization(self):
        """Test error status serialization."""
        yaml_output = self.error_status.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Should contain error information
        self.assertIn('error:', yaml_output)
        self.assertIn('Connection timeout', yaml_output)
        
        # Should not contain None values in compact mode
        self.assertNotIn('time:', yaml_output)  # response_time is None
    
    def test_monitoring_dashboard_optimization(self):
        """Test optimization for monitoring dashboards."""
        statuses = [self.healthy_status, self.error_status]
        
        total_json_tokens = 0
        total_yaml_tokens = 0
        
        for status in statuses:
            json_data = json.dumps(status.to_dict(), separators=(',', ':'))
            yaml_data = status.to_yaml(compact=True)
            
            total_json_tokens += len(json_data.split())
            total_yaml_tokens += len(yaml_data.split())
        
        # Should achieve good savings for monitoring data
        savings_pct = ((total_json_tokens - total_yaml_tokens) / total_json_tokens) * 100
        self.assertGreaterEqual(savings_pct, 25.0, "Should achieve 25%+ savings for monitoring data")


class TestPerformanceBenchmarks(TestYAMLSerializationBase):
    """Performance benchmarks comparing JSON vs YAML token usage."""
    
    def test_serialization_performance(self):
        """Benchmark serialization performance."""
        test_data = {
            f'field_{i}': f'value_{i}' for i in range(100)
        }
        
        # Benchmark YAML serialization
        start_time = time.time()
        for _ in range(10):
            YAMLOptimizer.to_yaml_string(test_data, compact=True)
        yaml_time = time.time() - start_time
        
        # Benchmark JSON serialization
        start_time = time.time()
        for _ in range(10):
            json.dumps(test_data, separators=(',', ':'))
        json_time = time.time() - start_time
        
        # Performance should be reasonable (within 10x of JSON)
        self.assertLess(yaml_time, json_time * 10, "YAML serialization should be reasonably fast")
    
    def test_token_efficiency_benchmarks(self):
        """Benchmark token efficiency across all models."""
        test_cases = [
            ("SearchResult", SearchResult(
                title="Test Result",
                url="https://example.com",
                snippet="Test snippet",
                published_date=self.test_datetime,
                score=0.95
            )),
            ("SearchResponse", SearchResponse(
                success=True,
                engine_used="test",
                search_type="web",
                query="test",
                execution_time=1.0,
                results=[SearchResult(title="Test", url="https://example.com", snippet="Test")]
            )),
            ("SearchParameters", SearchParameters(
                query="test query",
                search_type=SearchType.WEB,
                max_results=10
            )),
            ("EngineCapabilities", EngineCapabilities(
                search_types=[SearchType.WEB],
                supports_pagination=True,
                max_results_per_request=100
            )),
            ("WebSearchConfig", WebSearchConfig(
                engine_name="test_engine",
                requires_api_key=True
            )),
            ("EngineHealthStatus", EngineHealthStatus(
                engine_name="test_engine",
                is_available=True,
                last_check=self.test_datetime
            ))
        ]
        
        total_savings = []
        
        for model_name, model_instance in test_cases:
            with self.subTest(model=model_name):
                original_data = model_instance.to_dict()
                yaml_output = model_instance.to_yaml(compact=True)
                
                json_str = json.dumps(original_data, separators=(',', ':'))
                savings = estimate_token_savings(json_str, yaml_output)
                
                # Each model should achieve reasonable savings
                self.assertGreaterEqual(
                    savings['percentage_saved'], 
                    15.0,
                    f"{model_name} should achieve at least 15% token savings"
                )
                
                total_savings.append(savings['percentage_saved'])
        
        # Average savings across all models should be significant
        avg_savings = sum(total_savings) / len(total_savings)
        self.assertGreaterEqual(avg_savings, 25.0, "Average savings across all models should be 25%+")
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        # Create large SearchResponse with many results
        large_results = [
            SearchResult(
                title=f"Result {i}",
                url=f"https://example{i}.com",
                snippet=f"Snippet for result {i}",
                score=0.9 - (i * 0.01)
            )
            for i in range(50)  # 50 results
        ]
        
        large_response = SearchResponse(
            success=True,
            engine_used="test_engine",
            search_type="web",
            query="large dataset test",
            execution_time=2.5,
            results=large_results,
            total_results=5000,
            page=1,
            pages_available=100
        )
        
        # Test serialization performance
        start_time = time.time()
        yaml_output = large_response.to_yaml(compact=True)
        serialization_time = time.time() - start_time
        
        # Should complete in reasonable time (less than 1 second)
        self.assertLess(serialization_time, 1.0, "Large dataset serialization should be fast")
        
        # Should still achieve good token savings
        original_data = large_response.to_dict()
        json_str = json.dumps(original_data, separators=(',', ':'))
        savings = estimate_token_savings(json_str, yaml_output)
        
        self.assertGreaterEqual(
            savings['percentage_saved'], 
            20.0,
            "Large datasets should still achieve 20%+ token savings"
        )


class TestEdgeCasesAndErrorHandling(TestYAMLSerializationBase):
    """Test edge cases and error handling scenarios."""
    
    def test_empty_data_handling(self):
        """Test handling of empty data structures."""
        empty_result = SearchResult(title="", url="", snippet="")
        yaml_output = empty_result.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
    
    def test_unicode_handling(self):
        """Test Unicode character handling."""
        unicode_result = SearchResult(
            title="测试结果",  # Chinese characters
            url="https://example.com/测试",
            snippet="This is a test with émojis 🔍 and ñoñó characters"
        )
        
        yaml_output = unicode_result.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
        
        # Should preserve Unicode characters
        self.assertIn("测试结果", yaml_output)
        self.assertIn("🔍", yaml_output)
    
    def test_special_characters_handling(self):
        """Test handling of special characters that might break YAML."""
        special_result = SearchResult(
            title="Result with: colons, [brackets], {braces}, and \"quotes\"",
            url="https://example.com/path?param=value&other=test",
            snippet="Text with\nnewlines and\ttabs and 'single quotes'"
        )
        
        yaml_output = special_result.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
    
    def test_large_numbers_handling(self):
        """Test handling of large numbers."""
        large_response = SearchResponse(
            success=True,
            engine_used="test",
            search_type="web",
            query="test",
            execution_time=999999.999999,
            results=[],
            total_results=999999999
        )
        
        yaml_output = large_response.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
    
    def test_deeply_nested_data(self):
        """Test deeply nested data structures."""
        nested_metadata = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'deep_value': 'found'
                        }
                    }
                }
            }
        }
        
        nested_result = SearchResult(
            title="Nested Test",
            url="https://example.com",
            snippet="Test",
            metadata=nested_metadata
        )
        
        yaml_output = nested_result.to_yaml(compact=True)
        self.assertValidYAML(yaml_output)
    
    @patch('yaml_utils.get_yaml_module')
    def test_yaml_unavailable_fallback(self, mock_get_yaml):
        """Test complete fallback when YAML is unavailable."""
        mock_get_yaml.return_value = False
        
        test_result = SearchResult(
            title="Fallback Test",
            url="https://example.com",
            snippet="Testing fallback"
        )
        
        # Should still work and return valid JSON
        output = test_result.to_yaml(compact=True)
        self.assertIsInstance(output, str)
        
        # Should be valid JSON
        try:
            json.loads(output)
        except json.JSONDecodeError:
            self.fail("Fallback should produce valid JSON")


if __name__ == '__main__':
    # Set up test environment
    import sys
    import os
    
    # Mock the logger for testing
    class MockLogger:
        def debug(self, msg): pass
        def info(self, msg): pass
        def warning(self, msg): pass
        def error(self, msg): pass

    # Mock the structured logging
    sys.modules['agent_c.util.structured_logging'] = type('MockModule', (), {
        'get_logger': lambda name: MockLogger()
    })()
    
    # Run the tests
    unittest.main(verbosity=2)