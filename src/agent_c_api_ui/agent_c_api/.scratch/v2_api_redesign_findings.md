# Agent C API V2 Redesign - Findings Document

## Overview
This document tracks our detailed analysis of each component of the v1 API as we work through our multi-session plan, starting with the core components.

## Session Progress Tracking

### Session 1: Foundation Core Components
- [x] `/core/models.py` - Examined
- [x] `/core/agent_bridge.py` - Examined
- [x] `/core/agent_manager.py` - Examined
- [x] `/core/file_handler.py` - Examined
- [x] `/core/middlewares.py` - Not found, functionality in other files
- [x] `/core/logging.py` - Not found, functionality in util/logging_utils.py
- [x] `/core/util/*` - Examined

### Session 2: Core API Components - Part 1
- [x] `/v1/agent.py` - Examined
- [x] `/v1/models.py` - Examined
- [x] `/v1/personas.py` - Examined

### Session 3: Core API Components - Part 2
- [x] `/v1/sessions.py` - Examined
- [x] `/v1/tools.py` - Examined
- [x] `/v1/chat.py` - Examined

### Session 4: File Management and LLM Models
- [x] `/v1/files.py` - Examined
- [x] `/v1/llm_models/agent_params.py` - Examined
- [x] `/v1/llm_models/tool_model.py` - Examined

### Session 5: Interactions Core
- [x] `/v1/interactions/interactions.py` - Examined
- [x] `/v1/interactions/events.py` - Examined
- [x] `/v1/agent.py` - Re-examined in context of interaction components

### Session 6: Interactions Supporting Components
- [x] `/v1/interactions/interaction_models/event_model.py` - Examined during Session 5
- [x] `/v1/interactions/interaction_models/interaction_model.py` - Examined during Session 5
- [x] `/v1/interactions/services/event_service.py` - Examined during Session 5
- [x] `/v1/interactions/services/interaction_service.py` - Examined during Session 5
- [x] `/v1/interactions/utils/file_utils.py` - Examined during Session 5

### Session 7: API Structure and Support
- [ ] `/v1/__init__.py` - Not yet examined
- [ ] `/api/dependencies.py` - Not yet examined

## Detailed Findings

### Core Components

#### `/core/models.py`

This file contains basic Pydantic models used throughout the API:

- `ChatMessage`: A model representing chat messages with associated metadata:
  - `session_id`: Unique identifier for the chat session
  - `message`: The actual content of the chat message
  - `persona`: The persona or character role for the message
  - `temperature`: Temperature parameter for LLM response generation
  - `llm_model`: Identifier for the specific LLM model to be used

- `FileUploadRequest`: A model for handling file upload requests:
  - `session_id`: Unique identifier for the session associated with the file upload

These models are relatively simple and serve as basic data structures for the API. The limited scope of these models suggests that more complex data structures might be defined elsewhere or created ad-hoc in the API endpoints.

#### `/core/agent_bridge.py`

This file contains the `AgentBridge` class which serves as the core interface between the API and the Agent C library. This is a substantial class (990 lines) that handles the majority of the agent functionality:

- **Session Management**
  - Initializes and manages chat sessions
  - Maintains session context and history

- **Tool Management**
  - Dynamically loads and configures tools based on selections
  - Updates tools during runtime without reinitializing the agent
  - Manages tool execution and results

- **AI Backend Support**
  - Supports multiple AI backends (OpenAI, Claude)
  - Configures model-specific parameters
  - Handles backend-specific event formats

- **Chat Streaming**
  - Processes and streams responses asynchronously
  - Manages different event types (text, tool calls, media, etc.)
  - Formats events into a consistent JSON structure for the client

- **Persona Management**
  - Loads and applies persona settings
  - Supports custom prompts

- **File Integration**
  - Processes files for multimodal capabilities
  - Converts files to appropriate input types (Image, Audio, File)

The `AgentBridge` class primarily serves as a communication layer between the Agent C framework and the API. The event handling methods (`_handle_tool_call`, `_handle_text_delta`, etc.) are focused on relaying events from the agent and tool layers to the UI, not implementing business logic. It serves as the main workhorse for the agent functionality, connecting the UI to the underlying Agent C framework.

#### `/core/agent_manager.py`

This file contains the `UItoAgentBridgeManager` class which manages multiple agent sessions in a thread-safe manner. It serves as a higher-level manager above the individual `AgentBridge` instances:

