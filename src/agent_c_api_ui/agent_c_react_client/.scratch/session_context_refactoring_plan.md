# SessionContext Refactoring Plan

This document outlines a detailed, incremental approach to refactoring the monolithic SessionContext into separate, focused contexts with a clean API service layer.

## Guiding Principles

1. **Incremental Changes** - Make small, focused changes that can be tested independently
2. **Backwards Compatibility** - Maintain backward compatibility during transition
3. **Separation of Concerns** - Each context should have a single responsibility
4. **Clear Interfaces** - Well-defined interfaces between contexts
5. **Testability** - Each change should be easily testable

## Phase 1: Create API Service Layer

**Goal**: Separate API calls from state management to create a clean service layer.

### Implementation Steps

1. Create a new `services` directory with:
   - `api.js` - Core API methods (fetch wrapper with error handling)
   - `session-api.js` - Session-specific API calls
   - `model-api.js` - Model-specific API calls
   - `tools-api.js` - Tool-specific API calls

2. Move API interaction code from SessionContext to appropriate service files

3. Update SessionContext to use the new service layer

### Verification

- All existing functionality should continue working
- API calls should be routed through the service layer
- Error handling should be improved and consistent

## Phase 2: Create Core SessionContext

**Goal**: Extract core session management into a dedicated context.

### Implementation Steps

1. Create `SessionContext.jsx` with core session state:
   - `sessionId`
   - `isReady`
   - `isInitialized`
   - `error`

2. Implement core functions:
   - `initializeSession()`
   - `handleSessionsDeleted()`

3. Update the monolithic context to use the new context internally

### Verification

- Session initialization should work correctly
- Session deletion should work correctly
- No changes to component behavior

## Phase 3: Create ModelContext

**Goal**: Extract model configuration into a dedicated context.

### Implementation Steps

1. Create `ModelContext.jsx` with model state:
   - `modelConfigs`
   - `modelName`
   - `selectedModel`
   - `modelParameters`
   - `personas`
   - `persona`
   - `customPrompt`

2. Implement model functions:
   - `updateModelSettings()`
   - `updatePersonaSettings()`
   - `updateParameterSettings()`

3. Make ModelContext consume SessionContext

4. Update the monolithic context to use the new context internally

### Verification

- Model selection should work correctly
- Persona selection should work correctly
- Parameter updates should work correctly

## Phase 4: Create UIStateContext

**Goal**: Extract UI state management into a dedicated context.

### Implementation Steps

1. Create `UIStateContext.jsx` with UI state:
   - `isOptionsOpen`
   - `isStreaming`
   - `isLoading`
   - `settingsVersion`

2. Implement UI functions:
   - `handleProcessingStatus()`
   - `setIsOptionsOpen()`

3. Update the monolithic context to use the new context internally

### Verification

- Options panel should open/close correctly
- Loading indicators should display correctly
- Streaming status should be tracked correctly

## Phase 5: Create ToolsContext

**Goal**: Extract tool management into a dedicated context.

### Implementation Steps

1. Create `ToolsContext.jsx` with tools state:
   - `availableTools`
   - `activeTools`

2. Implement tools functions:
   - `fetchAgentTools()`
   - `handleEquipTools()`

3. Make ToolsContext consume SessionContext

4. Update the monolithic context to use the new context internally

### Verification

- Tool fetching should work correctly
- Tool equipping should work correctly

## Phase 6: Update Components to Use New Contexts

**Goal**: Migrate components from monolithic context to specific contexts.

### Implementation Steps

1. Update `PersonaSelector.jsx` to use ModelContext
2. Update `CollapsibleOptions.jsx` to use multiple contexts
3. Update `ChatInterface.jsx` to use multiple contexts
4. Update `ToolSelector.jsx` to use ToolsContext
5. Update remaining components as needed

### Verification

- All components should function exactly as before
- Components should consume only the contexts they need

## Phase 7: Remove Monolithic Context

**Goal**: Complete the migration by removing the transitional monolithic context.

### Implementation Steps

1. Ensure all components use the new contexts
2. Remove the monolithic context provider
3. Update the main App component to include all the new context providers

### Verification

- Application should function with only the new contexts
- No references to the old monolithic context should remain

## Potential Challenges

1. **Context Dependencies**: Managing dependencies between contexts (e.g., ToolsContext needing sessionId from SessionContext)
2. **Component Updates**: Ensuring all components are updated to use the appropriate contexts
3. **Initialization Order**: Maintaining proper initialization order between contexts
4. **Testing**: Creating effective tests for each phase

## Mitigation Strategies

1. **Context Composition**: Nest context providers to handle dependencies
2. **HOCs or Custom Hooks**: Create higher-order components or custom hooks to simplify context consumption
3. **Monitoring**: Add temporary logging to track context usage and dependencies
4. **Parallel Implementations**: Maintain both implementations during transition

## Timeline

Each phase should take approximately 1 week:

- **Phase 1** (API Service Layer): 1 week
- **Phase 2-5** (Individual Contexts): 4 weeks
- **Phase 6** (Component Updates): 2 weeks
- **Phase 7** (Cleanup): 1 week

Total estimated time: 8 weeks