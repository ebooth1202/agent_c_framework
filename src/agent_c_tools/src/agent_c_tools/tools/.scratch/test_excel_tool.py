#!/usr/bin/env python3
"""
Basic test script for Excel tool to verify functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
tools_src = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(tools_src))

try:
    from agent_c_tools.tools.excel.tool import ExcelTools
    print("✓ Successfully imported ExcelTools")
except ImportError as e:
    print(f"✗ Failed to import ExcelTools: {e}")
    sys.exit(1)

async def basic_test():
    """Basic functionality test"""
    print("\n=== Testing Excel Tool Basic Functionality ===")
    
    # Create tool instance (minimal setup)
    excel_tool = ExcelTools()
    
    # Test create workbook
    try:
        result = await excel_tool.create_workbook()
        print("✓ create_workbook() executed successfully")
        print(f"  Result: {result[:100]}...")
    except Exception as e:
        print(f"✗ create_workbook() failed: {e}")
        return False
    
    # Test list sheets
    try:
        result = await excel_tool.list_sheets()
        print("✓ list_sheets() executed successfully")
        print(f"  Result: {result[:100]}...")
    except Exception as e:
        print(f"✗ list_sheets() failed: {e}")
        return False
    
    # Test create sheet
    try:
        result = await excel_tool.create_sheet(sheet_name="TestSheet")
        print("✓ create_sheet() executed successfully")
        print(f"  Result: {result[:100]}...")
    except Exception as e:
        print(f"✗ create_sheet() failed: {e}")
        return False
    
    # Test row reservation system
    try:
        result = await excel_tool.reserve_rows(row_count=100, sheet_name="TestSheet")
        print("✓ reserve_rows() executed successfully")
        print(f"  Result: {result[:100]}...")
    except Exception as e:
        print(f"✗ reserve_rows() failed: {e}")
        return False
    
    # Test append records
    try:
        test_records = [
            ["Name", "Age", "City"],
            ["John Doe", "30", "New York"],
            ["Jane Smith", "25", "Los Angeles"],
            ["Bob Johnson", "35", "Chicago"]
        ]
        result = await excel_tool.append_records(records=test_records, sheet_name="TestSheet")
        print("✓ append_records() executed successfully")
        print(f"  Result: {result[:100]}...")
    except Exception as e:
        print(f"✗ append_records() failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Excel Tool Test Script")
    print("=" * 50)
    
    success = asyncio.run(basic_test())
    
    if success:
        print("\n✓ All basic tests passed!")
        print("Excel tool is ready for use.")
    else:
        print("\n✗ Some tests failed.")
        sys.exit(1)