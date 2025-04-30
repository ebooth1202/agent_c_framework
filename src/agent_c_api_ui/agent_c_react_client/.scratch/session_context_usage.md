# SessionContext Usage Analysis

This document tracks how each component in the chat_interface directory uses the SessionContext.

## Session Context Structure

The SessionContext is a complex React context that manages multiple aspects of the application state:

### State Variables

#### Global Session & UI State
- `sessionId`: Current session identifier
- `error`: Error state for the application
- `settingsVersion`: Counter that increments when settings are updated
- `isOptionsOpen`: Controls visibility of options panel
- `isStreaming`: Indicates if message streaming is in progress
- `isLoading`: Loading state for the application
- `isInitialized`: Indicates if the context has been initialized
- `isReady`: Indicates if the session is ready for interaction
- `theme`: Current theme (light/dark/system)

#### Agent Settings & Configuration
- `persona`: Current persona name
- `temperature`: Temperature parameter for model
- `customPrompt`: Custom system prompt
- `modelConfigs`: Available model configurations
- `modelName`: Current model name
- `modelParameters`: Model-specific parameters
- `selectedModel`: Complete model configuration object

#### Data From Backend
- `personas`: Available personas
- `availableTools`: Available tools from backend
- `activeTools`: Currently equipped tools

### Key Functions

#### Initialization & Settings
- `fetchInitialData()`: Fetches initial data from backend
- `initializeSession()`: Initializes or reinitializes a session
- `updateAgentSettings()`: Updates agent settings (model, parameters, etc.)
- `saveConfigToStorage()`: Saves current configuration to localStorage

#### Tool Management
- `fetchAgentTools()`: Fetches currently equipped tools
- `handleEquipTools()`: Equips/unequips tools

#### UI State Management
- `handleProcessingStatus()`: Updates processing status
- `handleSessionsDeleted()`: Handles session deletion
- `handleThemeChange()`: Updates theme

### API Interactions

The context makes several API calls:
- `/initialize`: Create new session or update existing session
- `/personas`: Fetch available personas
- `/tools`: Fetch available tools
- `/models`: Fetch available models
- `/get_agent_tools/{sessionId}`: Get currently equipped tools
- `/update_settings`: Update session settings
- `/update_tools`: Update equipped tools

## Component Dependencies

### AgentConfigDisplay.jsx

**Overview**: Component that fetches and displays agent configuration in a tooltip.

**SessionContext Usage**:
- **State Variables Used**:
  - `sessionId`: Used to fetch agent configuration data
  - `settingsVersion`: Used to trigger refresh of configuration data

- **API Interactions**:
  - Makes API requests to `/get_agent_config/${sessionId}` to fetch agent configuration

- **Important Notes**:
  - This component doesn't directly use SessionContext but expects `sessionId` and `settingsVersion` as props
  - Provides detailed display of agent configuration including model, tools, and session IDs

### AgentConfigHoverCard.jsx

**Overview**: Enhanced version of AgentConfigDisplay that shows configuration in a hover card.

**SessionContext Usage**:
- **State Variables Used**:
  - `sessionId`: Used to fetch agent configuration data
  - `settingsVersion`: Used to trigger refresh of configuration data

- **API Interactions**:
  - Makes API requests to `/get_agent_config/${sessionId}` to fetch agent configuration

- **Important Notes**:
  - Similar to AgentConfigDisplay but with a different UI presentation
  - Requires `sessionId` and `settingsVersion` props that typically come from SessionContext

### AnimatedStatusIndicator.jsx

**Overview**: Simple visual indicator showing processing state with animation.

**SessionContext Usage**:
- **State Variables Used**: None directly

- **Functions Called**: None

- **Important Notes**:
  - Extremely simple component that takes an `isProcessing` prop
  - No direct dependencies on SessionContext

### AssistantMessage.jsx

**Overview**: Displays messages from the AI assistant with formatting and tools.

**SessionContext Usage**:
- **State Variables Used**: None directly

- **Functions Called**: None directly

- **Important Notes**:
  - Specialized component for rendering assistant messages
  - No direct dependencies on SessionContext
  - Handles tool calls display and token usage

### ChatInputArea.jsx

**Overview**: Component for user input, message sending, and file uploading.

**SessionContext Usage**:
- **State Variables Used**: None directly - receives everything as props
- **Functions Called**: None directly

- **Important Notes**:
  - This component is decoupled from SessionContext and receives all state/functions via props
  - It doesn't directly access SessionContext but calls functions that may update it
  - Good example of component with clean separation from context

### ChatInterface.jsx

**Overview**: Main container component for the chat interface.

