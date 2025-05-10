# API Service Layer Improvements - Phase 1, Step 1

## Changes to `api.js`

### 1. Updated API Base URL

- Changed the default base URL from `/api/v1` to `/api/v2` in `API_CONFIG`
- This ensures all API requests will target the v2 endpoints by default

```javascript
export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_URL || '/api/v2',  // Updated from v1 to v2
  timeout: DEFAULT_TIMEOUT,
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  },
};
```

### 2. Added `extractResponseData` Utility Function

- Created a new utility function to handle the standardized v2 response format
- Extracts `data`, `meta`, and `errors` fields from the response
- Falls back to returning the entire response as data if it doesn't match the expected format

```javascript
export function extractResponseData(response) {
  // Handle v2 API standard response format
  if (response && typeof response === 'object') {
    return {
      data: response.data !== undefined ? response.data : response,
      meta: response.meta || {},
      errors: response.errors || []
    };
  }
  
  // Return the response itself for endpoints that don't follow the standard format
  return { data: response, meta: {}, errors: [] };
}
```

### 3. Enhanced Error Handling

- Updated `processApiError` to handle the v2 API error format
- Added support for extracting detailed error information from the v2 response structure
- Preserved the error object's compatibility with existing code

```javascript
// Extract v2 API specific error format
if (responseData && responseData.detail) {
  const detail = responseData.detail;
  if (detail.message) {
    errorMessage = detail.message;
  }
  errorDetails = {
    error: detail.error,
    error_code: detail.error_code,
    params: detail.params
  };
}
```

### 4. Added Pagination Support for GET Requests

- Enhanced the `get` function to handle pagination parameters
- Added support for query parameters via the `params` option
- Properly formats and appends parameters to the request URL

```javascript
export function get(endpoint, options = {}) {
  // Extract pagination parameters if present
  const { params, ...restOptions } = options;
  
  // If pagination parameters are provided, add them to the query string
  if (params) {
    const queryParams = new URLSearchParams();
    
    // Add pagination parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryParams.append(key, value);
      }
    });
    
    // Append query string to endpoint if there are parameters
    const queryString = queryParams.toString();
    if (queryString) {
      endpoint = `${endpoint}${endpoint.includes('?') ? '&' : '?'}${queryString}`;
    }
  }
  
  return apiRequest(endpoint, { 
    method: 'GET', 
    ...restOptions 
  });
}
```

### 5. Added PATCH Method

- Added a dedicated `patch` function for PATCH requests
- This supports the RESTful update operations used in the v2 API

```javascript
export function patch(endpoint, data, options = {}) {
  return apiRequest(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
    ...options,
  });
}
```

### 6. Updated Error Message Extraction

- Enhanced error message extraction to look for v2 API's nested error format
- Updated the error message extraction in apiRequest to handle both v1 and v2 formats

```javascript
const error = new Error(
  errorData?.detail?.message || errorData?.message || `Request failed with status ${response.status}`
);
```

### 7. Updated Exports

- Added new functions to the default export object
- Included the new `extractResponseData` function and `patch` method

```javascript
export default {
  get,
  post,
  put,
  patch,  // New method
  delete: del,
  uploadFile,
  downloadFile,
  apiRequest,
  processApiError,
  showErrorToast,
  extractResponseData,  // New utility
  API_CONFIG,
};
```

## Additional Information

These changes form the foundation for the v2 API integration. The updated `api.js` file is now equipped to handle the standardized v2 response format, improved error reporting, and pagination support that will be used throughout the rest of the API service layer implementation.

Next steps will involve creating or updating specific service modules for different API resources.