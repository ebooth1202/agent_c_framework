# Config Loader Singleton API Reference

## Overview

This document provides a comprehensive API reference for the singleton configuration loaders in Agent C. All classes maintain backward compatibility while providing enhanced performance through singleton patterns and intelligent caching.

## Table of Contents

- [ConfigLoader](#configloader)
- [ModelConfigurationLoader](#modelconfigurationloader)
- [AgentConfigLoader](#agentconfigloader)
- [Singleton Infrastructure](#singleton-infrastructure)
- [Cache Management](#cache-management)
- [Testing Utilities](#testing-utilities)
- [Convenience Functions](#convenience-functions)

---

## ConfigLoader

Base configuration loader with singleton pattern and path resolution caching.

### Class Definition

```python
class ConfigLoader(metaclass=SingletonCacheMeta):
    """Base configuration loader with singleton behavior."""
```

### Constructor

```python
def __init__(self, config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (Optional[str]): Path to configuration directory. If None, uses `AGENT_C_CONFIG_PATH` environment variable or auto-detection.

**Returns:** ConfigLoader instance (singleton for identical parameters)

**Example:**
```python
# These return the same instance
loader1 = ConfigLoader("/path/to/config")
loader2 = ConfigLoader("/path/to/config")
assert loader1 is loader2  # True

# Different paths create different instances
loader3 = ConfigLoader("/different/path")
assert loader1 is not loader3  # True
```

### Instance Attributes

- `config_path` (str): Resolved configuration directory path
- `logger`: Logger instance for the class

### Class Methods

#### `clear_path_cache()`

```python
@classmethod
def clear_path_cache(cls) -> int
```

Clear the path resolution cache.

**Returns:** Number of cache entries cleared

**Example:**
```python
cleared_count = ConfigLoader.clear_path_cache()
print(f"Cleared {cleared_count} path cache entries")
```

#### `get_cache_stats()`

```python
@classmethod
def get_cache_stats(cls) -> Dict[str, Any]
```

Get comprehensive cache statistics.

**Returns:** Dictionary with singleton and path resolution statistics

**Example:**
```python
stats = ConfigLoader.get_cache_stats()
print(f"Path cache hit rate: {stats['path_resolution_stats']['hit_rate']:.2%}")
```

#### `invalidate_cache()`

```python
@classmethod
def invalidate_cache(cls, config_path: Optional[str] = None) -> Dict[str, Any]
```

Invalidate ConfigLoader caches.

**Parameters:**
- `config_path` (Optional[str]): If provided, invalidate singleton instance for this path

**Returns:** Dictionary with invalidation results

**Example:**
```python
results = ConfigLoader.invalidate_cache(config_path="/specific/path")
print(f"Singleton invalidated: {results['singleton_invalidated']}")
```

---

## ModelConfigurationLoader

Enhanced configuration loader for model configurations with multi-layer caching.

### Class Definition

```python
class ModelConfigurationLoader(ConfigLoader, metaclass=SingletonCacheMeta):
    """Loader for model configuration files with enhanced caching."""
```

### Constructor

```python
def __init__(self, config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (Optional[str]): Path to configuration directory

**Returns:** ModelConfigurationLoader instance (singleton for identical parameters)

**Example:**
```python
loader = ModelConfigurationLoader("/path/to/config")
config = loader.get_cached_config()
```

### Instance Attributes

- `config_file_path` (Path): Path to model_configs.json file
- `_cached_config` (Optional[ModelConfigurationFile]): Cached configuration object
- `_file_lock` (threading.RLock): Thread-safe file operations lock

### Instance Methods

#### `flattened_config()`

```python
def flattened_config() -> Dict[str, Any]
```

Flatten the cached model configuration into a dictionary.

**Returns:** Dictionary with model_id as keys and model configurations as values

**Example:**
```python
flattened = loader.flattened_config()
gpt4_config = flattened["gpt-4"]
print(f"GPT-4 vendor: {gpt4_config['vendor']}")
```

#### `load_from_json()`

```python
def load_from_json(self, json_path: Optional[Union[str, Path]] = None) -> ModelConfigurationFile
```

Load model configuration from JSON file with caching.

**Parameters:**
- `json_path` (Optional[Union[str, Path]]): Path to JSON file (uses default if None)

**Returns:** ModelConfigurationFile instance

**Raises:**
- `FileNotFoundError`: If JSON file doesn't exist
- `json.JSONDecodeError`: If JSON is malformed
- `ValidationError`: If JSON doesn't match schema

**Example:**
```python
config = loader.load_from_json("/custom/path/models.json")
```

#### `load_from_dict()`

```python
def load_from_dict(self, config_data: Dict[str, Any]) -> ModelConfigurationFile
```

Load model configuration from dictionary.

**Parameters:**
- `config_data` (Dict[str, Any]): Configuration data dictionary

**Returns:** ModelConfigurationFile instance

**Example:**
```python
config_dict = {"vendors": [...]}
config = loader.load_from_dict(config_dict)
```

#### `save_to_json()`

```python
def save_to_json(
    self, 
    config: ModelConfigurationFile,
    json_path: Optional[Union[str, Path]] = None,
    indent: int = 2
) -> None
```

Save model configuration to JSON file.

**Parameters:**
- `config` (ModelConfigurationFile): Configuration to save
- `json_path` (Optional[Union[str, Path]]): Save path (uses default if None)
- `indent` (int): JSON indentation level

**Example:**
```python
loader.save_to_json(config, "/backup/models.json")
```

#### `validate_file()`

```python
def validate_file(self, json_path: Optional[Union[str, Path]] = None) -> bool
```

Validate a model configuration JSON file.

**Parameters:**
- `json_path` (Optional[Union[str, Path]]): Path to validate (uses default if None)

**Returns:** True if valid, False otherwise

**Example:**
```python
is_valid = loader.validate_file("/path/to/models.json")
```

#### `get_cached_config()`

```python
def get_cached_config(self) -> Optional[ModelConfigurationFile]
```

Get the cached configuration if available.

**Returns:** Cached ModelConfigurationFile or None

#### `reload()`

```python
def reload(self) -> ModelConfigurationFile
```

Reload configuration from default path, bypassing cache.

**Returns:** Reloaded ModelConfigurationFile

#### `invalidate_file_cache()`

```python
def invalidate_file_cache(self, json_path: Optional[Union[str, Path]] = None) -> None
```

Invalidate cache for a specific JSON file.

**Parameters:**
- `json_path` (Optional[Union[str, Path]]): File to invalidate (uses default if None)

### Class Methods

#### `clear_model_caches()`

```python
@classmethod
def clear_model_caches(cls) -> Dict[str, int]
```

Clear all model configuration caches.

**Returns:** Dictionary with cache clear results

**Example:**
```python
results = ModelConfigurationLoader.clear_model_caches()
print(f"JSON cache cleared: {results['json_cache_cleared']} entries")
```

#### `get_cache_stats()`

```python
@classmethod
def get_cache_stats(cls) -> Dict[str, Any]
```

Get comprehensive cache statistics.

**Returns:** Dictionary with singleton, JSON parsing, and model config statistics

#### `invalidate_cache()`

```python
@classmethod
def invalidate_cache(cls, config_path: Optional[str] = None) -> Dict[str, Any]
```

Invalidate ModelConfigurationLoader caches.

**Parameters:**
- `config_path` (Optional[str]): If provided, invalidate singleton instance

**Returns:** Dictionary with invalidation results

---

## AgentConfigLoader

Simplified agent configuration loader with automatic migration and model config integration.

### Class Definition

```python
class AgentConfigLoader(ConfigLoader, metaclass=SingletonCacheMeta):
    """Simplified agent configuration loader with singleton behavior."""
```

### Constructor

```python
def __init__(
    self,
    default_model: str = 'claude-sonnet-4-20250514',
    model_configs: Optional[ModelConfigurationFile] = None,
    config_path: Optional[str] = None
)
```

**Parameters:**
- `default_model` (str): Default model ID to use
- `model_configs` (Optional[ModelConfigurationFile]): Model configuration (uses ModelConfigurationLoader singleton if None)
- `config_path` (Optional[str]): Path to configuration directory

**Returns:** AgentConfigLoader instance (singleton for identical parameters)

**Example:**
```python
# Uses ModelConfigurationLoader singleton automatically
loader = AgentConfigLoader(default_model="gpt-4")

# Explicit model config
model_config = ModelConfigurationLoader().get_cached_config()
loader = AgentConfigLoader(model_configs=model_config)
```

### Instance Attributes

- `model_configs` (ModelConfigurationFile): Model configuration object
- `agent_config_folder` (Path): Path to agents directory
- `_agent_config_cache` (Dict[str, AgentConfiguration]): Cached agent configurations
- `_default_model` (str): Default model ID
- `_auto_migrate` (bool): Always True (automatic migration enabled)
- `_target_version` (Optional[int]): Always None (latest version)
- `_migration_log` (Dict[str, Dict[str, Any]]): Migration tracking

### Instance Methods

#### `load_agents()`

```python
def load_agents(self) -> None
```

Load all agent configurations with caching.

#### `add_agent_config()`

```python
def add_agent_config(self, agent_config: AgentConfiguration) -> None
```

Add a new agent configuration to the loader.

**Parameters:**
- `agent_config` (AgentConfiguration): The agent configuration to add

**Example:**
```python
from agent_c.models.agent_config import AgentConfigurationV2

new_agent = AgentConfigurationV2(
    name="my_agent",
    model_id="gpt-4",
    agent_description="My custom agent",
    # ... other fields
)
loader.add_agent_config(new_agent)
```

#### `load_agent_config_file()`

```python
def load_agent_config_file(self, agent_config_path: str) -> Optional[AgentConfiguration]
```

Load an agent configuration from a YAML file.

**Parameters:**
- `agent_config_path` (str): Path to the YAML file

**Returns:** AgentConfiguration instance or None if failed

#### `duplicate()`

```python
def duplicate(self, agent_key: str) -> AgentConfiguration
```

Duplicate an existing agent configuration.

**Parameters:**
- `agent_key` (str): Key of the agent to duplicate

**Returns:** New AgentConfiguration with unique key

#### `get_migration_report()`

```python
def get_migration_report(self) -> Dict[str, Any]
```

Get a report of all migrations performed.

**Returns:** Dictionary with migration statistics and details

**Example:**
```python
report = loader.get_migration_report()
print(f"Migrated {report['total_migrated']} configurations")
```

#### `save_migrated_configs()`

```python
def save_migrated_configs(self, backup_dir: Optional[str] = None) -> None
```

Save all migrated configurations back to disk.

**Parameters:**
- `backup_dir` (Optional[str]): Directory to backup original files

#### `get_typed_config()`

```python
def get_typed_config(self, agent_name: str, version_type: type[T]) -> T
```

Get a configuration with specific version type checking.

**Parameters:**
- `agent_name` (str): Name of the agent
- `version_type` (type[T]): Expected configuration type

**Returns:** Typed configuration instance

**Example:**
```python
from agent_c.models.agent_config import AgentConfigurationV2
v2_config = loader.get_typed_config("my_agent", AgentConfigurationV2)
```

#### `get_latest_version_configs()`

```python
def get_latest_version_configs(self) -> Dict[str, CurrentAgentConfiguration]
```

Get all configurations as the latest version.

**Returns:** Dictionary mapping agent names to latest version configurations

### Properties

#### `catalog`

```python
@property
def catalog(self) -> Dict[str, AgentConfiguration]
```

Returns a catalog of all agent configurations.

**Example:**
```python
all_agents = loader.catalog
for agent_key, config in all_agents.items():
    print(f"Agent: {config.name}, Model: {config.model_id}")
```

#### `agent_names`

```python
@property
def agent_names(self) -> List[str]
```

Returns list of all agent names.

### Class Methods

#### `clear_agent_caches()`

```python
@classmethod
def clear_agent_caches(cls) -> Dict[str, int]
```

Clear all agent configuration caches.

**Returns:** Dictionary with cache clear results

#### `get_cache_stats()`

```python
@classmethod
def get_cache_stats(cls) -> Dict[str, Any]
```

Get comprehensive cache statistics.

**Returns:** Dictionary with singleton and agent config statistics

#### `invalidate_cache()`

```python
@classmethod
def invalidate_cache(
    cls, 
    config_path: Optional[str] = None, 
    default_model: Optional[str] = None
) -> Dict[str, Any]
```

Invalidate AgentConfigLoader caches.

**Parameters:**
- `config_path` (Optional[str]): If provided, invalidate singleton for this path
- `default_model` (Optional[str]): If provided, invalidate singleton for this model

**Returns:** Dictionary with invalidation results

---

## Singleton Infrastructure

### SingletonCacheMeta

Metaclass that implements cache key-based singleton pattern.

```python
class SingletonCacheMeta(type):
    """Metaclass for cache key-based singleton management."""
```

#### Methods Available on Singleton Classes

##### `clear_cache()`

```python
@classmethod
def clear_cache(cls) -> int
```

Clear all cached instances for this class.

##### `get_cache_stats()`

```python
@classmethod
def get_cache_stats(cls) -> Dict[str, int]
```

Get cache performance statistics.

##### `get_cached_instances()`

```python
@classmethod
def get_cached_instances(cls) -> int
```

Get count of currently cached instances.

##### `invalidate_instance()`

```python
@classmethod
def invalidate_instance(cls, *args, **kwargs) -> bool
```

Invalidate a specific cached instance.

### ThreadSafeLRUCache

High-performance LRU cache with TTL support.

```python
class ThreadSafeLRUCache:
    def __init__(self, max_size: int = 128, ttl_seconds: Optional[float] = None)
```

#### Methods

##### `get()`

```python
def get(self, key: str, default: Any = None) -> Any
```

Get item from cache.

##### `put()`

```python
def put(self, key: str, value: Any) -> None
```

Put item in cache.

##### `get_or_compute()`

```python
def get_or_compute(self, key: str, compute_func: Callable[[], Any]) -> Any
```

Get item from cache or compute and cache it.

##### `invalidate()`

```python
def invalidate(self, key: str) -> bool
```

Remove specific key from cache.

##### `clear()`

```python
def clear(self) -> int
```

Clear all cache entries.

##### `get_stats()`

```python
def get_stats(self) -> Dict[str, Any]
```

Get cache statistics.

### SharedCacheRegistry

Centralized cache management.

```python
shared_cache_registry = SharedCacheRegistry()
```

#### Methods

##### `get_cache()`

```python
def get_cache(
    self, 
    name: str, 
    max_size: int = 128, 
    ttl_seconds: Optional[float] = None
) -> ThreadSafeLRUCache
```

Get or create a named cache.

##### `clear_cache()`

```python
def clear_cache(self, name: str) -> int
```

Clear a specific named cache.

##### `clear_all_caches()`

```python
def clear_all_caches(self) -> Dict[str, int]
```

Clear all registered caches.

##### `get_all_stats()`

```python
def get_all_stats(self) -> Dict[str, Dict[str, Any]]
```

Get statistics for all registered caches.

### CacheNames

Standard cache names for config loader operations.

```python
class CacheNames:
    PATH_RESOLUTION = "path_resolution"
    FILE_CONTENT = "file_content"
    JSON_PARSING = "json_parsing"
    AGENT_CONFIGS = "agent_configs"
    MODEL_CONFIGS = "model_configs"
```

---

## Cache Management

### CacheManager

Utility class for managing singleton caches across multiple classes.

#### `clear_all_caches()`

```python
@staticmethod
def clear_all_caches(*classes: Type) -> Dict[str, int]
```

Clear caches for multiple singleton classes.

**Example:**
```python
from agent_c.util import CacheManager

results = CacheManager.clear_all_caches(
    ConfigLoader, 
    ModelConfigurationLoader, 
    AgentConfigLoader
)
```

#### `get_all_cache_stats()`

```python
@staticmethod
def get_all_cache_stats(*classes: Type) -> Dict[str, Dict[str, int]]
```

Get cache statistics for multiple singleton classes.

#### `get_cache_summary()`

```python
@staticmethod
def get_cache_summary(*classes: Type) -> Dict[str, Any]
```

Get comprehensive cache summary for multiple classes.

**Example:**
```python
summary = CacheManager.get_cache_summary(
    ConfigLoader, 
    ModelConfigurationLoader, 
    AgentConfigLoader
)
print(f"Total hit rate: {summary['hit_rate']:.2%}")
```

---

## Testing Utilities

### SingletonTestFixture

Test fixture for singleton classes.

```python
class SingletonTestFixture:
    def __init__(self, singleton_classes: List[Type])
```

#### Usage

```python
from agent_c.util import singleton_test_context

with singleton_test_context(ConfigLoader, ModelConfigurationLoader):
    # Tests run in isolated singleton environment
    loader1 = ConfigLoader("/test")
    loader2 = ConfigLoader("/test")
    assert loader1 is loader2
```

### CacheTestFixture

Test fixture for cache management testing.

```python
from agent_c.util import cache_test_context, CacheNames

with cache_test_context(CacheNames.MODEL_CONFIGS):
    # Tests run with clean cache state
    pass
```

### ConcurrencyTestHelper

Helper for testing concurrent access.

#### `test_singleton_thread_safety()`

```python
@staticmethod
def test_singleton_thread_safety(
    singleton_class: Type,
    args: tuple = (),
    kwargs: Optional[dict] = None,
    num_threads: int = 10,
    operations_per_thread: int = 100
) -> None
```

### PerformanceBenchmark

Performance benchmarking utilities.

#### `benchmark_singleton_performance()`

```python
@staticmethod
def benchmark_singleton_performance(
    singleton_class: Type,
    regular_class: Type,
    args: tuple = (),
    kwargs: Optional[dict] = None,
    iterations: int = 10000
) -> Dict[str, float]
```

**Example:**
```python
from agent_c.util import PerformanceBenchmark

results = PerformanceBenchmark.benchmark_singleton_performance(
    ConfigLoader,
    RegularConfigLoader,
    kwargs={'config_path': '/test'},
    iterations=1000
)
print(f"Speedup: {results['speedup']:.1f}x")
```

---

## Convenience Functions

### Agent Configuration Functions

#### `load_all_agents_latest()`

```python
def load_all_agents_latest(config_path: str) -> Dict[str, CurrentAgentConfiguration]
```

Load all agents and ensure they're migrated to the latest version.

#### `load_agents_preserve_versions()`

```python
def load_agents_preserve_versions(config_path: str) -> Dict[str, AgentConfiguration]
```

Load all agents (always migrated to latest in simplified version).

#### `migrate_all_agents_in_place()`

```python
def migrate_all_agents_in_place(config_path: str, backup_dir: str) -> Dict[str, Any]
```

Load all agents, migrate to latest version, and save back to disk.

**Example:**
```python
from agent_c.config.agent_config_loader import load_all_agents_latest

latest_agents = load_all_agents_latest("/path/to/config")
for agent_name, config in latest_agents.items():
    print(f"Agent: {agent_name}, Version: {config.version}")
```

---

## Error Handling

### Common Exceptions

- **`FileNotFoundError`**: Configuration files not found
- **`json.JSONDecodeError`**: Malformed JSON in configuration files
- **`ValidationError`**: Configuration data doesn't match expected schema
- **`ValueError`**: Invalid parameters or missing required data
- **`TypeError`**: Incorrect configuration version type requested

### Exception Examples

```python
try:
    loader = ModelConfigurationLoader("/nonexistent/path")
except FileNotFoundError as e:
    print(f"Configuration not found: {e}")

try:
    config = loader.get_typed_config("agent", AgentConfigurationV1)
except TypeError as e:
    print(f"Version mismatch: {e}")
```

---

## Performance Considerations

### Cache Configuration Guidelines

| Use Case | Max Size | TTL | Notes |
|----------|----------|-----|-------|
| Development | 50-100 | 5-10 min | Frequent changes |
| Testing | 10-50 | 1-5 min | Isolation important |
| Production | 100-500 | 30-60 min | Stability priority |
| High Volume | 500-1000 | 60+ min | Memory vs performance |

### Memory Usage

```python
# Monitor cache memory usage
summary = CacheManager.get_cache_summary(
    ConfigLoader, ModelConfigurationLoader, AgentConfigLoader
)
print(f"Total cached instances: {summary['total_instances']}")
print(f"Hit rate: {summary['hit_rate']:.2%}")
```

### Best Practices

1. **Reuse Parameters**: Use same parameters for maximum singleton benefits
2. **Monitor Hit Rates**: Aim for >80% cache hit rates
3. **Appropriate TTLs**: Balance freshness vs performance
4. **Test Isolation**: Always use test fixtures for singleton tests
5. **Cache Invalidation**: Only invalidate when necessary

---

## Version Information

- **API Version**: 1.0
- **Agent C Version**: Compatible with Agent C 2.0+
- **Python Version**: 3.8+
- **Thread Safety**: Full thread safety guaranteed
- **Backward Compatibility**: 100% backward compatible

---

## See Also

- [Config Loader Singleton Conversion Guide](config_loader_singleton_conversion.md)
- [Agent C Architecture Documentation](../README.md)
- [Model Configuration Schema](model_configuration_schema.md)
- [Agent Configuration Schema](agent_configuration_schema.md)