**SessionContext Usage**:
- **State Variables Used**: 
  - `sessionId`: Used for API calls and to identify the current session
  - `isReady`: Used to determine if the chat is ready for interaction
  - `activeTools`: Used to display tool information in the StatusBar
  - `settingsVersion`: Used to trigger UI updates when settings change
  - `isOptionsOpen`: Used to control the visibility of the options panel
  - `setIsOptionsOpen`: Used to toggle the options panel
  - `isInitialized`: Passed to CollapsibleOptions component
  - `customPrompt`: Used in API calls
  - `modelName`: Used in API calls and passed to CollapsibleOptions
  - `modelParameters`: Used in API calls and passed to CollapsibleOptions
  - `selectedModel`: Passed to CollapsibleOptions
  - `persona`: Passed to CollapsibleOptions
  - `personas`: Passed to CollapsibleOptions
  - `availableTools`: Passed to CollapsibleOptions

- **Functions Called**:
  - `handleProcessingStatus`: Called to update streaming status
  - `handleEquipTools`: Passed to CollapsibleOptions for tool management
  - `updateAgentSettings`: Passed to CollapsibleOptions for settings updates

- **API Interactions**:
  - Makes API requests to `/chat` to send messages
  - Makes API requests to `/cancel` to cancel streaming responses
  - Makes API requests to `/upload_file` to upload files
  - Makes API requests to `/files/{sessionId}` to check file processing status

### CollapsibleOptions.jsx

**Overview**: Collapsible panel that contains PersonaSelector and ToolSelector components.

**SessionContext Usage**:
- **State Variables Used**:
  - `isOptionsOpen`: Controls whether the panel is expanded
  - `setIsOptionsOpen`: Function to toggle panel visibility
  - `persona`: Passed to PersonaSelector
  - `customPrompt`: Passed to PersonaSelector
  - `modelName`: Passed to PersonaSelector
  - `modelConfigs`: Passed to PersonaSelector
  - `modelParameters`: Passed to PersonaSelector
  - `selectedModel`: Passed to PersonaSelector
  - `sessionId`: Passed to child components
  - `personas`: Passed to PersonaSelector
  - `availableTools`: Passed to ToolSelector
  - `activeTools`: Passed to ToolSelector
  - `isReady`: Passed to ToolSelector
  - `isInitialized`: Passed to PersonaSelector

- **Functions Called**:
  - `updateAgentSettings`: Passed to PersonaSelector
  - `handleEquipTools`: Passed to ToolSelector as `onEquipTools`

- **Important Notes**:
  - Acts as a bridge between SessionContext and configuration components (PersonaSelector, ToolSelector)
  - Manages tab state between settings and tools sections

### CopyButton.jsx
*To be analyzed*

### DragDropArea.jsx

**Overview**: Provides a drag-and-drop file upload interface with visual feedback.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None

- **Important Notes**:
  - This is a pure UI component with no direct SessionContext dependencies
  - Handles file drops and passes them to parent components

### DragDropOverlay.jsx
*To be analyzed*

### ExportHTMLButton.jsx
*To be analyzed*

### FileItem.jsx
*To be analyzed*

### FilesPanel.jsx
*To be analyzed*

### FileUploadManager.jsx

**Overview**: Manages file uploads, processing status, and selection.

**SessionContext Usage**:
- **State Variables Used**:
  - `sessionId`: Used for API calls to upload files

- **API Interactions**:
  - Makes API requests to `/upload_file` to upload files
  - Makes API requests to `/files/{sessionId}` to check file processing status

- **Important Notes**:
  - Maintains its own local state for files and selection
  - Receives `sessionId` as a prop from parent components
  - Provides file management functionality to the chat interface

### MarkdownMessage.jsx
*To be analyzed*

### MediaMessage.jsx
*To be analyzed*

### MessageItem.jsx

**Overview**: Factory component that renders different message types based on message properties.

**SessionContext Usage**:
- **State Variables Used**: None directly

- **Functions Called**: None directly

- **Important Notes**:
  - Acts as a router for different message types (user, assistant, system, tool calls, etc.)
  - No direct dependencies on SessionContext 
  - Renders specialized message components like UserMessage, AssistantMessage, etc.

### MessagesList.jsx

**Overview**: Displays the list of chat messages with auto-scrolling functionality.

**SessionContext Usage**:
- **State Variables Used**: None directly

- **Functions Called**: None directly

- **Important Notes**:
  - Acts as a container for message items
  - No direct dependencies on SessionContext but renders items that might access it
  - Handles auto-scrolling and expansion of tool calls

### ModelIcon.jsx
*To be analyzed*

### ModelParameterControls.jsx

**Overview**: Component for adjusting model-specific parameters like temperature and reasoning effort.

**SessionContext Usage**:
- **State Variables Used**:
  - `modelParameters`: Used to initialize local state for various parameters
  - `selectedModel`: Used to determine available parameters and their configurations

- **Functions Called**:
  - No direct SessionContext functions called, but calls parent's `onParameterChange` callback which typically calls `updateAgentSettings('PARAMETER_UPDATE', {...})` 

- **State Updates (Indirect)**:
  - Updates `modelParameters.temperature` through callbacks
  - Updates `modelParameters.reasoning_effort` through callbacks
  - Updates `modelParameters.extended_thinking` through callbacks
  - Updates `modelParameters.budget_tokens` through callbacks

