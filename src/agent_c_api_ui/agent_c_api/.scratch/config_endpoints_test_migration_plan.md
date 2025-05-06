# Config Endpoints Test Migration Plan

## Target Files

- **Source:** `//api/src/agent_c_api/tests/v2/config/test_endpoints.py`
- **Destination:** `//api/tests/unit/api/v2/config/test_endpoints.py`

## Migration Goals

1. Maintain all existing test functionality
2. Improve organization and readability
3. Add proper pytest markers
4. Enhance documentation
5. Fill gaps in test coverage

## Class Structure Design

Organize tests into classes by endpoint type:

```python
@pytest.mark.unit
@pytest.mark.config
@pytest.mark.endpoints
class TestConfigEndpoints:
    """Base class for common test functionality"""
    
    # Common setup or utility methods

@pytest.mark.unit
@pytest.mark.config
@pytest.mark.endpoints
class TestModelEndpoints(TestConfigEndpoints):
    """Tests for model configuration endpoints"""
    
    # Model endpoint tests

@pytest.mark.unit
@pytest.mark.config
@pytest.mark.endpoints
class TestPersonaEndpoints(TestConfigEndpoints):
    """Tests for persona configuration endpoints"""
    
    # Persona endpoint tests

@pytest.mark.unit
@pytest.mark.config
@pytest.mark.endpoints
class TestToolEndpoints(TestConfigEndpoints):
    """Tests for tool configuration endpoints"""
    
    # Tool endpoint tests

@pytest.mark.unit
@pytest.mark.config
@pytest.mark.endpoints
class TestSystemConfigEndpoint(TestConfigEndpoints):
    """Tests for the combined system configuration endpoint"""
    
    # System config endpoint tests
```

## Test Method Organization

Each test method should focus on a specific aspect:

- `test_[endpoint]_success` - Tests successful response
- `test_[endpoint]_not_found` - Tests 404 error response
- `test_[endpoint]_with_[filter]` - Tests filtered response
- `test_[endpoint]_error` - Tests error handling

## Additional Test Cases

Add the following missing test cases:

1. **Models list error** - Test error handling for the models list endpoint
2. **Personas list error** - Test error handling for the personas list endpoint
3. **Tools list error** - Test error handling for the tools list endpoint

## Fixture Usage

Use the following fixtures from conftest.py:

- `client` - For making requests to the API
- `mock_config_service` - For mocking the ConfigService

Ensure appropriate patching of the dependency injection using:

```python
@pytest.fixture
def mock_router_config_service(mock_config_service):
    with patch('agent_c_api.api.v2.config.router.get_config_service') as mock_service_factory:
        mock_service_factory.return_value = mock_config_service
        yield mock_config_service
```

## Expected Test Count

| Endpoint Group | Current Tests | Planned Tests | Notes |
|----------------|---------------|---------------|-------|
| Models | 3 | 4 | Add error case for list endpoint |
| Personas | 3 | 4 | Add error case for list endpoint |
| Tools | 4 | 5 | Add error case for list endpoint |
| System Config | 2 | 2 | No additional tests needed |
| **Total** | **12** | **15** | **+3 new tests** |

## Migration Steps

1. **Create New File Structure**
   - Create the new file with imports and class structure
   - Add appropriate markers
   - Add comprehensive docstrings

2. **Migrate Existing Tests**
   - Move each test to the appropriate class
   - Update assertions to maintain test coverage
   - Improve variable naming and comments

3. **Add Missing Tests**
   - Implement the 3 additional error case tests
   - Ensure they use the same patterns as existing tests

4. **Verify Test Logic**
   - Double check that the test logic is maintained
   - Verify that all service calls are correctly mocked
   - Ensure proper verification of responses

5. **Run Tests**
   - Verify that all tests pass
   - Check for any regressions or issues

## Potential Challenges

1. **Fixture Integration** - Ensure the existing fixtures work correctly with the new test structure
2. **Error Simulation** - Properly simulate error conditions for the new test cases
3. **TestClient Usage** - Maintain proper use of the TestClient within the class structure

## Expected Outcome

A well-structured, well-documented test file that:

- Maintains all existing test coverage
- Adds missing test cases
- Uses proper organization and documentation
- Follows pytest best practices
- Works with the existing fixtures