## Tools

The underlying agent code supports parallel tool use by GPT. This allows the model to fulfill  a request that involves multiple functions it far fewer calls.  "Check the weather, and grab the latest headline from each of the newsfeeds" results in two completion passes with parallel function calling and would have been at least three without it.

Parallel function calling combined with the speed and capability of GPT-4.5-turbo allows us to create small "lego bricks" that when combined with model instructions allow the model to accomplish almost anything.  The memory tool is a prime example, from a simple "If you need to store metadata on the user or session here's how you do so" we were able to build a detailed tracking system for treatments and outcomes using model instructions alone.

The `Toolset` acts as a container for one or more "tools".  The base class looks like this:

```
class Toolset:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        if self.name is None:
            raise "Toolsets must have a name"
        self.tool_cache: ToolCache = kwargs.get("tool_cache")
        self.section: Union[PromptSection, None] = kwargs.get('section', None)
        needed_keys: List[str] = kwargs.get('needed_keys', [])
        self.valid = self._validate_env_keys(needed_keys)
```

- `tool_cache` provides a reference to a shared diskcache.
- `section` allows subclasses to provide a `PromptSection` to be used when the tool is included if necessary.
- `needed_kesy` allows subclasses to declare an array of environment variables which must be set for the tool belt to be considered valid.
- `valid` setting this to true will make the tool belt as invalid and prevent it from being included in the agent tools.

A "tool" is a method on a `Toolset` that meets ALL of the following criteria:

- is decorated with a `json_schema` decorator, which MUST be imported with `from utils import json_schema` 
- is async
- accepts only `kwargs` for parameters.
- returns a string

The `json_schema` decorator is how we tell the model about the tool and that looks like this:

```
from typing import Callable, Dict, Union


def json_schema(description: str, params: Dict[str, Dict[str, Union[str, bool]]]) -> Callable:
    """
    A decorator to attach an OpenAI compatible JSON schema to a function. The schema contains
    information about the function's name, description, parameters, and required parameters.


    :param description: A description of the function.
    :param params: A dictionary containing information about the parameters of the function in a JSON Schema compatiable format
    :return: The original function with an attached JSON schema.
    """
```

Putting it all together here is an example `Toolset` with a tool for getting the weather in a location that makes use of the shared `tool_cache` and the default (one hour in seconds) time to live in order to avoid wasting bandwidth.

```
import json
import python_weather
from utils import json_schema
from tools.tool_set import Toolset, ToolsetBase


class WeatherTools(Toolset):
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
    async def get_current_weather(self, **kwargs):
        location_name = kwargs.get('location_name')

        results = self.tool_cache.get(f"weather://{location_name}")
        if results is not None:
            return results

        async with python_weather.Client(unit=python_weather.IMPERIAL) as client:
            weather = await client.get(location_name)

            forecasts: [dict] = []
            for forecast in weather.forecasts:
                forecasts.append({'date': forecast.date.strftime('%Y-%m-%d'),
                                  'high_temperature': forecast.highest_temperature,
                                  'low_temperature': forecast.lowest_temperature})

            results = json.dumps({"current_temperature": weather.current.temperature, "forecasts": forecasts})
            self.tool_cache.set(f"weather://{location_name}", results)

            return results
```

#### The base `Toolset`

The base Toolset provides a host of common things needed by other tools

