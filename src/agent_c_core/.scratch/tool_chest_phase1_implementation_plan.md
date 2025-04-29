# ToolChest Refactoring: Phase 1 Detailed Implementation Plan

This plan breaks down the Phase 1 refactoring of the `ToolChest` class into discrete, manageable steps. Each step builds incrementally on the previous ones while ensuring backward compatibility throughout the process.

## Step 1: Update Class Structure and Add New Properties

### 1.1 Add New Member Variables

Add the following member variables to the `ToolChest` class in the `__init__` method:

```python
# In ToolChest.__init__
# Rename existing variables for clarity
self.__tool_instances → self.__toolset_instances  # All instantiated toolsets

# Add new variables
self.__available_toolset_classes = kwargs.get('available_toolset_classes', Toolset.tool_registry)  # All available toolset classes
self.__active_toolset_instances = self.__toolset_instances.copy()  # Currently active toolsets (initially same as all instances)
self.__essential_toolset_names = kwargs.get('essential_toolset_names', [])  # Toolsets that should always be active
self.__toolsets_awaiting_init = {}  # Toolsets created but awaiting post_init
self.__init_kwargs = {}  # Store kwargs from init_tools call
```

This will maintain backward compatibility by keeping the current behavior (all instantiated toolsets are active) while adding support for the new functionality.

### 1.2 Add New Properties

Implement new properties to expose the additional state:

```python
@property
def available_tools(self) -> dict[str, Toolset]:
    """Returns all instantiated toolset instances."""
    return self.__toolset_instances
```

Also update the existing `active_tools` property to use the new member variable:

```python
@property
def active_tools(self) -> dict[str, Toolset]:
    """Returns the currently active toolset instances."""
    return self.__active_toolset_instances
```

## Step 2: Implement Metadata Update Method

Create a method to update all metadata (sections, schemas, maps) based on active toolsets:

```python
def _update_toolset_metadata(self):
    """Update tool sections, schemas, and maps based on active toolsets."""
    # Clear existing data
    self.__tool_sections = []
    self.__active_open_ai_schemas = []
    self._tool_name_to_instance_map = {}
    
    # Update with data from active toolsets
    for toolset in self.__active_toolset_instances.values():
        # Add sections
        if toolset.section is not None:
            self.__tool_sections.append(toolset.section)
        
        # Add schemas
        for schema in toolset.openai_schemas:
            self.__active_open_ai_schemas.append(schema)
            self._tool_name_to_instance_map[schema['function']['name']] = toolset
```

## Step 3: Implement Activation and Deactivation Methods

### 3.1 Implement `activate_toolset` Method

```python
async def activate_toolset(self, toolset_name_or_names: Union[str, List[str]], **kwargs) -> bool:
    """Activate one or more toolsets by name.
    
    Args:
        toolset_name_or_names: A single toolset name or list of toolset names to activate
        **kwargs: Additional arguments to pass to post_init if the toolset needs initialization
        
    Returns:
        bool: True if all toolsets were activated successfully, False otherwise
    """
    # Convert to list if a single string is provided
    toolset_names = [toolset_name_or_names] if isinstance(toolset_name_or_names, str) else toolset_name_or_names
    
    success = True
    for name in toolset_names:
        # Skip if already active
        if name in self.__active_toolset_instances:
            continue
            
        # Check if we've already instantiated this toolset
        if name in self.__toolset_instances:
            # Simply mark as active
            self.__active_toolset_instances[name] = self.__toolset_instances[name]
        else:
            # Find the class for this toolset
            toolset_class = next((cls for cls in self.__available_toolset_classes 
                                  if cls.__name__ == name), None)
            
            if not toolset_class:
                self.logger.warning(f"Toolset class {name} not found in available toolsets")
                success = False
                continue
                
            # Create instance
            try:
                # Merge kwargs with stored init_kwargs
                merged_kwargs = {**self.__init_kwargs, **kwargs, 'tool_chest': self}
                toolset_obj = toolset_class(**merged_kwargs)
                
                # Add to instances and active instances
                self.__toolset_instances[name] = toolset_obj
                self.__active_toolset_instances[name] = toolset_obj
                
                # Initialize the toolset
                await toolset_obj.post_init()
                self.logger.info(f"Activated toolset {name}")
            except Exception as e:
                self.logger.warning(f"Error activating toolset {name}: {str(e)}")
                success = False
    
    # Update metadata for active toolsets
    self._update_toolset_metadata()
    return success
```

### 3.2 Implement `deactivate_toolset` Method

