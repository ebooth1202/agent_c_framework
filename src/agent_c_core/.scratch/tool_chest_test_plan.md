# ToolChest Testing Plan

## Test Cases for New Functionality

### Basic Functionality Tests

1. **Initialize with essential toolsets**
   - Create a ToolChest with essential_toolset_names specified
   - Verify only essential toolsets are initialized after init_tools
   - Verify active_tools contains only essential toolsets

2. **Activate additional toolsets**
   - Initialize a ToolChest with some essential toolsets
   - Activate a non-essential toolset
   - Verify it appears in active_tools
   - Verify all tool schemas are updated correctly

3. **Deactivate non-essential toolset**
   - Initialize a ToolChest with some active toolsets
   - Deactivate a non-essential toolset
   - Verify it no longer appears in active_tools
   - Verify tool schemas are updated correctly

4. **Try to deactivate essential toolset**
   - Initialize a ToolChest with some essential toolsets
   - Try to deactivate an essential toolset
   - Verify it remains in active_tools
   - Verify a warning is logged

5. **Set active toolsets**
   - Initialize a ToolChest with some active toolsets
   - Set a new list of active toolsets
   - Verify active_tools contains only those toolsets plus any essential ones
   - Verify tool schemas are updated correctly

### Backward Compatibility Tests

1. **Old init_tools behavior**
   - Create a ToolChest without specifying essential_toolset_names
   - Call init_tools
   - Verify all available toolsets are activated (old behavior)

2. **Using activate_tool instead of activate_toolset**
   - Verify that the old method still works with the new implementation

### Edge Case Tests

1. **Activating already active toolset**
   - Initialize a ToolChest with some active toolsets
   - Try to activate a toolset that's already active
   - Verify it doesn't cause any errors or duplicate entries

2. **Deactivating non-active toolset**
   - Initialize a ToolChest
   - Try to deactivate a toolset that's not active
   - Verify it doesn't cause any errors

3. **Activating non-existent toolset**
   - Try to activate a toolset that doesn't exist
   - Verify it returns False and logs a warning

4. **Multiple activations/deactivations**
   - Perform a series of activations and deactivations
   - Verify the final state is correct

## MCP-Specific Tests

1. **Server Connection during Activation**
   - Initialize an MCPToolChest without connecting to servers
   - Activate an MCP toolset
   - Verify servers are connected automatically

2. **Server Initialization**
   - Initialize an MCPToolChest with some essential MCP toolsets
   - Verify servers are connected during init_tools

## Performance Tests

1. **Lazy Initialization Benefits**
   - Create a ToolChest with many available toolsets but few essential ones
   - Measure time taken for init_tools
   - Compare with time taken for old implementation

2. **Activation Time**
   - Measure time to activate a previously uninitialized toolset
   - Measure time to activate a previously initialized but inactive toolset
   - Verify the second case is significantly faster

## Implementation Testing Strategy

1. **Unit Tests**
   - Create mock toolsets for testing without external dependencies
   - Test each new method in isolation
   - Verify correct behavior for each method

2. **Integration Tests**
   - Test the ToolChest with real toolsets
   - Verify all components work together correctly
   - Test full activation/deactivation cycles

3. **Regression Tests**
   - Ensure existing functionality continues to work
   - Test with existing agent implementations

## Test Implementation Plan

1. Create mock toolsets for testing
2. Implement basic unit tests for new methods
3. Add integration tests with real toolsets
4. Add performance benchmarks
5. Add regression tests with existing code