- **Session Lifecycle Management**
  - Creates new sessions with configured agents
  - Retrieves existing session data
  - Cleans up sessions when they're no longer needed

- **Thread Safety**
  - Uses per-session locks to ensure thread-safe operations
  - Manages concurrent access to session resources

- **Agent Configuration**
  - Configures agents with specified LLM models, backends, and tools
  - Maintains essential tool sets that must be included with all agents

- **Response Streaming**
  - Provides an interface for streaming responses from agents
  - Handles errors and edge cases during streaming

- **Interaction Control**
  - Supports cancellation of ongoing interactions
  - Offers debugging capabilities for troubleshooting sessions

The `UItoAgentBridgeManager` acts as a central repository for active sessions, maintaining a dictionary of session data (`ui_sessions`) and corresponding locks. It provides a clean interface for the API layer to interact with agent sessions without having to manage the complexities of the `AgentBridge` directly.

#### `/core/file_handler.py`

This file handles file operations for the API, consisting of two main classes:

- **FileMetadata**: A data class storing metadata about uploaded files, including:
  - File ID, name, size, MIME type
  - Upload timestamp and session association
  - Processing status and extracted text (if applicable)

- **FileHandler**: The main utility class for file operations:
  - **File Storage**: Saves uploaded files with session association
  - **File Processing**: Extracts text from documents where possible
  - **File Retrieval**: Gets file metadata and content
  - **Multimodal Support**: Converts files to appropriate agent input types (FileInput, ImageInput, AudioInput)
  - **Cleanup**: Manages file retention policies and session-based cleanup

The `FileHandler` provides comprehensive file management capabilities, handling different file types and integrating them with the agent system. It supports the multimodal capabilities of the agents by converting uploaded files to the appropriate input types based on their MIME types.

Interestingly, there appears to be a small `DocumentFileInput` class that extends or replaces the standard `FileInput` with text extraction capabilities, but the implementation is minimal in this file.

#### `/core/middlewares.py`

This file was not found in the codebase. Based on the inspection of other files, middleware functionality appears to be implemented in `core/util/middleware_logging.py` instead, and application middleware is configured in the `setup.py` file.

#### `/core/logging.py`

This file was not found in the codebase. Based on the inspection of other files, logging functionality appears to be implemented in `core/util/logging_utils.py` instead.

#### `/core/util/*`

The utility directory contains support modules for the core functionality:

- **`logging_utils.py`**: Provides a centralized logging system:
  - `LoggingManager`: Creates and configures loggers with consistent formatting
  - `ColoredFormatter`: Adds color to console logs based on log level
  - Debug mode management through shared threading events
  - Configuration for both file and console logging

- **`middleware_logging.py`**: Contains API request/response logging middleware:
  - `APILoggingMiddleware`: Intercepts HTTP requests and logs their details
  - Configurable logging of request/response bodies
  - Performance tracking of request processing time

These utility modules provide essential infrastructure services for the API, ensuring consistent logging and request tracking throughout the application.

### API Endpoints

#### `/v1/agent.py`

This file contains endpoints for managing agent settings and tools within a session context:

