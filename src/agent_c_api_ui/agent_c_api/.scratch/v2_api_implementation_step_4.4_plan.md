# Implementation Step 4.4: Events Refactoring

Based on our recent discovery that we were duplicating event models that already exist in the Agent C core framework, we need to refactor our approach to properly integrate with the existing event structures.

## What are we changing?

We're updating our event handling in the API to directly use the event models from `agent_c.models.events` instead of creating our own duplicate models. This impacts:

1. **Event Models** - Replacing our custom models with imports from the core framework
2. **Service Layer** - Updating services to work directly with core event types
3. **API Endpoints** - Ensuring endpoints correctly handle the core event types

## How are we changing it?

### 1. Model Updates

#### 1.1 Update `chat_models.py`

Instead of defining our own `ChatEvent` class, we'll import the relevant event models from the core framework:

```python
# Import core event models
from agent_c.models.events.base import BaseEvent
from agent_c.models.events.chat import (
    InteractionEvent, CompletionEvent, MessageEvent, 
    SystemMessageEvent, TextDeltaEvent, ThoughtDeltaEvent,
    HistoryEvent
)
from agent_c.models.events.tool_calls import ToolCallEvent, ToolCallDeltaEvent
```

We'll update our `ChatEventType` enum to match the types used in the core models or replace it entirely with direct references to the core event types.

#### 1.2 Update `history_models.py`

Similarly, we'll update our history models to use or extend the core event types:

```python
# Instead of defining our own Event class
from agent_c.models.events.base import BaseEvent
from agent_c.models.events.session_event import SessionEvent
```

### 2. Service Updates

#### 2.1 Update `HistoryService`

The service will be simplified to work directly with core event models:

- Remove conversions between V1 event types and our custom V2 models
- Update return types to use core event models
- Ensure proper typing throughout

#### 2.2 Update `EventService`

The event service will stream events directly in the core format:

- Remove unnecessary format conversions
- Update streaming methods to provide proper typing
- Update control methods to match core event structures

### 3. API Endpoint Updates

We'll update the endpoints to properly handle the core event types:

- Update request/response type annotations
- Ensure proper event serialization
- Update streaming handlers for compatibility

## Why are we changing it?

1. **Eliminate Duplication** - We're removing unnecessary duplication of event models

2. **Ensure Consistency** - Using the same event models throughout the entire system ensures consistency

3. **Simplify Maintenance** - By using the core models directly, changes to the event structure in the core are automatically reflected in the API

4. **Improve Code Quality** - Removing unnecessary conversion logic simplifies our codebase

## Implementation Steps

1. Update `chat_models.py` to import and use core event models
2. Update `history_models.py` to use core event types
3. Refactor `HistoryService` to work with core models
4. Update `EventService` to stream core event types
5. Update API endpoints to handle core event types properly
6. Update tests to work with the core event models

## Testing Approach

1. Update existing tests to work with the core event models
2. Verify that all endpoints still return the expected data
3. Test streaming endpoints to ensure they correctly deliver events in the proper format
4. Verify backward compatibility with existing API clients