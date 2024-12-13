## "Layer Cake" prompts

Much like the one shots which it is based on a `ChatAgent` can accept a `prompt` parameter which allows you to pass in a system prompt.  That's fine when you're just supplying directions for the model to take in processing the data you're sending it but for an agent we often want to equip it with information about the user it's talking with or other useful information.  It's also a pain to allow different people to focus on different parts of the prompt.

The initial version of this approach was written specifically so that I could allow clients to participate in instructing the model without them having to see all technical parts of the prompt that don't deal with the persona.  It was basically just a series of templates that used a bag of properties from the `__build_prpmpt_metadata` to gnerate the prompt.

Since then I've extended the functionality so that a section can supply the metadata it needs to complete the template without relying on a property bag to be passed in, though that's still supported.

### `PromptSection`
The file `centric_one_shot/prompting/prompt_section.py` defines the base class for a prompt section. They're Pydantic models that look like this:

```python
class PromptSection(BaseModel):
    name: str
    template: str
    render_section_header: bool = True
    required: bool = False
```

- `name` - IS a human readable name and will de displayed as a header if `render_section_header` is true.
- `tamplate` - A string template that will be rendered to gnerate the prompt text.
- `render_section_header` - Set this to false, if your section is really a subsection or continuation of the previous section.
- `required` - If this is set to true and the render of the template fails and exception will be thrown and the completion will not occur.  If it's false, the failure to render the section will be logged but the completion call will still go through.


#### Dynamic properties
`get_dynamic_properties` is called as part of the rendering process for each section.  It's job is to find any method tagged as property bag item, call it, and add the output to the property bag.

```python
async def get_dynamic_properties(self) -> Dict[str, Any]:
    dynamic_props: Dict[str, Any] = {}
    for attr_name in dir(self):
        # Skip internal or special attributes
        if attr_name.startswith('_'):
            continue

        attr = getattr(self, attr_name)
        if callable(attr) and getattr(attr, 'is_property_bag_item', False):
            try:
                dynamic_props[attr_name] = await attr()
            except Exception as e:
                logging.exception(f"Error getting dynamic property '{attr_name}': {e}")
    return dynamic_props
```

To mark a method as a property bags item. We make use of the aptly named `property_bag_item` function decorator.  Let's look at an actual section to see how that works.

#### `EnvironmentInfoSection`
The file `centric_one_shot/prompting/env_info_section.py` defines a simple section that lets the model know a little about the environment it's in. 

```python
class EnvironmentInfoSection(PromptSection):
    session_id: str

    def __init__(self, **data: Any):
        TEMPLATE = "current time: ${timestamp}.\nenvironment: ${env_name}\nsession id: ${session_id}"
        super().__init__(template=TEMPLATE, name="Runtime Environment", **data)

    @property_bag_item
    async def timestamp(self):
        local_time = datetime.now()
        local_time_with_tz = local_time.astimezone()
        formatted_timestamp = local_time_with_tz.strftime('%A %B %-d, %Y %-I:%M%p (%Z %z)')
        return formatted_timestamp

    @property_bag_item
    async def env_name(self):
        return os.environ.get("ENVIRONMENT", "Local_dev")
```

- `session_id` - Is static for the session so, we pass it in via the constructor for the section like so: `EnvironmentInfoSection(session_id=self.zep_cache.session.session_id)
- `TEMPLATE` contains the string template that will be used to render the output. The `${variable_name}` portions are where values from the property bag will be substituted in.
- `timestamp` and `env_name` are property bag items.  Their output will be added to the property bag using the method name as the key.
- Note that both property bag items are aysnc.  Everything along the critical path for completion needs to be async so that we don't block when running in a real multi-user application.
- Note also, that they return strings, as the value will be used in a string substitution.


### `PromptBuilder`
There's not a lot to say about `PromptBuilder` except how to use it.  It's a very simply object that holds an array of prompt sections and has a `render` method that simply calls each section in turn asking it to render and builds a string.

