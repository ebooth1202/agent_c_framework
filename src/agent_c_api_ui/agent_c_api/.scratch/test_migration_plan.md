# Agent C API Test Migration Plan

## Overview

This plan outlines a systematic approach to migrate tests from the current structure (`src/agent_c_api/tests`) to the new structure (`tests/`) while fixing issues and ensuring all tests pass. The migration will be performed in small, manageable batches organized by module and test type.

## Migration Principles

1. **Incremental Migration**: Migrate tests in small, logical batches
2. **Fix as We Go**: Address issues in tests during migration rather than after
3. **Test Before Commit**: Ensure each batch of migrated tests passes before moving to the next
4. **Improve as We Migrate**: Apply best practices to tests as they're migrated
5. **Document Changes**: Track significant changes and improvements

## Migration Workflow for Each Batch

1. Identify the next batch of tests to migrate
2. Copy tests to the new structure, preserving directory organization
3. Update imports and dependencies as needed
4. Fix any issues preventing the tests from running
5. Run the tests to ensure they pass
6. Improve test structure, organization, and patterns where needed
7. Document any significant changes or issues encountered

## Migration Batches

### Session 1: Configuration Tests

**Focus**: Migrate basic configuration tests

**Tasks**:
- Migrate model tests from `src/agent_c_api/tests/v2/config/test_models.py` to `tests/unit/api/v2/config/test_models.py`
- Migrate service tests from `src/agent_c_api/tests/v2/config/test_services.py` to `tests/unit/api/v2/config/test_services.py`
- Migrate endpoint tests from `src/agent_c_api/tests/v2/config/test_endpoints.py` to `tests/unit/api/v2/config/test_endpoints.py`
- Verify all configuration tests pass in the new structure

### Session 2: Models Tests

**Focus**: Migrate model validation tests

**Tasks**:
- Migrate chat model tests from `src/agent_c_api/tests/v2/models/test_chat_models.py` to `tests/unit/api/v2/models/test_chat_models.py`
- Migrate file model tests from `src/agent_c_api/tests/v2/models/test_file_models.py` to `tests/unit/api/v2/models/test_file_models.py`
- Migrate history model tests from `src/agent_c_api/tests/v2/models/test_history_models.py` to `tests/unit/api/v2/models/test_history_models.py`
- Migrate response model tests from `src/agent_c_api/tests/v2/models/test_response_models.py` to `tests/unit/api/v2/models/test_response_models.py`
- Migrate session model tests from `src/agent_c_api/tests/v2/models/test_session_models.py` to `tests/unit/api/v2/models/test_session_models.py`
- Migrate tool model tests from `src/agent_c_api/tests/v2/models/test_tool_models.py` to `tests/unit/api/v2/models/test_tool_models.py`
- Verify all model tests pass in the new structure

### Session 3: Utility Tests

**Focus**: Migrate utility function tests

**Tasks**:
- Migrate chat converter tests from `src/agent_c_api/tests/v2/utils/test_chat_converters.py` to `tests/unit/api/v2/utils/test_chat_converters.py`
- Migrate model converter tests from `src/agent_c_api/tests/v2/utils/test_model_converters.py` to `tests/unit/api/v2/utils/test_model_converters.py`
- Verify all utility tests pass in the new structure

### Session 4: Debug Endpoint Tests

**Focus**: Migrate debug functionality tests

**Tasks**:
- Migrate debug tests from `src/agent_c_api/tests/v2/debug/test_debug.py` to `tests/unit/api/v2/debug/test_debug.py`
- Verify all debug tests pass in the new structure

### Session 5: History and Events Tests

**Focus**: Migrate history and event tracking tests

**Tasks**:
- Migrate event tests from `src/agent_c_api/tests/v2/history/test_events.py` to `tests/unit/api/v2/history/test_events.py`
- Migrate history tests from `src/agent_c_api/tests/v2/history/test_history.py` to `tests/unit/api/v2/history/test_history.py`
- Migrate history model tests from `src/agent_c_api/tests/v2/history/test_models.py` to `tests/unit/api/v2/history/test_models.py`
- Verify all history tests pass in the new structure