```python
class Toolset:
       def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.session_manager: ChatSessionManager = kwargs.get("session_manager")
        self.tool_chest: 'ToolChest' = kwargs.get("tool_chest")
        required_tools: List[str] = kwargs.get("required_tools", [])
        for tool_name in required_tools:
            if tool_name not in self.tool_chest.active_tools:
                self.valid = self.tool_chest.activate_tool(tool_name)
                if not self.valid:
                    break

        self.tool_cache: ToolCache = kwargs.get("tool_cache")
        self.section: Union[PromptSection, None] = kwargs.get('section')

        self.agent_can_use_tools = kwargs.get("agent_can_use_tools", True)  # We assume the agent can use toolsets unless otherwise specified
        self.need_tool_user = kwargs.get("need_tool_user", True)            # By default toolsets are not valid for non-tool-using agents.

        needed_keys: List[str] = kwargs.get('needed_keys', [])
        self.tool_valid = self._validate_env_keys(needed_keys)

        if self.need_tool_user and not self.agent_can_use_tools:
            self.tool_valid = False

        self.openai_schemas = self.__openai_schemas()

        self.streaming_callback: Callable[..., None] = kwargs.get('streaming_callback')
        self.output_format: str = kwargs.get('output_format', 'raw')
        self.tool_role: str = kwargs.get('tool_role', 'tool')
```

#### The ToolChest

The reference app has an `__init_chat_agent` method which has code similar to this in it:

```python
# Declare a "tool chest" of toolsets for the model.
# In this reference app we're not supplying a tool_classes parameter so it will grab the "kitchen sink"
# of all tool classes that have been registered.
self.tool_chest = ToolChest()

# These are the default and extra options for the various toolsets, since the toolsets all use kwargs
# we can send them the whole bag of options without worry.
tool_opts = {'tool_cache': self.tool_cache, 'session_manager': self.session_manager, 'user_preferences': self.user_prefs,
             'workspaces': self.workspaces, 'streaming_callback': self.chat_callback}

self.logger.debug("Initializing GPT Chat Agent... Initializing toolsets...")
await self.tool_chest.init_tools(**tool_opts)
```

This tool chest provides a central location for tools to find each other fand for use to manage what tools are available to each agent.



#### Tool instructions

Since it's quite common for tools to need more model instruction than what might be in the decorator. The base class allows for a `PromptSection` to be declared.  The allows feed it into `PromptBuilder` like so:



```python
operating_sections.extend(self.tool_chest.active_tool_sections)
```

## Existing tools

### `MemoryTools`

This tool provides the model access to it's own key in the metadata for the user and session.  It leverages the  ZepCache to keep reads and writes to a minimum. The `_ai` key is stored in the metadata as a JSON string to work around a bug in Zep but it's actually a dictionary that gets serialized / deserialized each completion pass.  

The `MemorySection` prompt section provides the contents of these two dictionaries in YAML format to reduce the number of tokens it takes to render the content vs JSON.  It provides some basic instruction to the model but that definitely needs improved.

The `Ticco` agent makes HEAVY use of this tool and does so "autonomously".  There's a prompt section with dedicated instructions that read:

> Tools have been provided to you to record information in the "User KVPs" section.  It is imperative that you use this tool to record the little details about the user and the children under their care so that in future sessions you won't need as many clarifying questions.
> 
> - Maintain a list of the children under care of the user and the details you've learned about them in a `childern_under_care` key that represents them a collection of objects indexed by name.
>   - At a minimum we need to capture `name`, `age`, `gender`, `relation_to_user`, `reported_issues`, `behavioral_triggers`
>   - As the user reports back on strategies they've tried, or advice from you they've followed add them to a `stratgies_tried` list for the child along with their outcomes.
> - As you gain new biographic and situational knowledge, store it for future reference.
> - Review the metadata for any items where we're awaiting an outcome or follow up from the user for a child under their care
>   - If they mention a child with pending outcomes, make sure to ask about the strategy they were going to try.
> 
> **This is very critical for us to achieve our goals of helping kids affected by trauma. Consider it a top priority** 

This allows the model to store and make use of a rich data structure that ends up looking something like this:

