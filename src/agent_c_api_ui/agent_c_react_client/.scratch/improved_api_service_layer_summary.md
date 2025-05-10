# Improved API Service Layer for v2 API

## Overview

We have designed an improved API service layer to work with the new v2 RESTful API. The service layer maintains the same basic structure as our current implementation but with updated endpoints, parameter handling, and response processing to match the v2 API specifications.

## Design Approach

### 1. Base API Service

We've updated the base API service (`api_v2.js`) to support the v2 API:

- Updated base URL to use the v2 endpoint ('/api/v2')
- Added `extractResponseData` utility to handle the standard response format
- Enhanced error handling for the v2 error format
- Added support for pagination in GET requests
- Added PATCH method for partial updates

### 2. Domain-Specific Services

We've organized the API into domain-specific services that align with the v2 API's resource-oriented approach:

**Config API Service** (`config-api.js`):
- System configuration resources (/config/*)
- Models, personas, and tools information
- Consolidated system configuration

**Session API Service** (`session-api.js`):
- Session management (create, get, list, update, delete)
- Agent configuration
- Tool configuration management

**Chat API Service** (`chat-api.js`):
- Message handling with structured content
- File upload, management, and attachment
- Chat generation control

**History API Service** (`history-api.js`):
- Session history listing and details
- Event retrieval and streaming
- Replay controls

**Debug API Service** (`debug-api.js`):
- Session debugging information
- Agent state inspection

### 3. Backward Compatibility

To maintain backward compatibility during the transition period, we've created adapter functions (`v1-api-adapters.js`) that:

- Accept v1 parameter formats and convert them to v2 format
- Call the v2 API services
- Transform responses back to v1 format expected by existing components

## Implementation Files

1. **Base API Service**: `api_v2.js`
2. **Config API Service**: `config-api.js`
3. **Session API Service**: `session-api.js`
4. **Chat API Service**: `chat-api.js`
5. **History API Service**: `history-api.js`
6. **Debug API Service**: `debug-api.js`
7. **Combined Export**: `services-index.js`
8. **v1 Compatibility Adapters**: `v1-api-adapters.js`

## Notable Changes from v1 to v2

### 1. Endpoint Structure

- Resource-oriented endpoints (e.g., `/sessions/{id}` vs. multiple endpoint patterns)
- Consistent use of HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Logical grouping of related functionality

### 2. Response Format

- Standard response wrapper: `{ data, meta, errors }`
- Pagination information in `meta` for list endpoints
- Consistent error format with detailed information

### 3. Parameter Naming

- Consistent naming: `model_id` vs. `model_name`, `persona_id` vs. `persona_name`
- RESTful URL parameters instead of body parameters where appropriate

### 4. Streaming Format

- Structured JSON events instead of raw text chunks
- Event typing for different content types (text, tool calls, etc.)
- More detailed event information

## Migration Strategy

We recommend a phased approach for implementing this service layer:

### Phase 1: Foundational Infrastructure

1. Implement the core API service with error handling
2. Create TypeScript interfaces (if using TypeScript)
3. Implement config service to replace parts of model, persona, and tools APIs

### Phase 2: Key Services Implementation

1. Implement session service with agent configuration
2. Implement chat service with updated message format
3. Implement file management functionality

### Phase 3: Extended Functionality

1. Implement history service for event access
2. Implement debug service for diagnostics
3. Create combined service exports

### Phase 4: Component Integration

1. Create v1 compatibility adapters
2. Update component imports to use appropriate services
3. Test and validate functionality
4. Gradually replace v1 API usage with v2

## Conclusion

The improved API service layer provides a more structured, maintainable approach to interacting with the v2 API. By leveraging resource-oriented endpoints, consistent response formats, and proper error handling, we'll be able to build a more robust application that takes full advantage of the new API capabilities.

The adapter pattern provides a smooth transition path, allowing components to be migrated incrementally without disrupting the entire application.