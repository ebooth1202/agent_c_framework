# Making the magic happen

Back in lesson one I wrote:

> Later we'll get into all the wonderful ways we can use and abuse the system prompt to work "magic"

This is the lesson where we start to get into those ways.  This isn't one of those "how to write a GPT prompt" guides either.  Oddly enough for a lesson on system prompts there's not going to be a lot of talk about prompting.

## System prompts

One-shots can use straightforward  system prompts that just instruct them what to do with the user message and how to respond.  The instructions can be very complex, involving advanced prompt engineering techniques but at the end of the day, they're still a set of instructions for a single task.

**Prompt Engineering**

> The term "prompt engineering" gets thrown around a lot.  It's often misused and is known to generate sneers of derision from some segments of the LLM community.  Prompt engineering is a thing, but it's not what the hucksters try to sell people on.
> 
> Prompt engineering is a relatively new discipline for developing and optimizing prompts to efficiently use language models.  It's a MASSIVE topic and beyond the scope of this lesson.  But if you'd like to nerd out,  take a look at some of the prompting techniques on the [Prompt Engineering Guide](https://www.promptingguide.ai/techniques) website.

An interactive agent can be expected to handle multiple things.  Users want their agent to "learn" about them.  They'd like their agents to perform a wide variety of tasks, each requiring a tool  We as the IP owners don't want our IP leaked.  If we're hosting a chatbot we don't want it agreeing to sell a car for $1, or telling someone to harm themselves.  The list goes on and on.

All of that functionality is only possible via the system prompt, and to a lesser extent the tool definitions.  The model doesn't "know" what the date is, there's a line in the system prompt saying "*Today is Friday 4/7/2024 it is 14:45 UTC-5*". The model doesn't "remember" that my name is Donavan and I work for Centric, there's a "User Bio" section in the system prompt that gets populated with metadata from the user record.  Sure the agent stored the metadata, but it doesn't know that unless we tell it.

If we wanted to put together a system prompt for a publicly facing agent we'd to a system prompt that:

- Prevents the prompt itself from being leaked.

- Keeps things on topic

- Refuses to offer medical advice and directs the user to medical professionals.

- Refuses to assist with emergencies or hazardous situations and directs the user to the authorities.

- Provides a "persona".

- Provides more detailed directions for tools that tool definitions can't cover

- Tells the agent about the user/world/current events

- Tells the agent the things it has "remembered"

We've got to cram all that into a string to hand to the model each completion pass.   This is an outline of sorts for an Agent C system prompt.  Our prompts are in Markdown and the full prompt can't be embedded into into Markdown code block here  without things getting wonky.

```markdown
<ILikePie>PREAMBLE</ILikePie>
<operating_guidelines>

**guardrails**

## Safety Instructions

## Your Persona
</operating_guidelines>

<tool_guidelines>
## RSS Feeds
### Available feeds.

## User Preferences

## Workspaces
### Available Workspaces

## DALL-E-3
</tool_guidelines>

# Helpful information

## Runtime Environment
### Session Info
####Session Metadata

## User Information

### System provided data (User)

### Assistant data (User)
```

Even without the text in each section, that's a LOT.  Then when you consider that some of that information needs to be updated after a tool call completes, but before you send the results back, things can get complicated.  Let's talk about how Agent C helps manage this

**Why XML?**

> Astute readers will note that I said our prompts were in Markdown and I then showed you **terrible** XML. This is where some of that prompt engineering I've mentioned comes into play.
> 
> By enclosing portions of our prompt we create what amount to "named entities" for text.  As the conversation starts growing and the token count climbs the model can start getting a bit fuzzy about what directions it follows.  By establishing `operating_guidelines` and `tool_guidelines` as "things" we can help the model hold on to them and it allows the model to ignore the extra tool instructions when it doesn't need them in the attention algorithm. 
> 
> The opening `<ILikePie>` tag is a "fuse". If that token ever shows up in the chat event stream you immediately know that someone has bypassed any prompt protection guardrails you have in place.  This isn't foolproof protection mind you, but it'll stop "script kiddies".  Adding more / different fuses might be advisable.

Oh and...

**Why Markdown**

> In a nutshell, Markdown uses the least extra tokens of all of the markup languages the models understand.  The models can follow the structure of headers, bullets etc.   

## Prompt composition in Agent C

Our prompt composition system allows us to build a "layer cake" system prompt,  comprised of a series of `PromptSection` objects.  A `PromptBuilder` is responsible for rendering those sections into a string to be used for the prompt.

### Prompt Sections

A `PromptSection` class represents our basic building block for prompts.  They are essentially wrappers around the Python string templating system, with a small bonus. They can be just a simple string and don't require any sort of subclass to use:

```python
persona_section = PromptSection(name="persona", 
                                template="You are a helpful assistant")
```

This would render as:

```t4
You are a helpful assistant
```

To prevent one section from bleeding into another you can either include some sort of divider in your template, or enable the `render_section_header` option in the constructor.  If we had done so above it would have rendered as:

```markdown
## persona
You are a helpful assistant
```

Now you should be able to count the prompt sections in the outline above, give or take a couple.

#### Static prompt sections

The module  `agent_c.prompting.simple_prompt_parts` has a dedicated `PersonaSection`  that serves as an easy to follow example of a static prompt section:

```python
class PersonaSection(PromptSection):
    def __init__(self, **data: Any):
        TEMPLATE = "You are a helpful agent assisting users in a calm, casual yet professional manner. " \
                   "Be friendly and cheerful and assist users with their requests while staying mindful of the operating guidelines"
        data['template'] = data.get('template', TEMPLATE)
        super().__init__(name="Your Persona", 
                         render_section_header=True, 
                         **data)
```

The `PromptSection` base class is a  [Pydantic](https://github.com/pydantic/pydantic)  model (as are all of the models but that's implied) so our init looks a little off.  All this class is doing is just setting the properties up of the base class.  A static section just makes it easy to reuse blocks of instructions.

It bears noting that "static" isn't quite accurate. More like "semi-dynamic".  We'll discuss it more when we talk about dynamic sections, but you can still reference data from the "property bag" with "static" sections.

**Tool sections**

> The tool declarations often don't allow for the level of instruction required for the models to use complex tools.  At some point they'll solve this with the tools declarations but in the mean time Agent C allows tools to declare their own `PromptSections` which are usually just static sections like the one above but can be dynamic for more advanced tools.

#### Dynamic prompt sections

When a `PromptSection` is being rendered it is handed a "property bag" which is just a dictionary with string keys. Before passing that bag on to the string template render method, the base class will call any method on itself that's been decorated as property bag item and add the return to the property bag.  Here's a shortened example from the `UserPrefSection` for handling user preferences:

```python
template = "The available user preferences are: ${pref_names}\n\n"

@property_bag_item
async def pref_names(self):
    return ', '.join(f"`{pref.name}`" for pref in self.user_preferences)
```

When the section is rendered, the property bag will contain a `pref_names` key with the output of this method, which will then get passed to the string template renderer to do the replacements.

**Note:**

> A case could EASILY be made that this should use a real templating engine.  I agree!  Pull requests are welcome!

**Why the two methods?**

> The property bag approach, while far simpler has some drawbacks.
> 
> 1. All items must be placed in the bag by whatever is initiating the interaction.
> 
> 2. Whatever is initiating the interaction can't update the property bag until the interaction finishes.
> 
> Note: An "interaction" can be thought of as the time from when you call `chat` or `one_shot` till that call completes.  Any single interaction could have many MANY completion calls.
> 
> If you have a tool that provides information via a `PromptSection`  you want that information to be up to date for each completion call, not when the interaction finally wraps up

### 

### Prompt Builder, the last piece of the puzzle.

The `PromptBuilder` is almost inconsequential.  It's just a container that holds a list of `PromptSections` and when asked to render them, loops through them calling their own render method.

So if we wanted start using composition in our example we would start by turning out prompt into a persona and setting up our layers:

```python
prompt: str = "You are a helpful assistant helping people learn about, build and test AI agents"
my_sections = [PersonaSection(template=prompt)] + tool_chest.active_tool_sections
```

This adds our persona to the start of the prompt, then any prompt sections for active tools in the toolchest.

Next we need to hand the prompt builder off to the agent when we call chat:

```python
agent = GPTChatAgent(tool_chest=tool_chest, 
                     model_name="gpt-4-turbo-preview", 
                     streaming_callback=chat_callback)

while True:
    user_message = await ui.get_user_input()
    if user_message == "exit":
        break

    prompt_metadata = {}
    messages = await agent.chat(user_message=user_message, 
                                messages=messages,
                                prompt_builder=PromptBuilder(sections=my_sections),
                                prompt_metadata=prompt_metadata)
```

The file `learn/example_code/example_13.py`   has a full version of this.

We'll be touching on tool sections a bit more in the upcoming lesson but it will be far less heavy.