- **Important Notes**:
  - Relies on specific structure of `selectedModel.parameters` 
  - Adapts UI based on model type (showing different controls for different models)
  - Does not directly use SessionContext but is tightly coupled to its data structures

### PersonaSelector.jsx

**Overview**: Component for selecting and configuring AI personas and models.

**SessionContext Usage**:
- **State Variables Used**:
  - `persona`: Current persona name (received as `persona_name` prop)
  - `customPrompt`: Current custom system prompt
  - `modelName`: Current model identifier
  - `modelConfigs`: Available model configurations
  - `modelParameters`: Current parameter settings for the model
  - `selectedModel`: Complete configuration object for the current model
  - `isInitialized`: Used to sync local state with context

- **Functions Called**:
  - `updateAgentSettings`: Called when changing:  
    - Model (`MODEL_CHANGE`)
    - Persona (`SETTINGS_UPDATE`)
    - Custom prompt (`SETTINGS_UPDATE`)
    - Model parameters (`PARAMETER_UPDATE`)

- **State Updates**:
  - Updates `modelName` when model changes
  - Updates `persona` when persona changes
  - Updates `customPrompt` when custom prompt changes
  - Updates `modelParameters` when parameters change

- **Important Notes**:
  - This component is critical for model configuration and would be affected by any changes to the context structure
  - It depends on specific format of the `updateAgentSettings` function with its type parameter

### StatusBar.jsx

**Overview**: Component that displays session status, active tools, and provides export options.

**SessionContext Usage**:
- **State Variables Used**:
  - `isReady`: Used to determine status display
  - `activeTools`: Used to show equipped tools count and names
  - `sessionId`: Used for AgentConfigHoverCard
  - `settingsVersion`: Passed to AgentConfigHoverCard for refresh logic

- **Functions Called**: None directly

- **Important Notes**:
  - Primarily consumes SessionContext state for display purposes
  - Uses AgentConfigHoverCard which may have additional SessionContext dependencies

### SystemMessage.jsx

**Overview**: Displays system messages and errors with consistent styling.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None

- **Important Notes**:
  - Specialized component for system messages and error notifications
  - No direct dependencies on SessionContext

### ThoughtDisplay.jsx

**Overview**: Displays AI thinking/reasoning processes in a visually distinct container.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None

- **Important Notes**:
  - Specialized message display component for reasoning processes
  - No direct dependencies on SessionContext

### TokenUsageDisplay.jsx

**Overview**: Displays token usage statistics for AI responses.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None

- **Important Notes**:
  - Simple presentation component that displays token usage information
  - No direct dependencies on SessionContext

### ToolCallContext.jsx

**Overview**: Separate context provider for managing tool call state.

**SessionContext Usage**:
- **State Variables Used**: None - This is a separate context system
- **Functions Called**: None

- **Important Notes**:
  - This is a separate context that doesn't directly interact with SessionContext
  - Implements its own provider/consumer pattern for tool call management
  - Demonstrates a good pattern for how session context could be refactored into smaller contexts

### ToolCallDisplay.jsx
*To be analyzed*

### ToolCallItem.jsx
*To be analyzed*

### ToolCallManager.jsx

**Overview**: A component that manages tool call state and processing.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None directly

- **Important Notes**:
  - Similar to ToolCallContext.jsx but uses render props pattern instead of context
  - Provides tool call state management functionality but doesn't directly use SessionContext
  - Another example of separation of concerns that could be a model for SessionContext refactoring

### ToolSelector.jsx

**Overview**: Component for selecting and equipping tools for the agent.

**SessionContext Usage**:
- **State Variables Used**:
  - `availableTools`: List of all available tools organized by categories
  - `activeTools`: Currently equipped tools
  - `sessionId`: Used to verify if session is valid
  - `isReady`: Used to determine if tools can be equipped

- **Functions Called**:
  - `handleEquipTools`: Called when equipping tools (received as `onEquipTools` prop)

- **API Interactions**:
  - Triggers API request to `/update_tools` indirectly through `handleEquipTools`

- **Important Notes**:
  - The tool selection state is independent of SessionContext but synchronizes with it on submit
  - Uses local state for tracking selected tools before committing to context

### UserMessage.jsx

**Overview**: Displays user messages with consistent styling and formatting.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None

- **Important Notes**:
  - Specialized component for displaying user messages
  - No direct dependencies on SessionContext

### utils/htmlChatFormatter.jsx

**Overview**: Utilities for formatting chat messages as HTML for copying.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None

- **Important Notes**:
  - Pure utility functions with no direct SessionContext dependencies
  - Provides HTML and text formatting for message export functionality

### utils/MessageStreamProcessor.js

**Overview**: Utility for processing streaming message events from the chat API.

**SessionContext Usage**:
- **State Variables Used**: None directly
- **Functions Called**: None

- **Important Notes**:
  - Pure utility function with no direct SessionContext dependencies
  - Processes different event types from the streaming API
  - Calls appropriate handler functions based on event type