```python
def deactivate_toolset(self, toolset_name_or_names: Union[str, List[str]]) -> bool:
    """Deactivate one or more toolsets by name.
    
    Args:
        toolset_name_or_names: A single toolset name or list of toolset names to deactivate
        
    Returns:
        bool: True if all toolsets were deactivated successfully, False otherwise
    """
    # Convert to list if a single string is provided
    toolset_names = [toolset_name_or_names] if isinstance(toolset_name_or_names, str) else toolset_name_or_names
    
    success = True
    for name in toolset_names:
        # Skip if essential
        if name in self.__essential_toolset_names:
            self.logger.warning(f"Cannot deactivate essential toolset {name}")
            success = False
            continue
            
        # Skip if not active
        if name not in self.__active_toolset_instances:
            continue
            
        # Remove from active toolsets
        del self.__active_toolset_instances[name]
        self.logger.info(f"Deactivated toolset {name}")
    
    # Update metadata for active toolsets
    self._update_toolset_metadata()
    return success
```

### 3.3 Implement `set_active_toolsets` Method

```python
async def set_active_toolsets(self, toolset_names: List[str], **kwargs) -> bool:
    """Set the complete list of active toolsets.
    
    Args:
        toolset_names: List of toolset names to set as active
        **kwargs: Additional arguments to pass to post_init for newly activated toolsets
        
    Returns:
        bool: True if all toolsets were set successfully, False otherwise
    """
    # Ensure essential toolsets are included
    for essential in self.__essential_toolset_names:
        if essential not in toolset_names:
            toolset_names.append(essential)
    
    # Get current active toolsets that aren't in the new list
    to_deactivate = [name for name in self.__active_toolset_instances 
                     if name not in toolset_names and name not in self.__essential_toolset_names]
    
    # Get toolsets to activate
    to_activate = [name for name in toolset_names if name not in self.__active_toolset_instances]
    
    # Deactivate toolsets not in the new list
    deactivate_success = self.deactivate_toolset(to_deactivate)
    
    # Activate new toolsets
    activate_success = await self.activate_toolset(to_activate, **kwargs)
    
    return deactivate_success and activate_success
```

## Step 4: Update `init_tools` Method

Modify the existing `init_tools` method to support essential toolsets while maintaining backward compatibility:

```python
async def init_tools(self, **kwargs):
    """Initialize toolsets.
    
    For backward compatibility, if no essential toolsets are specified,
    this will initialize all available toolsets.
    
    Args:
        **kwargs: Arguments to pass to toolset initialization
    """
    # Store kwargs for later initialization
    self.__init_kwargs = kwargs
    
    # For backward compatibility
    if not self.__essential_toolset_names:
        # Old behavior: initialize all available toolsets
        toolset_names = [cls.__name__ for cls in self.__available_toolset_classes]
        await self.activate_toolset(toolset_names, **kwargs)
    else:
        # New behavior: only initialize essential toolsets
        await self.activate_toolset(self.__essential_toolset_names, **kwargs)
```

## Step 5: Update Support Methods

### 5.1 Update `add_tool_class` Method

```python
def add_tool_class(self, cls: Type[Toolset]):
    """Add a new toolset class to the available toolsets.
    
    Args:
        cls: The toolset class to add
    """
    if cls not in self.__available_toolset_classes:
        self.__available_toolset_classes.append(cls)
```

### 5.2 Update `add_tool_instance` Method

```python
async def add_tool_instance(self, instance: Toolset, activate: bool = True):
    """Add a new toolset instance directly.
    
    Args:
        instance: The toolset instance to add
        activate: Whether to also activate the toolset
    """
    name = instance.__class__.__name__
    self.__toolset_instances[name] = instance
    
    if activate:
        self.__active_toolset_instances[name] = instance
        self._update_toolset_metadata()
```

### 5.3 Add Backward Compatibility Method

```python
async def activate_tool(self, tool_name: str, **kwargs) -> bool:
    """Activates a tool by name (backward compatibility method).
    
    Args:
        tool_name: The name of the tool to activate.
        **kwargs: Additional arguments to pass to post_init if needed
        
    Returns:
        bool: True if the tool was activated successfully, False otherwise
    """
    return await self.activate_toolset(tool_name, **kwargs)
```

## Step 6: Add Documentation

Add comprehensive documentation to all new methods and properties, explaining the new concepts and usage patterns.

## Step 7: Create Unit Tests

Create a new test file `tests/test_tool_chest.py` that tests all new functionality while ensuring backward compatibility:

```python
# Test cases for new functionality:
# 1. Initialize with essential toolsets
# 2. Activate additional toolsets
# 3. Deactivate non-essential toolset
# 4. Try to deactivate essential toolset
# 5. Set active toolsets
# 6. Backward compatibility with old usage patterns
```

## Implementation Order

To ensure backward compatibility at each step, implement the changes in the following order:

1. Add new member variables and properties (Steps 1.1, 1.2) - maintains existing behavior
2. Add metadata update method (Step 2) - no behavior change yet
3. Implement the new methods (Steps 3.1, 3.2, 3.3, 5.1, 5.2, 5.3) - all optional features
4. Update init_tools method (Step 4) - maintains backward compatibility with conditional logic
5. Add documentation (Step 6)
6. Create unit tests (Step 7)

This approach allows incremental testing at each stage, ensuring that existing functionality continues to work while new features are added.