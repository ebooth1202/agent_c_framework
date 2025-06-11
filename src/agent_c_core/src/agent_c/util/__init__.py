from agent_c.util.detect_debugger import debugger_is_active
from agent_c.util.token_counter import TokenCounter
from agent_c.util.dict import filter_dict_by_keys
from agent_c.util.slugs import MnemonicSlugs
from agent_c.util.string import to_snake_case, generate_path_tree
from agent_c.util.singleton_cache import (
    SingletonCacheMeta, 
    CacheManager, 
    ThreadSafeLRUCache, 
    SharedCacheRegistry, 
    shared_cache_registry,
    CacheNames
)
