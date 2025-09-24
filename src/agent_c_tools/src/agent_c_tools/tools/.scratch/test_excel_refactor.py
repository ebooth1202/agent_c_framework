#!/usr/bin/env python3
"""
Basic test script for the refactored Excel tool to verify functionality.
"""

import sys
import os
import asyncio
import json
import tempfile
import shutil
from pathlib import Path

# Add the tools package to path
tools_path = Path(__file__).parent.parent / "src" / "agent_c_tools"
sys.path.insert(0, str(tools_path))

# Mock the necessary imports that might not be available in test environment
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")

class MockToolChest:
    def __init__(self):
        self.available_tools = {}
        self.agent = None

class MockWorkspaceTools:
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
        
    def validate_and_get_workspace_path(self, path):
        return None, "test", "test.xlsx"
        
    async def internal_write_bytes(self, path, data, mode):
        # Write to temp file
        file_path = Path(self.temp_dir) / "test.xlsx"
        with open(file_path, 'wb') as f:
            f.write(data)
        return json.dumps({"success": True})

# Mock the agent_c imports
sys.modules['agent_c.toolsets'] = type('Module', (), {
    'Toolset': type('Toolset', (), {
        '__init__': lambda self, **kwargs: None,
        'register': staticmethod(lambda cls, **kwargs: None)
    }),
    'json_schema': lambda **kwargs: lambda func: func
})()

sys.modules['agent_c.toolsets.tool_set'] = type('Module', (), {
    'Toolset': type('Toolset', (), {
        '__init__': lambda self, **kwargs: setattr(self, 'logger', MockLogger()) or setattr(self, 'tool_chest', MockToolChest()) or setattr(self, 'tool_cache', type('Cache', (), {'get': lambda self, k: None, 'set': lambda self, k, v, expire=None: None})()),
        'register': staticmethod(lambda cls, **kwargs: None)
    })
})()

sys.modules['agent_c.toolsets.json_schema'] = type('Module', (), {
    'json_schema': lambda **kwargs: lambda func: func
})()

# Mock helper modules
sys.modules['agent_c_tools.helpers.validate_kwargs'] = type('Module', (), {
    'validate_required_fields': lambda kwargs, fields: (True, None) if all(f in kwargs for f in fields) else (False, f"Missing required field")
})()

sys.modules['agent_c_tools.helpers.path_helper'] = type('Module', (), {
    'os_file_system_path': lambda workspace_tool, unc_path: Path(workspace_tool.temp_dir) / "test.xlsx",
    'ensure_file_extension': lambda path, ext: path if path.endswith(f'.{ext}') else f"{path}.{ext}"
})()

sys.modules['agent_c_tools.helpers.media_file_html_helper'] = type('Module', (), {
    'get_file_html': lambda **kwargs: "<p>Excel file</p>"
})()

async def test_excel_tool():
    """Test the refactored Excel tool basic functionality."""
    print("🧪 Testing Refactored Excel Tool...")
    
    try:
        # Create temp directory for testing
        temp_dir = tempfile.mkdtemp()
        print(f"📁 Using temp directory: {temp_dir}")
        
        # Import the refactored Excel tool
        from tools.excel.tool import ExcelTools
        
        print("✅ Successfully imported ExcelTools")
        
        # Create tool instance
        excel_tool = ExcelTools()
        
        # Mock workspace tool
        excel_tool.workspace_tool = MockWorkspaceTools(temp_dir)
        
        print("✅ Successfully created ExcelTools instance")
        
        # Test 1: Create workbook
        print("\n📋 Test 1: Create workbook")
        result = await excel_tool.create_workbook()
        result_data = json.loads(result)
        print(f"Result: {result_data}")
        
        if result_data.get('success'):
            print("✅ Create workbook test passed")
        else:
            print(f"❌ Create workbook test failed: {result_data.get('error')}")
            return False
        
        # Test 2: List sheets
        print("\n📊 Test 2: List sheets")
        result = await excel_tool.list_sheets()
        result_data = json.loads(result)
        print(f"Result: {result_data}")
        
        if result_data.get('success'):
            print("✅ List sheets test passed")
        else:
            print(f"❌ List sheets test failed: {result_data.get('error')}")
            return False
        
        # Test 3: Append records
        print("\n📝 Test 3: Append records")
        test_records = [
            ["Name", "Age", "City"],
            ["John", "30", "New York"],
            ["Jane", "25", "Los Angeles"],
            ["Bob", "35", "Chicago"]
        ]
        
        result = await excel_tool.append_records(
            records=test_records,
            sheet_name="TestSheet"
        )
        result_data = json.loads(result)
        print(f"Result: {result_data}")
        
        if result_data.get('success'):
            print("✅ Append records test passed")
        else:
            print(f"❌ Append records test failed: {result_data.get('error')}")
            return False
        
        # Test 4: Save workbook
        print("\n💾 Test 4: Save workbook")
        result = await excel_tool.save_workbook(
            path="//test/test_output.xlsx"
        )
        result_data = json.loads(result)
        print(f"Result: {result_data}")
        
        if result_data.get('success'):
            print("✅ Save workbook test passed")
            
            # Check if file was actually created
            file_path = Path(temp_dir) / "test.xlsx"
            if file_path.exists():
                print(f"✅ File created successfully: {file_path}")
                print(f"📏 File size: {file_path.stat().st_size} bytes")
            else:
                print("❌ File was not created")
                return False
        else:
            print(f"❌ Save workbook test failed: {result_data.get('error')}")
            return False
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"🧹 Cleaned up temp directory: {temp_dir}")

async def test_business_logic_components():
    """Test the business logic components independently."""
    print("\n🔧 Testing Business Logic Components...")
    
    try:
        # Test WorkbookManager
        print("\n📊 Testing WorkbookManager")
        from tools.excel.business_logic.workbook_manager import WorkbookManager
        
        workbook_manager = WorkbookManager()
        result = workbook_manager.create_workbook()
        
        if result.success:
            print("✅ WorkbookManager create_workbook passed")
        else:
            print(f"❌ WorkbookManager create_workbook failed: {result.error}")
            return False
        
        # Test ConcurrencyManager  
        print("\n🔄 Testing ConcurrencyManager")
        from tools.excel.business_logic.concurrency_manager import ConcurrencyManager
        
        concurrency_manager = ConcurrencyManager()
        reservation_result = await concurrency_manager.reserve_rows(
            row_count=10,
            sheet_name="TestSheet", 
            current_max_row=5
        )
        
        if reservation_result.success:
            print("✅ ConcurrencyManager reserve_rows passed")
        else:
            print(f"❌ ConcurrencyManager reserve_rows failed: {reservation_result.error}")
            return False
        
        # Test ExcelOperations
        print("\n📝 Testing ExcelOperations") 
        from tools.excel.business_logic.excel_operations import ExcelOperations
        
        excel_operations = ExcelOperations()
        # This would need a real workbook to test fully, but we can test object creation
        print("✅ ExcelOperations created successfully")
        
        print("\n🎉 Business logic component tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Business logic test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting Excel Tool Refactoring Tests\n")
    
    # Test business logic components first
    bl_success = await test_business_logic_components()
    
    if not bl_success:
        print("❌ Business logic tests failed - stopping")
        return False
    
    # Test integrated tool
    tool_success = await test_excel_tool()
    
    if bl_success and tool_success:
        print("\n🎉 All tests passed! Refactored Excel tool is working properly.")
        return True
    else:
        print("\n❌ Some tests failed - refactored Excel tool needs attention.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)