# Workspaces

We're taking a little detour here for a couple of reasons.  The first being that the 0Workspace tool will use used by the tool we create when we do the lesson on creating tools.  The second is because adding it, even to the example agent you've been building allows you to start using your agent to help you write code, even modifying Agent C itself.



## Introducing Workspaces

The `WorkspaceTools`  subclass of `Toolset` provides the `ChatAgent` with access to a file system with the following tools:

- ls(path: str) - List the contents of a path.  (`dir` for the Windows folks)

- read(path: str) - Read the contents of a text file.

- write(path: str, data: str, mode: str)  - Write a text file to a path.  Mode can be `write` or `append` and defaults to `write`.



All paths are relative to, and constrained to the workspace.  `ls ../` will not work for example.

Each of those tools takes an additional parameter of `workspace` which is a string id/name of of the workspace containing the path.  We can pass in a list of `Workspace` objects when we initialize them or on the fly with the `add_workspace` method on the tool.



### The Workspace object

The `BaseWorkspace` class defines the interface for workspaces.  In addition to the methods you'd expect given the tools above there are additional methods meant to make it easier to work with workspaces 



```python
async def path_exists(self, file_path: str) -> bool:
    raise NotImplementedError

def full_path(self, path: str, mkdirs: bool = True) -> Union[str, None]:
    return None

async def read_bytes_internal(self, file_path: str) -> bytes:
    raise NotImplementedError

async def read_bytes_base64(self, file_path: str) -> str:
    raise NotImplementedError

async def write_bytes(self, file_path: str, mode: str, data: bytes) -> str:
    raise NotImplementedError


```



The method names and parameters for most of these fairly self explanatory however the `full_path` is a bit opaque.   This method is used to turn a relative path within the workspace to a full path that's valid for the workspace type.  The `mkdirs` parameter will ensure that all subfolders exist for the path before returning.  Consider the following.

```python
workspace = LocalStorageWorkspace("/path/to/workspace")

nested_path = 'some/nested/path'
nested_file = f"{nested_path}/file.md" 

workspace.path_exists(nested_path )
# Returns False

path_to_write = workspace.full_path(nested_file, False)
# Returns: /path/to/workspace/some/nested/path/file.md

workspace.path_exists(nested_path)
# Returns False

with open(path_to_write, "w") as file:
    file.write(data)
# Rasies an exception

path_to_write = workspace.full_path(nested_file)
# Returns: /path/to/workspace/some/nested/path/file.md

workspace.path_exists(nested_path)
# Returns True

with open(path_to_write, "w") as file:
    file.write(data)
# Writes data


```



**A note on workspace objects**

> Currently only the `LocalStorageWorkspace` type exists, but support for Azure and S3 are planned.  This would be really low hanging fruit for anyone wanting to contribute.
> 
> The functionality that exists in the Workspace currently is basically the functionality that I've needed in order to complete projects / build other tools.  By all means feel free to improve this tool!.



## Adding a Workspace to our agent

First we need to import the tool and local storage workspace:

```python
from agent_c_tools.tools.workspace import WorkspaceTools  # noqa
from agent_c_tools.tools.workspace.local_storage import LocalStorageWorkspace
```



Next we'll create a `LocalStorageWorkspace` mapped to our `lab_code` sub folder and add make sure it get's handed off when the `Toolset` initializes:

```python
tool_chest = ToolChest()

path = os.path.join(os.getcwd(), 'learn/lab_code')
lab_workspace = LocalStorageWorkspace(name="lab", workspace_path=path)

await tool_chest.init_tools(workspaces=[lab_workspace])
```



It might be nice to know just what the heck the agent is up to when it starts using all these tools, especially when it's reading and writing files.  So let's  modify our handler for the event stream to let us know what it's up to.

> Note: Workspaces **can** be read only



```python
if event.tool_use_active is not None:
    if event.tool_use_active:
        tools = "\n- ".join([tool.name for tool in event.tool_calls])
        ui.print_message("Tool", f"# Agent is using the following toolsets:\n{tools}\n")
    else:
        ui.print_role_token("Tool", "\nAgent has stopped using toolsets\n")
```

If the `tool_use_active` portion of the event has a value at all, then either it's telling tools are being called and with what parameters via an array of `CompletionToolCall` models or it's telling us that the `ChatAgent` has finished executing the tool calls and is sending the results back to the model.



The file `learn/example_code/example_14.py` has the complete version of this.  



###### Run this and prompt the model with:

> could you write me a poem and save it as "poem.md" in the lab workspace?



Note that I was explicit in telling it I wanted to to save it to the lab workspace.  You always want to be explicit in referring to reading and writing from/to workspaces



**When I ran this example I received this poem:**



> Rivers of digital dreams flow,  
> In the lab where ideas grow.  
> Bytes and bits in harmony dance,  
> Crafting reality in every glance.  
> 
> In the heart of silicon beats,  
> A world where the virtual meets.  
> The code weaves a tale so bold,  
> In the lab, where futures unfold.  
> 
> Through circuits, our thoughts take flight,  
> Turning darkness into light.  
> In this realm, we dare to dream,  
> Creating worlds, or so it seems.  
> 
> So here's to the lab, a space so vast,  
> Where the future is forged, and legends cast.  
> In the glow of screens, we find our muse,  
> In the lab, where we craft the news.



### Your agent can write code...

**Run the example and prompt the model with:**

> Could you generate the code to calculate a fib sequence in python and save it as fib.py in the lab workspace?



You should get something like:

```python
def fib(n):
    if n <= 1:
        return n
    else:
        return fib(n-1) + fib(n-2)

# Example usage:
# print(fib(10))
```



**Note**

> The models get a little twitchy when the user message contains language related to saving things to a disk. SO MANY people thought ChatGPT could save code to their local disk for them that Open AI gave even their foundation model a complex about making sure to tell the user it can't save code for them, even when it actually can. 
> 
> Some of the coding personas in the `personas` folder have explicit model instructions to get around this tendency.  They also serve as a good example of how to configure an agent to write *decent* code.





## Conclusion


























