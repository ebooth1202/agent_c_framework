"""Tool discovery and loading for the MCP ToolChest Server.

This module provides functions for discovering and loading Agent C tools
from various packages and registering them with a ToolChest.
"""

import importlib
import inspect
import pkgutil
import sys
import logging
from typing import Any, Dict, List, Optional, Set, Type

from agent_c.toolsets import ToolChest
from agent_c.toolsets.tool_set import Toolset

logger = logging.getLogger(__name__)


def discover_toolsets(package_names: List[str]):
    """Discover all toolset classes in the specified packages.
    
    Args:
        package_names: List of package names to search for toolsets
        
    Returns:
        List of discovered toolset classes
    """
    for package_name in package_names:
        try:
            importlib.import_module(package_name)
        except ImportError as e:
            logger.warning(f"Error importing package {package_name}: {e}")


def import_packages(package_names: List[str]) -> None:
    """Import specified packages to trigger tool registration.
    
    Many tools register themselves when imported, so this function
    ensures that the specified packages are imported.
    
    Args:
        package_names: List of package names to import
    """
    for package_name in package_names:
        try:
            importlib.import_module(package_name)
            logger.info(f"Imported package: {package_name}")
        except ImportError as e:
            logger.warning(f"Error importing package {package_name}: {e}")


async def discover_and_load_tools(tool_chest: ToolChest, discover_packages: List[str], 
                           import_packages_list: List[str], tool_config: Dict[str, Dict[str, Any]],
                           tool_opts: Optional[Dict[str, Any]] = None) -> None:
    """Discover and load tools into a ToolChest.
    
    Args:
        tool_chest: ToolChest to load tools into
        discover_packages: Packages to discover toolsets from
        import_packages_list: Additional packages to import
        tool_config: Configuration for specific tools
        tool_opts: Optional dictionary of options to pass to init_tools
    """
    # Import additional packages first
    import_packages(import_packages_list)
    logger.info(f"Registered {len(Toolset.tool_registry)} toolsets.")
    
    # Discover toolset classes
    discover_toolsets(discover_packages)
    await tool_chest.init_tools(**tool_opts)

    logger.info(f"Enabled {len(tool_chest.active_tools)} tools.")