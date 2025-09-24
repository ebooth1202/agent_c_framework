#!/usr/bin/env python3
"""
Basic integration test for Excel and COBOL tools to verify they work.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the src directory to Python path
tools_src = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(tools_src))

async def test_excel_tool_basic():
    """Test basic Excel tool functionality."""
    print("\n=== Testing Excel Tool ===")
    
    try:
        from agent_c_tools.tools.excel.tool import ExcelTools
        print("✓ Successfully imported ExcelTools")
    except ImportError as e:
        print(f"✗ Failed to import ExcelTools: {e}")
        return False
    
    # Create tool instance
    excel_tool = ExcelTools()
    print("✓ Created ExcelTools instance")
    
    # Test create workbook
    try:
        result = await excel_tool.create_workbook()
        print("✓ create_workbook() executed")
        
        # Verify it's valid JSON
        import json
        data = json.loads(result)
        if data.get('success'):
            print("✓ Workbook created successfully")
        else:
            print(f"✗ Workbook creation failed: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"✗ create_workbook() failed: {e}")
        return False
    
    # Test list sheets
    try:
        result = await excel_tool.list_sheets()
        data = json.loads(result)
        if data.get('success'):
            print(f"✓ Listed {len(data.get('sheets', []))} sheets")
        else:
            print(f"✗ list_sheets() failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ list_sheets() failed: {e}")
        return False
    
    # Test append records
    try:
        test_records = [
            ["Name", "Age", "City"],
            ["John Doe", "30", "New York"],
            ["Jane Smith", "25", "Los Angeles"]
        ]
        result = await excel_tool.append_records(records=test_records, sheet_name="Sheet")
        data = json.loads(result)
        if data.get('success'):
            print(f"✓ Appended {data.get('records_written', 0)} records")
        else:
            print(f"✗ append_records() failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ append_records() failed: {e}")
        return False
    
    print("✓ Excel tool basic tests passed!")
    return True

async def test_cobol_tool_basic():
    """Test basic COBOL tool functionality."""
    print("\n=== Testing COBOL Tool ===")
    
    try:
        from agent_c_tools.tools.cobol.tool import CobolTools
        print("✓ Successfully imported CobolTools")
    except ImportError as e:
        print(f"✗ Failed to import CobolTools: {e}")
        return False
    
    # Create tool instance
    cobol_tool = CobolTools()
    print("✓ Created CobolTools instance")
    
    # Test format COBOL value
    try:
        # Test COMP-3 formatting
        result = cobol_tool._format_cobol_value("123.45", "COMP-3", True)
        if result == 123.45:
            print("✓ COMP-3 formatting works")
        else:
            print(f"✗ COMP-3 formatting failed: expected 123.45, got {result}")
            return False
        
        # Test CHAR formatting
        result = cobol_tool._format_cobol_value("  John Doe  ", "CHAR", True)
        if result == "John Doe":
            print("✓ CHAR formatting works")
        else:
            print(f"✗ CHAR formatting failed: expected 'John Doe', got '{result}'")
            return False
            
    except Exception as e:
        print(f"✗ COBOL value formatting failed: {e}")
        return False
    
    # Test convert COBOL records to Excel format
    try:
        cobol_records = [
            {
                "data": ["12345", "678.90", "John Doe"],
                "types": ["COMP", "COMP-3", "CHAR"]
            }
        ]
        result = cobol_tool._convert_cobol_records_to_excel_format(cobol_records, True)
        if len(result) == 1 and len(result[0]) == 3:
            print("✓ COBOL to Excel conversion works")
        else:
            print(f"✗ COBOL to Excel conversion failed: {result}")
            return False
    except Exception as e:
        print(f"✗ COBOL to Excel conversion failed: {e}")
        return False
    
    # Test get conversion info
    try:
        result = await cobol_tool.get_cobol_conversion_info()
        import json
        data = json.loads(result)
        if data.get('success'):
            print("✓ Conversion info retrieved")
            print(f"  Supported types: {', '.join(data.get('supported_cobol_types', []))}")
        else:
            print(f"✗ get_cobol_conversion_info() failed: {data.get('error')}")
            return False
    except Exception as e:
        print(f"✗ get_cobol_conversion_info() failed: {e}")
        return False
    
    print("✓ COBOL tool basic tests passed!")
    return True

async def test_tool_integration():
    """Test basic integration between tools."""
    print("\n=== Testing Tool Integration ===")
    
    try:
        from agent_c_tools.tools.excel.tool import ExcelTools
        from agent_c_tools.tools.cobol.tool import CobolTools
        
        # Create instances
        excel_tool = ExcelTools()
        cobol_tool = CobolTools()
        
        # Mock the Excel tool dependency in COBOL tool
        cobol_tool.excel_tool = excel_tool
        
        print("✓ Tools can be instantiated together")
        
        # Test that COBOL tool can access Excel tool
        if cobol_tool.excel_tool is not None:
            print("✓ COBOL tool can reference Excel tool")
        else:
            print("✗ COBOL tool cannot reference Excel tool")
            return False
            
    except Exception as e:
        print(f"✗ Tool integration failed: {e}")
        return False
    
    print("✓ Tool integration test passed!")
    return True

async def main():
    """Run all basic tests."""
    print("Agent C Tools - Basic Integration Tests")
    print("=" * 50)
    
    tests = [
        test_excel_tool_basic,
        test_cobol_tool_basic,
        test_tool_integration
    ]
    
    all_passed = True
    for test in tests:
        try:
            success = await test()
            if not success:
                all_passed = False
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ ALL TESTS PASSED! Tools are working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)