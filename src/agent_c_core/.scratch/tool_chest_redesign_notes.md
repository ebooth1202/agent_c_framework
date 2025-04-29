The ToolChest (`//core/agent_c/toolsets/tool_chest.py`) was written with an interface that supports the notion of a set of active tools vs available tools.  When it was implemented however there weren't many tools so a shortcut was taken to make all tools active tools.  This has become a problem as having only a subset of tools available means reinitializing the tool chest and tools.

We need to support to fully support the active tools vs available tools concept without requiring a reinit of the toolchest or creating a new instance of a tool we've already created.  

We also need to support the notion of essential tools that are always equipped as there are several foundational tools or commonly used tools we want available.

I think we should also cleanup the terminology being used in this, as it's really handling Toolsets, not tools and at some point we're going to want to support enabling individual tools within toolsets.

## Understanding the ToolChest vs MCPToolChest
The base ToolChest in Agent C is built to support Agent C ToolSets which have multiple tools on them, and support a much richer feature set and what is provided via MCP

The MCPToolChest inherits from the ToolChest to provide a way to make MCP based tools fit into the Agent C tool ecosystem.  It's there to support tools that are NOT Agent C tools, but could be used as if they were.

## Goals
1. We don't want to initialize every tool in the registry at startup.  We need to only initialize the essential tools.  
     - We can cache the data from the original `ToolChest.init_tools` call and use that as a default, and have the activate methods allow them to pass in a different dictionary.
2. We should probably make the Toolset management methods accept a string or an array of strings to make life easier on the application layer devs. 
   - Something like `activate_toolset(self, toolset_name_or_names: Union[str, List[str]])`
   - In addition to the adding  / removing ToolSets, we need a `set_active_toolsets` that just sets what the list should be.
   - Since these will need to init tools **lazily** the various methods for activating tools must be async and support supplying a new blob of data for the `post_init` on the tool.

## How toolset initialization CURRENTLY works.
1. Application layer creates a ToolChest and supplies a list of ToolSets they want available.
   - If they don't supply one ALL tools in the Toolset.tool_registry are considered available.
   - This list, like the registry **list** are toolset CLASS names.
   - Because of the shortcuts taken, "available" amd "active" mean the same thing.
2. Later the application calls init_tools on the toolchest 
   - This should loop through any active tool, for which we don't have an instance of in `__tool_instances` and:
     - Create an instance of it
     - Call it's async `post_init` with hte params supplied by the application in kw args plus a reference to itself.
   - Note that since currently "available" amd "active" mean the same thing, this means we initialize every tool if the registry is used...

## How toolset initialization should work
1. Application layer creates a ToolChest and supplies a list of ToolSets they want available, and a list that they consider essential.
   - If they don't supply an available list ALL ToolSets in the Toolset.tool_registry are considered available.
   - Again we're talking about class names, not single tool names.
2. Later the application calls init_tools on the toolchest 
   - This should loop through any active / essential ToolSets, for which we don't have an instance of in `__toolset_instances` and:
     - Create an instance of it
     - Call it's async `post_init` with hte params supplied by the application in kw args plus a reference to itself.
   - Also add it to `__active_toolset_instances`
3. Activating additional Toolsets
   - If we don't have an instance of it in `__toolset_instances` then:
     - Create an instance of it
     - Call it's async `post_init` with hte params supplied by the application in kw args plus a reference to itself.
   - Also add it to `__active_toolset_instances`
