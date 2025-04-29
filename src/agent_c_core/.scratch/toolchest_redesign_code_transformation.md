# ToolChest Redesign Code Transformation

This document outlines the specific code changes needed to implement the toolset redesign. It shows the before and after for key methods in the ToolChest class.

## 1. Class Variables and Constructor

### Before

```python
class ToolChest:
    def __init__(self, **kwargs):
        self.__tool_instances = {}
        self.__tool_classes = kwargs.get('tool_classes', [])
        self.__tool_sections = []
        self.logger = logging.getLogger(__name__)
```

### After

```python
class ToolChest:
    def __init__(self, **kwargs):
        # Renamed for clarity
        self.__toolset_instances = {}
        # For backward compatibility, still accept tool_classes
        self.__toolset_classes = kwargs.get('tool_classes', [])
        
        # New attributes for managing active/essential toolsets
        self.__active_toolset_names = set()
        self.__essential_toolset_names = set()
        
        # Process essential toolsets from constructor
        essential_toolsets = kwargs.get('essential_toolsets', [])
        if isinstance(essential_toolsets, str):
            essential_toolsets = [essential_toolsets]
        self.__essential_toolset_names = set(essential_toolsets)
        
        # Process active toolsets from constructor
        active_toolsets = kwargs.get('active_toolsets', [])
        if isinstance(active_toolsets, str):
            active_toolsets = [active_toolsets]
        # Active includes both specified active and essential
        self.__active_toolset_names = set(active_toolsets) | self.__essential_toolset_names
        
        # If no active toolsets were specified but tool_classes were,
        # assume all tool_classes should be active for backward compatibility
        if not self.__active_toolset_names and self.__toolset_classes:
            self.__active_toolset_names = set(cls.__name__ for cls in self.__toolset_classes)
        
        self.__tool_sections = []
        self.logger = logging.getLogger(__name__)
        
        # Cache for initialization parameters
        self.__init_kwargs = {}
```

## 2. Toolset Activation Methods (New)

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
            # Ensure it's initialized if we access active toolsets
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

## 3. Updated activate_tool Method

### Before

```python
def activate_tool(self, tool_name: str) -> bool:
    """Activates a tool by name. Currently, this is a placeholder method.
    
    Args:
        tool_name (str): The name of the tool to activate.
    
    Returns:
        bool: Returns True if the tool is activated, otherwise False.  For now.
    """
    # For now, until needed, this will always return true
    return True
```

### After

```python
def activate_tool(self, tool_name: str) -> bool:
    """Activates a tool by name. Use activate_toolset instead.
    
    This method is maintained for backward compatibility but will be removed in a future version.
    Please use activate_toolset instead.
    
    Args:
        tool_name (str): The name of the tool to activate.
    
    Returns:
        bool: Returns True if the tool is activated, otherwise False.
    """
    warnings.warn(
        "ToolChest.activate_tool is deprecated. Use ToolChest.activate_toolset instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.activate_toolset(tool_name)
```

## 4. Updated active_tools Property

### Before

```python
@property
def active_tools(self) -> dict[str, Toolset]:
    """Property that returns the active tool instances.
    Currently, all toolsets are the active toolsets but that will change.
    
    Returns:
        dict[str, Toolset]: Dictionary of active tool instances.
    """
    return self.__tool_instances
```

