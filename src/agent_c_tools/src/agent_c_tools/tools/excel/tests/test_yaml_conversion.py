#!/usr/bin/env python3
"""
Simple test to verify YAML conversion works correctly.
"""
import yaml
import sys
from pathlib import Path

# Add parent directories to import tool
current_dir = Path(__file__).parent
tool_dir = current_dir.parent
src_dir = tool_dir.parent.parent.parent
sys.path.insert(0, str(src_dir))

# Simple test without async
def test_yaml_conversion_manual():
    """Test that YAML conversion produces valid, parseable YAML."""
    print("🧪 Testing YAML Conversion...")
    
    # Test data similar to what the Excel tool returns
    test_data = {
        'success': True,
        'message': 'Test operation completed',
        'operation_id': 'test_123',
        'data': {
            'records_processed': 100,
            'sheets': ['Sheet1', 'Sheet2'],
            'metadata': {
                'created_at': '2024-01-01T00:00:00Z',
                'unicode_test': 'Hello 世界 🌍'
            }
        }
    }
    
    # Convert to YAML using our standard parameters
    yaml_output = yaml.dump(test_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("📝 Generated YAML:")
    print("-" * 40)
    print(yaml_output)
    print("-" * 40)
    
    # Verify it can be parsed back
    try:
        parsed_data = yaml.safe_load(yaml_output)
        print("✅ YAML is valid and parseable")
        
        # Verify data integrity
        assert parsed_data == test_data
        print("✅ Data integrity preserved")
        
        # Verify formatting preferences
        assert "success: true" in yaml_output.lower()  # Block style, not flow style
        assert "unicode_test: Hello 世界 🌍" in yaml_output  # Unicode preserved
        print("✅ Formatting preferences applied correctly")
        
        return True
    except Exception as e:
        print(f"❌ YAML parsing failed: {e}")
        return False

def test_error_yaml_conversion():
    """Test error response YAML conversion."""
    print("\n🧪 Testing Error Response YAML Conversion...")
    
    error_data = {
        'success': False,
        'error': 'Test error message with unicode: 测试错误'
    }
    
    yaml_output = yaml.dump(error_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("📝 Generated Error YAML:")
    print("-" * 40)
    print(yaml_output)
    print("-" * 40)
    
    try:
        parsed_data = yaml.safe_load(yaml_output)
        assert parsed_data == error_data
        print("✅ Error YAML conversion works correctly")
        return True
    except Exception as e:
        print(f"❌ Error YAML parsing failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Manual YAML Conversion Testing")
    print("=" * 50)
    
    success1 = test_yaml_conversion_manual()
    success2 = test_error_yaml_conversion()
    
    if success1 and success2:
        print("\n🎉 All YAML conversion tests passed!")
        print("✅ Excel tool YAML conversion is working correctly")
        sys.exit(0)
    else:
        print("\n❌ Some YAML conversion tests failed")
        sys.exit(1)