- **Agent Settings Management**:
  - `update_agent_settings`: Updates agent parameters (temperature, reasoning_effort, etc.)
    - Accepts a `AgentUpdateParams` object with the parameters to update and the session ID
    - Validates and processes only parameters that were provided (using Pydantic's exclude_unset=True)
    - Meticulously tracks changes made for reporting
    - Reinitializes the agent when parameters change
    - Returns detailed information about changes made, skipped values, and any failed updates

- **Agent Configuration**:
  - `get_agent_config`: Retrieves the configuration of an agent in a specific session
    - Takes a `ui_session_id` path parameter
    - Returns comprehensive configuration including model info, tools, and session IDs
    - Enhances the basic agent config with additional session-related information

- **Tool Management**:
  - `update_agent_tools`: Updates the list of tools for an agent
    - Accepts a `ToolUpdateRequest` with session ID and the new list of tools
    - Validates that the tools list is a proper array
    - Updates the agent's tools and stores the active tool list in the session data
    - Returns success status with the updated tool list and session IDs
  - `get_agent_tools`: Retrieves the list of tools for an agent
    - Takes a `ui_session_id` path parameter
    - Returns the initialized tools list from the agent configuration

- **Debugging**:
  - `debug_agent_state`: Provides information about the agent's state
    - Takes a `ui_session_id` path parameter
    - Returns both the agent bridge parameters and the internal agent parameters for debugging
  - `debug_chat_session`: Retrieves debug information about a chat session
    - Takes a `ui_session_id` path parameter
    - Delegates to the agent manager's debug_session method
    - Returns detailed session debug information

The endpoints in this file operate on agents *within* specific sessions (identified by ui_session_id), creating confusion in the API naming. The file relies heavily on the `UItoAgentBridgeManager` dependency to access and modify session and agent state. The endpoints follow an RPC-style pattern rather than RESTful conventions (e.g., `/update_settings` instead of a PUT or PATCH to a resource).

#### Relevant Supporting Models for `/v1/agent.py`

- **`AgentCommonParams` (in `/v1/llm_models/agent_params.py`)**:
  - Base Pydantic model with common agent parameters
  - Fields include:
    - `persona_name`: Name of the persona to use (defaults to "default")
    - `custom_prompt`: Optional custom prompt for the persona
    - `temperature`: Optional temperature parameter for chat models
    - `reasoning_effort`: Optional reasoning effort parameter for OpenAI models
    - `budget_tokens`: Optional budget tokens parameter for some Claude models

- **`AgentUpdateParams` (in `/v1/llm_models/agent_params.py`)**:
  - Extends `AgentCommonParams` to add session identification
  - Adds `ui_session_id` field to identify which session to update

- **`AgentInitializationParams` (in `/v1/llm_models/agent_params.py`)**:
  - Extends `AgentCommonParams` with parameters for agent initialization
  - Additional fields include:
    - `model_name`: Required name of the model to use
    - `backend`: Optional backend provider (default: "openai")
    - `max_tokens`: Optional maximum tokens for model output
    - `ui_session_id`: Optional existing session ID for transferring chat sessions
  - Implements sophisticated validation and parameter transformation methods:
    - `validate_and_set_defaults`: Sets appropriate defaults based on the selected model
    - `to_agent_kwargs`: Maps parameters to the format expected by the underlying agent
    - `to_additional_params`: Provides additional parameters for session creation

- **`ToolUpdateRequest` (in `/v1/llm_models/tool_model.py`)**:
  - Simple model for tool update requests
  - Fields include:
    - `ui_session_id`: Session ID for the agent to update
    - `tools`: List of tool identifiers to enable for the agent

These models provide a structured approach to parameter validation and transformation, ensuring that the API receives well-formed requests and translates them appropriately for the underlying agent system.

#### `/v1/models.py`

This file contains a single endpoint for listing available models:

- **Model Listing**:
  - `list_models`: Retrieves the list of available models from a configuration file
    - No parameters required
    - Loads models from the `MODELS_CONFIG` imported from the `config_loader` module
    - Transforms the data from a hierarchical structure (grouped by vendor) into a flattened structure for frontend consumption
    - Returns detailed information about each model including ID, label, description, backend, parameters, capabilities, and allowed inputs

The models are loaded from a configuration file (`MODELS_CONFIG`) which is imported from the `config_loader` module. This endpoint doesn't require any session information and doesn't depend on the agent manager, making it a clear candidate for the 'configuration' category in our v2 API design.

The implementation is straightforward - it iterates through the vendors and their models in the configuration, flattening the structure to create a simple list of model objects with all relevant details included.

#### `/v1/personas.py`

This file contains a single endpoint for listing available personas:

- **Persona Listing**:
  - `list_personas`: Retrieves the list of available personas from a directory
    - No parameters required
    - Scans the `PERSONA_DIR` (from settings) for Markdown (.md) files recursively
    - For each persona file, it extracts:
      - A name (derived from the file path, with directory separators replaced by ' - ')
      - The full content of the file (the actual persona definition)
      - The original filename
    - Returns a list of persona objects with name, content, and file information

The personas are loaded from files in a directory specified by the `PERSONA_DIR` setting. Like the models endpoint, this one doesn't require any session information and doesn't depend on the agent manager, also making it a candidate for the 'configuration' category in our v2 API design.

The implementation reads Markdown files from the personas directory, assuming each file represents a persona definition. It transforms the file path into a readable name by replacing directory separators with hyphens, making nested directory structures more presentable.

## Initial Observations

Based on examination of the core components, we can make several key observations about the current architecture:

1. **Centralized Session Management**: The API uses a two-tier approach to session management:
   - `UItoAgentBridgeManager` manages multiple sessions at a high level
   - Individual `AgentBridge` instances handle the details of each session

2. **Comprehensive File Handling**: The `FileHandler` provides robust file operations, supporting various file types and integrating them with the agent system.

3. **Minimal Core Data Models**: The core models are surprisingly minimal, with just `ChatMessage` and `FileUploadRequest` defined in `models.py`. This suggests that most data structures might be defined ad-hoc in API endpoints or in separate modules.

4. **Strong Infrastructure**: The utility modules provide solid logging and middleware infrastructure, indicating a focus on operational visibility.

5. **High Cohesion in Components**: Each core component has clear, focused responsibilities, though the `AgentBridge` class is quite large and handles multiple concerns.

6. **Clean Application Setup**: The `setup.py` file shows a well-structured approach to application configuration, with proper middleware and metadata handling.

7. **Multiple Backend Support**: The core components are designed to work with different LLM backends (OpenAI, Claude), showing flexibility in the architecture.

8. **Configuration-Based Resources**: Both models and personas are loaded from static sources (configuration files and markdown files), not from a database. This indicates a configuration-driven approach for these resources.

9. **API Naming Confusion**: The endpoints in `/v1/agent.py` operate on agents within specific sessions, creating ambiguity about whether they're session management or agent management endpoints. This confirms our initial observation about confusing terminology.

10. **Mix of API Styles**: Some endpoints follow a RESTful pattern, while others are more RPC-like. For instance, `/v1/agent.py` has `/update_settings` (RPC-style) rather than a more RESTful approach using HTTP methods on resources.

11. **Detailed Parameter Handling**: The agent parameter models in `/v1/llm_models/agent_params.py` show sophisticated validation and transformation logic, accommodating different LLM backends with their specific parameter requirements.

12. **Thorough Error Handling**: The endpoints include comprehensive error handling with appropriate HTTP status codes and detailed error messages, showing a focus on API robustness.

13. **Debug-Friendly Design**: The inclusion of specific debugging endpoints indicates a developer-friendly approach, facilitating troubleshooting and development.

These observations reinforce the need for a cleaner API design in v2, with consistent naming, logical grouping of endpoints, and clear separation of concerns.

#### `/v1/sessions.py`

This file contains endpoints for session management:

- **Session Initialization**:
  - `initialize_agent`: Creates a new agent session with specified parameters
    - Takes an `AgentInitializationParams` object with model name, backend, etc.
    - Supports transferring chat history from an existing session if `ui_session_id` is provided
    - Returns both the UI session ID and the internal Agent C session ID
  
- **Session Verification**:
  - `verify_session`: Checks if a session exists and is valid
    - Takes a `ui_session_id` path parameter
    - Returns a simple boolean indicating validity

- **Session Deletion**:
  - `delete_all_sessions`: Removes all active sessions
    - Requires no parameters
    - Cleans up resources for all sessions
    - Returns the count of deleted sessions

The file shows naming inconsistency with the first endpoint being called `initialize_agent` when it's actually creating a session (with an agent configured). There's also no endpoint for deleting a single session, which seems like an oversight. The endpoints follow a mix of RESTful and RPC patterns, with inconsistent path naming (`/initialize` vs `/sessions`).

#### `/v1/tools.py`

This file contains a single endpoint for listing available tools:

- **Tool Listing**:
  - `tools_list`: Retrieves all available tools from the Agent C Toolset registry
    - Takes no parameters
    - Dynamically discovers tools from the Toolset registry
    - Categorizes tools by module namespace (Core, Demo, Voice, RAG)
    - Identifies 'essential' tools that are required for basic functionality
    - Returns a structured object with tool categories and details

The file also handles conditional imports of optional tool modules (agent_c_demo, agent_c_rag), gracefully handling cases where these components aren't installed. The endpoint follows a REST-style GET pattern for a collection (`/tools`).

Tools are treated as configuration items rather than mutable resources - they can be listed and selected but not created or modified through the API. Each tool entry includes name, module, documentation, and 'essential' status.

#### `/v1/chat.py`

This file contains endpoints for the core chat functionality:

- **Chat Interaction**:
  - `chat_endpoint`: Handles sending messages to the agent and streaming responses
    - Takes form parameters `ui_session_id`, `message`, and optional `file_ids`
    - Verifies the session exists
    - Parses file IDs if provided
    - Returns a streaming response that yields tokens in real-time
    - Uses appropriate headers to ensure proper streaming behavior

- **Interaction Cancellation**:
  - `cancel_chat`: Cancels an ongoing chat interaction
    - Takes a `ui_session_id` form parameter
    - Verifies the session exists
    - Calls the agent_manager to cancel the interaction
    - Returns a JSON response with the cancellation status

The endpoints follow an RPC-style pattern (`/chat` and `/cancel`) rather than RESTful resource paths. Parameters are provided as form data rather than JSON. The file includes commented-out alternative streaming configurations, suggesting challenges with different environments handling streaming responses.

The core functionality is the streaming chat, which allows real-time responses from the agent and supports attaching files to messages. Both endpoints include thorough error handling and detailed logging.

## Connection Points

- **Agent Bridge and API Endpoints**: The `/v1/agent.py` endpoints directly interact with the `AgentBridge` class via the `UItoAgentBridgeManager`. This shows a tight coupling between the API layer and the agent management layer.

- **Configuration and API**: The `/v1/models.py` and `/v1/personas.py` endpoints rely on static configuration sources, not directly interacting with the core agent components. This indicates a cleaner separation for these resources.

- **Session and Agent Relationship**: The API endpoints in `/v1/agent.py` clearly demonstrate the tight coupling between sessions and agents, where agent operations always occur within a session context.

- **Parameter Models and Agent Integration**: The parameter models defined in `/v1/llm_models/agent_params.py` show careful design to bridge between API requests and the specific requirements of different LLM backends, providing flexibility while maintaining a consistent API interface.

#### `/v1/files.py`

This file contains endpoints for file management within sessions:

- **File Upload**:
  - `upload_file`: Handles file uploads for a specific session
    - Takes form parameters `ui_session_id` and a file attachment
    - Verifies the session exists
    - Saves the file and associates it with the session
    - Sets the file handler on the agent if it doesn't already have one
    - Processes the file in the background for text extraction
    - Returns metadata about the uploaded file

- **File Listing**:
  - `get_session_files`: Lists all files for a specific session
    - Takes a `ui_session_id` path parameter
    - Verifies the session exists
    - Returns detailed information about all files for the session

- **File Retrieval**:
  - `get_file`: Retrieves a specific file
    - Takes `ui_session_id` and `file_id` path parameters
    - Verifies the session exists
    - Returns metadata about the requested file (missing actual file download functionality)

- **File Deletion**:
  - `delete_file`: Deletes a specific file
    - Takes `ui_session_id` and `file_id` path parameters
    - Verifies the session exists
    - Deletes the file both from storage and from the session's file list
    - Returns a success message

The file also includes a background task for cleaning up expired files based on the retention policy (7 days). The endpoints consistently verify session existence before processing file operations, showing a clear tie between files and sessions. All file operations use appropriate error handling with HTTP status codes.

Interestingly, the `get_file` endpoint appears to not actually return the file content, but only its metadata - which seems like a potential oversight.

Review note: WE will rename this `get_file_meta`

#### `/v1/llm_models/agent_params.py`

This file contains Pydantic models for agent parameters:

- **`AgentCommonParams`**:
  - Base model with common agent parameters
  - Fields include:
    - `persona_name`: Name of the persona to use (defaults to "default")
    - `custom_prompt`: Optional custom prompt for the persona
    - `temperature`: Optional temperature parameter for chat models
    - `reasoning_effort`: Optional reasoning effort parameter for OpenAI models
    - `budget_tokens`: Optional budget tokens parameter for some Claude models

- **`AgentUpdateParams`**:
  - Extends `AgentCommonParams` to add session identification
  - Adds `ui_session_id` field to identify which session to update

- **`AgentInitializationParams`**:
  - Extends `AgentCommonParams` with parameters for agent initialization
  - Additional fields include:
    - `model_name`: Required name of the model to use
    - `backend`: Optional backend provider (default: "openai")
    - `max_tokens`: Optional maximum tokens for model output
    - `ui_session_id`: Optional existing session ID for transferring chat sessions
  - Implements sophisticated validation and parameter transformation methods:
    - `validate_and_set_defaults`: Sets appropriate defaults based on the selected model
    - `to_agent_kwargs`: Maps parameters to the format expected by the underlying agent
    - `to_additional_params`: Provides additional parameters for session creation

The models in this file provide a structured approach to parameter validation and transformation, ensuring that the API receives well-formed requests and translates them appropriately for the underlying agent system. The validation logic is particularly sophisticated, handling different model types and their specific parameter requirements.

#### `/v1/llm_models/tool_model.py`

This file contains a single, simple model for tool updates:

- **`ToolUpdateRequest`**:
  - Basic model for tool update requests
  - Fields include:
    - `ui_session_id`: Session ID for the agent to update
    - `tools`: List of tool identifiers to enable for the agent

The minimal nature of this model reflects the simple structure of tool update requests, where only a session ID and a list of tool names are required.

#### `/v1/interactions/interactions.py`

This file implements an API router for managing chat interaction logs:

- **Interaction Listing**:
  - `list_sessions`: Lists all available interaction sessions with pagination and sorting
    - Takes optional query parameters for pagination (`limit`, `offset`) and sorting (`sort_by`, `sort_order`)
    - Returns a list of `InteractionSummary` objects with basic information about each session

- **Interaction Retrieval**:
  - `get_session`: Gets detailed information about a specific interaction session
    - Takes a `session_id` path parameter
    - Returns an `InteractionDetail` object with comprehensive information including files, event types, metadata, etc.

- **Session Files Retrieval**:
  - `get_session_files`: Gets a list of all JSONL files associated with a specific session
    - Takes a `session_id` path parameter
    - Returns a list of file names

- **Session Deletion**:
  - `delete_session`: Deletes a session directory and all its files
    - Takes a `session_id` path parameter
    - Returns a success status message

The router uses the `InteractionService` for session operations, abstracting the underlying storage and retrieval logic. It primarily provides read access to historical chat interactions, with the exception of the delete operation. The routes follow RESTful conventions more closely than some other parts of the API.

#### `/v1/interactions/events.py`

This file implements an API router for working with individual events within interaction sessions:

- **Event Retrieval**:
  - `get_events`: Retrieves events for a specific session with filtering options
    - Takes a `session_id` path parameter and optional query parameters for filtering (`event_types`, `start_time`, `end_time`, `limit`)
    - Returns a list of `Event` objects

- **Event Streaming**:
  - `stream_events`: Streams events for a specific session, optionally in real-time
    - Takes a `session_id` path parameter and optional query parameters for filtering and playback options (`event_types`, `real_time`, `speed_factor`)
    - Returns a streaming response with server-sent events

- **Replay Status**:
  - `get_replay_status`: Gets the current status of a session replay
    - Takes a `session_id` path parameter
    - Returns the current replay status (position, playing/paused, etc.)

- **Replay Control**:
  - `control_replay`: Controls a session replay (play, pause, stop, seek)
    - Takes a `session_id` path parameter and a `ReplayControlRequest` body
    - Returns a success status with the action performed

This router is focused on the detailed events within a session, particularly for replay and analysis purposes. It works with the `EventService` for event operations. The streaming capabilities are notable, allowing for real-time replay of session events at adjustable speeds.

#### `/v1/interactions/interaction_models`

This directory contains models for interaction data:

- **`event_model.py`**:
  - `ReplayControlRequest`: Model for controlling replay operations (play, pause, stop, seek)
  - `EventType`: Enum of possible event types (system_prompt, completion, thought_delta, etc.)
  - `Event`: Comprehensive model for individual interaction events with timestamps, content, and metadata

- **`interaction_model.py`**:
  - `InteractionSummary`: Basic model for session summary information (ID, timestamps, counts)
  - `InteractionDetail`: Extended model with detailed session information (files, event types, metadata, etc.)

These models provide a structured representation of interaction data, supporting both summary-level viewing of sessions and detailed examination of individual events.

#### `/v1/interactions/services`

This directory contains service classes that implement the business logic for interaction operations:

- **`event_service.py`**:
  - `EventService`: Manages event-related operations:
    - Retrieving filtered events from session files
    - Streaming events with real-time timing options
    - Controlling replay operations (play, pause, stop, seek)
    - Creating structured Event objects from raw data

- **`interaction_service.py`**:
  - `InteractionService`: Manages session-level operations:
    - Listing sessions with pagination and sorting
    - Retrieving detailed session information
    - Getting files associated with a session
    - Deleting sessions and their files
    - Reading and parsing JSONL log files

These services abstract the storage details and provide a clean interface for the API routers to work with. They handle the complexities of file operations, JSON parsing, and data transformation.

#### `/v1/interactions/utils`

This directory contains utility functions for working with interaction files:

- **`file_utils.py`**:
  - `get_session_directory`: Gets the path to the sessions directory
  - `read_jsonl_file`: Reads and parses a JSONL file into a list of dictionaries

These utilities provide basic file operations for the interaction services, particularly for locating and reading session log files.

## Design Recommendations

(This section will contain our recommendations for the v2 API design based on findings)