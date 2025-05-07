from datetime import datetime
import json
from typing import Dict, List, Any, Optional, Union, Sequence

from agent_c.models.events.chat import MessageEvent, InteractionEvent
from agent_c.models.events.tool_calls import ToolCallEvent
from redis import asyncio as aioredis

class ChatRepository:
    """Repository for managing chat messages in Redis"""
    
    def __init__(self, redis_client: aioredis.Redis, session_id: str):
        """
        Initialize the chat repository.
        
        Args:
            redis_client (aioredis.Redis): Redis client instance
            session_id (str): The session ID
        """
        self.redis = redis_client
        self.session_id = session_id
    
    async def add_message(self, message: Union[MessageEvent, Dict[str, Any]]) -> None:
        """
        Add a message to the chat session.
        
        Args:
            message (Union[MessageEvent, Dict[str, Any]]): The message to add
        """
        # Convert to dict if needed
        if isinstance(message, MessageEvent):
            msg_data = message.model_dump()
        else:
            msg_data = message
        
        # Add timestamp if not present
        if "timestamp" not in msg_data:
            msg_data["timestamp"] = datetime.now().isoformat()
        
        # Convert any non-string values
        msg_data = {k: json.dumps(v) if not isinstance(v, str) else v 
                    for k, v in msg_data.items()}
        
        # Add to Redis stream
        await self.redis.xadd(f"session:{self.session_id}:messages", msg_data)
        
        # Update session updated_at time
        await self.redis.hset(f"session:{self.session_id}:meta", "updated_at", 
                            datetime.now().isoformat())
    
    async def get_messages(self, start: str = "-", end: str = "+", count: int = 100) -> List[Dict[str, Any]]:
        """
        Get messages from the chat session.
        
        Args:
            start (str): Start ID for range query
            end (str): End ID for range query
            count (int): Maximum number of messages to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of messages
        """
        # Get messages from Redis stream
        messages = await self.redis.xrange(f"session:{self.session_id}:messages", start, end, count)
        
        # Process messages
        result = []
        for msg_id, msg_data in messages:
            # Convert message ID to string
            msg_id_str = msg_id.decode("utf-8") if isinstance(msg_id, bytes) else msg_id
            
            # Process message data
            processed_data = {}
            for k, v in msg_data.items():
                # Convert bytes to string
                key = k.decode("utf-8") if isinstance(k, bytes) else k
                value = v.decode("utf-8") if isinstance(v, bytes) else v
                
                # Try to parse JSON values
                try:
                    if key not in ["timestamp", "role", "content", "format"]:
                        processed_value = json.loads(value)
                    else:
                        processed_value = value
                except json.JSONDecodeError:
                    processed_value = value
                    
                processed_data[key] = processed_value
            
            # Add message ID
            processed_data["id"] = msg_id_str
            result.append(processed_data)
        
        return result
    
    async def get_meta(self) -> Dict[str, Any]:
        """
        Get session metadata.
        
        Returns:
            Dict[str, Any]: Session metadata
        """
        # Get metadata from Redis hash
        meta_data = await self.redis.hgetall(f"session:{self.session_id}:meta")
        
        # Process metadata
        result = {}
        for k, v in meta_data.items():
            # Convert bytes to string
            key = k.decode("utf-8") if isinstance(k, bytes) else k
            value = v.decode("utf-8") if isinstance(v, bytes) else v
            
            # Try to parse JSON values
            try:
                if key not in ["created_at", "updated_at", "name", "description"]:
                    processed_value = json.loads(value)
                else:
                    processed_value = value
            except json.JSONDecodeError:
                processed_value = value
                
            result[key] = processed_value
        
        return result
    
    async def set_meta(self, key: str, value: Any) -> None:
        """
        Set session metadata.
        
        Args:
            key (str): Metadata key
            value (Any): Metadata value
        """
        # Convert value to string if needed
        if not isinstance(value, str):
            value = json.dumps(value)
            
        # Set metadata in Redis hash
        await self.redis.hset(f"session:{self.session_id}:meta", key, value)
    
    async def get_managed_meta(self) -> Dict[str, Any]:
        """
        Get managed session metadata.
        
        Returns:
            Dict[str, Any]: Managed session metadata
        """
        # Get metadata from Redis hash
        meta_data = await self.redis.hgetall(f"session:{self.session_id}:managed_meta")
        
        # Process metadata (same as get_meta)
        result = {}
        for k, v in meta_data.items():
            # Convert bytes to string
            key = k.decode("utf-8") if isinstance(k, bytes) else k
            value = v.decode("utf-8") if isinstance(v, bytes) else v
            
            # Try to parse JSON values
            try:
                processed_value = json.loads(value)
            except json.JSONDecodeError:
                processed_value = value
                
            result[key] = processed_value
        
        return result
    
    async def set_managed_meta(self, key: str, value: Any) -> None:
        """
        Set managed session metadata.
        
        Args:
            key (str): Metadata key
            value (Any): Metadata value
        """
        # Convert value to string if needed
        if not isinstance(value, str):
            value = json.dumps(value)
            
        # Set metadata in Redis hash
        await self.redis.hset(f"session:{self.session_id}:managed_meta", key, value)
    
    async def add_tool_call(self, tool_call: Union[ToolCallEvent, Dict[str, Any]]) -> None:
        """
        Add a tool call to the chat session.
        
        Args:
            tool_call (Union[ToolCallEvent, Dict[str, Any]]): The tool call to add
        """
        # Convert to dict if needed
        if isinstance(tool_call, ToolCallEvent):
            tool_data = tool_call.model_dump()
        else:
            tool_data = tool_call
        
        # Add timestamp if not present
        if "timestamp" not in tool_data:
            tool_data["timestamp"] = datetime.now().isoformat()
        
        # Convert any non-string values
        tool_data = {k: json.dumps(v) if not isinstance(v, str) else v 
                    for k, v in tool_data.items()}
        
        # Add to Redis stream
        await self.redis.xadd(f"session:{self.session_id}:tool_calls", tool_data)
        
        # Update session updated_at time
        await self.redis.hset(f"session:{self.session_id}:meta", "updated_at", 
                            datetime.now().isoformat())
    
    async def get_tool_calls(self, start: str = "-", end: str = "+", count: int = 100) -> List[Dict[str, Any]]:
        """
        Get tool calls from the chat session.
        
        Args:
            start (str): Start ID for range query
            end (str): End ID for range query
            count (int): Maximum number of tool calls to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of tool calls
        """
        # Get tool calls from Redis stream
        tool_calls = await self.redis.xrange(f"session:{self.session_id}:tool_calls", start, end, count)
        
        # Process tool calls (same approach as get_messages)
        result = []
        for call_id, call_data in tool_calls:
            # Convert ID to string
            call_id_str = call_id.decode("utf-8") if isinstance(call_id, bytes) else call_id
            
            # Process tool call data
            processed_data = {}
            for k, v in call_data.items():
                # Convert bytes to string
                key = k.decode("utf-8") if isinstance(k, bytes) else k
                value = v.decode("utf-8") if isinstance(v, bytes) else v
                
                # Try to parse JSON values
                try:
                    if key not in ["timestamp", "name", "description"]:
                        processed_value = json.loads(value)
                    else:
                        processed_value = value
                except json.JSONDecodeError:
                    processed_value = value
                    
                processed_data[key] = processed_value
            
            # Add call ID
            processed_data["id"] = call_id_str
            result.append(processed_data)
        
        return result
    
    async def add_interaction(self, messages: Sequence[Union[MessageEvent, Dict[str, Any]]], 
                            tool_calls: Optional[Sequence[Union[ToolCallEvent, Dict[str, Any]]]] = None,
                            interaction_id: Optional[str] = None) -> str:
        """
        Add multiple messages as a single interaction to the chat session.
        
        Args:
            messages (Sequence[Union[MessageEvent, Dict[str, Any]]]): Messages to add
            tool_calls (Optional[Sequence[Union[ToolCallEvent, Dict[str, Any]]]]): Tool calls to add
            interaction_id (Optional[str]): Custom interaction ID
            
        Returns:
            str: The interaction ID
        """
        # Generate interaction ID if not provided
        if interaction_id is None:
            from uuid import uuid4
            interaction_id = str(uuid4())
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Create a Redis transaction pipeline
        pipe = self.redis.pipeline()
        
        # Add interaction metadata
        interaction_meta = {
            "timestamp": timestamp,
            "message_count": str(len(messages)),
            "tool_call_count": str(len(tool_calls) if tool_calls else 0)
        }
        pipe.hset(f"session:{self.session_id}:interaction:{interaction_id}", mapping=interaction_meta)
        
        # Add all messages with the interaction ID
        for i, message in enumerate(messages):
            # Convert to dict if needed
            if isinstance(message, MessageEvent):
                msg_data = message.model_dump()
            else:
                msg_data = message.copy()  # Create a copy to avoid modifying the original
            
            # Add interaction ID and timestamp
            msg_data["interaction_id"] = interaction_id
            if "timestamp" not in msg_data:
                msg_data["timestamp"] = timestamp
            
            # Add order index
            msg_data["interaction_index"] = str(i)
            
            # Convert any non-string values
            msg_data = {k: json.dumps(v) if not isinstance(v, str) else v 
                        for k, v in msg_data.items()}
            
            # Add to Redis stream
            pipe.xadd(f"session:{self.session_id}:messages", msg_data)
        
        # Add tool calls if provided
        if tool_calls:
            for i, tool_call in enumerate(tool_calls):
                # Convert to dict if needed
                if isinstance(tool_call, ToolCallEvent):
                    tool_data = tool_call.model_dump()
                else:
                    tool_data = tool_call.copy()  # Create a copy to avoid modifying the original
                
                # Add interaction ID and timestamp
                tool_data["interaction_id"] = interaction_id
                if "timestamp" not in tool_data:
                    tool_data["timestamp"] = timestamp
                
                # Add order index
                tool_data["interaction_index"] = str(i)
                
                # Convert any non-string values
                tool_data = {k: json.dumps(v) if not isinstance(v, str) else v 
                            for k, v in tool_data.items()}
                
                # Add to Redis stream
                pipe.xadd(f"session:{self.session_id}:tool_calls", tool_data)
        
        # Update session updated_at time
        pipe.hset(f"session:{self.session_id}:meta", "updated_at", timestamp)
        
        # Update interactions index
        pipe.sadd(f"session:{self.session_id}:interactions", interaction_id)
        
        # Execute pipeline
        await pipe.execute()
        
        return interaction_id
    
    async def get_interactions(self) -> List[str]:
        """
        Get all interaction IDs for the chat session.
        
        Returns:
            List[str]: List of interaction IDs
        """
        # Get interaction IDs from Redis set
        interactions = await self.redis.smembers(f"session:{self.session_id}:interactions")
        
        # Convert to strings
        return [interaction.decode("utf-8") if isinstance(interaction, bytes) else interaction
                for interaction in interactions]
    
    async def get_interaction(self, interaction_id: str) -> Dict[str, Any]:
        """
        Get details of a specific interaction.
        
        Args:
            interaction_id (str): The interaction ID
            
        Returns:
            Dict[str, Any]: Interaction details including messages and tool calls
        """
        # Get interaction metadata
        meta = await self.redis.hgetall(f"session:{self.session_id}:interaction:{interaction_id}")
        
        # Process metadata
        meta_dict = {}
        for k, v in meta.items():
            key = k.decode("utf-8") if isinstance(k, bytes) else k
            value = v.decode("utf-8") if isinstance(v, bytes) else v
            meta_dict[key] = value
        
        # Get messages for this interaction
        all_messages = await self.get_messages()
        interaction_messages = [msg for msg in all_messages 
                              if msg.get("interaction_id") == interaction_id]
        
        # Get tool calls for this interaction
        all_tool_calls = await self.get_tool_calls()
        interaction_tool_calls = [call for call in all_tool_calls 
                                if call.get("interaction_id") == interaction_id]
        
        # Sort by interaction_index if available
        interaction_messages.sort(key=lambda x: int(x.get("interaction_index", 0)))
        interaction_tool_calls.sort(key=lambda x: int(x.get("interaction_index", 0)))
        
        # Build result
        result = {
            "id": interaction_id,
            "timestamp": meta_dict.get("timestamp"),
            "messages": interaction_messages,
            "tool_calls": interaction_tool_calls,
            "metadata": meta_dict
        }
        
        return result