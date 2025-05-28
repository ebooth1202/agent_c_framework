import asyncio
from typing import Dict, Any, Optional, List

class AsyncExpiringCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._expiry_tasks: Dict[str, asyncio.Task] = {}
        self.default_ttl = default_ttl

    async def set(self, key: str, session_data: Dict[str, Any]):
        # if key in self._expiry_tasks:
        #     self._expiry_tasks[key].cancel()

        self._cache[key] = session_data

        # # Schedule expiration
        # task = asyncio.create_task(self._expire_after(key, self.default_ttl))
        # self._expiry_tasks[key] = task

    # async def _expire_after(self, key: str, delay: int):
    #     await asyncio.sleep(delay)
    #     self._cache.pop(key, None)
    #     self._expiry_tasks.pop(key, None)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(key)

    def list_active(self) -> List[str]:
        return list(self._cache.keys())
