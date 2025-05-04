# Events Refactor Plan

After examining the core repository's event models, we need to revise our approach to avoid duplicating event model definitions in our API. This document outlines a plan to properly integrate with the core event models.

## Current Issues

1. We've created our own event models in the API (e.g., `ChatEvent`, `Event`) that duplicate functionality already present in the core repository's `agent_c.models.events` package.

2. Our services are performing unnecessary conversions between V1 event models, core event models, and our custom V2 models.

3. This duplication makes maintenance more difficult and could lead to inconsistencies between the API and core.

## Core Event Models Overview

The Agent C core framework already defines well-structured event models:

1. **BaseEvent** - Foundation for all events with automatic type assignment

2. **SessionEvent** - Events within a chat session with session_id and role

3. **Chat Events**:
   - `InteractionEvent` - Signifies start/end of an interaction
   - `CompletionEvent` - Information about completion API calls
   - `MessageEvent` - Complete message content
   - `TextDeltaEvent` - Chunks of message content
   - `ThoughtDeltaEvent` - Agent's thinking process
   - `HistoryEvent` - Chat history updates

4. **Tool Events**:
   - `ToolCallEvent` - Tool use initiation/completion
   - `ToolCallDeltaEvent` - Incremental tool call information

## Refactor Approach

### Phase 1: Import Core Models

1. Import the core event models directly in our API models package

2. Create any necessary extensions or wrappers while maintaining compatibility

3. Update type annotations and references throughout the codebase

### Phase 2: Refactor Services

1. Update `HistoryService` to work directly with core event models
   - Remove unnecessary conversions between V1/V2 formats
   - Ensure proper typing throughout

2. Update `EventService` to stream events directly without format conversion

3. Refactor any other services that handle events

### Phase 3: Update API Endpoints

1. Update request/response models to use core event types

2. Ensure proper OpenAPI documentation for the event models

3. Update streaming endpoints to use the correct event formats

## Implementation Steps

1. **Model Integration**
   - Create import bridges in our model files
   - Add proper type annotations and ensure consistency
   - Update response models to use or extend core models

2. **Service Updates**
   - Simplify history service to use core models directly
   - Update event service to stream native events
   - Fix any typing issues in service interfaces

3. **Endpoint Adjustments**
   - Update endpoint handlers to work with core model types
   - Ensure proper response serialization
   - Update streaming handlers for compatibility

4. **Documentation**
   - Update API documentation to reference core event models
   - Ensure OpenAPI schemas correctly represent the event models

## Benefits

1. **Reduced Duplication** - Eliminate redundant model definitions

2. **Better Consistency** - Ensure API and core use the same event representations

3. **Easier Maintenance** - Changes to core events automatically flow to API

4. **Simplified Code** - Remove unnecessary conversion logic

## Considerations

1. **Backward Compatibility** - Ensure existing API clients continue to work

2. **Versioning** - Document any changes to event structures

3. **Validation** - Ensure proper validation still occurs for all event payloads

4. **Performance** - Remove any unnecessary serialization/deserialization steps