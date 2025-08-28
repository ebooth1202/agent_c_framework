#!/usr/bin/env python3
"""
Integration Testing and Performance Validation for YAML Optimization

This script performs comprehensive integration testing of YAML serialization
with real web search tools usage scenarios. It validates token savings,
performance improvements, and ensures production readiness.

Usage:
    python integration_test_yaml.py
    python integration_test_yaml.py --performance-only
    python integration_test_yaml.py --detailed-report
"""

import asyncio
import json
import time
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import argparse
import sys
import os

# Add the web_search directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base.models import (
    SearchResult, SearchResponse, SearchParameters, WebSearchConfig,
    EngineCapabilities, EngineHealthStatus, SearchType, SafeSearchLevel, SearchDepth
)
from base.yaml_utils import get_yaml_info


@dataclass
class TestResult:
    """Test result structure for tracking performance and validation."""
    test_name: str
    success: bool
    json_tokens: int
    yaml_tokens: int
    token_reduction: float
    json_size_bytes: int
    yaml_size_bytes: int
    serialization_time_json: float
    serialization_time_yaml: float
    error_message: str = ""
    
    @property
    def size_reduction(self) -> float:
        """Calculate size reduction percentage."""
        return (self.json_size_bytes - self.yaml_size_bytes) / self.json_size_bytes * 100
    
    @property
    def meets_target(self) -> bool:
        """Check if token reduction meets 25% minimum target."""
        return self.token_reduction >= 25.0


