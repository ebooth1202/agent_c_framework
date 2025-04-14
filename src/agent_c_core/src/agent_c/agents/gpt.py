import os
import json

import openai
import tiktoken
import asyncio

from collections import defaultdict
from openai import AsyncOpenAI, AsyncStream, AsyncAzureOpenAI

from tiktoken import Encoding, encoding_for_model
from openai.types.chat import ChatCompletionChunk

from typing import Any, Dict, List, Union, Optional, Tuple

from agent_c.chat.session_manager import ChatSessionManager
from agent_c.models.input import FileInput
from agent_c.models.input.audio_input import AudioInput
from agent_c.models.events.chat import ReceivedAudioDeltaEvent
from agent_c.models.input.image_input import ImageInput
from agent_c.util.token_counter import TokenCounter
from agent_c.agents.base import BaseAgent
from agent_c.util.logging_utils import LoggingManager


class TikTokenTokenCounter(TokenCounter):
    """
    This is a token counter that uses the TikToken Encoding model to count tokens.
    """
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.encoder: Encoding = encoding_for_model(model_name)

    def count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))


class GPTChatAgent(BaseAgent):
    REASONING_MODELS: List[str] = ["o1", 'o1-mini', 'o3', 'o3-mini']

    def __init__(self, **kwargs) -> None:
        """
        Initialize ChatAgent object.

        Non-Base Parameters:
        client: AsyncOpenAI, default is AsyncOpenAI()
            The client to use for making requests to the Open AI API.
        """
        kwargs['model_name']: str = kwargs.get('model_name')
        kwargs['token_counter'] = kwargs.get('token_counter', TikTokenTokenCounter())
        super().__init__(**kwargs)
        self.schemas: Union[None, List[Dict[str, Any]]] = None

        # Initialize the client based on environment or provided client
        if kwargs.get("client", None) is None:
            if os.environ.get("AZURE_OPENAI_ENDPOINT", None) is not None and os.environ.get("AZURE_OPENAI_API_KEY", None) is not None:
                self.client = AsyncAzureOpenAI(
                    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
                    api_key=os.environ["AZURE_OPENAI_API_KEY"],
                    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-03-01-preview")
                )
                self.model_name = os.environ.get("AZURE_OPENAI_MODEL", self.model_name)
            else:
                self.client = kwargs.get("client", AsyncOpenAI())
        else:
            self.client = kwargs.get("client")

        self.encoding = tiktoken.encoding_for_model('gpt-3.5-turbo')
        self.can_use_tools = True
        self.supports_multimodal = True

        # Temporary until all the models support this
        if self.model_name in self.__class__.REASONING_MODELS:
            self.root_message_role = "developer"

        logging_manager = LoggingManager(__name__)
        self.logger = logging_manager.get_logger()

    def _generate_multi_modal_user_message(self, user_input: str, images: List[ImageInput], audio_clips: List[AudioInput], files: List[FileInput] = None) -> Union[List[dict[str, Any]], None]:
        """
        Generates a multimodal message containing text, images, audio, and file content.

        Args:
            user_input (str): The user's text message
            images (List[ImageInput]): List of image inputs to include
            audio_clips (List[AudioInput]): List of audio inputs to include
            files (List[FileInput]): List of file inputs to include

        Returns:
            Union[List[dict[str, Any]], None]: Formatted message content for OpenAI
        """
        self.logger.debug("Starting _generate_multi_modal_user_message")
        contents = []

        # Add text content if available
        if user_input is not None and len(user_input) > 0:
            contents.append({"type": "text", "text": user_input})

        # Add images
        for image in images:
            url: Union[str, None] = image.url

            if url is None and image.content is not None:
                url = f"data:{image.content_type};base64,{image.content}"

            if url is not None:
                contents.append({"type": "image_url", "image_url": {"url": url}})

        # Add audio clips
        for clip in audio_clips:
            contents.append({"type": "input_audio", "input_audio": {"data": clip.content, 'format': clip.format}})

        # Add file content as additional text blocks
        if files:
            for file in files:
                text_content = file.get_text_content()

                if text_content:
                    file_name = file.file_name or "unknown file"
                    contents.append({
                        "type": "text",
                        "text": f"Content from file {file_name}:\n{text_content}"
                    })
                else:
                    # If no text content available, at least mention the file
                    file_name = file.file_name or "unknown file"
                    contents.append({
                        "type": "text",
                        "text": f"[File uploaded by user: {file_name}. But preprocessing failed to extract any text]"
                    })

        return [{"role": "user", "content": contents}]

    async def __interaction_setup(self, **kwargs) -> dict[str, Any]:
        """
        Set up the interaction parameters for the OpenAI API request.

        Returns:
            dict[str, Any]: Dictionary containing completion options and callback options
        """
        self.logger.debug("Starting __interaction_setup")

        json_mode: bool = kwargs.get("json_mode", False)
        model_name: str = kwargs.get("model_name", self.model_name)
        if model_name is None:
            raise ValueError('GPT agent is missing a model_name')

        kwargs['prompt'] = kwargs.get('prompt', self.prompt)
        sys_prompt: str = await self._render_system_prompt(**kwargs)
        temperature: float = kwargs.get("temperature", self.temperature)
        max_tokens: Optional[int] = kwargs.get("max_tokens", None)
        tool_choice: str = kwargs.get("tool_choice", "auto")
        voice: Optional[str] = kwargs.get("voice", None)
        tool_chest = kwargs.get("tool_chest", self.tool_chest)

        messages = await self._construct_message_array(system_prompt=sys_prompt, **kwargs)
        functions: List[Dict[str, Any]] = tool_chest.active_open_ai_schemas

        # Configure completion options based on model type
        if model_name in self.__class__.REASONING_MODELS:
            reasoning_effort = kwargs.get("reasoning_effort", "medium")
            completion_opts = {
                "model": model_name,
                "messages": messages,
                "stream": True,
                "reasoning_effort": reasoning_effort
            }
        else:
            completion_opts = {
                "model": model_name,
                "temperature": temperature,
                "messages": messages,
                "stream": True
            }
            if voice is not None:
                completion_opts['modalities'] = ["text", "audio"]
                completion_opts['audio'] = {"voice": voice, "format": "pcm16"}

        completion_opts['stream_options'] = {"include_usage": True}

        # Add tools if available
        if len(functions):
            completion_opts['tools'] = functions
            completion_opts['tool_choice'] = tool_choice

        # Add max tokens if specified
        if max_tokens is not None:
            completion_opts['max_completion_tokens'] = max_tokens

        # Set JSON response format if required
        if json_mode:
            completion_opts['response_format'] = {"type": "json_object"}

        # Add user identifier if available
        user = kwargs.get("user_name", None)
        if user is not None:
            completion_opts["user"] = user

        return {
            'completion_opts': completion_opts,
            'callback_opts': self._callback_opts(**kwargs),
            'tool_chest': tool_chest
        }

    async def one_shot(self, **kwargs) -> str:
        """
        Perform the chat operation as a one shot.

        Parameters:
            kwargs:
                temperature (float): Controls randomness
                model_name (str): The language model to be used
                prompt_metadata (dict): Metadata for rendering the prompt
                session_manager (ChatSessionManager): Session manager for message memory
                session_id (str): Session ID for the chat
                agent_role (str): Role of the agent in the chat
                messages (List[dict]): List of messages for the chat
                output_format (str): Format to signal the client to expect

        Returns:
            str: The text of the model response
        """
        kwargs['output_format'] = kwargs.get('output_format', 'raw')
        messages = await self.chat(**kwargs)
        return messages[-1]['content']

    async def _save_audio_interaction_to_session(self, mgr: ChatSessionManager, audio_id, transcript: str):
        """
        Save audio interaction to the session.

        Args:
            mgr (ChatSessionManager): The session manager
            audio_id (str): ID of the audio
            transcript (str): Transcript of the audio

        Returns:
            dict: Dictionary containing role and audio information
        """
        self.logger.debug("Starting _save_audio_interaction_to_session")
        await self._save_message_to_session(mgr, transcript, "assistant")
        return {"role": "assistant", "audio": {"id": audio_id}}

    @staticmethod
    def _init_stream_state() -> Dict[str, Any]:
        """
        Initialize the state dictionary for stream processing.

        Returns:
            Dict[str, Any]: Initial state for tracking stream progress
        """
        return {
            "collected_messages": [],
            "collected_tool_calls": [],
            "input_tokens": -1,
            "output_tokens": -1,
            "current_audio_id": None,
            "stop_reason": None,
            "usage_received": False,
            "complete": False,
            "interaction_id": None,
            "tool_calls_processed": False
        }

    async def _handle_text_delta(self, text: str, state: Dict[str, Any], callback_opts: Dict[str, Any]):
        """
        Handle text delta events.

        Args:
            text (str): Text content to process
            state (Dict[str, Any]): Current stream state
            callback_opts (Dict[str, Any]): Callback options
        """
        state["collected_messages"].append(text)
        try:
            await self._raise_text_delta(text, **callback_opts)
        except Exception as e:
            self.logger.error(f"Error raising text_delta event: {e}")

    async def _handle_audio_delta(self, audio_delta: Dict[str, Any], state: Dict[str, Any],
                                  callback_opts: Dict[str, Any]):
        """
        Handle audio delta events.

        Args:
            audio_delta (Dict[str, Any]): Audio data
            state (Dict[str, Any]): Current stream state
            callback_opts (Dict[str, Any]): Callback options
        """
        if state["current_audio_id"] is None:
            state["current_audio_id"] = audio_delta.get('id', None)

        transcript = audio_delta.get('transcript', None)
        if transcript is not None:
            state["collected_messages"].append(transcript)
            await self._raise_text_delta(transcript, **callback_opts)

        b64_audio = audio_delta.get('data', None)
        if b64_audio is not None:
            await self._raise_event(ReceivedAudioDeltaEvent(
                content_type="audio/L16",
                id=state["current_audio_id"],
                content=b64_audio,
                **callback_opts
            ))
        elif transcript is None:
            self.logger.warning("No audio data or transcript found in response")

    def _handle_tool_call_delta(self, tool_call, tool_calls):
        """
        Handle tool call delta events.

        Args:
            tool_call: The tool call delta
            tool_calls: List of current tool calls
        """
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

    async def _handle_completion_stop(self, state: Dict[str, Any], session_manager: ChatSessionManager,
                                      messages: List[Dict[str, Any]], callback_opts: Dict[str, Any],
                                      completion_opts: Dict[str, Any]):
        """
        Handle completion stop event.

        Args:
            state (Dict[str, Any]): Current stream state
            session_manager (ChatSessionManager): Session manager
            messages (List[Dict[str, Any]]): Current message list
            callback_opts (Dict[str, Any]): Callback options
            completion_opts (Dict[str, Any]): Completion options
        """
        # Raise completion end event with token usage information
        await self._raise_completion_end(
            completion_opts,
            stop_reason=state['stop_reason'],
            input_tokens=state['input_tokens'],
            output_tokens=state['output_tokens'],
            **callback_opts
        )

        # Only add text to messages if this is not a tool call
        # For tool calls, we'll get the real response in the follow-up API call
        if state['stop_reason'] != 'tool_calls' and not state["collected_tool_calls"]:
            # Process content based on whether we have audio or text
            output_text = "".join(state["collected_messages"])
            if output_text.strip():
                if state["current_audio_id"] is not None:
                    messages.append(await self._save_audio_interaction_to_session(
                        session_manager,
                        state["current_audio_id"],
                        output_text
                    ))
                else:
                    # Don't duplicate content if last message is already the same content
                    last_message = messages[-1] if messages else None
                    if not (last_message and last_message.get('role') == 'assistant' and last_message.get(
                            'content') == output_text):
                        messages.append(await self._save_interaction_to_session(session_manager, output_text))

        # Update history with final messages
        await self._raise_history_event(messages, **callback_opts)

        # Set completion flag
        state["complete"] = True

    async def _finalize_tool_calls(self, state: Dict[str, Any], tool_chest: Any, session_manager: ChatSessionManager,
                                   messages: List[Dict[str, Any]], callback_opts: Dict[str, Any]):
        """
        Finalize tool calls after receiving a complete message.

        Args:
            state (Dict[str, Any]): Current stream state
            tool_chest: Tool chest for calling functions
            session_manager (ChatSessionManager): Session manager
            messages (List[Dict[str, Any]]): Current message list
            callback_opts (Dict[str, Any]): Callback options
        """
        tool_calls = state["collected_tool_calls"]

        # Start tool call event
        await self._raise_tool_call_start(tool_calls, vendor="open_ai", **callback_opts)

        try:
            # Execute tool calls
            result_messages = await self.__tool_calls_to_messages(tool_calls, tool_chest)

            # End tool call event with results
            if result_messages:
                await self._raise_tool_call_end(tool_calls, result_messages[1:], vendor="open_ai", **callback_opts)
                messages.extend(result_messages)
                await self._raise_history_event(messages, **callback_opts)
        except Exception as e:
            self.logger.error(f"Failed calling toolsets: {e}")
            await self._raise_tool_call_end(tool_calls, [], vendor="open_ai", **callback_opts)
            await self._raise_system_event(f"An error occurred while processing tool calls: {e}", **callback_opts)

    async def _handle_retryable_error(self, error, delay, callback_opts):
        """
        Handle retryable errors with exponential backoff.

        Args:
            error: The error that occurred
            delay (int): Current delay time
            callback_opts (Dict[str, Any]): Callback options

        Returns:
            int: New delay time for next retry attempt
        """
        error_type = type(error).__name__
        await self._raise_system_event(
            f"{error_type} during API call. Delaying for {delay} seconds.\n",
            **callback_opts
        )
        await self._exponential_backoff(delay)
        return delay * 2  # Return the new delay for the next attempt

    async def _process_stream_event(self, chunk, state: Dict[str, Any], tool_chest: Any,
                                    session_manager: ChatSessionManager, messages: List[Dict[str, Any]],
                                    callback_opts: Dict[str, Any], completion_opts: Dict[str, Any]) -> bool:
        """
        Process a single event from the OpenAI stream.

        Args:
            chunk: The chunk from the OpenAI stream
            state (Dict[str, Any]): Current stream state
            tool_chest: Tool chest for calling functions
            session_manager (ChatSessionManager): Session manager
            messages (List[Dict[str, Any]]): Current message list
            callback_opts (Dict[str, Any]): Callback options
            completion_opts (Dict[str, Any]): Completion options

        Returns:
            bool: Whether to continue processing the stream
        """
        if chunk.choices is None:
            self.logger.debug("Choices in response is None - continuing")
            return True

        if len(chunk.choices) == 0:
            self.logger.debug("No choices in chunk - likely usage information")

            # Update token counts if available
            if chunk.usage is not None:
                state['input_tokens'] = chunk.usage.prompt_tokens
                state['output_tokens'] = chunk.usage.completion_tokens
                state['usage_received'] = True

            # If we have a stop reason and we're done with tools, handle completion stop
            if state['stop_reason']:
                await self._handle_completion_stop(state, session_manager, messages, callback_opts, completion_opts)

                # If we have tool calls to process, do that before ending
                if state['stop_reason'] == 'tool_calls' or len(state["collected_tool_calls"]):
                    await self._finalize_tool_calls(state, tool_chest, session_manager, messages, callback_opts)

                return False  # Stop processing the stream

            return True  # Continue processing the stream

        # Process choice content
        first_choice = chunk.choices[0]

        # If we have a finish reason, record it for later processing
        if first_choice.finish_reason is not None:
            state['stop_reason'] = first_choice.finish_reason

            # If tool calls were requested, mark for follow-up
            if first_choice.finish_reason == 'tool_calls':
                self.logger.debug("Tool calls detected from finish_reason")
                state["tool_calls_processed"] = True

        # Process different types of deltas
        if first_choice.delta.tool_calls is not None:
            self.logger.debug("Processing tool call fragment")
            self._handle_tool_call_delta(first_choice.delta.tool_calls[0], state["collected_tool_calls"])

            # Mark that we've seen tool calls
            if len(state["collected_tool_calls"]) > 0:
                state["tool_calls_processed"] = True

        elif first_choice.delta.content is not None:
            self.logger.debug(f"Processing text fragment: {first_choice.delta.content[:20]}...")
            await self._handle_text_delta(first_choice.delta.content, state, callback_opts)

        elif first_choice.delta.model_extra and first_choice.delta.model_extra.get('audio', None) is not None:
            self.logger.debug("Processing audio fragment")
            await self._handle_audio_delta(first_choice.delta.model_extra['audio'], state, callback_opts)

        return True  # Continue processing the stream

    async def _handle_gpt_stream(self, completion_opts: Dict[str, Any], tool_chest: Any,
                                 session_manager: ChatSessionManager, messages: List[Dict[str, Any]],
                                 callback_opts: Dict[str, Any], interaction_id) -> Tuple[List[Dict[str, Any]], Dict[str, Any], bool]:
        """
        Handle the OpenAI API streaming response.

        Args:
            completion_opts (Dict[str, Any]): Completion options for the API request
            tool_chest: Tool chest for calling functions
            session_manager (ChatSessionManager): Session manager
            messages (List[Dict[str, Any]]): Current message list
            callback_opts (Dict[str, Any]): Callback options

        Returns:
            Tuple[List[Dict[str, Any]], Dict[str, Any], bool]: Updated messages, state, and tool calls processed flag
        """
        await self._raise_completion_start(completion_opts, **callback_opts)

        # Initialize state
        state = self._init_stream_state()
        state['interaction_id'] = interaction_id

        # Start streaming
        self.logger.debug("Starting stream processing")
        response = await self.client.chat.completions.create(**completion_opts)

        try:
            async for chunk in response:
                # Process each chunk and check if we should continue
                continue_processing = await self._process_stream_event(
                    chunk, state, tool_chest, session_manager,
                    messages, callback_opts, completion_opts
                )

                if not continue_processing:
                    break

            # Final check if we need to close things out
            if not state['complete'] and state['collected_messages']:
                # If we have collected messages but haven't completed yet, finalize
                await self._handle_completion_stop(state, session_manager, messages, callback_opts, completion_opts)

                # If we have tool calls, process them
                if state['stop_reason'] == 'tool_calls' or len(state["collected_tool_calls"]):
                    await self._finalize_tool_calls(state, tool_chest, session_manager, messages, callback_opts)
                    state["tool_calls_processed"] = True

        except Exception as e:
            self.logger.error(f"Error during stream processing: {e}")
            raise

        # Use the flag that was set during processing instead of recomputing
        return messages, state, state["tool_calls_processed"]

    async def chat(self, **kwargs) -> List[dict[str, Any]]:
        """
        Perform the chat operation.

        kwargs:
            temperature (float): Controls randomness
            model_name (str): The language model to be used
            prompt_metadata (dict): Metadata for rendering the prompt
            session_manager (ChatSessionManager): Session manager for message memory
            session_id (str): Session ID for the chat
            agent_role (str): Role of the agent in the chat
            messages (List[dict]): List of messages for the chat
            output_format (str): Format to signal the client to expect

        Returns:
            List[dict[str, Any]]: A list of messages from the chat
        """
        self.logger.debug("Starting chat")
        opts = await self.__interaction_setup(**kwargs)
        messages = opts['completion_opts']['messages']
        session_manager = kwargs.get("session_manager", None)
        tool_chest = opts['tool_chest']

        delay = 1  # Initial delay between retries

        async with self.semaphore:
            self.logger.debug("Starting Interaction")
            interaction_id = await self._raise_interaction_start(**opts['callback_opts'])

            # Add a loop to handle follow-up API calls for tool use
            tool_calls_loop = True

            while tool_calls_loop and delay <= self.max_delay:
                try:
                    # Process the stream with all handling encapsulated
                    messages, state, tool_calls_processed = await self._handle_gpt_stream(
                        opts['completion_opts'],
                        tool_chest,
                        session_manager,
                        messages,
                        opts['callback_opts'],
                        interaction_id
                    )

                    # If tool calls were processed, we need to make another API call
                    if tool_calls_processed:
                        self.logger.debug("Tool calls processed, making follow-up API call for assistant response")
                        # Update the messages in the completion options for the next API call
                        opts['completion_opts']['messages'] = messages
                        # Continue the loop to make another API call
                        self.logger.debug(f"Follow-up messages: {json.dumps(messages[-3:])}")
                        self.logger.debug(f"Follow-up response received, message count: {len(messages)}")
                        continue
                    else:
                        # No more tool calls, we're done
                        tool_calls_loop = False
                        # End the interaction
                        await self._raise_interaction_end(id=interaction_id, **opts['callback_opts'])
                        self.logger.debug("Chat completed successfully")
                        return messages

                except openai.BadRequestError as e:
                    self.logger.error(f"Invalid request occurred: {e}")
                    await self._raise_system_event(f"Invalid request error: {e}", **opts['callback_opts'])
                    await self._raise_completion_end(opts["completion_opts"], stop_reason="exception",
                                                     **opts['callback_opts'])
                    await self._raise_interaction_end(id=interaction_id, **opts['callback_opts'])
                    raise

                except (openai.APITimeoutError, openai.InternalServerError) as e:
                    # Handle retryable errors
                    delay = await self._handle_retryable_error(e, delay, **opts['callback_opts'])
                    if delay > self.max_delay:
                        await self._raise_interaction_end(id=interaction_id, **opts['callback_opts'])
                        raise

                except Exception as e:
                    self.logger.error(f"Error occurred during chat completion: {e}")
                    await self._raise_system_event(f"Exception in chat completion: {e}", **opts['callback_opts'])
                    await self._raise_completion_end(opts["completion_opts"], stop_reason="exception",
                                                     **opts['callback_opts'])
                    await self._raise_interaction_end(id=interaction_id, **opts['callback_opts'])
                    raise

        # This should not be reached as we either return or raise
        self.logger.error("Chat reached end of function without proper return")
        return messages

    async def __tool_calls_to_messages(self, tool_calls, tool_chest):
        """
        Convert tool calls to message format and execute them.

        Args:
            tool_calls: List of tool calls to process
            tool_chest: Tool chest containing available functions

        Returns:
            List of messages resulting from tool calls
        """

        async def make_call(tool_call):
            fn = tool_call['name']
            args = json.loads(tool_call['arguments'])
            ai_call = {
                "id": tool_call['id'],
                "function": {"name": fn, "arguments": tool_call['arguments']},
                'type': 'function'
            }

            try:
                function_response = await self._call_function(tool_chest, fn, args)
                call_resp = {
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "name": fn,
                    "content": function_response
                }
            except Exception as e:
                call_resp = {
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "name": fn,
                    "content": f"Exception: {e}"
                }

            return ai_call, call_resp

        # Schedule all the calls concurrently
        tasks = [make_call(tool_call) for tool_call in tool_calls]
        completed_calls = await asyncio.gather(*tasks)

        # Unpack the resulting ai_calls and resp_calls
        ai_calls, results = zip(*completed_calls)

        return [{'role': 'assistant', 'tool_calls': list(ai_calls), 'content': ''}] + list(results)