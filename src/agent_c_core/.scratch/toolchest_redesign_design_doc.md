# ToolChest Redesign Design Document

## Current Implementation Overview

The current ToolChest implementation has several limitations:

1. **No separation between available and active toolsets**: When toolsets are added to the ToolChest, they are all considered active, which forces initialization of all available tools.

2. **Terminology inconsistency**: The class uses terms like `tool_instances` and `tool_classes` when it's actually managing toolsets, not individual tools.

3. **No concept of essential toolsets**: Cannot designate certain toolsets as always active.

4. **Inefficient reinitialization**: To change active toolsets, the entire ToolChest needs to be reinitialized or recreated.

## Proposed Changes

### 1. Core Data Structure Changes

Rename and add new attributes to better reflect what we're managing:

```python
class ToolChest:
    def __init__(self, **kwargs):
        # Rename for clarity about what we're storing
        self.__toolset_instances = {}  # All initialized toolset instances
        self.__active_toolset_names = set()  # Names of currently active toolsets
        self.__essential_toolset_names = set()  # Names of essential toolsets (always active)
        
        # For backward compatibility, still accept tool_classes
        self.__toolset_classes = kwargs.get('tool_classes', [])
        
        # Track essential toolsets from initialization
        essential_toolsets = kwargs.get('essential_toolsets', [])
        if isinstance(essential_toolsets, str):
            essential_toolsets = [essential_toolsets]
        self.__essential_toolset_names = set(essential_toolsets)
        
        # Initialize active toolsets to include both specified and essential
        active_toolsets = kwargs.get('active_toolsets', [])
        if isinstance(active_toolsets, str):
            active_toolsets = [active_toolsets]
        self.__active_toolset_names = set(active_toolsets) | self.__essential_toolset_names
        
        self.__tool_sections = []
        self.logger = logging.getLogger(__name__)
```

### 2. New and Modified Methods

#### A. Toolset Activation Management

```python
def activate_toolset(self, toolset_name_or_names: Union[str, List[str]]) -> bool:
    """Activate one or more toolsets by name.
    
    Args:
        toolset_name_or_names: The name or list of names of toolsets to activate
        
    Returns:
        bool: True if all toolsets were successfully activated, False otherwise
    """
    names_to_activate = [toolset_name_or_names] if isinstance(toolset_name_or_names, str) else toolset_name_or_names
    success = True
    
    for name in names_to_activate:
        if name in self.__toolset_instances or name in Toolset.tool_registry:
            self.__active_toolset_names.add(name)
        else:
            self.logger.warning(f"Cannot activate unknown toolset: {name}")
            success = False
    
    return success

def deactivate_toolset(self, toolset_name_or_names: Union[str, List[str]]) -> bool:
    """Deactivate one or more toolsets by name, except for essential toolsets.
    
    Args:
        toolset_name_or_names: The name or list of names of toolsets to deactivate
        
    Returns:
        bool: True if all toolsets were successfully deactivated, False otherwise
    """
    names_to_deactivate = [toolset_name_or_names] if isinstance(toolset_name_or_names, str) else toolset_name_or_names
    success = True
    
    for name in names_to_deactivate:
        if name in self.__essential_toolset_names:
            self.logger.warning(f"Cannot deactivate essential toolset: {name}")
            success = False
        elif name in self.__active_toolset_names:
            self.__active_toolset_names.remove(name)
        else:
            self.logger.warning(f"Cannot deactivate inactive toolset: {name}")
            success = False
    
    return success

def set_active_toolsets(self, toolset_names: List[str]) -> bool:
    """Set the complete list of active toolsets, preserving essential toolsets.
    
    Args:
        toolset_names: The list of names of toolsets to set as active
        
    Returns:
        bool: True if the operation was successful, False otherwise
    """
    # Always include essential toolsets
    new_active_set = set(toolset_names) | self.__essential_toolset_names
    
    # Validate all names
    unknown_toolsets = [name for name in new_active_set 
                         if name not in self.__toolset_instances and name not in Toolset.tool_registry]
    
    if unknown_toolsets:
        self.logger.warning(f"Unknown toolsets requested: {unknown_toolsets}")
        return False
    
    # Update active set
    self.__active_toolset_names = new_active_set
    return True

def add_essential_toolset(self, toolset_name_or_names: Union[str, List[str]]) -> bool:
    """Mark one or more toolsets as essential, meaning they cannot be deactivated.
    
    Args:
        toolset_name_or_names: The name or list of names of toolsets to mark as essential
        
    Returns:
        bool: True if all toolsets were successfully marked essential, False otherwise
    """
    names_to_add = [toolset_name_or_names] if isinstance(toolset_name_or_names, str) else toolset_name_or_names
    success = True
    
    for name in names_to_add:
        if name in self.__toolset_instances or name in Toolset.tool_registry:
            self.__essential_toolset_names.add(name)
            # Also make sure it's active
            self.__active_toolset_names.add(name)
        else:
            self.logger.warning(f"Cannot mark unknown toolset as essential: {name}")
            success = False
    
    return success
```

#### B. Modified Initialization Method

