#!/usr/bin/env python3
"""
Simple debug script to investigate AgentConfigLoader state.
"""
import sys
import os
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent.absolute()
print(f"Project root: {project_root}")

# Add agent_c_core to path
agent_c_path = project_root / "src" / "agent_c_core" / "src"
sys.path.insert(0, str(agent_c_path))

print(f"Added to path: {agent_c_path}")
print(f"Path exists: {agent_c_path.exists()}")

try:
    from agent_c.config.agent_config_loader import AgentConfigLoader
    print("✓ Successfully imported AgentConfigLoader")
except Exception as e:
    print(f"✗ Failed to import AgentConfigLoader: {e}")
    sys.exit(1)

# Initialize the loader
config_path = str(project_root / "agent_c_config")
print(f"Config path: {config_path}")
print(f"Config path exists: {Path(config_path).exists()}")

try:
    loader = AgentConfigLoader(config_path=config_path)
    print("✓ AgentConfigLoader initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize AgentConfigLoader: {e}")
    import traceback
    print(traceback.format_exc())
    sys.exit(1)

# Check catalog
try:
    catalog = loader.catalog
    catalog_keys = list(catalog.keys())
    print(f"\n✓ Successfully got catalog with {len(catalog_keys)} agents")
    
    # Look for mystery world related agents
    mystery_agents = [key for key in catalog_keys if any(term in key.lower() for term in ['mystery', 'shadow_pines', 'space_station', 'victorian'])]
    print(f"Mystery world related agents: {mystery_agents}")
    
    # Show all agent keys for reference
    print(f"\nAll agent keys: {sorted(catalog_keys)}")
    
except Exception as e:
    print(f"✗ Failed to get catalog: {e}")
    import traceback
    print(traceback.format_exc())

# Check migration report
try:
    migration_report = loader.get_migration_report()
    print(f"\n✓ Migration report keys: {list(migration_report.keys())}")
    if migration_report:
        for key, value in migration_report.items():
            print(f"  {key}: {value}")
except Exception as e:
    print(f"✗ Failed to get migration report: {e}")
    import traceback
    print(traceback.format_exc())