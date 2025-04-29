# ToolChest Redesign Implementation Plan

## Overview

This document outlines the step-by-step implementation plan for the ToolChest redesign based on the requirements in the design document. The goal is to modify the `ToolChest` class to properly support the concept of available vs. active toolsets, and to add support for essential toolsets.

## Implementation Steps

### Phase 1: Core Data Structure Changes

1. **Update Class Attributes**
   - Rename `__tool_instances` to `__toolset_instances` for clarity
   - Rename `__tool_classes` to `__toolset_classes` for consistency
   - Add new attributes:
     - `__active_toolset_names`: Set of names of currently active toolsets
     - `__essential_toolset_names`: Set of names of toolsets that should always be active
     - `__init_kwargs`: Cache for initialization parameters

2. **Update Constructor**
   - Modify `__init__` to accept and process new parameters:
     - `essential_toolsets`: Toolsets that should always be active
     - `active_toolsets`: Initially active toolsets
   - Ensure backward compatibility with existing `tool_classes` parameter
   - Initialize sets properly, handling both string and list inputs

### Phase 2: Implement Toolset Management Methods

1. **Activation Methods**
   - Implement `activate_toolset(toolset_name_or_names)` to activate one or more toolsets
   - Implement `deactivate_toolset(toolset_name_or_names)` to deactivate non-essential toolsets
   - Implement `set_active_toolsets(toolset_names)` to directly set the active toolset list (preserving essentials)
   - Implement `add_essential_toolset(toolset_name_or_names)` to mark toolsets as essential

2. **Helper Methods**
   - Implement `_ensure_active_toolsets_initialized()` to make sure all active toolsets are properly initialized

### Phase 3: Modify Existing Methods

1. **Update Property Methods**
   - Modify `active_tools` to use the new attribute structure (and rename to `active_toolsets` with alias)
   - Update `active_open_ai_schemas` to only include active toolsets
   - Update `active_claude_schemas` to only include active toolsets
   - Update `active_tool_sections` to only include active toolsets

2. **Update Tool Initialization**
   - Modify `init_tools` to only initialize active toolsets that aren't already initialized
   - Cache initialization parameters for future toolset activations

3. **Update Tool Call Handling**
   - Ensure `call_tools` and `_execute_tool_call` look at active toolsets only

### Phase 4: Backward Compatibility

1. **Alias Methods**
   - Add `@property def active_tools(self)` that calls `active_toolsets` for backward compatibility
   - Update `activate_tool` to call `activate_toolset` but emit a deprecation warning

2. **Documentation**
   - Update class docstrings to reflect the new functionality
   - Add deprecation warnings to methods that will eventually be removed

### Phase 5: Update MCPToolChest

1. **Inheritance**
   - Ensure MCPToolChest properly inherits from the updated ToolChest
   - Update `init_tools` in MCPToolChest to call the parent implementation correctly

## Testing Plan

### Unit Tests

1. **Basic Functionality Tests**
   - Test creating a ToolChest with various initialization parameters
   - Test activating and deactivating toolsets
   - Test setting active toolsets directly

2. **Essential Toolsets Tests**
   - Test adding essential toolsets
   - Verify essential toolsets cannot be deactivated
   - Verify essential toolsets are preserved when setting active toolsets

3. **Initialization Tests**
   - Verify toolsets are only initialized once
   - Verify lazy initialization works when accessing active toolsets

4. **Backward Compatibility Tests**
   - Verify old methods still work as expected
   - Verify deprecated methods emit appropriate warnings

5. **Error Handling Tests**
   - Test handling of invalid toolset names
   - Test initialization failures

### Integration Tests

1. **MCPToolChest Tests**
   - Verify MCPToolChest works with the new ToolChest architecture
   - Test activating/deactivating MCP toolsets

2. **Agent Integration Tests**
   - Verify agents can properly use the updated ToolChest
   - Test changing active toolsets during an agent session

## Incremental Rollout Plan

1. **Release 1: Core Changes**
   - Implement core data structure changes
   - Add new methods with full backward compatibility

2. **Release 2: Deprecation**
   - Add deprecation warnings to old methods
   - Update documentation to encourage use of new methods

3. **Release 3: Final Cleanup**
   - Eventually remove deprecated methods in a future major version

## Dependencies and Risks

1. **Dependencies**
   - The implementation touches core components used by agents
   - Any code directly accessing `__tool_instances` will need updates

2. **Risks**
   - Backward compatibility issues if implementation details have been relied upon
   - Performance impact if testing reveals issues with lazy initialization

3. **Mitigation Strategies**
   - Thorough testing with existing agents and applications
   - Detailed documentation on migration path
   - Phased rollout with deprecation warnings before removal