# Initial steps with Agent C

The codebase that is now Agent C emerged out of the "Simple One Shot" framework.  The initial `ChatAgent` class was a proof of concept that adapted the `ToolUseOneShot` into an interactive tool using agent written back in July of 2023.  It sat on the shelf until the spring of 2024 when it got dusted off and polished up for the Ticco agent for Trauma Free World.  It did fine for an MVP but the models have advanced a LOT since the day that was put together and so Agent C was born to take advantage of what was unfeasible back then.

At it's core, the `ChatAgent` class in Agent C is just a wrapper about the "chat completion" APIs provided by the vendors. It can be used as nothing more than that so that's where these lessons will start.  

## Understanding completions

Completions with large language models involve using an API to send user input (prompts) to the model and receive generated text (completions) in response.  *Chat completions* provide "syntactic sugar" that let's us use a list of messages as the input for the completion.

It's important to understand that, when all is said and done, chat completions are still a matter of sending text to an API and receiving text back. Whether we're dealing with individual prompts or a sequence of messages formatted as a conversation, the large language model processes the text input and generates text output based on the patterns it has learned. This remains true until we venture into the realm of multimodal models, which can process and generate more than just text.  All that stuff about embeddings, vectors and what not are OUTSIDE of the actual model interaction.

It's also important to keep in mind that from the models "perspective" the entire conversation happens each time you make a completion call.  For right now, just understand that it happens.  We'll discuss ramifications later.

There are many parameters involved in a completion call but between the vendors and Agent C there are sensible defaults for everything except the user input.  This shows the simplest usage of Agent C possible.

```python
# Import the GPT Agent
from agent_c import GPTChatAgent

async def main():
    # Create an instance of the agent
    agent = GPTChatAgent()

    # Send in a text prompt, get a text response
    result: str = await agent.one_shot(user_message="What is the capital of France?")

    print(result)
```

The file `learn/example_code/example_1.py` has a version of this that includes the necessary `asyncio` boilerplate to run it. You should be able to just open the file in PyCharm and run it using the "Current file" configuration.

This implicitly uses gpt-3.5-turbo as it's the default model for that agent. It sends in a question via the `oneshot` interface to the agent which returns a string output.

The file `learn/example_code/example_2.py` shows the key parameters involved:

```python
async def main():
    agent = GPTChatAgent()

    temperature: float = 0.5
    model_name: str = "gpt-3.5-turbo"
    user_message: str = "What is the capital of France?"
    prompt: str = "You always respond as if you're annoyed"

    result: str = await agent.one_shot(model_name=model_name,
                                       user_message=user_message,
                                       prompt=prompt,
                                       temperature=temperature)

    print(result)
```

- `temperature` can be thought of as increasing variety in responses.  The closer to zero it is the more consistent, but more robotic, the responses become.
- `model_name` should be self explanatory see the Open AI docs for an up-to-date list.
- `prompt` this string forms the system prompt.

System prompts play a crucial role in the interaction between humans and large language models (LLMs). These prompts serve as initial instructions or context provided to the LLM, guiding its response generation and behavior. They can be used to set the tone, establish the desired output format, or provide specific constraints or guidelines for the LLM to follow.

Having control of the system prompt alone is worth using the API.  If you've had problems getting ChatGPT or Claude to follow your directions, the system prompts injected by the vendors are likely to blame.

Later we'll get into all the wonderful ways we can use and abuse the system prompt to work "magic" for now thinking of it as "the instructions for what to do with the user message" is probably the most clear.