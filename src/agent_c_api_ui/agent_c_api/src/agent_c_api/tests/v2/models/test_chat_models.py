# src/agent_c_api/tests/v2/models/test_chat_models.py
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from agent_c_api.api.v2.models.chat_models import (
    ChatMessageContent, ChatMessage, ChatRequest, 
    ChatEventType, ChatEvent
)
from agent_c_api.api.v2.models.tool_models import (
    ToolCall, ToolResult
)

def test_chat_message_content_text():
    # Test text content
    content = ChatMessageContent(
        type="text",
        text="Hello, world!"
    )
    assert content.type == "text"
    assert content.text == "Hello, world!"
    assert content.file_id is None
    assert content.mime_type is None
    
    # Test missing text for text type
    with pytest.raises(ValueError):
        ChatMessageContent(type="text")

def test_chat_message_content_image():
    # Test image content
    content = ChatMessageContent(
        type="image",
        file_id="img-123",
        mime_type="image/jpeg"
    )
    assert content.type == "image"
    assert content.text is None
    assert content.file_id == "img-123"
    assert content.mime_type == "image/jpeg"
    
    # Test missing file_id for image type
    with pytest.raises(ValueError):
        ChatMessageContent(type="image")

def test_chat_message_content_file():
    # Test file content
    content = ChatMessageContent(
        type="file",
        file_id="doc-456",
        mime_type="application/pdf"
    )
    assert content.type == "file"
    assert content.text is None
    assert content.file_id == "doc-456"
    assert content.mime_type == "application/pdf"
    
    # Test missing file_id for file type
    with pytest.raises(ValueError):
        ChatMessageContent(type="file")

def test_chat_message():
    message_id = uuid4()
    now = datetime.now()
    content = ChatMessageContent(type="text", text="Hello")
    
    # Test with minimal fields
    message = ChatMessage(
        role="user",
        content=[content]
    )
    assert message.id is None
    assert message.role == "user"
    assert message.created_at is None
    assert len(message.content) == 1
    assert message.content[0].text == "Hello"
    assert message.tool_calls is None
    assert message.tool_results is None
    
    # Test with all fields
    tool_call = ToolCall(tool_id="calculator", parameters={"expression": "2+2"})
    tool_result = ToolResult(tool_id="calculator", success=True, result=4)
    
    message = ChatMessage(
        id=message_id,
        role="assistant",
        created_at=now,
        content=[content],
        tool_calls=[tool_call],
        tool_results=[tool_result]
    )
    assert message.id == message_id
    assert message.role == "assistant"
    assert message.created_at == now
    assert len(message.content) == 1
    assert len(message.tool_calls) == 1
    assert message.tool_calls[0].tool_id == "calculator"
    assert len(message.tool_results) == 1
    assert message.tool_results[0].result == 4

def test_chat_request():
    content = ChatMessageContent(type="text", text="What is 2+2?")
    message = ChatMessage(role="user", content=[content])
    
    # Test with default streaming
    request = ChatRequest(message=message)
    assert request.message.role == "user"
    assert request.message.content[0].text == "What is 2+2?"
    assert request.stream is True
    
    # Test with streaming disabled
    request = ChatRequest(message=message, stream=False)
    assert request.stream is False

def test_chat_event_type():
    # Test event type constants
    assert ChatEventType.MESSAGE_START == "message_start"
    assert ChatEventType.MESSAGE_TEXT == "message_text"
    assert ChatEventType.TOOL_CALL == "tool_call"
    assert ChatEventType.TOOL_RESULT == "tool_result"
    assert ChatEventType.MESSAGE_END == "message_end"
    assert ChatEventType.ERROR == "error"

def test_chat_event():
    now = datetime.now()
    
    # Test text event
    event = ChatEvent(
        event_type=ChatEventType.MESSAGE_TEXT,
        data={"text": "Hello, world!"},
        timestamp=now
    )
    assert event.event_type == "message_text"
    assert event.data == {"text": "Hello, world!"}
    assert event.timestamp == now
    
    # Test tool call event
    event = ChatEvent(
        event_type=ChatEventType.TOOL_CALL,
        data={
            "tool_id": "calculator",
            "parameters": {"expression": "2+2"}
        },
        timestamp=now
    )
    assert event.event_type == "tool_call"
    assert event.data["tool_id"] == "calculator"
    assert event.timestamp == now