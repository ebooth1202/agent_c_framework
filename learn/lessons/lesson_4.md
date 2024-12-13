# Chat Agents

So far we've been using the `one_shot` interface for the `ChatAgent`. As the name implies it is intended for simple "*give input get output, done!* " types of tasks. The `one_shot` interface is for non-interactive work.  If you're building AI into a pipeline somewhere this is your workhorse.  

If we think of an LLM in general a kitchen knife, i.e. a general purpose tool that's good at multiple things in the kitchen, a one-shot is more akin to a "slap chop"  a single purpose kitchen tool that's great if you need that one task it performs done.

 **<u>Tool-using</u> interactive** agents on the other hand are more akin to hiring a chef or restaurant manager that LOVES to be told what to do.  

**Keep in mind**

> Agents can use tools to perform all sorts of tasks, but agents can also BE tools. A very complex task can be wrapped in a one-shot and exposed as a tool.  A very very complex task might have yet another one-shot using multiple other one-shots as tools.
> 
> Any given one-shot can use whatever model works best, allowing us to minimize usage of more expensive models.

## Switching over to the chat interface

The `chat` and `one_shot` interfaces have identical function signatures.  `one_shot` actually calls `chat` to do the heavy lifting behind the scenes.  What's different is the the return type.   `chat` returns a list of messages, including the tool calls and tool results.  

The list of messages will be dictionary versions of this model:

```python
class Message(BaseModel):
    """
    An individual message with a role and content.
    """
    role: str
    content: Optional[Union[str, List[Union[TextContent, ImageContent]]]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    function: Optional[FunctionCall] = None
```

- `role` - This will be one of `assistant`, `system`, `user`, `tool` depending on the type of message.

- `content` - Will contain the content of the message.  We'll be dealing with the simple version where content is always a string for a while.

- `function` and `name` - Should never be set and will be removed when function calling goes away for good.

- We'll talk about the tool related ones later.

We can adapt our last example over to the chat interface by doing the same thing the `one_shot` interface does: Grab the text of the last message and ignore the rest.

```python
results: List[dict[str, Any]] = await agent.chat(prompt=prompt, user_message=location, model_name=model_name)
print(f"\n\nModel: {model_name}")

print(results[-1]['content'])
```

The file `learn/example_code/example_10.py` has the full version of this code.

## Creating a chat loop

To create a simple chat UI we're going to bring in a couple Python packages. "Prompt Toolkit" gives provides async text input and "Rich Console" and it's family allow us to use colors and other types of formatting easily.  We'll also create a small helper class to manage our UI for us:

```python
from prompt_toolkit import PromptSession
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

class ExampleUI:
    def __init__(self):
        self.rich_console = Console()
        self.prompt_session = PromptSession()

    def line_separator(self, label, style="bold"):
        self.rich_console.print()
        self.rich_console.print(Rule(title=label, style=style, align="right"))

    async def get_user_input(self) -> str:
        self.line_separator("You")
        return await self.prompt_session.prompt_async(': '))

    def print_message(self, role: str,  content: str):
        self.line_separator(role)
        self.rich_console.print(Markdown(content))
```

As before, we'll create out `ChatAgent` however we'll simplify our calls to chat by passing in our `model_name`, `tool_chest` and `prompt` to the constructor so that they become the defaults used by the `chat` call.  While we're setting up we'll  declare a variable to hold out message array and create an instance of our UI.

```python
tool_chest = ToolChest()
await tool_chest.init_tools()

prompt: str = "You are a helpful assistant helping people learn about, build and test AI agents"
agent = GPTChatAgent(tool_chest=tool_chest, prompt=prompt, model_name="gpt-4-turbo-preview")

messages: Union[List[dict[str, Any]], None] = None
ui = ExampleUI()
```

Next we'll start our input loop up:

```python
while True:
    user_message = await ui.get_user_input(": ")
    if user_message == "exit":
        break

    messages = await agent.chat(user_message=user_message, messages=messages)

    ui.print_message(messages[-1]['role'], messages[-1]['content'])
```

The first time we call `agnet.chat`  our`messages` param will be `None`.  That tells the `ChatAgent` that it needs to construct the message list itself.  When `chat` completes for the first time, `messages` will hold at least three messages

1. The `role` == `system` message 

2. The `role` == `user` message, containing the user input we sent

3. Zero or more more `role`== `tool` messages

4. The `role` == `assistant` message.

Each time around the loop after that will append:

1. The `role` == `user` message, containing the user input we sent

2. Zero or more more `role`== `tool` messages

3. The `role` == `assistant` message.

The file `learn/example_code/example_11.py` is a full copy of this code.

## The chat event stream

All agents and many tools can make use of a `streaming_callback` that it will publish `ChatEvents` to.  We won't dive into all the details of the event stream, but we will dip our toes into it to make our example more interactive.

To start with we'll modify our UI layer a bit to deal with tokens in addition to complete messages. As well as tracking the last role that was displayed:

```python
class ExampleUI:
    def __init__(self):
        self.rich_console = Console()
        self.prompt_session = PromptSession()
        self.last_role = ""

    def line_separator(self, label, style="bold"):
        self.rich_console.print("\b\b")
        self.rich_console.print(Rule(title=label, style=style, align="right"))

    async def get_user_input(self) -> str:
        self.line_separator("You")
        self.last_role = "You"
        return await self.prompt_session.prompt_async(': ')

    def print_message(self, role: str, content: str):
        self.last_role = role
        self.line_separator(role)
        self.rich_console.print(Markdown(content))

    def print_role_token(self, role: str, token: str):
        if self.last_role != role:
            self.line_separator(role)
            self.last_role = role

        self.rich_console.print(token, end="")
```

Next we'll set up callback to receive the events and pass it to the `ChatAgent`

```python
async def chat_callback(event: ChatEvent):
    if event.content is not None:
        ui.print_role_token(event.role, event.content)

agent = GPTChatAgent(tool_chest=tool_chest, 
                     prompt=prompt, 
                     model_name="gpt-4-turbo-preview", 
                     streaming_callback=chat_callback)
```

Then we can simplify our input loop a bit:

```python
while True:
    user_message = await ui.get_user_input()
    if user_message == "exit":
        break

    messages = await agent.chat(user_message=user_message, 
                                messages=messages)
```

The file `learn/example_code/example_12.py` contains the full implementation of this.  If you ask this version about the weather at a location you'll be able to read the current conditions as the forecast is being displayed.

There's a LOT more to this event stream, but this makes a good stopping point for this lesson.
