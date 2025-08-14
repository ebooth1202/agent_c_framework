#!/usr/bin/env python3
"""
Performance Validation Script for YAML Optimization

This script validates that YAML optimization meets all performance targets
and business requirements. It performs comprehensive performance analysis
and generates detailed reports for production readiness assessment.

Usage:
    python performance_validation_yaml.py
    python performance_validation_yaml.py --target-reduction 30
    python performance_validation_yaml.py --business-analysis
"""

import json
import time
import yaml
import statistics
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
class PerformanceMetrics:
    """Performance metrics for a single test."""
    model_name: str
    test_scenario: str
    json_tokens: int
    yaml_tokens: int
    json_size_bytes: int
    yaml_size_bytes: int
    json_serialization_time: float
    yaml_serialization_time: float
    token_reduction_percent: float
    size_reduction_percent: float
    meets_target: bool
    iterations: int = 1


class YAMLPerformanceValidator:
    """Comprehensive performance validator for YAML optimization."""
    
    def __init__(self, target_reduction: float = 25.0):
        self.target_reduction = target_reduction
        self.metrics: List[PerformanceMetrics] = []
        self.yaml_info = get_yaml_info()
        self.start_time = datetime.now()
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (word-based approximation)."""
        return len(text.split())
    
    def measure_performance(self, obj, model_name: str, scenario: str, iterations: int = 100) -> PerformanceMetrics:
        """Measure performance with multiple iterations for accuracy."""
        json_times = []
        yaml_times = []
        
        # Warm up
        for _ in range(5):
            json.dumps(obj.to_dict())
            obj.to_yaml(compact=True)
        
        # Measure JSON serialization
        for _ in range(iterations):
            start_time = time.perf_counter()
            json_output = json.dumps(obj.to_dict())
            json_times.append(time.perf_counter() - start_time)
        
        # Measure YAML serialization
        for _ in range(iterations):
            start_time = time.perf_counter()
            yaml_output = obj.to_yaml(compact=True)
            yaml_times.append(time.perf_counter() - start_time)
        
        # Calculate metrics
        json_tokens = self.count_tokens(json_output)
        yaml_tokens = self.count_tokens(yaml_output)
        json_size = len(json_output.encode('utf-8'))
        yaml_size = len(yaml_output.encode('utf-8'))
        
        token_reduction = (json_tokens - yaml_tokens) / json_tokens * 100
        size_reduction = (json_size - yaml_size) / json_size * 100
        
        return PerformanceMetrics(
            model_name=model_name,
            test_scenario=scenario,
            json_tokens=json_tokens,
            yaml_tokens=yaml_tokens,
            json_size_bytes=json_size,
            yaml_size_bytes=yaml_size,
            json_serialization_time=statistics.mean(json_times),
            yaml_serialization_time=statistics.mean(yaml_times),
            token_reduction_percent=token_reduction,
            size_reduction_percent=size_reduction,
            meets_target=token_reduction >= self.target_reduction,
            iterations=iterations
        )
    
    def validate_search_result_performance(self):
        """Validate SearchResult performance across scenarios."""
        self.log("Validating SearchResult performance...")
        
        # Scenario 1: Minimal result
        minimal_result = SearchResult(
            title="Minimal Result",
            url="https://example.com",
            snippet="Short snippet"
        )
        metrics1 = self.measure_performance(minimal_result, "SearchResult", "Minimal")
        self.metrics.append(metrics1)
        
        # Scenario 2: Complete result with metadata
        complete_result = SearchResult(
            title="Complete Research Paper: Advanced Machine Learning Techniques for Natural Language Processing",
            url="https://arxiv.org/abs/2024.12345",
            snippet="This comprehensive research paper presents novel approaches to machine learning in natural language processing, including transformer architectures, attention mechanisms, and advanced optimization techniques for large-scale language models.",
            published_date=datetime(2024, 6, 15, 14, 30, 45, 123456),
            score=0.97,
            source="arxiv.org",
            metadata={
                'authors': ['Dr. Jane Smith', 'Prof. John Doe', 'Dr. Alice Johnson'],
                'institution': 'Stanford University',
                'citation_count': 1247,
                'keywords': ['machine learning', 'NLP', 'transformers', 'attention'],
                'abstract_length': 2847,
                'paper_type': 'research',
                'peer_reviewed': True,
                'open_access': True,
                'doi': '10.1000/journal.2024.12345',
                'bibtex': '@article{smith2024advanced,\n  title={Advanced ML Techniques},\n  author={Smith, Jane and Doe, John},\n  year={2024}\n}'
            }
        )
        metrics2 = self.measure_performance(complete_result, "SearchResult", "Complete_With_Metadata")
        self.metrics.append(metrics2)
        
        # Scenario 3: Sparse result (many None/empty fields)
        sparse_result = SearchResult(
            title="Sparse Result Title",
            url="https://sparse.example.com",
            snippet="Basic snippet without additional data",
            published_date=None,
            score=None,
            source="",
            metadata={}
        )
        metrics3 = self.measure_performance(sparse_result, "SearchResult", "Sparse_Fields")
        self.metrics.append(metrics3)
        
        self.log(f"SearchResult validation completed: {len([m for m in [metrics1, metrics2, metrics3] if m.meets_target])}/3 meet target")
    
    def validate_search_response_performance(self):
        """Validate SearchResponse performance with different result set sizes."""
        self.log("Validating SearchResponse performance...")
        
        def create_test_results(count: int) -> List[SearchResult]:
            return [
                SearchResult(
                    title=f"Performance Test Result {i+1}: Comprehensive Analysis of Topic {i+1}",
                    url=f"https://performance-test-{i+1}.example.com/comprehensive-analysis",
                    snippet=f"This is a detailed performance test result {i+1} that includes comprehensive analysis and extensive content to simulate real-world search result data with varying lengths and complexity.",
                    published_date=datetime.now() - timedelta(days=i) if i % 3 == 0 else None,
                    score=0.95 - (i * 0.02) if i < 20 else None,
                    source=f"performance-test-{i+1}.example.com" if i % 4 == 0 else "",
                    metadata={
                        'result_index': i,
                        'category': 'performance_test',
                        'complexity': 'high' if i % 5 == 0 else 'medium',
                        'content_length': 150 + (i * 10)
                    } if i % 6 == 0 else {}
                )
                for i in range(count)
            ]
        
        # Small response (5 results)
        small_response = SearchResponse(
            success=True,
            engine_used="performance_test_engine",
            search_type="research",
            query="performance validation test query small dataset",
            execution_time=0.85,
            results=create_test_results(5),
            total_results=5,
            page=1,
            metadata={'test_type': 'small_response', 'validation_run': True}
        )
        metrics1 = self.measure_performance(small_response, "SearchResponse", "Small_5_Results")
        self.metrics.append(metrics1)
        
        # Medium response (20 results)
        medium_response = SearchResponse(
            success=True,
            engine_used="performance_test_engine_v2",
            search_type="research",
            query="performance validation test query medium dataset with comprehensive analysis",
            execution_time=2.35,
            results=create_test_results(20),
            total_results=20,
            page=1,
            pages_available=2,
            metadata={
                'test_type': 'medium_response',
                'validation_run': True,
                'query_complexity': 'high',
                'result_diversity': 0.87,
                'processing_stats': {
                    'parsing_time': 0.15,
                    'ranking_time': 1.85,
                    'filtering_time': 0.35
                }
            }
        )
        metrics2 = self.measure_performance(medium_response, "SearchResponse", "Medium_20_Results")
        self.metrics.append(metrics2)
        
        # Large response (100 results)
        large_response = SearchResponse(
            success=True,
            engine_used="performance_test_enterprise_engine",
            search_type="web",
            query="comprehensive performance validation test query large dataset enterprise scale analysis",
            execution_time=5.75,
            results=create_test_results(100),
            total_results=100,
            page=1,
            pages_available=10,
            metadata={
                'test_type': 'large_response',
                'validation_run': True,
                'enterprise_features': True,
                'result_clustering': True,
                'duplicate_removal': True,
                'quality_scoring': 0.94,
                'geographic_distribution': {
                    'north_america': 45,
                    'europe': 30,
                    'asia_pacific': 20,
                    'other': 5
                },
                'content_analysis': {
                    'average_relevance': 0.89,
                    'topic_coverage': 0.92,
                    'freshness_score': 0.78
                }
            }
        )
        metrics3 = self.measure_performance(large_response, "SearchResponse", "Large_100_Results", iterations=10)  # Fewer iterations for large data
        self.metrics.append(metrics3)
        
        self.log(f"SearchResponse validation completed: {len([m for m in [metrics1, metrics2, metrics3] if m.meets_target])}/3 meet target")
    
    def validate_search_parameters_performance(self):
        """Validate SearchParameters performance in API scenarios."""
        self.log("Validating SearchParameters performance...")
        
        # Basic parameters
        basic_params = SearchParameters(
            query="basic performance test",
            engine="auto",
            search_type=SearchType.WEB
        )
        metrics1 = self.measure_performance(basic_params, "SearchParameters", "Basic_API_Call")
        self.metrics.append(metrics1)
        
        # Complex research parameters
        complex_params = SearchParameters(
            query="comprehensive performance validation test for complex research parameters with multiple filters and advanced options",
            engine="tavily_research",
            search_type=SearchType.RESEARCH,
            max_results=50,
            safesearch=SafeSearchLevel.MODERATE,
            language="en-US",
            region="north_america",
            include_images=True,
            include_domains=[
                "arxiv.org", "nature.com", "science.org", "ieee.org", "acm.org",
                "springer.com", "elsevier.com", "wiley.com", "taylor-francis.com"
            ],
            exclude_domains=[
                "wikipedia.org", "reddit.com", "quora.com", "yahoo.com",
                "ask.com", "answers.com", "stackexchange.com"
            ],
            search_depth=SearchDepth.ADVANCED,
            start_date=datetime(2020, 1, 1),
            end_date=datetime.now(),
            page=1,
            additional_params={
                'boost_recent': True,
                'min_citation_count': 5,
                'peer_reviewed_only': True,
                'include_preprints': False,
                'subject_areas': ['computer_science', 'artificial_intelligence', 'machine_learning'],
                'author_affiliation_filter': ['university', 'research_institute'],
                'language_detection': True,
                'content_type_filter': ['research_paper', 'technical_report', 'conference_paper'],
                'quality_threshold': 0.8,
                'relevance_boost_keywords': ['performance', 'optimization', 'efficiency', 'scalability']
            }
        )
        metrics2 = self.measure_performance(complex_params, "SearchParameters", "Complex_Research_API")
        self.metrics.append(metrics2)
        
        # High-frequency API parameters
        api_params = SearchParameters(
            query="high frequency API call performance test",
            engine="google_serp",
            search_type=SearchType.NEWS,
            max_results=25,
            safesearch=SafeSearchLevel.STRICT,
            language="en",
            region="us",
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now(),
            additional_params={
                'sort_by': 'publishedAt',
                'category': 'technology',
                'source_quality': 'high',
                'duplicate_filter': True
            }
        )
        metrics3 = self.measure_performance(api_params, "SearchParameters", "High_Frequency_API")
        self.metrics.append(metrics3)
        
        self.log(f"SearchParameters validation completed: {len([m for m in [metrics1, metrics2, metrics3] if m.meets_target])}/3 meet target")
    
    def validate_configuration_performance(self):
        """Validate configuration model performance."""
        self.log("Validating configuration performance...")
        
        # Enterprise engine capabilities
        enterprise_capabilities = EngineCapabilities(
            search_types=[SearchType.WEB, SearchType.NEWS, SearchType.RESEARCH, SearchType.EDUCATIONAL],
            supports_pagination=True,
            supports_date_filtering=True,
            supports_domain_filtering=True,
            supports_safe_search=True,
            supports_language_filtering=True,
            supports_region_filtering=True,
            supports_image_search=True,
            supports_content_extraction=True,
            max_results_per_request=200,
            rate_limit_per_minute=10000
        )
        metrics1 = self.measure_performance(enterprise_capabilities, "EngineCapabilities", "Enterprise_Full_Features")
        self.metrics.append(metrics1)
        
        # Production configuration
        production_config = WebSearchConfig(
            engine_name="production_enterprise_search_engine_v3",
            requires_api_key=True,
            api_key_name="PRODUCTION_ENTERPRISE_SEARCH_API_KEY",
            base_url="https://api.enterprise-search.production.company.com/v3/search",
            timeout=90,
            max_retries=5,
            retry_delay=2.5,
            capabilities=enterprise_capabilities,
            default_parameters={
                'safe_search': 'moderate',
                'language': 'en',
                'region': 'global',
                'include_metadata': True,
                'response_format': 'json',
                'quality_threshold': 0.7,
                'content_filtering': True,
                'duplicate_detection': True,
                'result_clustering': True,
                'performance_optimization': True
            },
            health_check_url="https://api.enterprise-search.production.company.com/v3/health",
            cache_ttl=900
        )
        metrics2 = self.measure_performance(production_config, "WebSearchConfig", "Production_Enterprise")
        self.metrics.append(metrics2)
        
        # Health monitoring
        production_health = EngineHealthStatus(
            engine_name="production_enterprise_search_engine_v3",
            is_available=True,
            last_check=datetime.now(),
            response_time=0.45,
            error_message=None,
            api_key_configured=True,
            capabilities=enterprise_capabilities
        )
        metrics3 = self.measure_performance(production_health, "EngineHealthStatus", "Production_Monitoring")
        self.metrics.append(metrics3)
        
        self.log(f"Configuration validation completed: {len([m for m in [metrics1, metrics2, metrics3] if m.meets_target])}/3 meet target")
    
    def validate_scalability_performance(self):
        """Validate performance at scale."""
        self.log("Validating scalability performance...")
        
        # Batch API responses simulation
        batch_responses = []
        for i in range(50):  # 50 API responses
            results = [
                SearchResult(
                    title=f"Batch Result {j+1} for API Call {i+1}",
                    url=f"https://batch-api-{i}-{j}.com",
                    snippet=f"Scalability test result {j+1} for API call {i+1} in batch processing scenario.",
                    published_date=datetime.now() - timedelta(hours=j) if j % 4 == 0 else None,
                    score=0.9 - (j * 0.03) if j < 15 else None
                )
                for j in range(15)  # 15 results per response
            ]
            
            response = SearchResponse(
                success=True,
                engine_used="scalability_test_engine",
                search_type="web",
                query=f"scalability test query {i+1}",
                execution_time=1.2 + (i * 0.01),
                results=results,
                total_results=15,
                metadata={'batch_id': i, 'scalability_test': True}
            )
            batch_responses.append(response)
        
        # Measure batch serialization performance
        start_time = time.perf_counter()
        json_outputs = [json.dumps(response.to_dict()) for response in batch_responses]
        json_batch_time = time.perf_counter() - start_time
        
        start_time = time.perf_counter()
        yaml_outputs = [response.to_yaml(compact=True) for response in batch_responses]
        yaml_batch_time = time.perf_counter() - start_time
        
        # Calculate batch metrics
        total_json_tokens = sum(self.count_tokens(output) for output in json_outputs)
        total_yaml_tokens = sum(self.count_tokens(output) for output in yaml_outputs)
        total_json_size = sum(len(output.encode('utf-8')) for output in json_outputs)
        total_yaml_size = sum(len(output.encode('utf-8')) for output in yaml_outputs)
        
        batch_metrics = PerformanceMetrics(
            model_name="SearchResponse",
            test_scenario="Scalability_Batch_50_API_Responses",
            json_tokens=total_json_tokens,
            yaml_tokens=total_yaml_tokens,
            json_size_bytes=total_json_size,
            yaml_size_bytes=total_yaml_size,
            json_serialization_time=json_batch_time,
            yaml_serialization_time=yaml_batch_time,
            token_reduction_percent=(total_json_tokens - total_yaml_tokens) / total_json_tokens * 100,
            size_reduction_percent=(total_json_size - total_yaml_size) / total_json_size * 100,
            meets_target=(total_json_tokens - total_yaml_tokens) / total_json_tokens * 100 >= self.target_reduction,
            iterations=1
        )
        self.metrics.append(batch_metrics)
        
        self.log(f"Scalability validation completed: {batch_metrics.token_reduction_percent:.1f}% reduction")
    
    def run_validation(self):
        """Run all performance validation tests."""
        self.log("Starting YAML optimization performance validation...")
        self.log(f"Target token reduction: {self.target_reduction}%")
        self.log(f"YAML library: {self.yaml_info['version'] if self.yaml_info['available'] else 'Not Available'}")
        
        # Run all validation tests
        self.validate_search_result_performance()
        self.validate_search_response_performance()
        self.validate_search_parameters_performance()
        self.validate_configuration_performance()
        self.validate_scalability_performance()
        
        self.log("Performance validation completed")
    
    def analyze_business_impact(self) -> Dict[str, Any]:
        """Analyze business impact of YAML optimization."""
        successful_metrics = [m for m in self.metrics if m.meets_target]
        
        if not successful_metrics:
            return {'error': 'No successful metrics to analyze'}
        
        # API Response Analysis
        api_metrics = [m for m in successful_metrics if 'SearchResponse' in m.model_name]
        if api_metrics:
            avg_api_reduction = statistics.mean([m.token_reduction_percent for m in api_metrics])
            avg_tokens_per_response = statistics.mean([m.json_tokens for m in api_metrics])
            tokens_saved_per_response = avg_tokens_per_response * (avg_api_reduction / 100)
            
            # Business scenarios
            api_analysis = {
                'average_reduction_percent': avg_api_reduction,
                'tokens_saved_per_response': tokens_saved_per_response,
                'business_scenarios': {
                    'small_business': {
                        'monthly_calls': 1000,
                        'monthly_tokens_saved': tokens_saved_per_response * 1000,
                        'annual_tokens_saved': tokens_saved_per_response * 12000
                    },
                    'medium_business': {
                        'monthly_calls': 10000,
                        'monthly_tokens_saved': tokens_saved_per_response * 10000,
                        'annual_tokens_saved': tokens_saved_per_response * 120000
                    },
                    'enterprise': {
                        'monthly_calls': 100000,
                        'monthly_tokens_saved': tokens_saved_per_response * 100000,
                        'annual_tokens_saved': tokens_saved_per_response * 1200000
                    }
                }
            }
        else:
            api_analysis = {'error': 'No API response metrics available'}
        
        # Configuration Analysis
        config_metrics = [m for m in successful_metrics if 'Config' in m.model_name or 'Capabilities' in m.model_name]
        if config_metrics:
            avg_config_reduction = statistics.mean([m.token_reduction_percent for m in config_metrics])
            config_analysis = {
                'average_reduction_percent': avg_config_reduction,
                'use_cases': [
                    'Multi-environment configuration deployment',
                    'Microservices configuration management',
                    'CI/CD pipeline configuration',
                    'Infrastructure as Code templates'
                ]
            }
        else:
            config_analysis = {'error': 'No configuration metrics available'}
        
        # Monitoring Analysis
        monitoring_metrics = [m for m in successful_metrics if 'Health' in m.model_name]
        if monitoring_metrics:
            avg_monitoring_reduction = statistics.mean([m.token_reduction_percent for m in monitoring_metrics])
            avg_tokens_per_check = statistics.mean([m.json_tokens for m in monitoring_metrics])
            tokens_saved_per_check = avg_tokens_per_check * (avg_monitoring_reduction / 100)
            
            monitoring_analysis = {
                'average_reduction_percent': avg_monitoring_reduction,
                'tokens_saved_per_check': tokens_saved_per_check,
                'monitoring_scenarios': {
                    'small_deployment': {
                        'engines': 5,
                        'checks_per_day': 7200,  # Every minute
                        'daily_tokens_saved': tokens_saved_per_check * 7200,
                        'monthly_tokens_saved': tokens_saved_per_check * 216000
                    },
                    'enterprise_deployment': {
                        'engines': 100,
                        'checks_per_day': 144000,  # Every minute per engine
                        'daily_tokens_saved': tokens_saved_per_check * 144000,
                        'monthly_tokens_saved': tokens_saved_per_check * 4320000
                    }
                }
            }
        else:
            monitoring_analysis = {'error': 'No monitoring metrics available'}
        
        return {
            'api_responses': api_analysis,
            'configuration_management': config_analysis,
            'monitoring_systems': monitoring_analysis,
            'overall_statistics': {
                'total_tests': len(self.metrics),
                'successful_tests': len(successful_metrics),
                'success_rate': len(successful_metrics) / len(self.metrics) * 100,
                'average_token_reduction': statistics.mean([m.token_reduction_percent for m in successful_metrics]),
                'average_size_reduction': statistics.mean([m.size_reduction_percent for m in successful_metrics])
            }
        }
    
    def generate_performance_report(self, include_business_analysis: bool = False) -> str:
        """Generate comprehensive performance validation report."""
        successful_metrics = [m for m in self.metrics if m.meets_target]
        failed_metrics = [m for m in self.metrics if not m.meets_target]
        
        # Calculate statistics
        if successful_metrics:
            avg_token_reduction = statistics.mean([m.token_reduction_percent for m in successful_metrics])
            avg_size_reduction = statistics.mean([m.size_reduction_percent for m in successful_metrics])
            min_token_reduction = min([m.token_reduction_percent for m in successful_metrics])
            max_token_reduction = max([m.token_reduction_percent for m in successful_metrics])
        else:
            avg_token_reduction = min_token_reduction = max_token_reduction = avg_size_reduction = 0
        
        report_lines = [
            "=" * 90,
            "YAML OPTIMIZATION PERFORMANCE VALIDATION REPORT",
            "=" * 90,
            f"Validation Time: {datetime.now() - self.start_time}",
            f"Target Token Reduction: {self.target_reduction}%",
            f"YAML Library: {self.yaml_info['version'] if self.yaml_info['available'] else 'Not Available'}",
            "",
            "PERFORMANCE SUMMARY:",
            f"  Total Tests: {len(self.metrics)}",
            f"  Tests Meeting Target: {len(successful_metrics)}",
            f"  Tests Below Target: {len(failed_metrics)}",
            f"  Success Rate: {len(successful_metrics)/len(self.metrics)*100:.1f}%",
            "",
            "TOKEN REDUCTION STATISTICS:",
            f"  Average Reduction: {avg_token_reduction:.1f}%",
            f"  Minimum Reduction: {min_token_reduction:.1f}%",
            f"  Maximum Reduction: {max_token_reduction:.1f}%",
            f"  Average Size Reduction: {avg_size_reduction:.1f}%",
            "",
            "DETAILED RESULTS BY MODEL:",
            "-" * 90,
        ]
        
        # Group metrics by model
        models = {}
        for metric in self.metrics:
            if metric.model_name not in models:
                models[metric.model_name] = []
            models[metric.model_name].append(metric)
        
        for model_name, model_metrics in models.items():
            successful_model_metrics = [m for m in model_metrics if m.meets_target]
            report_lines.extend([
                f"{model_name}:",
                f"  Tests: {len(model_metrics)} | Successful: {len(successful_model_metrics)} | Success Rate: {len(successful_model_metrics)/len(model_metrics)*100:.1f}%"
            ])
            
            if successful_model_metrics:
                avg_reduction = statistics.mean([m.token_reduction_percent for m in successful_model_metrics])
                report_lines.append(f"  Average Token Reduction: {avg_reduction:.1f}%")
            
            for metric in model_metrics:
                status = "✅" if metric.meets_target else "❌"
                report_lines.append(
                    f"    {status} {metric.test_scenario}: {metric.token_reduction_percent:.1f}% "
                    f"({metric.json_tokens:,} → {metric.yaml_tokens:,} tokens)"
                )
            report_lines.append("")
        
        # Performance analysis
        report_lines.extend([
            "SERIALIZATION PERFORMANCE:",
            "-" * 90,
        ])
        
        json_times = [m.json_serialization_time for m in self.metrics]
        yaml_times = [m.yaml_serialization_time for m in self.metrics]
        
        if json_times and yaml_times:
            avg_json_time = statistics.mean(json_times)
            avg_yaml_time = statistics.mean(yaml_times)
            time_difference = ((avg_yaml_time - avg_json_time) / avg_json_time * 100) if avg_json_time > 0 else 0
            
            report_lines.extend([
                f"Average JSON Serialization Time: {avg_json_time:.6f}s",
                f"Average YAML Serialization Time: {avg_yaml_time:.6f}s",
                f"Time Difference: {time_difference:+.1f}% ({'slower' if time_difference > 0 else 'faster'} than JSON)",
                ""
            ])
        
        # Business impact analysis
        if include_business_analysis:
            business_impact = self.analyze_business_impact()
            report_lines.extend([
                "BUSINESS IMPACT ANALYSIS:",
                "-" * 90,
            ])
            
            if 'api_responses' in business_impact and 'error' not in business_impact['api_responses']:
                api_data = business_impact['api_responses']
                report_lines.extend([
                    f"API Response Optimization:",
                    f"  Average token reduction: {api_data['average_reduction_percent']:.1f}%",
                    f"  Tokens saved per response: {api_data['tokens_saved_per_response']:.0f}",
                    "",
                    "Business Scenarios (Annual Savings):",
                ])
                
                for scenario, data in api_data['business_scenarios'].items():
                    report_lines.append(
                        f"  {scenario.replace('_', ' ').title()}: "
                        f"{data['annual_tokens_saved']:,.0f} tokens "
                        f"({data['monthly_calls']:,} calls/month)"
                    )
                report_lines.append("")
            
            if 'monitoring_systems' in business_impact and 'error' not in business_impact['monitoring_systems']:
                monitoring_data = business_impact['monitoring_systems']
                report_lines.extend([
                    f"Monitoring System Optimization:",
                    f"  Average token reduction: {monitoring_data['average_reduction_percent']:.1f}%",
                    f"  Tokens saved per health check: {monitoring_data['tokens_saved_per_check']:.0f}",
                    "",
                    "Monitoring Scenarios (Monthly Savings):",
                ])
                
                for scenario, data in monitoring_data['monitoring_scenarios'].items():
                    report_lines.append(
                        f"  {scenario.replace('_', ' ').title()}: "
                        f"{data['monthly_tokens_saved']:,.0f} tokens "
                        f"({data['engines']} engines)"
                    )
                report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "RECOMMENDATIONS:",
            "-" * 90,
        ])
        
        success_rate = len(successful_metrics) / len(self.metrics) * 100
        
        if success_rate >= 95:
            report_lines.extend([
                "🎉 EXCELLENT PERFORMANCE - READY FOR PRODUCTION",
                "   All models exceed performance targets",
                "   Immediate deployment recommended",
                ""
            ])
        elif success_rate >= 85:
            report_lines.extend([
                "✅ GOOD PERFORMANCE - PRODUCTION READY",
                "   Most models meet targets",
                "   Consider optimizing underperforming scenarios",
                ""
            ])
        elif success_rate >= 70:
            report_lines.extend([
                "⚠️  ACCEPTABLE PERFORMANCE - REVIEW REQUIRED",
                "   Some models below target",
                "   Optimization needed before full deployment",
                ""
            ])
        else:
            report_lines.extend([
                "❌ PERFORMANCE ISSUES - OPTIMIZATION REQUIRED",
                "   Multiple models below target",
                "   Significant optimization needed",
                ""
            ])
        
        if failed_metrics:
            report_lines.extend([
                "Failed Tests Requiring Attention:",
                *[f"  • {m.model_name} - {m.test_scenario}: {m.token_reduction_percent:.1f}% (target: {self.target_reduction}%)" 
                  for m in failed_metrics],
                ""
            ])
        
        report_lines.extend([
            "Next Steps:",
            "1. Address any failed test scenarios",
            "2. Implement production monitoring for performance tracking",
            "3. Consider caching strategies for frequently serialized objects",
            "4. Monitor real-world performance after deployment",
            "",
            "=" * 90
        ])
        
        return "\n".join(report_lines)


def main():
    """Main function to run performance validation."""
    parser = argparse.ArgumentParser(description="YAML Optimization Performance Validation")
    parser.add_argument("--target-reduction", type=float, default=25.0,
                       help="Target token reduction percentage (default: 25.0)")
    parser.add_argument("--business-analysis", action="store_true",
                       help="Include detailed business impact analysis")
    parser.add_argument("--output", type=str, default="yaml_performance_validation_report.txt",
                       help="Output file for validation report")
    
    args = parser.parse_args()
    
    # Create validator and run validation
    validator = YAMLPerformanceValidator(target_reduction=args.target_reduction)
    
    try:
        validator.run_validation()
        
        # Generate and display report
        report = validator.generate_performance_report(include_business_analysis=args.business_analysis)
        print("\n" + report)
        
        # Save report to file
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        validator.log(f"Report saved to {args.output}")
        
        # Exit with appropriate code
        successful_tests = len([m for m in validator.metrics if m.meets_target])
        total_tests = len(validator.metrics)
        success_rate = successful_tests / total_tests * 100
        
        if success_rate >= 85:
            print(f"\n🎉 Performance validation successful! {success_rate:.1f}% of tests meet targets.")
            sys.exit(0)
        else:
            print(f"\n⚠️  Performance validation completed with concerns. {success_rate:.1f}% of tests meet targets.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Performance validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()