# Migration Plan: test_history_models.py

## Migration Overview

This document outlines the plan for migrating the history models test file from its current location to the new test structure, while addressing identified issues and expanding coverage.

**Source Path:** `//api/src/agent_c_api/tests/v2/models/test_history_models.py`
**Destination Path:** `//api/tests/unit/api/v2/models/test_history_models.py`

## Migration Steps

### Step 1: Set Up New Test Structure

1. Create the new test file with appropriate imports:
   ```python
   import pytest
   from datetime import datetime, timedelta
   from uuid import UUID, uuid4
   import json
   from pydantic import ValidationError
   
   from agent_c_api.api.v2.models.history_models import (
       HistorySummary, HistoryDetail, EventFilter, 
       PaginationParams, HistoryListResponse, 
       StoredEvent, ChatEventUnion, 
       ReplayStatus, ReplayControl
   )
   ```

2. Define pytest markers:
   ```python
   pytestmark = [
       pytest.mark.unit,
       pytest.mark.models,
       pytest.mark.history
   ]
   ```

3. Add fixtures for common test data:
   ```python
   @pytest.fixture
   def session_id():
       return uuid4()
   
   @pytest.fixture
   def timestamp_now():
       return datetime.now()
   
   @pytest.fixture
   def timestamp_later(timestamp_now):
       return timestamp_now + timedelta(hours=1)
   ```

### Step 2: Migrate and Enhance Existing Tests

Organize tests into classes by model, starting with the ones that already have tests:

#### HistorySummaryTests

```python
class TestHistorySummary:
    """Tests for the HistorySummary model
    
    HistorySummary contains key information about a session's history 
    including identifiers, timestamps, and basic metrics.
    """
    
    def test_valid_summary(self, session_id, timestamp_now, timestamp_later):
        """Test creating a valid history summary"""
        # Test implementation similar to existing test_history_summary
    
    def test_missing_required_field(self, session_id, timestamp_now):
        """Test validation when required field is missing"""
        # Test implementation similar to existing test
    
    def test_serialization(self, session_id, timestamp_now, timestamp_later):
        """Test JSON serialization and deserialization"""
        # New test for JSON serialization
    
    def test_schema_example(self):
        """Test that schema example is valid according to the model"""
        # New test for schema example validation
```

#### EventFilterTests

```python
class TestEventFilter:
    """Tests for the EventFilter model
    
    EventFilter provides parameters for filtering history events by type,
    time range, and limiting the result set size.
    """
    
    def test_default_values(self):
        """Test default values are set correctly"""
        # Test implementation similar to existing test_event_filter
    
    def test_custom_values(self, timestamp_now):
        """Test setting custom values"""
        # Test implementation similar to existing test_event_filter
    
    def test_limit_validation(self):
        """Test validation of limit field (min/max values)"""
        # New test for field validation
    
    def test_serialization(self, timestamp_now):
        """Test JSON serialization and deserialization"""
        # New test for JSON serialization
    
    def test_schema_examples(self):
        """Test that schema examples are valid according to the model"""
        # New test for schema examples
```

#### ReplayStatusTests and ReplayControlTests

Follow similar structure for ReplayStatus and ReplayControl models.

### Step 3: Add Tests for Untested Models

Add new test classes for the untested models:

#### HistoryDetailTests

```python
class TestHistoryDetail:
    """Tests for the HistoryDetail model
    
    HistoryDetail extends HistorySummary with additional information about
    the session's contents, including file records and event types.
    """
    
    def test_valid_detail(self, session_id, timestamp_now, timestamp_later):
        """Test creating a valid history detail"""
        # Implementation
    
    def test_inheritance_from_summary(self, session_id, timestamp_now, timestamp_later):
        """Test that HistoryDetail properly inherits from HistorySummary"""
        # Implementation
    
    def test_optional_fields(self, session_id, timestamp_now, timestamp_later):
        """Test optional fields can be omitted"""
        # Implementation
    
    def test_serialization(self, session_id, timestamp_now, timestamp_later):
        """Test JSON serialization and deserialization"""
        # Implementation
    
    def test_schema_example(self):
        """Test that schema example is valid according to the model"""
        # Implementation
```

Follow similar patterns for PaginationParams, HistoryListResponse, and StoredEvent models.

### Step 4: Integration Tests

Add tests for integration with related models:

```python
class TestHistoryModelIntegrations:
    """Tests for interactions between history models
    
    These tests verify that the history models work correctly together
    and with related models from other modules.
    """
    
    def test_stored_event_with_chat_event(self):
        """Test StoredEvent with different types of ChatEventUnion"""
        # Implementation using different event types
    
    def test_history_list_with_summaries(self, session_id, timestamp_now):
        """Test HistoryListResponse with multiple HistorySummary items"""
        # Implementation
```

## Final Structure

The final test file structure will look like:

```
test_history_models.py
├── imports
├── pytest markers
├── fixtures
├── TestHistorySummary
│   ├── test_valid_summary
│   ├── test_missing_required_field
│   ├── test_serialization
│   └── test_schema_example
├── TestHistoryDetail
│   ├── ...
├── TestEventFilter
│   ├── ...
├── TestPaginationParams
│   ├── ...
├── TestHistoryListResponse
│   ├── ...
├── TestStoredEvent
│   ├── ...
├── TestReplayStatus
│   ├── ...
├── TestReplayControl
│   ├── ...
└── TestHistoryModelIntegrations
    ├── ...
```

## Migration Verification

After migration, verify that:

1. All existing test functionality is preserved
2. New tests pass and provide enhanced coverage
3. Test classes and methods have appropriate docstrings
4. Pytest markers are correctly applied
5. The file follows the project's code style guidelines

## Requirements

- pytest
- pytest-asyncio (if needed for async tests)
- The implementation code must be accessible from the new test location

## Next Steps

After completing the migration:

1. Document any issues found during migration
2. Update the migration tracker
3. Consider adding similar tests for related models in other files