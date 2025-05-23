# Weather Tool Tests - Two-Level Testing Strategy

## Testing Philosophy

This weather tool uses a **two-level testing strategy** that provides both fast feedback and realistic validation:

### **Component Tests** (`test_weather_component.py`)
- **Purpose**: Test the Weather class as an isolated component
- **Scope**: Weather class functionality with real API calls
- **Benefits**: Fast feedback, isolated testing, validate data processing
- **What it tests**:
  - `Weather.get_formatted_weather_data()` directly
  - Data formatting, JSON structure, error handling
  - Weather class behavior with external API calls

### **Integration Tests** (`test_weather_integration.py`)
- **Purpose**: Test the complete user-facing tool interface
- **Scope**: WeatherTools → Weather class → external API (end-to-end)
- **Benefits**: Realistic validation, tests actual user experience
- **Uses**: Enhanced debug_tool with centralized configuration loading
- **Configuration**: Automatically loads .env and .local_workspaces.json from agent_c base directory
- **What it tests**:
  - `WeatherTools.get_current_weather()` via debug_tool
  - Complete tool interface workflow
  - Tool delegation and parameter handling

## Running Tests

### Prerequisites
```bash
pip install -r test-requirements.txt
```

### Run All Tests (Recommended)
```bash
python run_tests.py
# or
python run_tests.py all
```

### Run Specific Test Types
```bash
# Component tests only (fast)
python run_tests.py component

# Integration tests only (complete validation)
python run_tests.py integration
```

### Run with pytest directly
```bash
# All tests
pytest -v

# Specific test files
pytest test_weather_component.py -v
pytest test_weather_integration.py -v

# By test markers (recommended)
pytest -m component -v      # Component tests only
pytest -m integration -v    # Integration tests only

# Combine markers
pytest -m "component or integration" -v  # All tests
```

## What Each Test Level Validates

### **Component Tests** ✅
- Weather class methods work correctly
- Data formatting produces valid JSON
- Error handling with invalid locations
- Data consistency between raw and formatted responses
- Different locale and unit configurations

### **Integration Tests** ✅
- Tool interface accepts parameters correctly
- Tool delegates to Weather class properly
- Complete end-to-end workflow functions
- Tool error handling and parameter validation
- Real user experience validation

## Test Strategy Benefits

### **Fast Development Workflow**
1. **Component tests** provide quick feedback during development
2. **Integration tests** provide confidence before deployment

### **Comprehensive Coverage**
- **Component level**: Validates business logic works correctly
- **Integration level**: Validates user interface works correctly

### **Realistic Testing**
- Both levels make real API calls (no mocking)
- Tests validate actual functionality users experience
- Catches real issues with external dependencies

## Notes

- **Real API calls**: Both test levels make actual calls to weather service
- **Internet required**: Tests need connectivity to function
- **Rate limits**: Some tests may fail due to API rate limiting
- **Network issues**: Occasional failures due to network connectivity

## Example Test Output

```bash
🧪 Running Weather Tool Tests (Component + Integration)...
=================== Running test_weather_component.py ===================
test_weather_component.py::TestWeatherClientComponent::test_get_formatted_weather_data_real_location PASSED
test_weather_component.py::TestWeatherClientComponent::test_get_formatted_weather_data_invalid_location PASSED
✅ Tests in test_weather_component.py passed!

=================== Running test_weather_integration.py ===================
test_weather_integration.py::TestWeatherToolsIntegration::test_weather_tool_real_location PASSED
test_weather_integration.py::TestWeatherToolsIntegration::test_weather_tool_invalid_location PASSED
✅ Tests in test_weather_integration.py passed!

🎉 All all tests passed!
```

This testing strategy ensures both **fast development feedback** and **realistic end-to-end validation**!
