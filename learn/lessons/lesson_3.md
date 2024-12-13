# Tool use in agents

This lesson introduces the basics of tool use in Agent C.  We will continue to work with the one-shot interface to the agent to keep things simple. This will not cover creating tools.  There's an existing doc for that if you're in a hurry but tool creation lessons will follow shortly.  

As I was writing this the Claude tool use SDK left alpha and entered beta.  Their implantation of tools is very similar to the Open AI API and using tools with Claude and Agent C will be the same as it is with Open AI.

## An introduction to tool use via the API

You will often hear the terms "tool use" and "function calling" used interchangeably. In concept they are, however there is a distinction with the Open AI chat completion API. While the way you declare tools vs functions is virtually identical `functions` are called one at at time `tools` can be used in parallel.  Functions are deprecated and will soon be removed.

Parallel tool use combined with the speed and affordability of GPT-4-Turbo is what moved agents from the lab to the real world. Slow and expensive GPT-4 to plodding through the function calls it needed to perform complex tasks made any sort of real-world agent unfeasible.  

### Declaring a tool

In Open AI the `tools` portion of the chat completion is an array of `ChatCompletionToolParam` models.  The `type` property is always `function` and the `function.parameters` is in [JSON Schema format](https://json-schema.org/understanding-json-schema). 

```json
"toolsets": [
    {
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            }
          },
          "required": [
            "location"
          ]
        }
      }
    }
  ]  
```

In Anthropic it's very similar but just different enough to require new code:

```json
"toolsets": [
    {
      "name": "get_weather",
      "description": "Get the current weather in a given location",
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          }
        },
        "required": [
          "location"
        ]
      }
    }
  ]
```

### Model tool use

When the model wants to use tools, the `finish_reason` for the choice will be `tool_calls`. Note: When I talk about the how the completion API works I'll be talking about the non-streaming API.  The streaming version of tools calls is essentially "wait till you have all of the pieces of the `tool_calls` array".

The first `ChatCompletionMessage` in the `messages` portion of the `choice` will contain an array of `ChatCompletionMessageToolCall` call object in `tool_calls`. So `response.chboices[0].messages[0].tool_calls` would look something like the block below to call the weather tool.

```json
"tool_calls": [
    {
      "id": "call_2PArU89L2uf4uIzRqnph4SrN",
      "function": {
        "arguments": "{\n  \"location\": \"Glasgow, Scotland\",\n  \"format\": \"celsius\"\n}",
        "name": "get_current_weather"
      },
      "type": "function"
    }
  ]
```

We need to JSON decode the string in the `arguments` field which gives a dictionary of key/value pairs representing the argument names and values for the function it wants to call.

We would call the function and then create a tool response for the model:

```python
call_resp = {"role": "tool", 
             "tool_call_id": tool_call_id, 
             "name": function_name,
             "content": function_response
             }
```

We then add the tool call message from the agent and our tool call response to the messages array and rerun the completion.  The model will evaluate the responses from the tool calls and either start streaming a response to the user or respond with more tool calls.

**A quick word about `choices`**

> One of the parameters you can specify on the chat completion call is `n`. It defaults to 1, but can be set higher and will result in multiple results for the same completion call.  Each result is a `choice`.  Agent C doesn't support multiple choices in the response as the use case for them is very niche and if you need it, you can easily adapt the chat call to a non-streaming version that can support multiple choices.  

## Tool use in Agent C

Agent C has some syntactic sugar and classes that make creating and using tools easier.  We have an internal model for tool use that consists of:

- Tools - A method the model can call

- Toolsets - A collection of related tools.

- Tool chests - A collection of toolsets.

### 

### Tools

Much like the how the APIs define them a "tool" in Agent C is declared with a JSON schema.  However, in Agent C we attach the JSON schema to the method it declares with a function decorator.  Here's that same weather tool declaration for the Agent C version of that tool.

```python
@json_schema(
            'Call this to get the weather forecast for a location. Make sure you check what location to use',
            {
                'location_name': {
                    'type': 'string',
                    'description': 'The location to get the weather for',
                    'required': True
                }
            }
    )
    async def get_current_weather(self, **kwargs) -> str:
        location_name = kwargs.get('location_name')
```

The schema decorator requires that the tool creator provide the description as the first parameter and a dictionary of the parameters in JSON schema format as the second with one minor difference:  `required` is an attribute of each parameter instead of have a separate `required` param that's an array on the decorator.

In addition to the schema decorator, all tool methods must adhere to three conventions:

1. Tool methods much be async.
2. Tool methods must accept only keyword arguments as parameters.
3. Tool methods must return a string or something that auto converts to a string.

**Fun fact**

> Making tool use easy was a big part of the reason I moved away from LangChain.  The JSON schema decorator is probably the oldest code in the framework, it's code I brought with me to Centric when I joined.  

### 

### Toolsets

In the one shot framework a `Toolset` was any object that had one or more decorated tool methods on it. Now that equipping the models with multiple tools is feasible Agent C has solidified this convention into a base class for sets of tools.  Toolsets have their own name and that name is added too the tool name before sending to the model.  This both prevents collisions on simple tool names like `get_data` it also allows us to map back to the toolset containing the tool we want to use.

Using this weather tool as an example, the `Toolset` for this would be `WeatherTools` with the `name` "weather".  This would end up being sent to the model as `weather_get_current_forecast`. When we parse the `tool_calls` array from the models we extract the prefix and use it to look up the `Toolset` with the tool it wants to call.

As we talk about tools, remember that LLMs are inherently non-deterministic.

> The separator for the toolset name is a configuration value.  Since its inception the schema decorator used `-` as the separator, which allowed for underscores in the name of the toolset, e.g. `toolset-tool_name`.  It worked great since a dash in a name wasn't valid python syntax.  Unfortunately, the recent preview release models often get confused and would sometimes use `toolset.tool_name` or `toolset_tool_name` .  Experimenting with using a dot was slightly more stable but I think the model just assumes that since there are underscores everywhere else, that dot must be a mistake about 5-10% of the time.  The only separator that's stable 100% of the time is the underscore.  Currently any underscores in toolset names are stripped, but that will be changing soon, I just have to tweak how toolsets get looked up.

There's a lot of functionality baked into the `Toolset` classes that we will cover later when we cover creating tools.  We'll talk about actually using them in an agent after we cover one more thing.

## Toolchests

A `ToolChest` object maintains a list of all known and active tools.  Providing an instance of this class to the `ChatAgent` allows it to both properly fill out the tools portion of the completion call but to also call those tools on behalf of the agent.

### ToolChest Initialization

Most tools will "register" themselves on import making them "magically" available for use by the `ToolChest`.  

When we initialize a `ToolChest` we either provide it with a list of tool class:

```python
from agent_c.toolsets.tool_chest import ToolChest
from agent_c_tools.tools.weather import WeatherTools
from agent_c.toolsets.web import WebTools

tool_chest = ToolChest(tool_classes=[WeeatherTools, WebTools])
```

Or we can let it draw from the tool registry for the list.

```python
from agent_c.toolsets.tool_chest import ToolChest

# Import every tool in the global tgools/__init__.py
from agent_c.toolsets import *

tool_chest = ToolChest()
```

If we knew for certain that the only tool imports were in our file that first example could have been:

```python
from agent_c.toolsets.tool_chest import ToolChest
from agent_c_tools.tools.weather import WeatherTools
from agent_c.toolsets.web import WebTools

tool_chest = ToolChest()
```

If we'd like to use the registry but still add own own extra tools we can do so:

```python
from agent_c.toolsets.tool_chest import ToolChest

# Import every tool in the global tgools/__init__.py
from agent_c.toolsets import *

tool_chest = ToolChest()

tool_chest.add_tool_class(MyUnRegisteredToolClass)
```

---

### Toolset Initialization

Once we've constructed a `ToolChest` the tools within it need initialized.  The tool initialization is done separately so that tools which need to make async calls to configure themselves can do so.  We can construct a dictionary of options that get passed into the tools.

```python
tool_opts = {'streaming_callback': self.chat_callback}
await tool_chest.init_tools(**tool_opts)
```

**Note:**

This way we construct this will be changing to something more like the following in the near future.

```python
tool_opts = { 'global':  {'streaming_callback': self.chat_callback},
              'toolset': {...}
            }
```

If we have a `Toolset` that we've initialized on our own, we can add it to the `ToolChest` with the following:

```python
tool_chest.add_tool_instance(my_unregistered_and_initialiszed_tool)
```

**Note:**

> Currently all valid and registered toolsets are considered active.  There's a stub of an interface that mimics there being a difference so that code can be written with dynamic tool selection in mind but it has not yet been implemented.

## Creating a tool-using one-shot

- First we import our tool, create a toolchest and then out chat agent.

```python
from agent_c.toolsets.tool_chest import ToolChest
from agent_c_tools.tools.weather import WeatherTools  # noqa
from agent_c.agents.gpt import GPTChatAgent

tool_chest = ToolChest()
await tool_chest.init_tools()

agent = GPTChatAgent(tool_chest=tool_chest)
```

**Note** PyCharm will helpfully remove "unused" imports.  Adding the `# nowqa`comment signals PyCharm that you know better than it does.

- Next we define a prompt that tells the model explicitly to use the tool if the user just supplies a location

```python
prompt: str = ("If the user message contains only the name of a location. "
               "Use the weather_get_current_weather tool to get the weather forecast for that location "
               "and report it to the user.")
```

- Next we call the completion

```python
location: str = "Columbus, Ohio"
result: str = await agent.one_shot(prompt=prompt, user_message=location)

print(result)
```

The file `learn/example_code/example_9.py` has a full version of this example.  It runs the example in both 3.5-turbo and 4-turbo-preview as this serves as a great example of the how the models have evolved their output.  As you can see in the block below 3.5 will just regurgitate the data, while 4-turbo will give it some polish.

```markdown
Model: gpt-3.5-turbo
The current weather in Columbus, Ohio is as follows:
- Temperature: 41°F
- Feels like: 35°F
- Description: Partly cloudy

Here are the forecasts for the next few days:
- April 5, 2024: High of 43°F, Low of 36°F
- April 6, 2024: High of 45°F, Low of 33°F
- April 7, 2024: High of 57°F, Low of 34°F


Model: gpt-4-turbo-preview
The current weather in Columbus, Ohio is partly cloudy with a temperature of 41°F, though it feels like 35°F. Here's the forecast for the next few days:
- **April 5, 2024**: High of 43°F, low of 36°F
- **April 6, 2024**: High of 45°F, low of 33°F
- **April 7, 2024**: High of 57°F, low of 34°F
```

## Coming up next:  Chat