```python
def init_tools(self, **kwargs):
    """Asynchronously initializes the active toolsets in the tool chest.
    
    This method will initialize each active toolset one at a time, allowing toolsets 
    that depend on others to access them during their initialization. Toolsets that 
    have already been initialized will not be initialized again.
    
    Args:
        **kwargs: Arbitrary keyword arguments to pass to the toolset instances during initialization.
    """
    # Cache kwargs for later activations
    self.__init_kwargs = kwargs
    
    # Get all active toolset names that need initialization
    toolset_names_to_init = self.__active_toolset_names - set(self.__toolset_instances.keys())
    
    # Initialize all toolsets in the active set that aren't already initialized
    for toolset_name in toolset_names_to_init:
        if toolset_name not in Toolset.tool_registry:
            self.logger.warning(f"Toolset {toolset_name} not found in registry")
            continue
            
        # Create instance if needed
        toolset_cls = Toolset.tool_registry[toolset_name]
        try:
            # Initialize with a reference to this tool chest
            kwargs['tool_chest'] = self
            instance = toolset_cls(**kwargs)
            self.__toolset_instances[toolset_name] = instance
            
            # Add to tool sections if it has one
            if hasattr(instance, 'section') and instance.section is not None:
                self.__tool_sections.append(instance.section)
                
            # Call post_init if it exists
            if hasattr(instance, 'post_init'):
                instance.post_init()
                
        except Exception as e:
            self.logger.error(f"Error initializing toolset {toolset_name}: {e}")
```

#### C. Updated Active Toolsets Properties

```python
@property
def active_toolsets(self) -> dict[str, Toolset]:
    """Property that returns the active toolset instances.
    
    Returns:
        dict[str, Toolset]: Dictionary of active toolset instances.
    """
    # Initialize any active toolsets that aren't initialized yet
    self._ensure_active_toolsets_initialized()
    
    # Return only active instances
    return {name: self.__toolset_instances[name] 
            for name in self.__active_toolset_names 
            if name in self.__toolset_instances}

@property
def active_open_ai_schemas(self) -> List[dict]:
    """Property that returns the active toolset instances in Open AI format.
    
    Returns:
        List[dict]: List of OpenAI tool schemas from active toolsets.
    """
    schemas = []
    for name, toolset in self.active_toolsets.items():
        schemas.extend(toolset.tool_schemas())
    return schemas

@property
def active_tool_sections(self) -> List[PromptSection]:
    """Property that returns the `PromptSection` for each active toolset.
    
    Returns:
        List[PromptSection]: List of active tool sections.
    """
    active_sections = []
    for name, toolset in self.active_toolsets.items():
        if hasattr(toolset, 'section') and toolset.section is not None:
            active_sections.append(toolset.section)
    return active_sections

def _ensure_active_toolsets_initialized(self):
    """Helper method to ensure all active toolsets are initialized."""
    for name in list(self.__active_toolset_names):
        if name not in self.__toolset_instances:
            if name in Toolset.tool_registry:
                # Initialize just this toolset
                kwargs = self.__init_kwargs.copy() if hasattr(self, '__init_kwargs') else {}
                kwargs['tool_chest'] = self
                try:
                    toolset_cls = Toolset.tool_registry[name]
                    instance = toolset_cls(**kwargs)
                    self.__toolset_instances[name] = instance
                    
                    # Add to tool sections if it has one
                    if hasattr(instance, 'section') and instance.section is not None:
                        self.__tool_sections.append(instance.section)
                        
                    # Call post_init if it exists
                    if hasattr(instance, 'post_init'):
                        instance.post_init()
                except Exception as e:
                    self.logger.error(f"Error initializing toolset {name}: {e}")
            else:
                self.logger.warning(f"Active toolset {name} not found in registry")
                # Remove from active set since it's invalid
                if name not in self.__essential_toolset_names:
                    self.__active_toolset_names.remove(name)
```

### 3. Changes to MCPToolChest

The MCPToolChest will need to be updated to inherit from the new ToolChest and ensure its init_tools method properly calls the parent implementation:

```python
class MCPToolChest(ToolChest):
    # ... existing code ...
    
    def init_tools(self, **kwargs):
        """Override of ToolChest.init_tools to also initialize MCP servers.
        
        Args:
            **kwargs: Arguments to pass to the parent class and tools during initialization
        """
        # Connect to MCP servers first
        self.connect_servers()
        
        # Then initialize tools through parent class
        super().init_tools(**kwargs)
```

## Backward Compatibility

To maintain backward compatibility, we need to ensure:

1. The `__init__` method still accepts and correctly processes the `tool_classes` parameter
2. The `activate_tool` method remains but is updated to work with the new architecture
3. Properties like `active_tools` are renamed to `active_toolsets` but aliases are maintained

## Migration Path

For a smooth transition:

1. Add deprecation warnings for old methods/properties that will eventually be removed
2. Document the new methods and changes in the class docstring
3. Update any internal usage of the old methods to use the new ones

## Testing Recommendations

Test cases should cover:

1. Basic functionality (activating/deactivating toolsets)
2. Essential toolsets (cannot be deactivated)
3. Initialization behavior (toolsets only initialized once)
4. Backward compatibility (old methods still work)
5. Error conditions (trying to activate/deactivate invalid toolsets)

## Estimated Impact

These changes should have minimal impact on existing code while providing the following benefits:

1. Better performance by only initializing toolsets that are actually needed
2. More intuitive API for managing active vs. available toolsets
3. Support for essential toolsets that are always available
4. Clearer terminology that reflects what's actually being managed (toolsets, not tools)