```yaml
 children_under_care:
   Billy:
     age: will be 5 in July
     behavioral_triggers:
       - visiting biological parents
     relation_to_user: foster son
     reported_issues:
       - spitting
       - pulling hair
     strategies_tried:
       - outcome: possibly helped, not sure
         strategy: spending quiet time after visits and talking about feelings
       - outcome: not successful, too stimulating
         strategy: sensory play with playdough
       - outcome: pending feedback
         strategy: using a calming jar
   Lisa:
     age: 3
     behavioral_triggers: []
     relation_to_user: foster daughter
     reported_issues: []
   Ricky:
     age: 13
     behavioral_triggers: []
     relation_to_user: son
     reported_issues:
       - resentment towards foster siblings
     strategies_tried: []
```

This tells the model HOW to use the tool and tries to steer it towards usage but it's not nearly effective enough and will fail to record lots of details.

We provide the model a process to follow when formulating it's responses:

- Before responding to the user message take the following steps:
  
  1. Evaluate the user message to determine if we've learned new information about them or the child under their care and:
     1. If new information was given: 
        1. If we did learn new information, use the memory tool to update the user metadata and record this new information as directed in the `Gather information` section
        2. Once the tool use is complete proceed to follow the guidelines for a normal response below
     2. If there's nothing worth storing in the metadata craft continue following these steps
  2. Determine if the user is indicating that they're going to try one of the strategies you've provided:
     1. Record the strategy in the metadata record for the child with a pending outcome.
     2. Create an `admin_postive` feedback entry, indicating that the user is following advice given
     3. Let the user know you're eager to hear how it worked out for them or discuss alternatives in a future session.

- When responding to the user:
  
  1. Generate three possible responses internally
  2. Review each against the critical guidelines and respond only with the shortest one that best adheres to the guidelines but bias towards including clarifying questions as long as the response stays conversational.

In "AI Bro" speak that's  "We engage the self reflection and introspection capabilities of the model to produce an output that best adheres to the foundation principles"  I personally call it "tell it to think before opening it's fat mouth".

Keep in mind that LLMs are completion engines at heart.  They "want" to generate output.  If you need the model to perform an action before generate content you need to lay out a step by step process for formulating a response it you want it to consistently follow the rules.

During integration testing with this tool the Ticco agent still missed a number opportunities. So we added an ACTUAL one-shot to the prompt:

> User: My foster son billy seems to suddenly want to spit on people.
> 
> ** Assistant stores the details about a child named billy, that's a foster to the user and has "spitting" as a behavioral issue ** 
> 
> Assistant: It sounds like Billy is expressing himself in a challenging way. Let's try to understand what might be triggering this behavior. Has anything changed recently in his environment or routine that could be upsetting him? Also, how old is Billy? This information can help tailor the approach to his needs.
> 
> User: He'll be 5 in July, and it's usually after visiting his bio parents.
> 
> ** Assistant stores the child's age and the behavioral trigger **
> 
> Assistant: Visits with biological parents can be quite emotional for kids, especially at Billy's age. It's possible he's feeling confused or overwhelmed and doesn't know how to express those big feelings. After visits, you might try spending some quiet time together, doing something he enjoys, to help him feel secure and connected. Also, gently talking to him about his feelings can help. You could say something like, "Visits with mom and dad can be a lot, huh? It's okay to feel upset. Let's find a calm way to express those feelings." Remember, connecting with Billy before trying to correct the behavior is key.
> 
> Does this sound like something you're willing to try?  Would you like to talk through some other ideas?
> 
> User: Yeah I think I can try that.
> 
> ** Assistant stores a note on the child record to follow up on the suggested strategy if the child is mentioned in a future session **
> 
> Assistant: Great!  Glad to hear it. Please feel free to come back to let me know how it worked out for you or if you'd like to continue discussing options.

This example conversation complete with lines to indicate the when the model should engage the tool was the final reinforcement that Ticco needed to reliably make use of the tool.

**Status**
This is a "reference tool", not a demo or toy.  It will very likely be made better, and is intended for use in production agents.

### Feedback

This tool introduces a feedback system using the same sort of metadata manipulation as the `MemoryTools` uses.  This gives the model the ability to record feedback in the chat session either at the explicit direction of the use or by rules laid out in the instructions.  Ticco uses this to record `admin_positive` feedback on the session.

