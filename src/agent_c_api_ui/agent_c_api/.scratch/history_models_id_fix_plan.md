# History Models ID Fix Plan

## Issue Description

During the migration of tests for `history_models.py`, we identified a critical issue: the models are using UUIDs for session identifiers instead of the company-standard MnemonicSlugs system. According to our rules:

> Many of the v2 models and endpoints were created under the false assumption that GUIDs would be used for IDs. The ID naming rules have been added to your rules for you to be aware of so that we can correct any bad IDs as part of this process.

The MnemonicSlugs system uses readable word combinations (e.g., "tiger-castle") that are deterministically generated from input strings. These are more human-friendly and follow the company's ID naming conventions.

## Affected Models

The following models in `history_models.py` incorrectly use UUID for session_id:

1. `HistorySummary`
2. `HistoryDetail` (inherits from HistorySummary)
3. `ReplayStatus`

## Fix Implementation Plan

### 1. Update history_models.py

1. Change the session_id field type from UUID to str in all affected models
2. Update field descriptions to reflect the MnemonicSlugs system
3. Update schema examples to use MnemonicSlug-style IDs instead of UUIDs
4. Add documentation about the ID format to help API consumers

### 2. Update Tests

1. Modify the session_id fixture to generate MnemonicSlug-style IDs instead of UUIDs
2. Update all test cases to work with string IDs rather than UUID objects
3. Fix schema example validations to handle string IDs
4. Add specific tests to verify ID handling conforms to the MnemonicSlugs system

### 3. Integration Considerations

1. Ensure compatibility with other modules that interact with these models
2. Verify the models can still properly serialize/deserialize with the updated ID format
3. Consider adding validation that IDs follow the MnemonicSlugs format

## Implementation Details

### Model Changes

```python
# Before
class HistorySummary(BaseModel):
    session_id: UUID = Field(
        ..., 
        description="Unique identifier for the session"
    )
    # ...

# After
class HistorySummary(BaseModel):
    session_id: str = Field(
        ..., 
        description="Unique session identifier in MnemonicSlug format (e.g., 'tiger-castle')"
    )
    # ...
```

### Test Changes

```python
# Before
@pytest.fixture
def session_id():
    """Generate a random session ID for testing"""
    return uuid4()

# After
@pytest.fixture
def session_id():
    """Generate a session ID for testing using the MnemonicSlugs format"""
    return "tiger-castle"  # Fixed value for testing
```

### Example Updates

```python
# Before in model_config
"example": {
    "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    # ...
}

# After in model_config
"example": {
    "session_id": "tiger-castle",
    # ...
}
```

## Testing Strategy

1. Unit tests should verify that the models accept string IDs in the MnemonicSlugs format
2. Tests should validate that serialization/deserialization works correctly with the new ID format
3. Integration tests should verify compatibility with other components

## Migration Approach

1. Update the model definitions first
2. Update the test fixtures and tests
3. Verify all tests pass with the new ID format
4. Update the migration tracker with the changes made