### After

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
def active_tools(self) -> dict[str, Toolset]:
    """Property that returns the active tool instances.
    This is an alias for active_toolsets maintained for backward compatibility.
    
    Returns:
        dict[str, Toolset]: Dictionary of active toolset instances.
    """
    warnings.warn(
        "ToolChest.active_tools is deprecated. Use ToolChest.active_toolsets instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.active_toolsets
```

## 5. Updated init_tools Method

### Before

```python
def init_tools(self, **kwargs):
    """Asynchronously initializes the toolsets in the tool chest.
    
    This method will initialize each tool one at a time, allowing toolsets that depend on others to access them during their initialization.
    
    Args:
        **kwargs: Arbitrary keyword arguments to pass to the tool instances during initialization.
    """
    # Just look through class registry for available tools?
    tool_registry = Toolset.tool_registry
    if not self.__tool_classes:
        self.logger.info("No tool classes specified, loading all from registry.")
        for cls_name, cls in tool_registry.items():
            try:
                # Create a tool instance for each class that is in the registry
                kwargs['tool_chest'] = self
                instance = cls(**kwargs)
                self.__tool_instances[cls_name] = instance

                if hasattr(instance, 'section') and instance.section is not None:
                    self.__tool_sections.append(instance.section)
                
                # Call post_init if it exists
                if hasattr(instance, 'post_init'):
                    instance.post_init()
            except Exception as e:
                self.logger.error(f"Error initializing tool {cls_name}: {e}")
    else:
        for cls in self.__tool_classes:
            try:
                # Initialize with a reference to this tool chest
                kwargs['tool_chest'] = self
                instance = cls(**kwargs)
                self.__tool_instances[cls.__name__] = instance
                
                if hasattr(instance, 'section') and instance.section is not None:
                    self.__tool_sections.append(instance.section)
                
                # Call post_init if it exists
                if hasattr(instance, 'post_init'):
                    instance.post_init()
            except Exception as e:
                self.logger.error(f"Error initializing tool {cls.__name__}: {e}")
```

### After

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
    self.__init_kwargs = kwargs.copy()
    
    # Handle backward compatibility case where no active toolsets were specified
    if not self.__active_toolset_names:
        if self.__toolset_classes:
            # Use toolset classes specified in constructor
            for cls in self.__toolset_classes:
                self.__active_toolset_names.add(cls.__name__)
        else:
            # If nothing specified, activate all from registry for backward compatibility
            self.logger.info("No active toolsets specified, activating all from registry.")
            self.__active_toolset_names = set(Toolset.tool_registry.keys())
    
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

## 6. Updated Schema Properties

### Before (partial example for active_open_ai_schemas)

```python
@property
def active_open_ai_schemas(self) -> List[dict]:
    """Property that returns the active tool instances in Open AI format.
    
    Returns:
        dict[str, Toolset]: Dictionary of active tool instances.
    """
    schemas = []
    for name, toolset in self.__tool_instances.items():
        schemas.extend(toolset.tool_schemas())
    return schemas
```

### After 

```python
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
```

## 7. Updated MCPToolChest init_tools Method

### Before

```python
def init_tools(self, **kwargs):
    """Override of ToolChest.init_tools to also initialize MCP servers.
    
    Args:
        **kwargs: Arguments to pass to the parent class and tools during initialization
    """
    # Connect to MCP servers
    self.connect_servers()
    
    # Then initialize tools through parent class
    super().init_tools(**kwargs)
```

### After

There are no changes needed for this method, as it already calls the parent implementation correctly.

## 8. Updated call_tools and _execute_tool_call Methods

These methods should be updated to use the active_toolsets property instead of directly accessing __tool_instances to ensure they only work with active toolsets.

## Complete Class Definition

After all these changes, the ToolChest class definition should include:

```python
class ToolChest:
    """A collection of toolsets that can be used by an agent.
    
    This class manages a set of available toolsets and allows activating/deactivating
    them as needed. Essential toolsets can be designated which are always active.
    
    Attributes:
        __toolset_instances (dict[str, Toolset]): A private dictionary to store instances of toolsets.
        __toolset_classes (list[Type[Toolset]]): A private list to store the classes of the toolsets.
        __active_toolset_names (set[str]): Names of currently active toolsets.
        __essential_toolset_names (set[str]): Names of toolsets that are always active.
        __tool_sections (List[PromptSection]): A private list to store sections of the prompt.
        logger (logging.Logger): An instance of a logger.
    """
    
    # ... method implementations as shown above ...
```