Feedback entries include the most recent message ID from the agent so that we know which response generated the feedback. Feedback can be positive, negative, or undetermined.  And special `admin` categories for each exist.  

The model instructions for the tool tell the model that the return result will direct it on how to proceed.

- `admin_*` feedback is silent.  Aside from a tool use notification there's nothing to indicate that the model has just recorded your feedback.  This is primarily to prevent the model from thanking/analogizing to the user when we've forced it to record feedback.
- `positive` feedback will cause the model to thank the user for their feedback.
- `negative` feedback will generate an apology from the model and if there is ACTIONABLE feedback it will generate a new response based on their feedback and ask "was this better?"
- `undetermined` feedback is silently recorded.    

**Status**
This is a "reference tool", not a demo or toy.  It will very likely be made better, and is intended for use in production agents.

### The Workspace Tool

This tool allows the mode read/write access to one or more "Workspace" objects.  It can read, write and append to files within the workspace but can not get to arbitrary files unless you do something silly like set a workspace root to be your ACTUAL root folder of your disk.

**Status**
This is a "reference tool" under active development

### Local Storage Workspace

This allows the workspace tool to provide workspaces that use local storage.  It replaces the old File System Tool 

### Azure Workspace

This provides supports for workspaces based on Azure File Storage  

**Status**
This is a work in progress reference tool. Not at all yet ready, but listed here so folks know it's coming

### LinkedIn

This tool allows the model the ability to pull a LinkedIn profile. It use a non official client and can fail if you haven't logged into LinkedIn via your browser lately.

**Status**
This is a 100% throwaway tool made for a very specific demo.  A more robust tool that uses the official API and wasn't slapped together in minutes would be useful though.

### `RSSTools`

This gives the model the ability to fetch RSS feeds from a handful of sources.  See `/src/gent_c/tools/rss/__init__.py` for how to define a feed.  
The directions for use instruct the model to use the wbe tool for the full article.  

**Status**
Mostly a demo tool

### Centric RAG

This tool give the model the ability to call the legacy RAG agent behind the "Ask Centric Docs" plugin. 

**Status**
This is a 100% throwaway tool made for a very specific demo. This will be replaced by the `Query Vector Store` tool not that `Agent C` exists and can leverage `centric_segmentation`.  

### Query Vector Store

This tool will give the model to formulate it's own queries of a vector store to find relevant segments. [This post](https://gist.github.com/Donavan/5f92837bfec473ed0f17265db0a0c522) was a quick write up I did on the approach right after I had a version of it working reliably.  But like all things "back then" it was slow and expensive.  

**Status**
The initial version of this tool will be a lift and shift of that code from a spike over to this framework.

Long term this tool should be able to leverage the Weaviate hybrid search but even GPT-4 struggled. Progress made since 4.5 warrants another try at some point.

### `WeatherTools`

This tool lets the model grab a weather forecast using a python library.

**Status**
This is a toy/demo tool not intended for production use. 

### `Web`

This allows the model to fetch the contents of a web page.  However, HTML has a TON of tokens in it that aren't content so we need to convert that HTML content into something smaller like Markdown. The Web tool has makes uses of classes inherited from  `ContentConverter` to convert HTML into a model friendly format. Different formatters can be used based on a regex on the URL.  

The default formatter will employ the readability algorithm to extract the main content of the page and convert it to Markdown.
See the `web_tool.md` file for more info.

**Status**
This is a "reference tool", no major changes anticipated.

### `User Bio`

This tool allows the model to maintain a profile of the user in order to better tailor it's output.  It's modeled on the child tracker for Ticco, and is under heavy development. Uses the memory tool for heavy lifting

**Status**
This is a work in progress reference tool

## We need more tools!

This is one area people could have an immediate impact on the capabilities of our agents. We need people who will say "It'd be really cool if an agent can do X" that also know how to write the code to do X.
