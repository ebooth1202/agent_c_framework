import os
import json
import openai
import tiktoken
import asyncio
import logging


from collections import defaultdict
from openai import AsyncOpenAI, AsyncStream, AsyncAzureOpenAI


from tiktoken import Encoding, encoding_for_model
from openai.types.chat import  ChatCompletionChunk


from typing import Any, Dict, List, Union, Optional, Callable, AsyncGenerator

from agent_c.chat.session_manager import ChatSessionManager
from agent_c.models.image_input import ImageInput
from agent_c.util.token_counter import TokenCounter
from agent_c.agents.base import BaseAgent
from agent_c.toolsets.tool_set import Toolset


class TikTokenTokenCounter(TokenCounter):
    """
    This is a token counter that uses the TikToken Encoding model to count tokens.
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.encoder: Encoding = encoding_for_model(model_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

class GPTChatAgent(BaseAgent):

    def __init__(self, **kwargs) -> None:
        """
        Initialize ChatAgent object.

        Non-Base Parameters:
        client: AsyncOpenAI, default is AsyncOpenAI()
            The client to use for making requests to the Open AI API.
        """
        kwargs['model_name'] = kwargs.get('model_name', "gpt-4o")
        kwargs['token_counter'] = kwargs.get('token_counter', TikTokenTokenCounter())
        super().__init__(**kwargs)
        self.schemas: Union[None, List[Dict[str, Any]]] = None
        if kwargs.get("client", None) is None:
            if os.environ.get("AZURE_OPENAI_ENDPOINT", None) is not None and os.environ.get("AZURE_OPENAI_API_KEY", None) is not None:
                self.client = AsyncAzureOpenAI(azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                                               api_key=os.environ["AZURE_OPENAI_API_KEY"],
                                               api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-03-01-preview"))
                self.model_name = os.environ.get("AZURE_OPENAI_MODEL", self.model_name)
            else:
                self.client = kwargs.get("client", AsyncOpenAI())

        self.encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        self.can_use_tools = True
        self.supports_multimodal = True

        # Temporary until all the models support this
        if self.model_name in ["gpt-o1", 'gpt-o1-mini', 'gpt-o3', 'gpt-o3-mini']:
            self.root_message_role = "developer"


    def _generate_multi_modal_user_message(self, user_input: str, images: List[ImageInput]) -> Union[List[dict[str, Any]], None]:
        if self.mitigate_image_prompt_injection:
            text = f"User: {user_input}{BaseAgent.IMAGE_PI_MITIGATION}"
        else:
            text = user_input

        contents = [{"type": "text", "text": text}]

        for image in images:
            url: Union[str, None] = image.url

            if url is None and image.content is not None:
                url = f"data:{image.content_type};base64,{image.content}"

            if url is not None:
                contents.append({"type": "image_url", "image_url": {"url": url}})

        return [{"role": "user", "content": contents}]

    async def __call_function(self, function_id: str, function_args: Dict) -> Any:
        """
        Call a function asynchronously.

        Parameters:
        function_id: str
            Identifies the function to be called.
        function_args: Dict
            Arguments for the function to be called.

        Returns: The function call result.
        """
        toolset, function_name = function_id.split(Toolset.tool_sep, 1)
        try:
            src_obj: Toolset = self.tool_chest.active_tools[toolset]
            if src_obj is None:
                return f"{toolset} is not a valid toolset."

            function_to_call: Any = getattr(src_obj, function_name)

            return await function_to_call(**function_args)
        except Exception as e:
            logging.exception(f"Failed calling {function_name} on {toolset}. {e}")
            return f"Important!  Tell the user an error occurred calling {function_name} on {toolset}. {e}"

    async def __interaction_setup(self, **kwargs) -> dict[str, Any]:
        json_mode: bool = kwargs.get("json_mode", False)
        model_name: str = kwargs.get("model_name", self.model_name)
        kwargs['prompt'] = kwargs.get('prompt', self.prompt)
        sys_prompt: str = await self._render_system_prompt(**kwargs)
        temperature: float = kwargs.get("temperature", self.temperature)
        max_tokens: Union[int, None] = kwargs.get("max_tokens", None)

        messages = await self._construct_message_array(system_prompt=sys_prompt, **kwargs)

        functions: List[Dict[str, Any]] = self.tool_chest.active_open_ai_schemas
        completion_opts = {"model": model_name, "temperature": temperature, "messages": messages, "stream": True}
        if len(functions):
            completion_opts['tools'] = functions

        if max_tokens is not None:
            completion_opts['max_tokens'] = max_tokens

        if json_mode:
            completion_opts['response_format'] = {"type": "json_object"}

        user = kwargs.get("user_name", None)
        if user is not None:
            completion_opts["user"] = user



        return {'completion_opts':completion_opts, 'callback_opts': self._callback_opts(**kwargs)}

    async def one_shot(self, **kwargs) -> str:
        """
               Perform the chat operation as a one shot.

               Parameters:
               temperature: float, default is self. temperature
                   Controls randomness. Low temperature results in more focused and deterministic output.
               model_name: str, default is self.model_name
                   The language model to be used.
               prompt_metadata: dict, default is empty dict
                   Metadata to be used for rendering the prompt via the PromptBuilder
               session_manager: ChatSessionManager, default is None
                   A session manager to use for the message memory / session info
               session_id: str, default is "none"
                   The session id to use for the chat, if you haven't provided a session manager.
               agent_role: str, default is "assistant"
                   The role of the agent in the chat event stream
               messages: List[dict[str, Any]], default is None
                   A list of messages to use for the chat.
                   If this is not provided, but a session manager is, the messages will be constructed from the session.
               output_format: str, default is "raw"
                   The format to signal the client to expect

               Returns: The text of the model response.
               """
        kwargs['output_format'] = kwargs.get('output_format', 'raw')
        messages = await self.chat(**kwargs)
        return messages[-1]['content']

    async def chat(self, **kwargs) -> List[dict[str, Any]]:
        """
        Perform the chat operation.

        Parameters:
        temperature: float, default is self. temperature
            Controls randomness. Low temperature results in more focused and deterministic output.
        model_name: str, default is self.model_name
            The language model to be used.
        prompt_metadata: dict, default is empty dict
            Metadata to be used for rendering the prompt via the PromptBuilder
        session_manager: ChatSessionManager, default is None
                   A session manager to use for the message memory / session info
       session_id: str, default is "none"
           The session id to use for the chat, if you haven't provided a session manager.
       agent_role: str, default is "assistant"
           The role of the agent in the chat event stream
       messages: List[dict[str, Any]], default is None
           A list of messages to use for the chat.
           If this is not provided, but a session manager is, the messages will be constructed from the session.
        agent_role: str, default is "assistant"
            The role of the agent in the chat event stream
        output_format: str, default is "markdown"
            The format to signal the client to expect

        Returns: A list of messages from the chat.
        """
        opts = await self.__interaction_setup(**kwargs)
        messages: List[dict[str, str]] = opts['completion_opts']['messages']
        session_manager: Union[ChatSessionManager, None] = kwargs.get("session_manager", None)
        interacting: bool = True

        delay = 1  # Initial delay between retries

        async with self.semaphore:
            while interacting and delay < self.max_delay:
                try:
                    tool_calls = []
                    stop_reason: Union[str, None] = None
                    await self._cb_completion(True, **opts['callback_opts'])
                    response: AsyncStream[ChatCompletionChunk] = await self.client.chat.completions.create(**opts['completion_opts'])
                    await self._cb_completion(False, **opts['callback_opts'])

                    collected_messages: List[str] = []

                    try:
                        async for chunk in response:
                            if len(chunk.choices) == 0:
                                continue
                            if stop_reason is None:
                                stop_reason = chunk.choices[0].finish_reason

                            delta = chunk.choices[0].delta
                            if delta.tool_calls is not None:
                                self.__handle_tool_use_fragment(delta.tool_calls[0], tool_calls)
                                # await self._cb_tools(tool_calls, **opts['callback_opts'])

                            elif delta.content is None and chunk.choices[0].finish_reason == 'tool_calls':
                                try:
                                    await self._cb_tools(tool_calls, **opts['callback_opts'])
                                    result_messages = await self.__tool_calls_to_messages(tool_calls)
                                    await self._cb_tools(**opts['callback_opts'])
                                except Exception as e:
                                    logging.exception(f"Failed calling toolsets {e}")
                                    result_messages = []
                                messages.extend(result_messages)
                            else:
                                chunk_message: Union[str, None] = delta.content
                                if chunk_message is not None:
                                    if len(collected_messages) == 0:
                                        await self._cb_start(True, **opts['callback_opts'])
                                    collected_messages.append(chunk_message)
                                    await self._cb_token(chunk_message, **opts['callback_opts'])

                        if stop_reason != 'tool_calls':
                            output_text = "".join(collected_messages)
                            messages.append(await self._save_interaction_to_session(session_manager, output_text))
                            await self._cb_messages(messages, **opts['callback_opts'])
                            interacting = False

                    except openai.APIError as e:
                        logging.exception("OpenAIError occurred while streaming responses: %s", e)
                        await self._cb_system(f"An error occurred while streaming responses. {e}\n. Backing off delay at {delay} seconds.",
                                              **opts['callback_opts'])
                        if delay >= self.max_delay:
                            raise
                        await self._exponential_backoff(delay)
                        delay *= 2

                except openai.BadRequestError as e:
                    logging.exception("Invalid request occurred: %s", e)
                    for message in messages:
                        print(json.dumps(message))
                    raise
                except openai.APITimeoutError as e:
                    logging.exception("OpenAIError occurred: %s", e)
                    if delay >= self.max_delay:
                        raise
                    await self._exponential_backoff(delay)
                    delay *= 2
                except openai.InternalServerError as e:
                    logging.exception("Open AI InternalServerError occurred: %s", e)
                    if delay >= self.max_delay:
                        raise
                    await self._exponential_backoff(delay)
                    delay *= 2
                except Exception as e:
                    s = e.__str__()
                    logging.exception("Error occurred during chat completion: %s", e)
                    raise

        return messages


    @staticmethod
    def __handle_tool_use_fragment(tool_call, tool_calls):
        index = tool_call.index
        if index == len(tool_calls):
            tool_calls.append(defaultdict(str))
        if tool_call.id:
            tool_calls[index]['id'] = tool_call.id
        if tool_call.function:
            if tool_call.function.name:
                tool_calls[index]['name'] = tool_call.function.name
            if tool_call.function.arguments:
                tool_calls[index]['arguments'] += (tool_call.function.arguments)

    async def __tool_calls_to_messages(self, tool_calls):
        async def make_call(tool_call):
            fn = tool_call['name'] #.replace(".", Toolset.tool_sep)  # The agent sometimes messes this up
            args = json.loads(tool_call['arguments'])
            ai_call = {"id": tool_call['id'],
                       "function": {"name": fn, "arguments": tool_call['arguments']},
                       'type': 'function'
                       }
            try:
                function_response = await self.__call_function(fn, args)

                call_resp = {"role": "tool", "tool_call_id": tool_call['id'], "name": fn,
                             "content": function_response}

            except Exception as e:
                call_resp = {"role": "tool", "tool_call_id": tool_call['id'], "name": fn,
                             "content": f"Exception: {e}"}

            return ai_call, call_resp

        # Schedule all the calls concurrently
        tasks = [make_call(tool_call) for tool_call in tool_calls]
        completed_calls = await asyncio.gather(*tasks)

        # Unpack the resulting ai_calls and resp_calls
        ai_calls, results = zip(*completed_calls)

        return [{'role': 'assistant', 'tool_calls': list(ai_calls), 'content': ''}] + list(results)
