# v2 API Implementation Step 6.1: Debug Endpoints - Detailed Plan

## Overview

This plan outlines the implementation of debug endpoints for the v2 API. These endpoints provide detailed information about sessions and agent state for development and troubleshooting purposes. The implementation will follow RESTful principles while leveraging the existing debug functionality in the agent_manager.

## Current State

The v1 API currently has two debug endpoints:
1. `/api/v1/debug_agent_state/{ui_session_id}` - Shows the state of an agent and its components
2. `/api/v1/chat_session_debug/{ui_session_id}` - Provides general session debugging information

These endpoints are not designed in a RESTful manner and are scattered within other API modules. In v2, we will consolidate these into a dedicated debug module with proper RESTful paths.

## What We're Changing

We'll implement two new RESTful debug endpoints in the v2 API:

1. `GET /api/v2/debug/sessions/{session_id}` - Provides comprehensive session debugging information
2. `GET /api/v2/debug/agent/{session_id}` - Provides detailed information about the agent's state

These endpoints will reuse the existing debugging logic from the agent_manager but with improved response models and error handling.

## How We're Changing It

### 1. Create Debug Models

Create Pydantic models to standardize the debug endpoint responses, making the API more consistent and the responses more predictable.

### 2. Implement Debug Module

Create a dedicated debug module (`debug.py`) with the two endpoints that leverage the existing agent_manager debugging capabilities but with improved error handling and response formatting.

### 3. Router Integration

Update the debug module's `__init__.py` to include the new debug router, making the endpoints available in the API.

### 4. Create Comprehensive Tests

Implement thorough tests to ensure the debug endpoints function correctly in various scenarios.

## Why We're Changing It

1. **Improved Organization**: Dedicated debug module provides better code organization
2. **RESTful Design**: New endpoints follow RESTful principles with resource-oriented URLs
3. **Standardized Responses**: Pydantic models ensure consistent response formats
4. **Enhanced Error Handling**: Properly handle and communicate errors to clients
5. **Better Documentation**: OpenAPI annotations provide clear documentation

## Implementation Tasks

### 1. Create Debug Models

- Create models for session debug information
- Create models for agent debug information
- Include proper typing and documentation

### 2. Create Debug Module

- Create `debug.py` with session and agent debug endpoints
- Implement proper error handling
- Add OpenAPI documentation annotations
- Add authorization checks for these sensitive endpoints

### 3. Update Router Configuration

- Update `debug/__init__.py` to include the debug router

### 4. Create Tests

- Create test file at `tests/v2/debug/test_debug.py`
- Implement tests for both endpoints
- Test error handling for non-existent sessions
- Test authorization checks

## Technical Details

### Response Models

- **SessionDebugInfo**: Comprehensive session information including chat history statistics
- **AgentDebugInfo**: Details about agent configuration, state, and tool availability

### Error Handling

- 404 Not Found: When session ID doesn't exist
- 403 Forbidden: When authorization checks fail (if implemented)
- 500 Internal Server Error: For unexpected errors during debug info retrieval

### Testing Focus Areas

- Verify all expected fields are present in responses
- Ensure error handling works correctly
- Verify compatibility with the existing agent_manager debugging methods

## Implementation Process

1. Create debug models
2. Implement debug endpoints
3. Create comprehensive tests
4. Update router integration
5. Verify functionality with manual testing

## Code Components

### Files to Create

1. `src/agent_c_api/api/v2/debug/debug.py` - Main debug module
2. `src/agent_c_api/tests/v2/debug/test_debug.py` - Tests for debug endpoints

### Files to Modify

1. `src/agent_c_api/api/v2/debug/__init__.py` - Update to include debug router

## Dependencies and Requirements

- Existing agent_manager.debug_session method
- FastAPI and Pydantic for endpoint and model definitions
- Properly configured test environment for debug endpoint testing