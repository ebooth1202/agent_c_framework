#!/usr/bin/env python3
"""Simple test to verify tool imports work."""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
current_dir = Path(__file__).parent
tools_src = current_dir.parent / 'src'
sys.path.insert(0, str(tools_src))

print("Testing tool imports...")

try:
    from agent_c_tools.tools.excel.tool import ExcelTools
    print("✓ ExcelTools imported successfully")
except Exception as e:
    print(f"✗ ExcelTools import failed: {e}")
    sys.exit(1)

try:
    from agent_c_tools.tools.cobol.tool import CobolTools
    print("✓ CobolTools imported successfully")
except Exception as e:
    print(f"✗ CobolTools import failed: {e}")
    sys.exit(1)

# Test basic instantiation
try:
    excel_tool = ExcelTools()
    print("✓ ExcelTools instance created")
except Exception as e:
    print(f"✗ ExcelTools instantiation failed: {e}")
    sys.exit(1)

try:
    cobol_tool = CobolTools()
    print("✓ CobolTools instance created")
except Exception as e:
    print(f"✗ CobolTools instantiation failed: {e}")
    sys.exit(1)

print("✅ All import tests passed! Tools are properly structured.")