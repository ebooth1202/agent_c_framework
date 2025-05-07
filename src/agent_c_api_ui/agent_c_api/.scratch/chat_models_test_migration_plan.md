# Migration Plan for test_chat_models.py

## Source and Destination

- **Source Path:** `//api/src/agent_c_api/tests/v2/models/test_chat_models.py`
- **Destination Path:** `//api/tests/unit/api/v2/models/test_chat_models.py`

## Migration Approach

### 1. Create New File Structure

Create a properly organized class structure with better documentation:

```python
# tests/unit/api/v2/models/test_chat_models.py

import pytest
from datetime import datetime
from uuid import UUID, uuid4
from agent_c_api.api.v2.models.chat_models import (
    ChatMessageContent, ChatMessage, ChatRequest, ChatResponse,
    ChatEventType, ChatEventUnion
)
from agent_c_api.api.v2.models.tool_models import (
    ToolCall, ToolResult
)

# Import core models for conversion tests
from agent_c.models.events.chat import MessageEvent
from agent_c.models.common_chat import TextContentBlock

@pytest.mark.unit
@pytest.mark.models
@pytest.mark.chat
class TestChatModels:
    """Tests for the chat models used in the API v2.
    
    These tests verify that the chat-related models correctly validate input,
    store properties, and handle conversion between API models and core models.
    """
    
    class TestChatMessageContent:
        """Tests for the ChatMessageContent model.
        
        ChatMessageContent represents different types of content in a chat message,
        such as text, images, or file attachments.
        """
        
        def test_text_content(self):
            # Test implementation...
            
        def test_image_content(self):
            # Test implementation...
            
        def test_file_content(self):
            # Test implementation...
            
        def test_to_content_block(self):
            # New test for conversion to core content blocks
            
        def test_from_content_block(self):
            # New test for conversion from core content blocks
    
    class TestChatMessage:
        """Tests for the ChatMessage model.
        
        ChatMessage represents a message in a chat conversation, which can contain
        multiple content parts, tool calls, and tool results.
        """
        
        def test_basic_properties(self):
            # Test implementation...
            
        def test_to_message_event(self):
            # New test for conversion to core MessageEvent
            
        def test_from_message_event(self):
            # New test for conversion from core MessageEvent
    
    class TestChatRequest:
        """Tests for the ChatRequest model.
        
        ChatRequest is used to send a message to the agent with streaming control.
        """
        
        def test_properties(self):
            # Test implementation...
    
    class TestChatResponse:
        """Tests for the ChatResponse model.
        
        ChatResponse is used for non-streaming responses, containing the complete
        message from the assistant.
        """
        
        def test_properties(self):
            # New test for ChatResponse model
    
    class TestChatEventType:
        """Tests for the ChatEventType enum.
        
        ChatEventType defines the possible event types during a streaming chat interaction.
        """
        
        def test_constants(self):
            # Test implementation...
```

### 2. Implement Tests

#### 2.1 Existing Tests Migration

- Migrate all existing test functions to the new class structure
- Ensure assertions and test logic remain the same
- Update method names for clarity within the class context

#### 2.2 New Tests Implementation

Implement the following new tests to improve coverage:

1. `TestChatMessageContent.test_to_content_block`
   - Test conversion from ChatMessageContent to core content blocks
   - Cover text, image, and file types
   - Verify properties are correctly transferred

2. `TestChatMessageContent.test_from_content_block`
   - Test conversion from core content blocks to ChatMessageContent
   - Cover TextBlock, ImageBlock, and FileBlock types
   - Verify properties are correctly transferred
   - Test error handling for unknown block types

3. `TestChatMessage.test_to_message_event`
   - Test conversion from ChatMessage to core MessageEvent
   - Verify role, content, and other properties are correctly transferred
   - Test with different content types

4. `TestChatMessage.test_from_message_event`
   - Test conversion from core MessageEvent to ChatMessage
   - Verify role, content, and other properties are correctly transferred

5. `TestChatResponse.test_properties`
   - Test the ChatResponse model properties
   - Verify it correctly stores a ChatMessage and completion_id

### 3. Implementation Steps

1. Create the new test file with the class structure
2. Implement the existing tests in the new structure
3. Add the new tests for improved coverage
4. Update imports to match the new project structure
5. Run tests to verify functionality

### 4. Verification

After migration, run the following command to verify the tests:

```bash
python -m pytest tests/unit/api/v2/models/test_chat_models.py -v
```

The output should show that all tests are passing, and the new tests are providing additional coverage.