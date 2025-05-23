# Agent C Tools - Testing Guide

## Two-Level Testing Strategy

This guide explains how to implement **component tests** and **integration tests** for Agent C tools using our proven testing architecture.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Component Tests](#component-tests)
3. [Integration Tests](#integration-tests)
4. [Test Setup and Configuration](#test-setup-and-configuration)
5. [Running Tests](#running-tests)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

---

## Testing Philosophy

### **Two-Level Testing Strategy**

We use a **two-level approach** that provides both fast feedback and realistic validation:

#### **Component Tests** 🏗️
- **Purpose**: Test business logic classes/functions in isolation
- **Scope**: Individual classes with real external API calls
- **Benefits**: Fast feedback, isolated testing, validate data processing
- **Speed**: Fast (seconds)

#### **Integration Tests** 🔗
- **Purpose**: Test complete user-facing tool interface 
- **Scope**: Tool class → Business logic → External APIs (end-to-end)
- **Benefits**: Realistic validation, tests actual user experience
- **Speed**: Moderate (10-30 seconds)

### **What We Don't Test** ❌

- **Tool classes directly** - They're just 3 lines of delegation
- **Mocked scenarios** - They prove nothing about real functionality
- **Internal implementation details** - We test behavior, not internals

### **Why This Works**

- **Component tests** give you fast feedback during development
- **Integration tests** give you confidence that users get what they expect
- **No mocking** means tests catch real issues
- **Focused scope** means tests are maintainable and meaningful

---

## Component Tests

Component tests validate that your business logic classes work correctly with real external dependencies.

### **What Component Tests Validate** ✅

- Business logic functions/methods work correctly
- Data formatting produces valid output
- Error handling with invalid inputs
- Data consistency and type validation
- Different configuration options

### **Component Test Structure**

```python
"""
Component tests for the [domain] functionality.
These tests call the [BusinessClass] directly to validate its functionality.
"""
import pytest
import json
from datetime import date
import sys
import os

# Add parent directory to import your business logic
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from your_business_module import YourBusinessClass


class TestYourBusinessClassComponent:
    """Component tests for YourBusinessClass that test real functionality."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.business_client = YourBusinessClass(config='test_config')
    
    @pytest.mark.component
    @pytest.mark.asyncio
    async def test_main_functionality_success(self):
        """Test successful operation with valid input."""
        input_data = "valid_test_input"
        
        result = await self.business_client.process_for_tool(input_data)
        
        # Validate it's not an error
        assert not result.startswith("Error:")
        
        # Parse and validate JSON structure
        parsed_result = json.loads(result)
        assert "expected_field" in parsed_result
        
        # Validate data types and ranges
        assert isinstance(parsed_result["expected_field"], str)
        # Add more specific validations
    
    @pytest.mark.component 
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling with invalid input."""
        invalid_input = "invalid_test_input"
        
        result = await self.business_client.process_for_tool(invalid_input)
        
        # Should return error message
        assert result.startswith("Error:")
        assert "meaningful error description" in result.lower()
    
    @pytest.mark.component
    @pytest.mark.asyncio  
    async def test_different_configurations(self):
        """Test with different configuration options."""
        different_client = YourBusinessClass(config='different_config')
        
        result = await different_client.process_for_tool("test_input")
        
        # Validate configuration affects output appropriately
        if not result.startswith("Error:"):
            parsed = json.loads(result)
            # Add configuration-specific validations
    
    def test_initialization(self):
        """Test class initialization with different parameters."""
        # Test various initialization combinations
        clients = [
            YourBusinessClass(),  # defaults
            YourBusinessClass(config='custom'),
            YourBusinessClass(param1='value1', param2='value2')
        ]
        
        for client in clients:
            assert hasattr(client, 'expected_attribute')
            # Add more initialization validations


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### **Weather Tool Component Test Example**

```python
class TestWeatherClientComponent:
    def setup_method(self):
        self.weather_client = Weather(locale='en', unit='imperial')
    
    @pytest.mark.component
    @pytest.mark.asyncio
    async def test_get_formatted_weather_data_real_location(self):
        result = await self.weather_client.get_formatted_weather_data("New York")
        
        assert not result.startswith("Error getting weather:")
        
        weather_data = json.loads(result)
        assert "currently" in weather_data
        
        currently = weather_data["currently"]
        assert isinstance(currently["current_temperature"], int)
        assert 0 <= currently["humidity"] <= 100
```

---

## Integration Tests

Integration tests validate that the complete tool interface works correctly using the debug_tool.

### **What Integration Tests Validate** ✅

- Tool interface accepts parameters correctly
- Tool delegates to business logic properly  
- Complete end-to-end workflow functions
- Tool error handling and parameter validation
- Real user experience validation

### **Integration Test Structure**

```python
"""
Integration tests for the [tool_name] tool using debug_tool.
These tests call the actual [ToolClass] interface that users interact with.
"""
import pytest
import json
import sys
import os

# Add the tool_debugger directory to the path
tool_debugger_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
    'tool_debugger'
)
sys.path.insert(0, tool_debugger_path)

from debug_tool import ToolDebugger


class TestYourToolsIntegration:
    """Integration tests for YourTools that test the complete user interface."""
    
    def setup_method(self):
        self.debugger = None
    
    def teardown_method(self):
        if self.debugger:
            # Clean up any resources if needed
            pass
    
    async def setup_tool(self):
        """Helper method to set up the tool for testing."""
        # ToolDebugger automatically loads .env and .local_workspaces.json 
        self.debugger = ToolDebugger(init_local_workspaces=False)
        await self.debugger.setup_tool(
            tool_import_path='agent_c_tools.YourTools',
            tool_opts={}  # Config loaded automatically from .env
        )
        return self.debugger
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_main_functionality(self):
        """Test main functionality through the tool interface."""
        debugger = await self.setup_tool()
        
        # Call the tool through its actual interface
        results = await debugger.run_tool_test(
            tool_name='your_tool_method_name',
            tool_params={'param1': 'test_value'}
        )
        
        # Extract and validate content
        content = debugger.extract_content_from_results(results)
        assert content is not None
        assert not content.startswith("Error:")
        
        # Parse and validate structure
        structured_content = debugger.extract_structured_content(results)
        assert structured_content is not None
        assert "expected_field" in structured_content
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test error handling through the tool interface."""
        debugger = await self.setup_tool()
        
        # Call with invalid parameters
        results = await debugger.run_tool_test(
            tool_name='your_tool_method_name',
            tool_params={'param1': 'invalid_value'}
        )
        
        # Should get an error message
        content = debugger.extract_content_from_results(results)
        assert content is not None
        assert content.startswith("Error:")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self):
        """Test parameter handling through tool interface."""
        debugger = await self.setup_tool()
        
        # Test missing parameters
        results = await debugger.run_tool_test(
            tool_name='your_tool_method_name',
            tool_params={}  # Missing required parameters
        )
        
        content = debugger.extract_content_from_results(results)
        assert content is not None
        # Should handle missing parameters gracefully
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_tool_availability(self):
        """Test that the tool is properly set up and available."""
        debugger = await self.setup_tool()
        
        # Check that the tool is available
        available_tools = debugger.get_available_tool_names()
        assert 'your_tool_method_name' in available_tools
        
        # Optionally print debug info
        debugger.print_tool_info()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### **Weather Tool Integration Test Example**

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_weather_tool_real_location(self):
    debugger = await self.setup_weather_tool()
    
    results = await debugger.run_tool_test(
        tool_name='get_current_weather',
        tool_params={'location_name': 'New York'}
    )
    
    content = debugger.extract_content_from_results(results)
    assert not content.startswith("Error getting weather:")
    
    structured_content = debugger.extract_structured_content(results)
    assert "currently" in structured_content
```

---

## Test Setup and Configuration

### **Directory Structure**

```
your_tool/
├── tool.py                     # Tool interface
├── business_logic.py           # Business logic (or util/ directory)
└── tests/                      # All test files
    ├── test_business_component.py   # Component tests
    ├── test_tool_integration.py     # Integration tests
    ├── pytest.ini                   # Test configuration
    ├── run_tests.py                 # Test runner
    ├── test-requirements.txt        # Test dependencies
    └── README.md                    # Test documentation
```

### **pytest.ini Configuration**

```ini
[pytest]
testpaths = .
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers --strict-config --disable-warnings
markers =
    asyncio: marks tests as async
    component: component tests that test individual classes in isolation
    integration: integration tests that test complete workflows end-to-end
    slow: marks tests as slow running
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

### **test-requirements.txt**

```txt
# Test requirements
pytest>=7.0.0
pytest-asyncio>=0.21.0

# For integration tests using debug_tool
python-dotenv>=1.0.0
```

### **Test Runner Script**

```python
#!/usr/bin/env python3
"""
Test runner for [tool_name] - runs both component and integration tests.
"""
import subprocess
import sys
import os

def run_tests(test_type="all"):
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tests_dir)
    
    try:
        if test_type == "component":
            pytest_args = [sys.executable, "-m", "pytest", "-v", "-m", "component"]
        elif test_type == "integration":
            pytest_args = [sys.executable, "-m", "pytest", "-v", "-m", "integration"]  
        else:  # all
            pytest_args = [sys.executable, "-m", "pytest", "-v"]
        
        result = subprocess.run(pytest_args, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("\\nSTDERR:") 
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error running tests: {e}")
        return False

if __name__ == "__main__":
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    success = run_tests(test_type)
    sys.exit(0 if success else 1)
```

---

## Running Tests

### **Install Dependencies**

```bash
cd your_tool/tests
pip install -r test-requirements.txt
```

### **Run All Tests**

```bash
# Using test runner (recommended)
python run_tests.py

# Using pytest directly
pytest -v
```

### **Run Specific Test Types**

```bash
# Component tests only (fast feedback)
python run_tests.py component
pytest -m component -v

# Integration tests only (end-to-end validation)  
python run_tests.py integration
pytest -m integration -v
```

### **Run Individual Test Files**

```bash
pytest test_business_component.py -v
pytest test_tool_integration.py -v
```

---

## Best Practices

### **Component Test Best Practices** ✅

1. **Test real functionality** - Make actual API calls, don't mock everything
2. **Validate data structure** - Check JSON format, data types, required fields
3. **Test error scenarios** - Invalid inputs, network issues, API errors
4. **Test configuration options** - Different settings, parameters, modes
5. **Keep tests focused** - One concept per test method

### **Integration Test Best Practices** ✅

1. **Test user experience** - What users actually call and expect
2. **Use debug_tool properly** - Let it handle configuration loading
3. **Test complete workflows** - End-to-end scenarios
4. **Validate tool interface** - Parameter handling, error responses
5. **Test tool availability** - Ensure tools are registered correctly

### **General Testing Best Practices** ✅

1. **Use descriptive test names** - `test_weather_data_with_invalid_location`
2. **Add pytest marks** - `@pytest.mark.component` / `@pytest.mark.integration`
3. **Handle flaky tests** - Skip tests that fail due to network issues
4. **Document test purpose** - Clear docstrings explaining what's being tested
5. **Keep tests maintainable** - Don't test implementation details

### **What NOT to Test** ❌

1. **Don't test tool classes directly** - They're just delegation
2. **Don't mock everything** - Defeats the purpose of validation
3. **Don't test internal details** - Test behavior, not implementation
4. **Don't create complex test setups** - Keep it simple and focused
5. **Don't duplicate component logic in integration tests** - Different purposes

---

## Troubleshooting

### **Common Issues**

#### **Tests Can't Import Modules**
```python
# Add this to your test files
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

#### **Debug Tool Can't Find agent_c Directory**
```python
# Specify path explicitly if auto-detection fails
debugger = ToolDebugger(
    init_local_workspaces=False,
    agent_c_base_path=r"C:\\path\\to\\agent_c"
)
```

#### **API Rate Limiting Issues**
```python
# Skip tests when API returns errors
if content.startswith("Error:") and "rate limit" in content.lower():
    pytest.skip("API rate limit reached, skipping test")
```

#### **Pytest Marks Not Recognized**
- Check `pytest.ini` has `[pytest]` section header (not `[tool:pytest]`)
- Ensure markers are properly defined in pytest.ini
- Use `pytest --markers` to see registered marks

### **Test Debugging Tips**

1. **Run single tests** - `pytest test_file.py::TestClass::test_method -v`
2. **Add print statements** - Temporary debugging with `print()` statements
3. **Use pytest fixtures** - For common setup/teardown
4. **Check test order** - Tests should be independent
5. **Validate test data** - Ensure test inputs are realistic

---

## Example: Complete Test Setup

See the **Weather Tool** in `tools/weather/tests/` for a complete example that demonstrates:

- ✅ Component tests for Weather class
- ✅ Integration tests using debug_tool
- ✅ Proper pytest configuration
- ✅ Test runner with marker support
- ✅ Clean test organization
- ✅ Real API validation
- ✅ Professional test output

This testing approach ensures your tools are **reliable, maintainable, and actually work**! 🧪✅

For more details, see:
- [Tool Debugger Guide](TOOL_DEBUGGER_GUIDE.md) - Manual debugging techniques
- [Migration Guide](MIGRATION_GUIDE.md) - Refactoring existing tools
- [Developer Guide](DEVELOPER_GUIDE.md) - Architecture principles
