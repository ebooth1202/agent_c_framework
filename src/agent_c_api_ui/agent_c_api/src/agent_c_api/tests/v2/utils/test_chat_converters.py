import pytest
from uuid import uuid4

from agent_c.models.events.chat import MessageEvent
from agent_c_api.api.v2.models.chat_models import (
    ChatMessage,
    ChatMessageContent
)
from agent_c_api.api.v2.utils.model_converters import (
    chat_message_to_message_event,
    message_event_to_chat_message
)


class TestChatMessageConverters:
    
    def test_chat_message_to_message_event(self):
        # Create a chat message with text content
        chat_message = ChatMessage(
            role="user",
            content=[
                ChatMessageContent(type="text", text="Hello, how are you?")
            ]
        )
        
        session_id = str(uuid4())
        
        # Convert to message event
        message_event = chat_message_to_message_event(chat_message, session_id)
        
        # Verify conversion
        assert isinstance(message_event, MessageEvent)
        assert message_event.session_id == session_id
        assert message_event.role == "user"
        assert message_event.content == "Hello, how are you?"
        assert message_event.format == "markdown"
    
    def test_chat_message_to_message_event_multiple_content(self):
        # Create a chat message with multiple text content blocks
        chat_message = ChatMessage(
            role="assistant",
            content=[
                ChatMessageContent(type="text", text="Hello!"),
                ChatMessageContent(type="text", text="How can I help you today?")
            ]
        )
        
        session_id = str(uuid4())
        
        # Convert to message event
        message_event = chat_message_to_message_event(chat_message, session_id)
        
        # Verify conversion (text should be joined with newlines)
        assert isinstance(message_event, MessageEvent)
        assert message_event.role == "assistant"
        assert message_event.content == "Hello!\nHow can I help you today?"
    
    def test_message_event_to_chat_message(self):
        # Create a message event
        session_id = str(uuid4())
        message_event = MessageEvent(
            session_id=session_id,
            role="user",
            content="Hello, test message",
            format="markdown"
        )
        
        # Convert to chat message
        chat_message = message_event_to_chat_message(message_event)
        
        # Verify conversion
        assert isinstance(chat_message, ChatMessage)
        assert chat_message.role == "user"
        assert len(chat_message.content) == 1
        assert chat_message.content[0].type == "text"
        assert chat_message.content[0].text == "Hello, test message"
    
    def test_message_event_conversion_roundtrip(self):
        # Start with a message event
        session_id = str(uuid4())
        original_event = MessageEvent(
            session_id=session_id,
            role="assistant",
            content="This is a test message for roundtrip conversion",
            format="markdown"
        )
        
        # Convert to chat message and back
        chat_message = message_event_to_chat_message(original_event)
        converted_event = chat_message_to_message_event(chat_message, session_id)
        
        # Verify roundtrip conversion preserved essential data
        assert converted_event.session_id == original_event.session_id
        assert converted_event.role == original_event.role
        assert converted_event.content == original_event.content
        assert converted_event.format == original_event.format