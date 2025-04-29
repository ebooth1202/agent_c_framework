# ToolChest Implementation Details

## Phase 1: Base ToolChest Changes

### Step 1: Update Class Structure

We need to modify the class structure to support the distinction between available and active toolsets:

```python
class ToolChest:
    def __init__(self, **kwargs):
        # Available toolset classes (all possible toolsets)
        self.__available_toolset_classes = kwargs.get('available_toolset_classes', Toolset.tool_registry)
        
        # Essential toolset names (always active)
        self.__essential_toolset_names = kwargs.get('essential_toolset_names', [])
        
        # All instantiated toolsets (available for activation)
        self.__toolset_instances = {}
        
        # Currently active toolsets (subset of instances)
        self.__active_toolset_instances = {}
        
        # Toolsets that need initialization
        self.__toolsets_awaiting_init = {}
        
        # Store init kwargs for later initialization
        self.__init_kwargs = {}
        
        # Other existing properties
        self.logger = logging.getLogger(__name__)
        self.__tool_sections = []
        self.__active_open_ai_schemas = []
        self._tool_name_to_instance_map = {}
```

### Step 2: Update Properties

Modify existing properties to use the new naming and add new properties:

```python
@property
def active_tools(self) -> dict[str, Toolset]:
    """Returns the currently active toolset instances."""
    return self.__active_toolset_instances

@property
def available_tools(self) -> dict[str, Toolset]:
    """Returns all instantiated toolset instances."""
    return self.__toolset_instances
```

### Step 3: Update tool_sections, schemas and maps

Create a method to update the tool sections, schemas, and maps based on active toolsets:

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

### Step 4: Implement activation and deactivation methods

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

### Step 5: Update init_tools method

```python
async def init_tools(self, **kwargs):
    """Initialize essential toolsets and store kwargs for later.
    
    Args:
        **kwargs: Arguments to pass to toolset initialization
    """
    # Store kwargs for later initialization
    self.__init_kwargs = kwargs
    
    # Initialize essential toolsets
    if self.__essential_toolset_names:
        await self.activate_toolset(self.__essential_toolset_names, **kwargs)
```

### Step 6: Update add_tool_class and add_tool_instance methods

```python
def add_tool_class(self, cls: Type[Toolset]):
    """Add a new toolset class to the available toolsets.
    
    Args:
        cls: The toolset class to add
    """
    if cls not in self.__available_toolset_classes:
        self.__available_toolset_classes.append(cls)

async def add_tool_instance(self, instance: Toolset, activate: bool = True):
    """Add a new toolset instance directly.
    
    Args:
        instance: The toolset instance to add
        activate: Whether to also activate the toolset
    """
    name = instance.name
    self.__toolset_instances[name] = instance
    
    if activate:
        self.__active_toolset_instances[name] = instance
        self._update_toolset_metadata()
```

### Step 7: Update activate_tool method for backward compatibility

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

## Phase 2: MCPToolChest Updates

The `MCPToolChest` class will need to be updated to handle server connections properly during activation/deactivation:

```python
class MCPToolChest(ToolChest):
    async def init_tools(self, **kwargs):
        """Initialize essential toolsets and connect to MCP servers.
        
        Args:
            **kwargs: Arguments to pass to toolset initialization
        """
        # Connect to servers
        self.connect_servers()
        
        # Call parent init_tools
        await super().init_tools(**kwargs)
    
    async def activate_toolset(self, toolset_name_or_names, **kwargs):
        """Override to ensure MCP servers are connected before activating."""
        # Ensure servers are connected
        if not self.server_connected:
            self.connect_servers()
        
        # Call parent activate_toolset
        return await super().activate_toolset(toolset_name_or_names, **kwargs)
```

## Migration Path

To ensure backward compatibility, we need to make sure existing code continues to work with the new implementation:

1. Keep the same method signatures for backward compatibility
2. Make `init_tools` initialize all tools if no essential tools are specified (old behavior)
3. Add deprecation warnings for methods that will change in future versions

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
    
    # Initialize essential toolsets
    if self.__essential_toolset_names:
        await self.activate_toolset(self.__essential_toolset_names, **kwargs)
    else:
        # Backward compatibility: initialize all available toolsets
        toolset_names = [cls.__name__ for cls in self.__available_toolset_classes]
        await self.activate_toolset(toolset_names, **kwargs)
```