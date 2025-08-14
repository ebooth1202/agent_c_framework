"""
YAML serialization utilities for web search models.

This module provides optimized YAML serialization utilities designed for
token efficiency while maintaining readability and functionality.
"""

import json
from typing import Dict, Any, Optional, Union, List, Set
from datetime import datetime
from enum import Enum
from functools import lru_cache
from agent_c.util.structured_logging import get_logger

logger = get_logger(__name__)

# Global YAML module cache
_yaml_module = None
_yaml_version = None

def get_yaml_module():
    """
    Lazy import of YAML module with fallback handling and version validation.
    
    Returns:
        yaml module if available, False if not available
    """
    global _yaml_module, _yaml_version
    if _yaml_module is None:
        try:
            import yaml
            _yaml_module = yaml
            _yaml_version = getattr(yaml, '__version__', 'unknown')
            
            # Validate required YAML features
            _validate_yaml_features(yaml)
            
            logger.debug(f"YAML module loaded successfully (version: {_yaml_version})")
        except ImportError:
            _yaml_module = False
            logger.warning("PyYAML not available, falling back to JSON serialization")
        except Exception as e:
            _yaml_module = False
            logger.warning(f"YAML module validation failed: {e}, falling back to JSON")
    return _yaml_module


def _validate_yaml_features(yaml_module):
    """
    Validate that the YAML module has all required features.
    
    Args:
        yaml_module: The imported yaml module
        
    Raises:
        AttributeError: If required features are missing
    """
    required_features = ['dump', 'safe_load', 'YAMLError']
    for feature in required_features:
        if not hasattr(yaml_module, feature):
            raise AttributeError(f"YAML module missing required feature: {feature}")
    
    # Test basic functionality
    try:
        test_data = {'test': 'validation'}
        yaml_str = yaml_module.dump(test_data)
        parsed_data = yaml_module.safe_load(yaml_str)
        if parsed_data != test_data:
            raise ValueError("YAML round-trip validation failed")
    except Exception as e:
        raise RuntimeError(f"YAML functionality test failed: {e}")


def get_yaml_info():
    """
    Get information about the YAML module status.
    
    Returns:
        Dictionary with YAML module information
    """
    yaml_module = get_yaml_module()
    return {
        'available': yaml_module is not False,
        'version': _yaml_version,
        'module': str(yaml_module) if yaml_module else None,
        'fallback_active': yaml_module is False
    }


# Compact field name mappings for token optimization
COMPACT_FIELD_NAMES = {
    # SearchResponse fields
    'search_type': 'type',
    'engine_used': 'engine',
    'execution_time': 'time',
    'total_results': 'total',
    'pages_available': 'pages',
    
    # SearchResult fields
    'published_date': 'date',
    
    # SearchParameters fields
    'max_results': 'max',
    'include_images': 'images',
    'include_domains': 'inc_domains',
    'exclude_domains': 'exc_domains',
    'search_depth': 'depth',
    'start_date': 'from',
    'end_date': 'to',
    'additional_params': 'extra',
    
    # EngineCapabilities fields
    'search_types': 'types',
    'supports_pagination': 'pagination',
    'supports_date_filtering': 'date_filter',
    'supports_domain_filtering': 'domain_filter',
    'supports_safe_search': 'safe_search',
    'supports_language_filtering': 'lang_filter',
    'supports_region_filtering': 'region_filter',
    'supports_image_search': 'img_search',
    'supports_content_extraction': 'extract',
    'max_results_per_request': 'max_per_req',
    'rate_limit_per_minute': 'rate_limit',
    
    # WebSearchConfig fields
    'engine_name': 'name',
    'requires_api_key': 'needs_key',
    'api_key_name': 'key_name',
    'base_url': 'url',
    'max_retries': 'retries',
    'retry_delay': 'delay',
    'default_parameters': 'defaults',
    'health_check_url': 'health_url',
    'cache_ttl': 'cache',
    
    # EngineHealthStatus fields
    'engine_name': 'name',
    'is_available': 'available',
    'last_check': 'checked',
    'response_time': 'time',
    'error_message': 'error',
    'api_key_configured': 'key_ok'
}

# Sensitive field patterns for security filtering
SENSITIVE_FIELD_PATTERNS = {
    'api_key', 'api_key_name', 'password', 'secret', 'token', 'auth', 'credential'
}

# Default values to exclude in compact mode
DEFAULT_VALUES = {
    'page': 1,
    'max_results': 10,
    'timeout': 30,
    'max_retries': 3,
    'retry_delay': 1.0,
    'cache_ttl': 300,
    'language': 'en',
    'region': 'us',
    'include_images': False,
    'safesearch': 'moderate',
    'search_depth': 'standard',
    'engine': 'auto'
}