class YAMLIntegrationTester:
    """Comprehensive integration tester for YAML optimization."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.yaml_info = get_yaml_info()
        self.start_time = datetime.now()
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (approximate word-based counting)."""
        return len(text.split())
    
    def measure_serialization_performance(self, obj, test_name: str) -> TestResult:
        """Measure serialization performance for an object."""
        try:
            # JSON serialization
            start_time = time.time()
            json_output = json.dumps(obj.to_dict())
            json_time = time.time() - start_time
            
            json_tokens = self.count_tokens(json_output)
            json_size = len(json_output.encode('utf-8'))
            
            # YAML serialization
            start_time = time.time()
            yaml_output = obj.to_yaml(compact=True)
            yaml_time = time.time() - start_time
            
            yaml_tokens = self.count_tokens(yaml_output)
            yaml_size = len(yaml_output.encode('utf-8'))
            
            # Calculate reduction
            token_reduction = (json_tokens - yaml_tokens) / json_tokens * 100
            
            # Validate YAML is parseable
            parsed = yaml.safe_load(yaml_output)
            if not isinstance(parsed, dict):
                raise ValueError("YAML output is not a valid dictionary")
            
            return TestResult(
                test_name=test_name,
                success=True,
                json_tokens=json_tokens,
                yaml_tokens=yaml_tokens,
                token_reduction=token_reduction,
                json_size_bytes=json_size,
                yaml_size_bytes=yaml_size,
                serialization_time_json=json_time,
                serialization_time_yaml=yaml_time
            )
            
        except Exception as e:
            return TestResult(
                test_name=test_name,
                success=False,
                json_tokens=0,
                yaml_tokens=0,
                token_reduction=0.0,
                json_size_bytes=0,
                yaml_size_bytes=0,
                serialization_time_json=0.0,
                serialization_time_yaml=0.0,
                error_message=str(e)
            )
    
    def test_search_result_scenarios(self):
        """Test SearchResult in various real-world scenarios."""
        self.log("Testing SearchResult scenarios...")
        
        # Scenario 1: Basic web search result
        basic_result = SearchResult(
            title="Introduction to Machine Learning - Stanford CS229",
            url="https://cs229.stanford.edu/",
            snippet="Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention."
        )
        result1 = self.measure_serialization_performance(basic_result, "SearchResult_Basic")
        self.results.append(result1)
        
        # Scenario 2: Complete research result with metadata
        research_result = SearchResult(
            title="Attention Is All You Need - Transformer Architecture Paper",
            url="https://arxiv.org/abs/1706.03762",
            snippet="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
            published_date=datetime(2017, 6, 12, 17, 57, 58),
            score=0.97,
            source="arxiv.org",
            metadata={
                'authors': ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar', 'Jakob Uszkoreit'],
                'citation_count': 89432,
                'venue': 'NIPS 2017',
                'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
                'abstract_length': 1342,
                'pdf_url': 'https://arxiv.org/pdf/1706.03762.pdf',
                'bibtex_key': 'vaswani2017attention'
            }
        )
        result2 = self.measure_serialization_performance(research_result, "SearchResult_Research_Complete")
        self.results.append(result2)
        
        # Scenario 3: News result with sparse data
        news_result = SearchResult(
            title="AI Breakthrough in Medical Diagnosis",
            url="https://news.example.com/ai-medical-breakthrough",
            snippet="Researchers announce significant advancement in AI-powered medical diagnosis systems.",
            published_date=datetime.now() - timedelta(hours=2),
            score=None,  # Will be filtered
            source="",   # Will be filtered
            metadata={}  # Will be filtered
        )
        result3 = self.measure_serialization_performance(news_result, "SearchResult_News_Sparse")
        self.results.append(result3)
        
        self.log(f"SearchResult tests completed: {len([r for r in [result1, result2, result3] if r.success])}/3 successful")
    
    def test_search_response_scenarios(self):
        """Test SearchResponse with various result set sizes."""
        self.log("Testing SearchResponse scenarios...")
        
        # Create sample results for different scenarios
        def create_sample_results(count: int) -> List[SearchResult]:
            results = []
            for i in range(count):
                result = SearchResult(
                    title=f"Search Result {i+1}: Advanced Topic in Computer Science",
                    url=f"https://example{i+1}.com/advanced-topic-{i+1}",
                    snippet=f"This is a comprehensive overview of advanced topic {i+1} in computer science, covering theoretical foundations, practical applications, and recent research developments in the field.",
                    published_date=datetime.now() - timedelta(days=i) if i % 3 == 0 else None,
                    score=0.95 - (i * 0.05) if i < 10 else 0.0,  # Some will be filtered
                    source=f"example{i+1}.com" if i % 4 == 0 else "",  # Some will be filtered
                    metadata={'index': i, 'category': 'computer_science'} if i % 5 == 0 else {}
                )
                results.append(result)
            return results
        
        # Scenario 1: Small response (5 results)
        small_response = SearchResponse(
            success=True,
            engine_used="google_serp",
            search_type="research",
            query="machine learning algorithms optimization",
            execution_time=1.25,
            results=create_sample_results(5),
            total_results=5,
            page=1,
            pages_available=1,
            metadata={'search_id': 'test_small_001', 'cache_hit': False}
        )
        result1 = self.measure_serialization_performance(small_response, "SearchResponse_Small_5_Results")
        self.results.append(result1)
        
        # Scenario 2: Medium response (15 results)
        medium_response = SearchResponse(
            success=True,
            engine_used="tavily",
            search_type="research",
            query="artificial intelligence ethics and bias in machine learning systems",
            execution_time=2.75,
            results=create_sample_results(15),
            total_results=15,
            page=1,
            pages_available=2,
            metadata={
                'search_id': 'test_medium_002',
                'cache_hit': False,
                'query_analysis': {
                    'complexity': 'high',
                    'domain': 'ai_ethics',
                    'intent': 'research'
                },
                'performance_metrics': {
                    'query_processing_time': 0.15,
                    'retrieval_time': 2.35,
                    'ranking_time': 0.25
                }
            }
        )
        result2 = self.measure_serialization_performance(medium_response, "SearchResponse_Medium_15_Results")
        self.results.append(result2)
        
        # Scenario 3: Large response (50 results)
        large_response = SearchResponse(
            success=True,
            engine_used="duckduckgo",
            search_type="web",
            query="comprehensive guide to distributed systems architecture patterns microservices",
            execution_time=4.50,
            results=create_sample_results(50),
            total_results=50,
            page=1,
            pages_available=5,
            metadata={
                'search_id': 'test_large_003',
                'cache_hit': False,
                'result_diversity': 0.85,
                'quality_score': 0.92,
                'engines_consulted': ['primary', 'fallback_1', 'fallback_2'],
                'geographic_distribution': {
                    'us': 25,
                    'eu': 15,
                    'asia': 10
                }
            }
        )
        result3 = self.measure_serialization_performance(large_response, "SearchResponse_Large_50_Results")
        self.results.append(result3)
        
        # Scenario 4: Error response
        error_response = SearchResponse(
            success=False,
            engine_used="newsapi",
            search_type="news",
            query="test error scenario",
            execution_time=0.05,
            results=[],
            total_results=0,
            error={
                'code': 'API_QUOTA_EXCEEDED',
                'message': 'Daily API quota exceeded',
                'retry_after': 3600,
                'documentation': 'https://newsapi.org/docs/errors'
            },
            metadata={'search_id': 'test_error_004', 'timestamp': datetime.now().isoformat()}
        )
        result4 = self.measure_serialization_performance(error_response, "SearchResponse_Error")
        self.results.append(result4)
        
        successful_tests = len([r for r in [result1, result2, result3, result4] if r.success])
        self.log(f"SearchResponse tests completed: {successful_tests}/4 successful")
    
    def test_search_parameters_scenarios(self):
        """Test SearchParameters in various API call scenarios."""
        self.log("Testing SearchParameters scenarios...")
        
        # Scenario 1: Basic web search parameters
        basic_params = SearchParameters(
            query="python web frameworks comparison",
            engine="auto",
            search_type=SearchType.WEB,
            max_results=10,
            safesearch=SafeSearchLevel.MODERATE
        )
        result1 = self.measure_serialization_performance(basic_params, "SearchParameters_Basic")
        self.results.append(result1)
        
        # Scenario 2: Complex research parameters
        research_params = SearchParameters(
            query="quantum computing algorithms for cryptography and security applications",
            engine="tavily",
            search_type=SearchType.RESEARCH,
            max_results=25,
            safesearch=SafeSearchLevel.OFF,
            language="en",
            region="global",
            include_images=True,
            include_domains=["arxiv.org", "nature.com", "science.org", "ieee.org", "acm.org"],
            exclude_domains=["wikipedia.org", "reddit.com", "quora.com"],
            search_depth=SearchDepth.ADVANCED,
            start_date=datetime(2020, 1, 1),
            end_date=datetime.now(),
            page=1,
            additional_params={
                'boost_recent': True,
                'min_citation_count': 10,
                'peer_reviewed_only': True,
                'include_preprints': False,
                'subject_areas': ['computer_science', 'physics', 'mathematics']
            }
        )
        result2 = self.measure_serialization_performance(research_params, "SearchParameters_Research_Complex")
        self.results.append(result2)
        
        # Scenario 3: News search with date filtering
        news_params = SearchParameters(
            query="artificial intelligence regulation policy 2024",
            engine="newsapi",
            search_type=SearchType.NEWS,
            max_results=50,
            safesearch=SafeSearchLevel.MODERATE,
            language="en",
            region="us",
            start_date=datetime(2024, 1, 1),
            end_date=datetime.now(),
            additional_params={
                'sort_by': 'publishedAt',
                'sources': 'bbc-news,cnn,reuters,associated-press',
                'exclude_sources': 'tabloid-news,gossip-sites'
            }
        )
        result3 = self.measure_serialization_performance(news_params, "SearchParameters_News_DateFiltered")
        self.results.append(result3)
        
        successful_tests = len([r for r in [result1, result2, result3] if r.success])
        self.log(f"SearchParameters tests completed: {successful_tests}/3 successful")
    
    def test_configuration_scenarios(self):
        """Test WebSearchConfig and EngineCapabilities scenarios."""
        self.log("Testing configuration scenarios...")
        
        # Scenario 1: Production engine configuration
        prod_capabilities = EngineCapabilities(
            search_types=[SearchType.WEB, SearchType.NEWS, SearchType.RESEARCH],
            supports_pagination=True,
            supports_date_filtering=True,
            supports_domain_filtering=True,
            supports_safe_search=True,
            supports_language_filtering=True,
            supports_region_filtering=True,
            supports_image_search=True,
            supports_content_extraction=True,
            max_results_per_request=100,
            rate_limit_per_minute=5000
        )
        
        prod_config = WebSearchConfig(
            engine_name="production_search_engine_v2",
            requires_api_key=True,
            api_key_name="PRODUCTION_SEARCH_API_KEY",
            base_url="https://api.production-search.com/v2/search",
            timeout=60,
            max_retries=5,
            retry_delay=2.0,
            capabilities=prod_capabilities,
            default_parameters={
                'safe_search': 'moderate',
                'language': 'en',
                'region': 'global',
                'include_metadata': True,
                'response_format': 'json'
            },
            health_check_url="https://api.production-search.com/v2/health",
            cache_ttl=600
        )
        
        result1 = self.measure_serialization_performance(prod_config, "WebSearchConfig_Production")
        self.results.append(result1)
        
        # Test capabilities separately
        result2 = self.measure_serialization_performance(prod_capabilities, "EngineCapabilities_Production")
        self.results.append(result2)
        
        # Scenario 2: Development configuration with minimal capabilities
        dev_capabilities = EngineCapabilities(
            search_types=[SearchType.WEB],
            supports_pagination=False,
            supports_date_filtering=False,
            supports_domain_filtering=False,
            supports_safe_search=True,
            max_results_per_request=20,
            rate_limit_per_minute=100
        )
        
        dev_config = WebSearchConfig(
            engine_name="dev_test_engine",
            requires_api_key=False,
            capabilities=dev_capabilities,
            timeout=30,
            max_retries=2
        )
        
        result3 = self.measure_serialization_performance(dev_config, "WebSearchConfig_Development")
        self.results.append(result3)
        
        result4 = self.measure_serialization_performance(dev_capabilities, "EngineCapabilities_Development")
        self.results.append(result4)
        
        successful_tests = len([r for r in [result1, result2, result3, result4] if r.success])
        self.log(f"Configuration tests completed: {successful_tests}/4 successful")
    
    def test_monitoring_scenarios(self):
        """Test EngineHealthStatus for monitoring systems."""
        self.log("Testing monitoring scenarios...")
        
        # Scenario 1: Healthy engine status
        healthy_status = EngineHealthStatus(
            engine_name="production_search_engine_v2",
            is_available=True,
            last_check=datetime.now(),
            response_time=0.25,
            error_message=None,
            api_key_configured=True,
            capabilities=EngineCapabilities(
                search_types=[SearchType.WEB, SearchType.NEWS, SearchType.RESEARCH],
                supports_pagination=True,
                supports_date_filtering=True,
                max_results_per_request=100,
                rate_limit_per_minute=5000
            )
        )
        result1 = self.measure_serialization_performance(healthy_status, "EngineHealthStatus_Healthy")
        self.results.append(result1)
        
        # Scenario 2: Degraded engine status
        degraded_status = EngineHealthStatus(
            engine_name="backup_search_engine",
            is_available=True,
            last_check=datetime.now() - timedelta(minutes=2),
            response_time=2.75,
            error_message="High response time detected, investigating",
            api_key_configured=True,
            capabilities=EngineCapabilities(
                search_types=[SearchType.WEB],
                supports_pagination=False,
                max_results_per_request=50,
                rate_limit_per_minute=1000
            )
        )
        result2 = self.measure_serialization_performance(degraded_status, "EngineHealthStatus_Degraded")
        self.results.append(result2)
        
        # Scenario 3: Failed engine status
        failed_status = EngineHealthStatus(
            engine_name="external_api_engine",
            is_available=False,
            last_check=datetime.now() - timedelta(minutes=15),
            response_time=None,
            error_message="API quota exceeded. Service will resume at 00:00 UTC.",
            api_key_configured=True,
            capabilities=None
        )
        result3 = self.measure_serialization_performance(failed_status, "EngineHealthStatus_Failed")
        self.results.append(result3)
        
        successful_tests = len([r for r in [result1, result2, result3] if r.success])
        self.log(f"Monitoring tests completed: {successful_tests}/3 successful")
    
    def test_security_features(self):
        """Test sensitive data filtering in WebSearchConfig."""
        self.log("Testing security features...")
        
        # Configuration with sensitive data
        sensitive_config = WebSearchConfig(
            engine_name="secure_production_engine",
            requires_api_key=True,
            api_key_name="SUPER_SECRET_API_KEY_DO_NOT_EXPOSE",
            base_url="https://secure-api.internal.company.com/search",
            timeout=45,
            default_parameters={
                'api_secret': 'another_secret_value',
                'password': 'admin_password_123',
                'token': 'bearer_token_xyz789',
                'private_key': 'rsa_private_key_content',
                'client_secret': 'oauth_client_secret'
            }
        )
        
        try:
            # Test secure mode (should filter sensitive data)
            secure_yaml = sensitive_config.to_yaml(compact=True, include_sensitive=False)
            secure_parsed = yaml.safe_load(secure_yaml)
            
            # Verify sensitive fields are filtered
            sensitive_fields_found = []
            for field in ['api_key_name', 'api_secret', 'password', 'token', 'private_key', 'client_secret']:
                if field in str(secure_parsed).lower():
                    sensitive_fields_found.append(field)
            
            if sensitive_fields_found:
                result1 = TestResult(
                    test_name="Security_SensitiveDataFiltering",
                    success=False,
                    json_tokens=0,
                    yaml_tokens=0,
                    token_reduction=0.0,
                    json_size_bytes=0,
                    yaml_size_bytes=0,
                    serialization_time_json=0.0,
                    serialization_time_yaml=0.0,
                    error_message=f"Sensitive fields not filtered: {sensitive_fields_found}"
                )
            else:
                # Measure performance of secure serialization
                result1 = self.measure_serialization_performance(sensitive_config, "Security_SensitiveDataFiltering")
                result1.test_name = "Security_SensitiveDataFiltering_Success"
            
            self.results.append(result1)
            
            # Test development mode (should include sensitive data)
            dev_yaml = sensitive_config.to_yaml(compact=True, include_sensitive=True)
            dev_parsed = yaml.safe_load(dev_yaml)
            
            # This should include the data (for development use)
            result2 = self.measure_serialization_performance(sensitive_config, "Security_DevelopmentMode")
            self.results.append(result2)
            
            successful_tests = 2 if result1.success and result2.success else (1 if result1.success or result2.success else 0)
            self.log(f"Security tests completed: {successful_tests}/2 successful")
            
        except Exception as e:
            error_result = TestResult(
                test_name="Security_Features_Error",
                success=False,
                json_tokens=0,
                yaml_tokens=0,
                token_reduction=0.0,
                json_size_bytes=0,
                yaml_size_bytes=0,
                serialization_time_json=0.0,
                serialization_time_yaml=0.0,
                error_message=str(e)
            )
            self.results.append(error_result)
            self.log(f"Security tests failed: {e}", "ERROR")
    
    def test_performance_benchmarks(self):
        """Run comprehensive performance benchmarks."""
        self.log("Running performance benchmarks...")
        
        # Benchmark 1: High-volume API scenario simulation
        self.log("Benchmark 1: High-volume API scenario")
        
        # Simulate 100 API responses
        api_responses = []
        for i in range(100):
            results = [
                SearchResult(
                    title=f"API Result {j+1} for Query {i+1}",
                    url=f"https://api-result-{i}-{j}.com",
                    snippet=f"This is API result {j+1} for query {i+1} in our high-volume benchmark test.",
                    published_date=datetime.now() - timedelta(hours=j) if j % 3 == 0 else None,
                    score=0.9 - (j * 0.05) if j < 10 else None
                )
                for j in range(10)  # 10 results per response
            ]
            
            response = SearchResponse(
                success=True,
                engine_used="benchmark_engine",
                search_type="web",
                query=f"benchmark query {i+1}",
                execution_time=1.0 + (i * 0.01),
                results=results,
                total_results=10,
                metadata={'benchmark_id': i, 'batch': 'high_volume_test'}
            )
            api_responses.append(response)
        
        # Measure batch serialization performance
        start_time = time.time()
        json_outputs = [json.dumps(response.to_dict()) for response in api_responses]
        json_batch_time = time.time() - start_time
        
        start_time = time.time()
        yaml_outputs = [response.to_yaml(compact=True) for response in api_responses]
        yaml_batch_time = time.time() - start_time
        
        # Calculate totals
        total_json_tokens = sum(self.count_tokens(output) for output in json_outputs)
        total_yaml_tokens = sum(self.count_tokens(output) for output in yaml_outputs)
        total_json_size = sum(len(output.encode('utf-8')) for output in json_outputs)
        total_yaml_size = sum(len(output.encode('utf-8')) for output in yaml_outputs)
        
        batch_result = TestResult(
            test_name="Performance_HighVolume_100_API_Responses",
            success=True,
            json_tokens=total_json_tokens,
            yaml_tokens=total_yaml_tokens,
            token_reduction=(total_json_tokens - total_yaml_tokens) / total_json_tokens * 100,
            json_size_bytes=total_json_size,
            yaml_size_bytes=total_yaml_size,
            serialization_time_json=json_batch_time,
            serialization_time_yaml=yaml_batch_time
        )
        self.results.append(batch_result)
        
        self.log(f"High-volume benchmark: {batch_result.token_reduction:.1f}% token reduction")
        self.log(f"Batch serialization - JSON: {json_batch_time:.3f}s, YAML: {yaml_batch_time:.3f}s")
        
        # Benchmark 2: Configuration management scenario
        self.log("Benchmark 2: Configuration management")
        
        configs = []
        for i in range(20):  # 20 different engine configurations
            capabilities = EngineCapabilities(
                search_types=[SearchType.WEB, SearchType.NEWS] if i % 2 == 0 else [SearchType.WEB],
                supports_pagination=i % 3 == 0,
                supports_date_filtering=i % 4 == 0,
                supports_domain_filtering=i % 5 == 0,
                max_results_per_request=50 + (i * 10),
                rate_limit_per_minute=1000 + (i * 100)
            )
            
            config = WebSearchConfig(
                engine_name=f"config_engine_{i+1}",
                requires_api_key=i % 2 == 0,
                api_key_name=f"API_KEY_{i+1}" if i % 2 == 0 else None,
                base_url=f"https://api{i+1}.example.com",
                timeout=30 + i,
                capabilities=capabilities
            )
            configs.append(config)
        
        # Measure configuration serialization
        start_time = time.time()
        config_json_outputs = [json.dumps(config.to_dict()) for config in configs]
        config_json_time = time.time() - start_time
        
        start_time = time.time()
        config_yaml_outputs = [config.to_yaml(compact=True, include_sensitive=False) for config in configs]
        config_yaml_time = time.time() - start_time
        
        config_json_tokens = sum(self.count_tokens(output) for output in config_json_outputs)
        config_yaml_tokens = sum(self.count_tokens(output) for output in config_yaml_outputs)
        
        config_result = TestResult(
            test_name="Performance_Configuration_Management_20_Configs",
            success=True,
            json_tokens=config_json_tokens,
            yaml_tokens=config_yaml_tokens,
            token_reduction=(config_json_tokens - config_yaml_tokens) / config_json_tokens * 100,
            json_size_bytes=sum(len(output.encode('utf-8')) for output in config_json_outputs),
            yaml_size_bytes=sum(len(output.encode('utf-8')) for output in config_yaml_outputs),
            serialization_time_json=config_json_time,
            serialization_time_yaml=config_yaml_time
        )
        self.results.append(config_result)
        
        self.log(f"Configuration benchmark: {config_result.token_reduction:.1f}% token reduction")
        
        # Benchmark 3: Monitoring system scenario
        self.log("Benchmark 3: Monitoring system")
        
        health_statuses = []
        for i in range(50):  # 50 engine health checks
            status = EngineHealthStatus(
                engine_name=f"monitored_engine_{i+1}",
                is_available=i % 10 != 0,  # 90% availability
                last_check=datetime.now() - timedelta(minutes=i),
                response_time=0.1 + (i * 0.05) if i % 10 != 0 else None,
                error_message=f"Engine {i+1} temporarily unavailable" if i % 10 == 0 else None,
                api_key_configured=True,
                capabilities=EngineCapabilities(
                    search_types=[SearchType.WEB],
                    max_results_per_request=50,
                    rate_limit_per_minute=1000
                ) if i % 10 != 0 else None
            )
            health_statuses.append(status)
        
        # Measure monitoring data serialization
        start_time = time.time()
        health_json_outputs = [json.dumps(status.to_dict()) for status in health_statuses]
        health_json_time = time.time() - start_time
        
        start_time = time.time()
        health_yaml_outputs = [status.to_yaml(compact=True) for status in health_statuses]
        health_yaml_time = time.time() - start_time
        
        health_json_tokens = sum(self.count_tokens(output) for output in health_json_outputs)
        health_yaml_tokens = sum(self.count_tokens(output) for output in health_yaml_outputs)
        
        health_result = TestResult(
            test_name="Performance_Monitoring_System_50_Health_Checks",
            success=True,
            json_tokens=health_json_tokens,
            yaml_tokens=health_yaml_tokens,
            token_reduction=(health_json_tokens - health_yaml_tokens) / health_json_tokens * 100,
            json_size_bytes=sum(len(output.encode('utf-8')) for output in health_json_outputs),
            yaml_size_bytes=sum(len(output.encode('utf-8')) for output in health_yaml_outputs),
            serialization_time_json=health_json_time,
            serialization_time_yaml=health_yaml_time
        )
        self.results.append(health_result)
        
        self.log(f"Monitoring benchmark: {health_result.token_reduction:.1f}% token reduction")
        self.log("Performance benchmarks completed")
    
    def run_all_tests(self, performance_only: bool = False):
        """Run all integration tests."""
        self.log("Starting YAML optimization integration tests...")
        self.log(f"YAML library status: {self.yaml_info}")
        
        if not performance_only:
            # Core functionality tests
            self.test_search_result_scenarios()
            self.test_search_response_scenarios()
            self.test_search_parameters_scenarios()
            self.test_configuration_scenarios()
            self.test_monitoring_scenarios()
            self.test_security_features()
        
        # Performance benchmarks
        self.test_performance_benchmarks()
        
        self.log("All tests completed")
    
    def generate_report(self, detailed: bool = False) -> str:
        """Generate comprehensive test report."""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        failed_tests = total_tests - successful_tests
        
        # Calculate overall statistics
        successful_results = [r for r in self.results if r.success]
        if successful_results:
            avg_token_reduction = sum(r.token_reduction for r in successful_results) / len(successful_results)
            avg_size_reduction = sum(r.size_reduction for r in successful_results) / len(successful_results)
            total_json_tokens = sum(r.json_tokens for r in successful_results)
            total_yaml_tokens = sum(r.yaml_tokens for r in successful_results)
            total_tokens_saved = total_json_tokens - total_yaml_tokens
            
            meets_target_count = len([r for r in successful_results if r.meets_target])
            target_success_rate = meets_target_count / len(successful_results) * 100
        else:
            avg_token_reduction = 0
            avg_size_reduction = 0
            total_tokens_saved = 0
            target_success_rate = 0
        
        # Generate report
        report_lines = [
            "=" * 80,
            "YAML OPTIMIZATION INTEGRATION TEST REPORT",
            "=" * 80,
            f"Test Execution Time: {datetime.now() - self.start_time}",
            f"YAML Library: {self.yaml_info['version'] if self.yaml_info['available'] else 'Not Available'}",
            "",
            "SUMMARY:",
            f"  Total Tests: {total_tests}",
            f"  Successful: {successful_tests}",
            f"  Failed: {failed_tests}",
            f"  Success Rate: {successful_tests/total_tests*100:.1f}%",
            "",
            "PERFORMANCE RESULTS:",
            f"  Average Token Reduction: {avg_token_reduction:.1f}%",
            f"  Average Size Reduction: {avg_size_reduction:.1f}%",
            f"  Total Tokens Saved: {total_tokens_saved:,}",
            f"  Target Achievement Rate: {target_success_rate:.1f}% (≥25% reduction)",
            "",
        ]
        
        # Add detailed results if requested
        if detailed:
            report_lines.extend([
                "DETAILED TEST RESULTS:",
                "-" * 80,
            ])
            
            for result in self.results:
                if result.success:
                    report_lines.extend([
                        f"✅ {result.test_name}",
                        f"   Token Reduction: {result.token_reduction:.1f}% ({result.json_tokens:,} → {result.yaml_tokens:,})",
                        f"   Size Reduction: {result.size_reduction:.1f}% ({result.json_size_bytes:,} → {result.yaml_size_bytes:,} bytes)",
                        f"   Serialization Time: JSON {result.serialization_time_json:.4f}s, YAML {result.serialization_time_yaml:.4f}s",
                        f"   Meets Target: {'Yes' if result.meets_target else 'No'}",
                        ""
                    ])
                else:
                    report_lines.extend([
                        f"❌ {result.test_name}",
                        f"   Error: {result.error_message}",
                        ""
                    ])
        
        # Add business impact analysis
        report_lines.extend([
            "BUSINESS IMPACT ANALYSIS:",
            "-" * 80,
        ])
        
        if successful_results:
            # Calculate business scenarios
            api_response_results = [r for r in successful_results if 'SearchResponse' in r.test_name]
            if api_response_results:
                avg_api_reduction = sum(r.token_reduction for r in api_response_results) / len(api_response_results)
                avg_tokens_per_response = sum(r.json_tokens for r in api_response_results) / len(api_response_results)
                tokens_saved_per_response = avg_tokens_per_response * (avg_api_reduction / 100)
                
                report_lines.extend([
                    f"API Response Optimization:",
                    f"  Average reduction per response: {avg_api_reduction:.1f}%",
                    f"  Tokens saved per response: {tokens_saved_per_response:.0f}",
                    f"  Monthly savings (10K calls): {tokens_saved_per_response * 10000:,.0f} tokens",
                    f"  Annual savings (120K calls): {tokens_saved_per_response * 120000:,.0f} tokens",
                    ""
                ])
            
            config_results = [r for r in successful_results if 'Config' in r.test_name]
            if config_results:
                avg_config_reduction = sum(r.token_reduction for r in config_results) / len(config_results)
                report_lines.extend([
                    f"Configuration Management:",
                    f"  Average reduction per config: {avg_config_reduction:.1f}%",
                    f"  Ideal for: Multi-environment deployments, microservices configuration",
                    ""
                ])
            
            monitoring_results = [r for r in successful_results if 'Health' in r.test_name or 'Monitoring' in r.test_name]
            if monitoring_results:
                avg_monitoring_reduction = sum(r.token_reduction for r in monitoring_results) / len(monitoring_results)
                report_lines.extend([
                    f"Monitoring Systems:",
                    f"  Average reduction per health check: {avg_monitoring_reduction:.1f}%",
                    f"  High-frequency monitoring: Significant cost savings at scale",
                    ""
                ])
        
        # Add recommendations
        report_lines.extend([
            "RECOMMENDATIONS:",
            "-" * 80,
        ])
        
        if target_success_rate >= 90:
            report_lines.append("✅ READY FOR PRODUCTION DEPLOYMENT")
            report_lines.append("   All models meet or exceed token reduction targets")
        elif target_success_rate >= 75:
            report_lines.append("⚠️  MOSTLY READY - MINOR OPTIMIZATIONS NEEDED")
            report_lines.append("   Most models meet targets, review failed tests")
        else:
            report_lines.append("❌ NEEDS OPTIMIZATION")
            report_lines.append("   Several models below target, requires investigation")
        
        report_lines.extend([
            "",
            "Next Steps:",
            "1. Review any failed tests and address issues",
            "2. Consider implementing caching for frequently serialized objects",
            "3. Monitor production performance after deployment",
            "4. Set up alerts for serialization performance degradation",
            "",
            "=" * 80
        ])
        
        return "\n".join(report_lines)
    
    def save_report(self, filename: str, detailed: bool = False):
        """Save test report to file."""
        report = self.generate_report(detailed)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        self.log(f"Report saved to {filename}")


def main():
    """Main function to run integration tests."""
    parser = argparse.ArgumentParser(description="YAML Optimization Integration Tests")
    parser.add_argument("--performance-only", action="store_true", 
                       help="Run only performance benchmarks")
    parser.add_argument("--detailed-report", action="store_true",
                       help="Generate detailed test report")
    parser.add_argument("--output", type=str, default="yaml_integration_test_report.txt",
                       help="Output file for test report")
    
    args = parser.parse_args()
    
    # Create tester and run tests
    tester = YAMLIntegrationTester()
    
    try:
        tester.run_all_tests(performance_only=args.performance_only)
        
        # Generate and display report
        report = tester.generate_report(detailed=args.detailed_report)
        print("\n" + report)
        
        # Save report to file
        tester.save_report(args.output, detailed=args.detailed_report)
        
        # Exit with appropriate code
        successful_tests = len([r for r in tester.results if r.success])
        total_tests = len(tester.results)
        
        if successful_tests == total_tests:
            print(f"\n🎉 All {total_tests} tests passed successfully!")
            sys.exit(0)
        else:
            failed_tests = total_tests - successful_tests
            print(f"\n⚠️  {failed_tests} out of {total_tests} tests failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Integration test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()