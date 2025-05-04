# Phase 7.1: API Router Integration Plan

## Overview

This step involves integrating all v2 routers into the main application to bring all components together into a unified API. We need to ensure all implemented resource routers are properly included in the v2 API router and that the routing and error handling are correctly configured.

## Current State

Based on our review, we've already:

1. Implemented configuration endpoints in `v2/config/`
2. Implemented session management in `v2/sessions/`
3. Implemented debug endpoints in `v2/debug/`
4. Created the history directory but the router is still commented out in the v2 `__init__.py`

The v2 router is already included in the main API router in `api/__init__.py`, but we need to ensure all implemented resource routers are correctly included in the v2 router.

## What We're Changing

We need to:

1. Check that all implemented sub-routers are correctly imported and included in the v2 router
2. Uncomment the history router if it has been implemented
3. Ensure consistent prefix patterns across all v2 endpoints
4. Check that error handling is consistent across all v2 endpoints
5. Test that all routes are properly registered and accessible

## How We're Changing It

1. **Update the v2 API `__init__.py`**:
   - Review all available routers (config, sessions, history, debug)
   - Ensure all implemented routers are properly imported and included
   - Uncomment history router if it's ready
   - Verify proper prefix structure for all routers

2. **Verify Router Registration**:
   - Create a simple debugging utility to list all registered routes
   - Confirm all expected v2 routes are properly registered

3. **Implement Consistent Error Handling**:
   - Ensure that all v2 endpoints use the standard APIResponse wrapper
   - Verify that error responses use appropriate HTTP status codes
   - Check that error messages follow a consistent format

## Why We're Changing It

1. **Unified API Experience**: All components should be accessible through a cohesive API structure
2. **Consistent Routing Pattern**: Ensures a predictable URL structure for API clients
3. **Complete Implementation**: Brings together all the individually implemented components
4. **Proper Error Handling**: Provides a consistent experience for error handling and reporting

## Implementation Tasks

1. Update `//api/src/agent_c_api/api/v2/__init__.py` to include all implemented routers
2. Create a simple utility to verify route registration (can be a temporary test script)
3. Test all routes to ensure they're accessible and working as expected
4. Document any issues or inconsistencies found during testing

## Testing Approach

1. **Manual Testing**:
   - Verify each v2 endpoint is accessible through the correct path
   - Test error handling by triggering error conditions (e.g., invalid session IDs)
   - Check response formats for consistency

2. **Automated Testing**:
   - Use existing test files to verify router integration
   - Add integration tests for router paths if needed

## Risks and Mitigations

- **Risk**: Some routes may have path conflicts or inconsistent prefix patterns
  - **Mitigation**: Carefully check all route prefixes and paths to ensure uniqueness and consistency

- **Risk**: Error handling may vary across different resource routers
  - **Mitigation**: Review error handling in all routers to ensure consistent patterns

- **Risk**: Some routers might be imported but not fully implemented
  - **Mitigation**: Only enable routers that have completed implementation and testing

## Delivery Criteria

1. Updated `v2/__init__.py` with all correctly included routers
2. Verification that all routes are properly registered
3. Consistent error handling across all v2 endpoints
4. Documentation of any issues or inconsistencies found during testing