class YAMLOptimizer:
    """
    Utility class for optimized YAML serialization with token efficiency focus.
    
    This class provides methods for converting dataclass objects to YAML format
    with various optimization strategies to reduce token consumption while
    maintaining readability and functionality.
    """
    
    @staticmethod
    def filter_for_yaml(
        data: Dict[str, Any], 
        compact: bool = True,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Filter and optimize data for YAML representation.
        
        Args:
            data: Dictionary to filter and optimize
            compact: Whether to use compact optimizations
            model_name: Name of the model for context-specific optimizations
            
        Returns:
            Filtered and optimized dictionary
        """
        if not compact:
            return data
        
        filtered = {}
        for key, value in data.items():
            if YAMLOptimizer._should_include_value(key, value, model_name):
                optimized_value = YAMLOptimizer._optimize_value(value, compact)
                filtered[key] = optimized_value
        
        return filtered
    
    @staticmethod
    def _should_include_value(key: str, value: Any, model_name: Optional[str] = None) -> bool:
        """
        Determine if a value should be included in compact mode.
        
        Args:
            key: Field name
            value: Field value
            model_name: Model context for specific rules
            
        Returns:
            True if value should be included
        """
        # Always skip None values
        if value is None:
            return False
        
        # Skip empty collections
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False
        
        # Skip default boolean False for capability flags
        if isinstance(value, bool) and not value and key.startswith('supports_'):
            return False
        
        # Skip default values
        if key in DEFAULT_VALUES and value == DEFAULT_VALUES[key]:
            return False
        
        # Model-specific rules
        if model_name == 'SearchResponse':
            # Skip pagination info if not relevant
            if key in ['page', 'pages_available'] and value in [None, 1]:
                return False
        
        elif model_name == 'SearchResult':
            # Skip score and source if not provided
            if key in ['score', 'source'] and value is None:
                return False
        
        elif model_name == 'EngineCapabilities':
            # Skip False capability flags
            if key.startswith('supports_') and value is False:
                return False
        
        return True
    
    @staticmethod
    def _optimize_value(value: Any, compact: bool = True) -> Any:
        """
        Optimize individual values for YAML serialization.
        
        Args:
            value: Value to optimize
            compact: Whether to use compact optimizations
            
        Returns:
            Optimized value
        """
        # Handle enums - convert to string values
        if isinstance(value, Enum):
            return value.value
        
        # Handle datetime objects
        if isinstance(value, datetime):
            return YAMLOptimizer._serialize_datetime(value)
        
        # Handle lists recursively
        if isinstance(value, list):
            return [YAMLOptimizer._optimize_value(item, compact) for item in value]
        
        # Handle dictionaries recursively
        if isinstance(value, dict):
            return {
                k: YAMLOptimizer._optimize_value(v, compact) 
                for k, v in value.items()
            }
        
        # Handle nested dataclasses
        if hasattr(value, 'to_yaml_dict'):
            return value.to_yaml_dict(compact=compact)
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        
        return value
    
    @staticmethod
    def _serialize_datetime(dt: datetime) -> str:
        """
        Optimize datetime serialization for token efficiency.
        
        Args:
            dt: Datetime object to serialize
            
        Returns:
            Optimized ISO format string
        """
        # Remove microseconds if zero for cleaner output
        if dt.microsecond == 0:
            return dt.strftime('%Y-%m-%dT%H:%M:%S')
        
        # Use standard ISO format with microseconds
        return dt.isoformat()
    
    @staticmethod
    def apply_compact_field_names(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply compact field names for token optimization.
        
        Args:
            data: Dictionary with original field names
            
        Returns:
            Dictionary with compact field names
        """
        return {
            COMPACT_FIELD_NAMES.get(key, key): value 
            for key, value in data.items()
        }
    
    @staticmethod
    def filter_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove sensitive data from dictionary.
        
        Args:
            data: Dictionary that may contain sensitive data
            
        Returns:
            Dictionary with sensitive fields removed
        """
        filtered = {}
        for key, value in data.items():
            if not YAMLOptimizer._is_sensitive_field(key):
                filtered[key] = value
            else:
                logger.debug(f"Filtered sensitive field: {key}")
        
        return filtered
    
    @staticmethod
    def _is_sensitive_field(field_name: str) -> bool:
        """
        Check if a field contains sensitive data.
        
        Args:
            field_name: Name of the field to check
            
        Returns:
            True if field is considered sensitive
        """
        field_lower = field_name.lower()
        return any(pattern in field_lower for pattern in SENSITIVE_FIELD_PATTERNS)
    
    @staticmethod
    def to_yaml_string(
        data: Dict[str, Any], 
        compact: bool = True,
        flow_style_threshold: int = 3,
        width: Optional[int] = None,
        safe_mode: bool = True
    ) -> str:
        """
        Convert dictionary to optimized YAML string with enhanced error handling.
        
        Args:
            data: Dictionary to convert
            compact: Whether to use compact formatting
            flow_style_threshold: Max items for flow style
            width: Line width for YAML output
            safe_mode: Use safe serialization (recommended)
            
        Returns:
            YAML string representation
        """
        yaml_module = get_yaml_module()
        
        # Fallback to JSON if YAML not available
        if yaml_module is False:
            logger.info("Using JSON fallback for YAML serialization")
            return YAMLOptimizer._json_fallback(data, compact)
        
        # Determine formatting options
        use_flow_style = compact and len(data) <= flow_style_threshold
        line_width = width or (120 if compact else 80)
        
        try:
            # Sanitize data for YAML serialization
            sanitized_data = YAMLOptimizer._sanitize_for_yaml(data) if safe_mode else data
            
            yaml_output = yaml_module.dump(
                sanitized_data,
                default_flow_style=use_flow_style,
                sort_keys=False,
                allow_unicode=True,
                width=line_width,
                indent=2 if not compact else None,
                default_style=None
            )
            
            # Validate output if in safe mode
            if safe_mode and not validate_yaml_output(yaml_output):
                logger.warning("Generated YAML failed validation, using JSON fallback")
                return YAMLOptimizer._json_fallback(data, compact)
            
            return yaml_output
            
        except Exception as e:
            logger.error(f"YAML serialization failed: {e}, falling back to JSON")
            return YAMLOptimizer._json_fallback(data, compact)
    
    @staticmethod
    def _sanitize_for_yaml(data: Any) -> Any:
        """
        Sanitize data to ensure YAML serialization compatibility.
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data safe for YAML serialization
        """
        if isinstance(data, dict):
            return {
                str(k): YAMLOptimizer._sanitize_for_yaml(v) 
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [YAMLOptimizer._sanitize_for_yaml(item) for item in data]
        elif isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, Enum):
            return data.value
        else:
            # Convert complex objects to string representation
            try:
                return str(data)
            except Exception:
                return f"<{type(data).__name__} object>"
    
    @staticmethod
    def _json_fallback(data: Dict[str, Any], compact: bool = True) -> str:
        """
        JSON fallback serialization with error handling.
        
        Args:
            data: Dictionary to serialize
            compact: Whether to use compact formatting
            
        Returns:
            JSON string representation
        """
        try:
            return json.dumps(
                data, 
                indent=None if compact else 2, 
                default=YAMLOptimizer._json_serializer,
                ensure_ascii=False
            )
        except Exception as e:
            logger.error(f"JSON fallback serialization failed: {e}")
            return f"{{\"error\": \"Serialization failed: {str(e)}\"}}"
    
    @staticmethod
    def _json_serializer(obj: Any) -> str:
        """
        Custom JSON serializer for complex objects.
        
        Args:
            obj: Object to serialize
            
        Returns:
            String representation of object
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        else:
            return str(obj)


class YAMLSerializationMixin:
    """
    Mixin class providing standard YAML serialization methods.
    
    This mixin can be added to dataclasses to provide consistent
    YAML serialization capabilities with token optimization.
    """
    
    def to_yaml(
        self, 
        compact: bool = True, 
        include_sensitive: bool = False,
        **kwargs
    ) -> str:
        """
        Convert to YAML string optimized for token efficiency.
        
        Args:
            compact: Use compact representation for token optimization
            include_sensitive: Include sensitive data like API keys
            **kwargs: Additional arguments passed to YAML serializer
            
        Returns:
            YAML string representation
        """
        data = self.to_yaml_dict(compact=compact, include_sensitive=include_sensitive)
        return YAMLOptimizer.to_yaml_string(data, compact=compact, **kwargs)
    
    def to_yaml_dict(
        self, 
        compact: bool = True, 
        include_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Convert to dictionary optimized for YAML serialization.
        
        Args:
            compact: Use compact representation for token optimization
            include_sensitive: Include sensitive data like API keys
            
        Returns:
            Dictionary suitable for YAML serialization
        """
        # Get model name for context-specific optimizations
        model_name = self.__class__.__name__
        
        # Start with existing to_dict() if available
        if hasattr(self, 'to_dict'):
            data = self.to_dict()
        else:
            # Build data dictionary from dataclass fields
            data = {}
            if hasattr(self, '__dataclass_fields__'):
                for field_name in self.__dataclass_fields__:
                    value = getattr(self, field_name)
                    data[field_name] = value
            else:
                # Fallback for non-dataclass objects
                data = {
                    key: value for key, value in self.__dict__.items()
                    if not key.startswith('_')
                }
        
        # Apply optimizations
        data = YAMLOptimizer.filter_for_yaml(data, compact=compact, model_name=model_name)
        
        # Apply compact field names if requested
        if compact:
            data = YAMLOptimizer.apply_compact_field_names(data)
        
        # Handle sensitive data
        if not include_sensitive:
            data = YAMLOptimizer.filter_sensitive_data(data)
        
        return data


# Utility functions for common operations
def estimate_token_savings(json_str: str, yaml_str: str) -> Dict[str, Any]:
    """
    Estimate token savings between JSON and YAML representations.
    
    Args:
        json_str: JSON string representation
        yaml_str: YAML string representation
        
    Returns:
        Dictionary with token analysis
    """
    # Simple token estimation (split by whitespace and punctuation)
    import re
    
    def count_tokens(text: str) -> int:
        # Split on whitespace and common punctuation
        tokens = re.findall(r'\w+|[^\w\s]', text)
        return len(tokens)
    
    json_tokens = count_tokens(json_str)
    yaml_tokens = count_tokens(yaml_str)
    
    savings = json_tokens - yaml_tokens
    percentage = (savings / json_tokens * 100) if json_tokens > 0 else 0
    
    return {
        'json_tokens': json_tokens,
        'yaml_tokens': yaml_tokens,
        'tokens_saved': savings,
        'percentage_saved': round(percentage, 1),
        'json_size': len(json_str),
        'yaml_size': len(yaml_str),
        'size_saved': len(json_str) - len(yaml_str)
    }


@lru_cache(maxsize=32)
def get_compact_field_mapping(model_name: str) -> Dict[str, str]:
    """
    Get cached compact field mapping for a specific model.
    
    Args:
        model_name: Name of the model class
        
    Returns:
        Dictionary mapping original field names to compact names
    """
    # Return subset of mappings relevant to the specific model
    # This could be expanded with model-specific mappings
    return COMPACT_FIELD_NAMES


def validate_yaml_output(yaml_str: str) -> bool:
    """
    Validate that YAML output is parseable with enhanced error handling.
    
    Args:
        yaml_str: YAML string to validate
        
    Returns:
        True if YAML is valid, False otherwise
    """
    if not yaml_str or not isinstance(yaml_str, str):
        return False
    
    yaml_module = get_yaml_module()
    if yaml_module is False:
        # If YAML not available, try JSON parsing
        try:
            json.loads(yaml_str)
            return True
        except (json.JSONDecodeError, TypeError, ValueError):
            return False
    
    try:
        parsed = yaml_module.safe_load(yaml_str)
        # Additional validation - ensure we got something meaningful
        return parsed is not None or yaml_str.strip() in ['', '~', 'null']
    except Exception:  # Catch all YAML-related exceptions
        return False


def check_yaml_dependencies() -> Dict[str, Any]:
    """
    Comprehensive check of YAML dependencies and capabilities.
    
    Returns:
        Dictionary with dependency status information
    """
    result = {
        'yaml_available': False,
        'yaml_version': None,
        'features_available': [],
        'features_missing': [],
        'fallback_active': True,
        'recommendations': []
    }
    
    yaml_module = get_yaml_module()
    
    if yaml_module is False:
        result['recommendations'].append(
            "Install PyYAML for optimal performance: pip install 'PyYAML>=6.0'"
        )
        return result
    
    # YAML is available
    result['yaml_available'] = True
    result['yaml_version'] = getattr(yaml_module, '__version__', 'unknown')
    result['fallback_active'] = False
    
    # Check available features
    features_to_check = [
        'dump', 'safe_load', 'load', 'safe_dump',
        'YAMLError', 'SafeLoader', 'SafeDumper'
    ]
    
    for feature in features_to_check:
        if hasattr(yaml_module, feature):
            result['features_available'].append(feature)
        else:
            result['features_missing'].append(feature)
    
    # Version-specific recommendations
    try:
        from packaging import version
        yaml_version = version.parse(result['yaml_version'])
        if yaml_version < version.parse('6.0'):
            result['recommendations'].append(
                f"Consider upgrading PyYAML from {result['yaml_version']} to >=6.0 for better performance"
            )
    except (ImportError, Exception):
        # packaging not available or version parsing failed
        pass
    
    return result


# Export main utilities
__all__ = [
    'YAMLOptimizer',
    'YAMLSerializationMixin',
    'get_yaml_module',
    'get_yaml_info',
    'check_yaml_dependencies',
    'estimate_token_savings',
    'validate_yaml_output',
    'COMPACT_FIELD_NAMES'
]