### Session 6: Session Service Tests

**Focus**: Migrate session management tests

**Tasks**:
- Migrate agent tests from `src/agent_c_api/tests/v2/sessions/test_agent.py` to `tests/unit/api/v2/sessions/test_agent.py`
- Migrate chat tests from `src/agent_c_api/tests/v2/sessions/test_chat.py` to `tests/unit/api/v2/sessions/test_chat.py`
- Migrate file tests from `src/agent_c_api/tests/v2/sessions/test_files.py` to `tests/unit/api/v2/sessions/test_files.py`
- Verify all session service tests pass in the new structure

### Session 7: Session Router and Integration Tests

**Focus**: Migrate router tests and add integration tests

**Tasks**:
- Migrate router tests from `src/agent_c_api/tests/v2/sessions/test_router.py` to `tests/unit/api/v2/sessions/test_router.py`
- Migrate service tests from `src/agent_c_api/tests/v2/sessions/test_service.py` to `tests/unit/api/v2/sessions/test_service.py`
- Create basic integration tests for sessions in `tests/integration/api/test_sessions.py`
- Verify all router and integration tests pass in the new structure

### Session 8: API Structure Tests and V1 Tests

**Focus**: Migrate API structure tests and v1 API tests

**Tasks**:
- Migrate API structure tests from `src/agent_c_api/tests/v2/test_api_structure.py` to `tests/unit/api/v2/test_api_structure.py`
- Migrate persona tests from `src/agent_c_api/tests/persona_test.py` to `tests/unit/api/v1/test_persona.py`
- Create basic structure for remaining v1 API tests
- Verify all structure and v1 API tests pass in the new structure

### Session 9: Core Tests and Finalization

**Focus**: Migrate core component tests and finalize the migration

**Tasks**:
- Create tests for core components in `tests/unit/core/`
- Implement basic functional tests in `tests/functional/`
- Verify all tests pass in the new structure
- Update documentation to reflect the new test structure
- Add notes on testing best practices

## Verification Process

After each session, run the following command to verify the migrated tests pass:

```bash
python -m pytest tests/unit/api/v2/[module] -v
```

Where `[module]` is the specific module being tested (e.g., `config`, `models`, etc.).

If all tests pass, proceed to the next session. If not, fix the issues before continuing.

## Documentation Guidelines

For each migrated test file, ensure:

1. Tests are properly marked with the appropriate pytest markers (`@pytest.mark.unit`, etc.)
2. Each test class has a clear docstring explaining its purpose
3. Each test method has a descriptive name and docstring
4. Fixtures are well-documented and organized
5. Test data and mocks are clearly defined and separated from test logic

## Context Template for Future Sessions

```
# Test Migration Context

We are currently migrating tests from the old structure (src/agent_c_api/tests/) to the new structure (tests/) following our test migration plan.

## Current Progress

We have completed the following sessions:
- [List completed sessions here]

## Current Session Focus

We are working on Session X: [Session Name]

The main tasks for this session are:
- [List specific tasks for this session]

## Recent Changes and Issues

- [Document any significant changes or issues encountered in previous sessions]

## Testing Guidelines

- Tests should be properly marked with pytest markers
- Test classes and methods should have clear docstrings
- Fixtures should be well-documented and organized
- Test data and mocks should be clearly defined
- Tests should follow the arrange/act/assert pattern

## Verification Process

After migrating tests, run:
```bash
python -m pytest tests/unit/api/v2/[module] -v
```

Ensure all tests pass before proceeding to the next batch.
```

## Conclusion

This migration plan provides a structured approach to migrating tests while improving their quality and organization. By following this plan and addressing issues as they're encountered, we can ensure that our test suite is comprehensive, well-organized, and maintainable.

The plan is flexible and can be adjusted based on findings during the migration process. If significant issues are encountered that require a change in approach, the plan should be updated accordingly.