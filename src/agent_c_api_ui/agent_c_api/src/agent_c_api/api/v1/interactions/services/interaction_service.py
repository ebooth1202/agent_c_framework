import os
import glob
import json
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

from agent_c_api.api.v1.interactions.interaction_models.interaction_model import InteractionSummary, InteractionDetail
from agent_c_api.api.v1.interactions.utils.file_utils import read_jsonl_file, get_session_directory

class InteractionService:
    async def list_sessions(self, limit: int, offset: int, sort_by: str, sort_order: str) -> List[InteractionSummary]:
        """
        List sessions with pagination and sorting - optimized to only read metadata file or first/last events
        """
        sessions_dir = get_session_directory()
        session_dirs = os.listdir(sessions_dir)

        # Get unique session IDs from directories
        session_summaries = []

        for session_id in session_dirs:
            session_dir = os.path.join(sessions_dir, session_id)
            if not os.path.isdir(session_dir):
                continue

            # Find all JSONL files for this session
            jsonl_files = glob.glob(os.path.join(session_dir, "*.jsonl"))
            if not jsonl_files:
                continue
                
            # Check for metadata file first - a faster way to get session info
            metadata_path = os.path.join(session_dir, "session_metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    
                    start_time = datetime.fromisoformat(metadata.get("start_time", "").replace("Z", "+00:00"))
                    end_time = datetime.fromisoformat(metadata.get("end_time", "").replace("Z", "+00:00"))
                    duration_seconds = metadata.get("duration_seconds")
                    event_count = metadata.get("event_count")
                    
                    session_summaries.append(InteractionSummary(
                        id=session_id,
                        start_time=start_time,
                        end_time=end_time,
                        duration_seconds=duration_seconds,
                        event_count=event_count,
                        file_count=len(jsonl_files)
                    ))
                    continue
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    # If metadata file is invalid, fall back to scanning events
                    pass
            
            # Optimize by only reading first and last events from each file
            # instead of loading all events
            start_time = None
            end_time = None
            interaction_count = 0
            
            for file_path in jsonl_files:
                # Count lines to get event count without loading all events
                with open(file_path, 'r') as f:
                    # Count non-empty lines
                    file_lines = sum(1 for line in f if line.strip())
                    interaction_count += file_lines
                
                # Get first event timestamp
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    if first_line:
                        try:
                            first_event = json.loads(first_line)
                            first_timestamp = datetime.fromisoformat(first_event["timestamp"].replace("Z", "+00:00"))
                            if start_time is None or first_timestamp < start_time:
                                start_time = first_timestamp
                        except (json.JSONDecodeError, KeyError, ValueError):
                            pass
                
                # Get last event timestamp
                last_line = ""
                with open(file_path, 'r') as f:
                    # Seek to the end and read backward until we find a complete line
                    try:
                        # Read the last 2KB which should contain the last line in most cases
                        f.seek(max(0, os.path.getsize(file_path) - 2048))
                        chunk = f.read(2048)
                        lines = chunk.split('\n')
                        if lines and lines[-1].strip():
                            last_line = lines[-1].strip()
                        elif len(lines) > 1:
                            last_line = lines[-2].strip()
                    except Exception:
                        # Fall back to reading the whole file if the above fails
                        f.seek(0)
                        last_line = list(filter(None, f.read().split('\n')))[-1]
                
                if last_line:
                    try:
                        last_event = json.loads(last_line)
                        last_timestamp = datetime.fromisoformat(last_event["timestamp"].replace("Z", "+00:00"))
                        if end_time is None or last_timestamp > end_time:
                            end_time = last_timestamp
                    except (json.JSONDecodeError, KeyError, ValueError):
                        pass

            if start_time and end_time:
                duration_seconds = (end_time - start_time).total_seconds()

                # Create a session metadata file for future quick access
                try:
                    metadata = {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "duration_seconds": duration_seconds,
                        "event_count": interaction_count
                    }
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f)
                except Exception:
                    # Continue even if we can't write metadata
                    pass

                session_summaries.append(InteractionSummary(
                    id=session_id,
                    start_time=start_time,
                    end_time=end_time,
                    duration_seconds=duration_seconds,
                    event_count=interaction_count,
                    file_count=len(jsonl_files)
                ))

        # Sort sessions
        if sort_by == "timestamp":
            sort_by = "start_time"

        session_summaries.sort(
            key=lambda x: getattr(x, sort_by),
            reverse=(sort_order.lower() == "desc")
        )

        # Apply pagination
        return session_summaries[offset:offset + limit]

    async def get_session(self, session_id: str) -> Optional[InteractionDetail]:
        """
        Get detailed information about a specific session.
        """
        sessions_dir = get_session_directory()
        session_dir = os.path.join(sessions_dir, session_id)

        if not os.path.isdir(session_dir):
            return None

        # Find all JSONL files for this session
        jsonl_files = glob.glob(os.path.join(session_dir, "*.jsonl"))
        if not jsonl_files:
            return None

        # Initialize session details
        start_time = None
        end_time = None
        event_count = 0
        event_types = {}
        has_thinking = False
        tool_calls = []
        user_id = None
        metadata = {}

        for file_path in jsonl_files:
            events = await read_jsonl_file(file_path)

            for event in events:
                # Count event types
                event_type = event.get("event", {}).get("type")
                if event_type:
                    event_types[event_type] = event_types.get(event_type, 0) + 1

                # Check for thinking
                if event_type == "thought_delta":
                    has_thinking = True

                # Track tool calls
                if event_type == "tool_call":
                    tool_call_data = event.get("event", {}).get("tool_calls", [])
                    for tool_call in tool_call_data:
                        tool_name = tool_call.get("name")
                        if tool_name and tool_name not in tool_calls:
                            tool_calls.append(tool_name)

                # Extract metadata from completion options
                if event_type == "completion_options":
                    metadata_data = event.get("event", {}).get("data", {}).get("metadata", {})
                    if metadata_data:
                        metadata.update(metadata_data)

                    # Extract user ID
                    if "user_id" in metadata_data:
                        user_id = metadata_data["user_id"]

                # Update timestamps
                timestamp = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
                if start_time is None or timestamp < start_time:
                    start_time = timestamp

                if end_time is None or timestamp > end_time:
                    end_time = timestamp

                event_count += 1

        if start_time and end_time:
            duration_seconds = (end_time - start_time).total_seconds()

            return InteractionDetail(
                id=session_id,
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration_seconds,
                event_count=event_count,
                file_count=len(jsonl_files),
                files=[os.path.basename(f) for f in jsonl_files],
                event_types=event_types,
                metadata=metadata,
                user_id=user_id,
                has_thinking=has_thinking,
                tool_calls=tool_calls
            )

        return None

    async def get_session_files(self, session_id: str) -> List[str]:
        """
        Get a list of all JSONL files for a specific session.
        """
        sessions_dir = get_session_directory()
        session_dir = os.path.join(sessions_dir, session_id)

        if not os.path.isdir(session_dir):
            return []

        jsonl_files = glob.glob(os.path.join(session_dir, "*.jsonl"))
        return [os.path.basename(f) for f in jsonl_files]
        
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session directory and all its files.
        """
        sessions_dir = get_session_directory()
        session_dir = os.path.join(sessions_dir, session_id)

        if not os.path.isdir(session_dir):
            return False
            
        try:
            # Use shutil.rmtree to delete the directory and all its contents
            shutil.rmtree(session_dir)
            return True
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return False