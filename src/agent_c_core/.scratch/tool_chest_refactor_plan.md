# ToolChest Refactoring Plan

## Current Issues

1. The ToolChest currently only supports "active" tools, with no distinction between "available" and "active" tools.
2. The shortcut taken to make all available tools active is causing problems with tool initialization.
3. There's no concept of "essential" tools that should always be equipped.
4. The current implementation requires reinitializing the entire ToolChest when changing which tools are active.
5. The `post_init` method is called on every tool during initialization, which can be expensive for tools that aren't needed immediately.

## Proposed Solution Architecture

### New Properties and Member Variables

```python
# In ToolChest class
__toolset_instances: dict[str, Toolset]       # All instantiated toolsets (available)
__active_toolset_instances: dict[str, Toolset] # Currently active toolsets
__essential_toolset_names: list[str]          # Toolsets that should always be active
__available_toolset_classes: list[Type[Toolset]] # All available toolset classes
__toolsets_awaiting_init: dict[str, Toolset]  # Toolsets created but awaiting post_init
__init_kwargs: dict                           # Stored kwargs from last init_tools call
```

### Refactored Methods

1. **Constructor** (`__init__`)
   - Accept `available_toolsets` (replaces current `tool_classes`)
   - Accept new `essential_toolsets` parameter
   - Initialize the data structures above

2. **New Method**: `activate_toolset(toolset_name_or_names: Union[str, List[str]], **kwargs)`
   - Handles activation of one or more toolsets by name
   - Lazily initializes toolsets if they haven't been initialized yet
   - Calls `post_init` only when a toolset is being activated
   - Supports supplying different init parameters per call

3. **New Method**: `deactivate_toolset(toolset_name_or_names: Union[str, List[str]])`
   - Removes toolsets from active list (but keeps them initialized for quick reactivation)
   - Cannot deactivate essential toolsets

4. **New Method**: `set_active_toolsets(toolset_names: List[str], **kwargs)`
   - Sets the complete list of active toolsets (except essential ones which remain)
   - Handles initialization of any not-yet-initialized toolsets
   - Updates open_ai_schemas and toolset maps accordingly

5. **Refactored Method**: `init_tools(**kwargs)`
   - Only initializes essential toolsets
   - Stores kwargs for later lazy initialization of non-essential toolsets
   - Updates all the necessary maps/lists based on toolsets

6. **Update Property**: `active_tools`
   - Return only the active toolsets

7. **New Property**: `available_tools`
   - Return all instantiated toolsets

### Implementation Flow

1. **Refactor the Base Class**
   - Update `ToolChest` with new properties and methods
   - Ensure backward compatibility where possible
   - Make sure `post_init` is called properly during activation

2. **Update Subclasses**
   - Modify `MCPToolChest` to work with the new approach
   - Ensure servers are connected properly during activation

3. **Update Tests**
   - Adapt existing tests to work with the new implementation
   - Add tests for new functionality (activate/deactivate, essential toolsets)

## Implementation Plan

### Phase 1: Base ToolChest Changes

1. Update `ToolChest.__init__` to accept and process new parameters
2. Implement the new data structures for tracking toolset state
3. Implement `activate_toolset` and `deactivate_toolset` methods
4. Refactor `init_tools` to only initialize essential toolsets
5. Implement `set_active_toolsets` method
6. Update properties to reflect the new architecture

### Phase 2: MCPToolChest Updates

1. Update `MCPToolChest.__init__` to correctly pass parameters to the parent class
2. Modify `init_tools` override to work with the new approach
3. Ensure server connections are handled correctly during activation/deactivation

### Phase 3: Test and Documentation

1. Update existing tests to work with the new implementation
2. Add tests for new functionality
3. Update documentation to reflect the new usage patterns