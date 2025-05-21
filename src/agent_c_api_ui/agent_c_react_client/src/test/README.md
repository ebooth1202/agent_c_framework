# Agent C React UI Testing Guide

## Testing Setup

This project uses the following testing stack:

- **Vitest**: A fast test runner built on top of Vite
- **Testing Library**: For testing React components
- **Custom Fetch Mocking**: For API service testing

## Running Tests

```bash
# Run all tests once
npm test

# Run tests in watch mode (during development)
npm run test:watch

# Run tests with coverage reporting
npm run test:coverage
```

## Test Structure

Tests are organized alongside the code they test, with a `.test.js` or `.spec.js` extension.

### Service Tests

API service tests are located in `src/services` with the same name as the service file but with a `.test.js` extension.

Example: `src/services/config-api.test.js` tests `src/services/config-api.js`.

## API Service Testing

### Fetch Mocking

APIy service tests use the utilities in `src/test/utils/api-test-utils.js` to mock the fetch function:

```javascript
import { setupFetchMock, setupNetworkErrorMock } from '../test/utils/api-test-utils';

describe('Your API Service', () => {
  let restoreFetch;

  afterEach(() => {
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
  });

  it('should fetch data successfully', async () => {
    // Setup fetch mock
    restoreFetch = setupFetchMock({
      '/your/endpoint': { success: true, data: { result: 'success' } }
    });

    // Call API and test result
    const result = await apiService.yourMethod();
    expect(result).toEqual({ result: 'success' });
  });
});
```

### Testing Utilities

Utility functions for testing API services in `src/test/utils/api-test-utils.js`:

- `setupFetchMock(mockResponses)`: Create fetch mocks for specified URL patterns
- `setupNetworkErrorMock(message)`: Mock a network error response

## Best Practices

1. **Test Isolation**: Each test should be independent. Clean up mocks after each test.

2. **Arrange-Act-Assert**: Structure tests using the AAA pattern:
   - Arrange: Set up test conditions and mocks
   - Act: Execute the code being tested
   - Assert: Verify the results

3. **Test Behaviors, Not Implementation**: Focus on testing what the code does, not how it does it.

4. **Mock Only What's Necessary**: Only mock the fetch function, not the entire API module.

5. **Comprehensive Coverage**: Test happy paths, error cases, and edge cases.

## Example Test

```javascript
import { describe, it, expect, afterEach } from 'vitest';
import * as myApi from './my-api';
import { setupFetchMock, setupNetworkErrorMock } from '../test/utils/api-test-utils';

describe('My API Service', () => {
  let restoreFetch;

  afterEach(() => {
    if (restoreFetch) {
      restoreFetch();
      restoreFetch = null;
    }
  });

  it('should fetch data successfully', async () => {
    // Arrange: Set up mock response
    const mockData = { success: true, data: { items: [1, 2, 3] } };
    restoreFetch = setupFetchMock({
      '/some/endpoint': mockData
    });

    // Act: Call the API method
    const result = await myApi.fetchSomeData();

    // Assert: Verify results
    expect(result).toEqual(mockData.data);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it('should handle errors', async () => {
    // Arrange: Set up error response
    restoreFetch = setupFetchMock({
      '/some/endpoint': {
        detail: { message: 'Server error' },
        status: 500
      }
    });

    // Act & Assert: Verify the API call throws the expected error
    await expect(myApi.fetchSomeData()).rejects.toThrow('Server error');
  });
});
```