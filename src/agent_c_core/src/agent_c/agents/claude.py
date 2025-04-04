import asyncio
import copy
import json
import logging

from typing import Any, List, Union, Dict, Optional
from anthropic import AsyncAnthropic, APITimeoutError, Anthropic

from agent_c.agents.base import BaseAgent
from agent_c.chat.session_manager import ChatSessionManager
from agent_c.models.input import FileInput
from agent_c.models.input.audio_input import AudioInput
from agent_c.models.input.image_input import ImageInput
from agent_c.util.token_counter import TokenCounter

class ClaudeChatAgent(BaseAgent):
    CLAUDE_MAX_TOKENS: int = 64000
    class ClaudeTokenCounter(TokenCounter):

        def __init__(self):
            self.anthropic: Anthropic = Anthropic()

        def count_tokens(self, text: str) -> int:
            response = self.anthropic.messages.count_tokens(
                model="claude-3-5-sonnet-latest",
                system="",
                messages=[{
                    "role": "user",
                    "content": text
                }],
            )

            return response.input_tokens


    def __init__(self, **kwargs) -> None:
        """
        Initialize ChatAgent object.

        Non-Base Parameters:
        client: AsyncAnthropic, default is AsyncAnthropic()
            The client to use for making requests to the Anthropic API.
        max_tokens: int, optional
            The maximum number of tokens to generate in the response.
        """
        kwargs['token_counter'] = kwargs.get('token_counter', ClaudeChatAgent.ClaudeTokenCounter())
        super().__init__(**kwargs)
        self.client: AsyncAnthropic = kwargs.get("client", AsyncAnthropic())
        self.supports_multimodal = True
        self.can_use_tools = True
        # JO: I need these as class level variables to adjust outside a chat call.
        self.max_tokens = kwargs.get("max_tokens", self.CLAUDE_MAX_TOKENS)
        self.budget_tokens = kwargs.get("budget_tokens", 0)
        self.logger: logging.Logger = logging.getLogger(__name__)



    async def __interaction_setup(self, **kwargs) -> dict[str, Any]:
        model_name: str = kwargs.get("model_name", self.model_name)
        if model_name is None:
            raise ValueError('Claude agent is missing a model_name')
        sys_prompt: str = await self._render_system_prompt(**kwargs)
        temperature: float = kwargs.get("temperature", self.temperature)
        max_tokens: int = kwargs.get("max_tokens", self.max_tokens)

        messages = await self._construct_message_array(**kwargs)
        callback_opts = self._callback_opts(**kwargs)

        tool_chest = kwargs.get("tool_chest", self.tool_chest)

        functions: List[Dict[str, Any]] = tool_chest.active_claude_schemas

        completion_opts = {"model": model_name, "messages": messages,
                           "system": sys_prompt,  "max_tokens": max_tokens,
                           'temperature': temperature}

        if '3-7-sonnet' in model_name:
            completion_opts['betas'] = ["token-efficient-tools-2025-02-19", "output-128k-2025-02-19"]

        budget_tokens: int = kwargs.get("budget_tokens", self.budget_tokens)
        if budget_tokens > 0:
            completion_opts['thinking'] = {"budget_tokens": budget_tokens, "type": "enabled"}
            completion_opts['temperature'] = 1


        if len(functions):
            completion_opts['tools'] = functions

        session_manager: Union[ChatSessionManager, None] = kwargs.get("session_manager", None)
        if session_manager is not None:
            completion_opts["metadata"] = {'user_id': session_manager.user.user_id}

        opts = {"callback_opts": callback_opts, "completion_opts": completion_opts, 'tool_chest': tool_chest}
        return opts

    @staticmethod
    def process_escapes(text):
        return text.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")

    async def chat(self, **kwargs) -> List[dict[str, Any]]:
        """
        Perform the chat operation.

        Parameters:
        session_id: str
            Unique identifier for the session.
        model_name: str, default is self.model_name
            The language model to be used.
        prompt_metadata: dict, default is empty dict
            Metadata to be used for rendering the prompt via the PromptBuilder
        model_name: str, default is self.model_name
            The name of the Claude model to use.
            - Can be one of "opus", "sonnet", or "haiku". In which case ANTHROPIC_MODEL_PATTERN will bs used
              to generate the model name.
            - A full Claude model name can also be used.
        session_manager: ChatSessionManager, default is None
            A session manager to use for the message memory / session info
        session_id: str, default is "none"
            The session id to use for the chat, if you haven't provided a session manager.
        agent_role: str, default is "assistant"
            The role of the agent in the chat event stream
        messages: List[dict[str, Any]], default is None
            A list of messages to use for the chat.
            If this is not provided, but a session manager is, the messages will be constructed from the session.
        output_format: str, default is "markdown"
            The format to signal the client to expect


        Returns: A list of messages.
        """
        opts = await self.__interaction_setup(**kwargs)
        callback_opts = opts["callback_opts"]
        tool_chest = opts['tool_chest']

        session_manager: Union[ChatSessionManager, None] = kwargs.get("session_manager", None)
        messages = opts["completion_opts"]["messages"]
        current_block_type: Optional[str] = None
        current_thought: Optional[dict[str, Any]] = None
        current_agent_msg: Optional[dict[str, Any]] = None

        # quick hack for now (lol)
        tts_inactive = 0
        tts_waiting = 1
        tts_emitting = 2
        think_tool_state = tts_inactive
        think_partial: str = ""

        delay = 1  # Initial delay between retries
        async with self.semaphore:
            interaction_id = await self._raise_interaction_start(**callback_opts)
            while delay <= self.max_delay:
                try:
                    await self._raise_completion_start(opts["completion_opts"], **callback_opts)
                    async with self.client.beta.messages.stream(**opts["completion_opts"]) as stream:
                        collected_tool_calls = []
                        input_tokens = 0
                        model_outputs = []

                        async for event in stream:
                            if event.type == "message_start":
                                input_tokens = event.message.usage.input_tokens

                            elif event.type == "content_block_delta":
                                delta = event.delta
                                if delta.type == "signature_delta":
                                    current_thought['signature'] = delta.signature
                                elif delta.type == "thinking_delta":
                                    if current_block_type == "redacted_thinking":
                                        current_thought['data'] = current_thought['data'] + delta.data
                                    else:
                                        current_thought['thinking'] = current_thought['thinking'] + delta.thinking
                                        await self._raise_thought_delta(delta.thinking, **callback_opts)
                                elif delta.type == "input_json_delta":
                                    j = delta.partial_json

                                    if think_tool_state == tts_waiting:
                                        think_partial = think_partial + j

                                        # Check if we've received the opening part of the thought
                                        prefix = '{"thought": "'
                                        if prefix in think_partial:
                                            start_pos = think_partial.find(prefix) + len(prefix)
                                            content = think_partial[start_pos:]

                                            # Start buffering content for escape sequence handling
                                            think_partial = ""
                                            think_escape_buffer = content
                                            think_tool_state = tts_emitting

                                            # Process and emit if we don't have a partial escape sequence
                                            if not think_escape_buffer.endswith('\\'):
                                                processed = self.process_escapes(think_escape_buffer)
                                                think_escape_buffer = ""  # Clear the buffer after processing
                                                await self._raise_thought_delta(processed, **callback_opts)

                                    elif think_tool_state == tts_emitting:
                                        # Add new content to our escape sequence buffer
                                        think_escape_buffer = think_escape_buffer + j

                                        # If we don't end with backslash, we can process
                                        if not think_escape_buffer.endswith('\\'):
                                            processed = self.process_escapes(think_escape_buffer)
                                            think_escape_buffer = ""  # Clear the buffer after processing

                                            # Check if we've hit the end of the JSON
                                            if processed.endswith('"}'):
                                                think_tool_state = tts_inactive
                                                # Remove closing quote and brace
                                                processed = processed[:-2]

                                            await self._raise_thought_delta(processed, **callback_opts)



                            elif event.type == 'message_stop':
                                output_tokens = event.message.usage.output_tokens
                                await self._raise_completion_end(opts["completion_opts"], stop_reason=stop_reason, input_tokens=input_tokens, output_tokens=output_tokens, **callback_opts)

                                # TODO: This will need moved when I fix tool call messages
                                assistant_content = self._format_model_outputs_to_text(model_outputs)
                                await self._save_interaction_to_session(session_manager, assistant_content)

                                messages.append({'role': 'assistant', 'content': model_outputs})

                                if stop_reason != 'tool_use':
                                    await self._raise_history_event(messages, **callback_opts)
                                    await self._raise_interaction_end(id=interaction_id, **callback_opts)
                                    return messages
                                else:
                                    await self._raise_tool_call_start(collected_tool_calls, vendor="anthropic",
                                                                      **callback_opts)

                                    # JOE: Fancy footwork for grabbing tool calls/results and adding them to messages for session history
                                    tool_response_messages = await self.__tool_calls_to_messages(collected_tool_calls, tool_chest)
                                    # For now we're not going to save tool calls/results to session history.  Too much incompatibility
                                    # Between claude/gpt.  This is being solved in another branch.
                                    # await self.process_tool_response_messages(session_manager, tool_response_messages)

                                    # TODO: These should probably be part of the model output
                                    messages.extend(tool_response_messages)
                                    await self._raise_tool_call_end(collected_tool_calls, messages[-1]['content'],
                                                                    vendor="anthropic", **callback_opts)
                                    await self._raise_history_event(messages, **callback_opts)

                            elif event.type == "content_block_start":
                                current_block_type = event.content_block.type
                                current_agent_msg = None
                                current_thought = None
                                think_tool_state = tts_inactive
                                think_partial = ""

                                if current_block_type == "text":
                                    content = event.content_block.text
                                    current_agent_msg = copy.deepcopy(event.content_block.model_dump())
                                    model_outputs.append(current_agent_msg)
                                    if len(content) > 0:
                                        await self._raise_text_delta(content, **callback_opts)
                                elif current_block_type == "tool_use":
                                    tool_call = event.content_block.model_dump()
                                    if event.content_block.name == "think":
                                        think_tool_state = tts_waiting

                                    collected_tool_calls.append(tool_call)
                                    await self._raise_tool_call_delta(collected_tool_calls, **callback_opts)
                                elif current_block_type == "thinking" or current_block_type == "redacted_thinking":
                                    current_thought = copy.deepcopy(event.content_block.model_dump())
                                    model_outputs.append(current_thought)

                                    if current_block_type == "redacted_thinking":
                                        content = "*redacted*"
                                    else:
                                        content = current_thought['thinking']

                                    await self._raise_thought_delta(content, **callback_opts)
                                else:
                                    await self._raise_system_event(f"content_block_start Unknown content type: {current_block_type}", **callback_opts)
                            elif event.type == "input_json":
                                collected_tool_calls[-1]['input'] = event.snapshot

                            elif event.type == "text":
                                if current_block_type == "text":
                                    current_agent_msg['text'] = current_agent_msg['text'] + event.text
                                    await self._raise_text_delta(event.text, **callback_opts)
                                elif current_block_type == "thinking" or current_block_type == "redacted_thinking":
                                    if current_block_type == "redacted_thinking":
                                        current_thought['data'] = current_thought['data'] + event.data
                                    else:
                                        current_thought['thinking'] = current_thought['thinking'] + event.text
                                        await self._raise_thought_delta(event.text, **callback_opts)


                            elif event.type == 'message_delta':
                                stop_reason = event.delta.stop_reason


                except APITimeoutError:
                    await self._raise_system_event(f"Timeout error calling `client.messages.stream`. Delaying for {delay} seconds.\n", **callback_opts)
                    await self._exponential_backoff(delay)
                    delay *= 2
                except Exception as e:
                    await self._raise_system_event(f"Exception calling `client.messages.stream`.\n\n{e}\n", **callback_opts)
                    await self._raise_completion_end(opts["completion_opts"], stop_reason="exception", **callback_opts)

                    return []

        return messages

    def _generate_multi_modal_user_message(self, user_input: str, images: List[ImageInput], audio: List[AudioInput],
                                           files: List[FileInput]) -> Union[List[dict[str, Any]], None]:
        """
        Generates a multimodal message containing text, images, and file content.

        This method formats various input types into a structure that can be sent to
        the Claude API, adhering to the Anthropic message format.

        Args:
            user_input (str): The user's text message
            images (List[ImageInput]): List of image inputs to include
            audio (List[AudioInput]): List of audio inputs (not directly supported by Claude)
            files (List[FileInput]): List of file inputs to include

        Returns:
            Union[List[dict[str, Any]], None]: Formatted message content for Claude
        """
        contents = []

        # Add images first
        for image in images:
            if image.content is None and image.url is not None:
                logging.warning(
                    f"ImageInput has no content and Claude doesn't support image URLs. Skipping image {image.url}")
                continue

            img_source = {"type": "base64", "media_type": image.content_type, "data": image.content}
            contents.append({"type": "image", "source": img_source})

        # Process file content
        file_content_blocks = []
        if files:
            logging.info(f"Processing {len(files)} file inputs in Claude _generate_multi_modal_user_message")

            for idx, file in enumerate(files):
                # Always try to use get_text_content() to get extracted text
                extracted_text = None

                # Check if get_text_content method exists and call it
                if hasattr(file, 'get_text_content') and callable(file.get_text_content):
                    extracted_text = file.get_text_content()
                    logging.info(
                        f"Claude: File {idx} ({file.file_name}): get_text_content() returned {len(extracted_text) if extracted_text else 0} chars")
                else:
                    logging.warning(f"Claude: File {idx} ({file.file_name}): get_text_content() method not available")

                if extracted_text:
                    file_name = file.file_name or "unknown file"
                    content_block = f"Content from file {file_name}:\n\n{extracted_text}"

                    file_content_blocks.append(content_block)
                    logging.info(f"Claude: File {idx} ({file.file_name}): Added extracted text to message")
                else:
                    # Fall back to mentioning the file without content
                    file_name = file.file_name or "unknown file"
                    file_content_blocks.append(f"[File attached: {file_name} (content could not be extracted)]")
                    logging.warning(
                        f"Claude: File {idx} ({file.file_name}): No text content available, adding file name only")

        # Prepare the main text content with file content
        main_text = user_input or ""

        # If we have file content blocks, add them before the user message
        if file_content_blocks:
            all_file_content = "\n\n".join(file_content_blocks)
            main_text = f"{all_file_content}\n\n{main_text}"

        # Add PI mitigation if needed
        if self.mitigate_image_prompt_injection and images:
            main_text = f"{main_text}{BaseAgent.IMAGE_PI_MITIGATION}"

        # Add the combined text as the final content block
        contents.append({"type": "text", "text": main_text})

        # For audio clips, since Claude doesn't support audio directly, just log a warning
        if audio and len(audio) > 0:
            logging.warning(
                f"Claude does not directly support audio input. Mentioned {len(audio)} audio clips in text.")

        return [{"role": "user", "content": contents}]

    async def one_shot(self, **kwargs) -> str:
        """
               Perform the chat operation as a one shot.

               Parameters:
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

    async def __tool_calls_to_messages(self, tool_calls, tool_chest):
        async def make_call(tool_call):
            fn = tool_call['name']
            args = tool_call['input']
            ai_call = copy.deepcopy(tool_call)
            try:
                function_response = await self._call_function(tool_chest, fn, args)
                call_resp = {"type": "tool_result", "tool_use_id": tool_call['id'],"content": function_response}
            except Exception as e:
                call_resp = {"role": "tool", "tool_call_id": tool_call['id'], "name": fn,
                             "content": f"Exception: {e}"}

            return ai_call, call_resp

        # Schedule all the calls concurrently
        tasks = [make_call(tool_call) for tool_call in tool_calls]
        completed_calls = await asyncio.gather(*tasks)

        # Unpack the resulting ai_calls and resp_calls
        ai_calls, results = zip(*completed_calls)

        return [{'role': 'assistant', 'content': list(ai_calls)},
                {'role': 'user', 'content': list(results)}]

    @staticmethod
    def _format_model_outputs_to_text(model_outputs: List[Dict[str, Any]]) -> str:
        """
        Convert Claude's model outputs into a single text string for session storage.
        CREATED BY JOE: May not be the best way
        Args:
            model_outputs: List of output blocks from Claude

        Returns:
            str: Combined text content from all text blocks
        """
        text_parts = []
        for output in model_outputs:
            if 'text' in output:
                text_parts.append(output['text'])
            elif 'thinking' in output:
                # use one or the other below lines for adding to message history, for now we're going to exclude
                # text_parts.append(f"[Thinking] {output['thinking']}") # Add thinking blocks to the output
                pass  # Skip thinking blocks by default

        return "".join(text_parts)

    async def process_tool_response_messages(self, session_manager, tool_response_messages):
        """
        Process the tool response messages from the assistant.
        CREATED BY JOE: May not be the best way
        Args:
            session_manager: to save messages to for chat history
            tool_response_messages: incoming tool response messages

        Returns:

        """
        # Process the assistant's tool call (first message) - has role of Assistant
        assistant_message = tool_response_messages[0]
        if isinstance(assistant_message.get('content', ''), list):
            content = json.dumps(assistant_message['content'])
        else:
            content = assistant_message.get('content', '')
        prefixed_content = "[Tool Call] " + content
        await self._save_message_to_session(session_manager, prefixed_content, 'assistant')

        # Process the tool result message (second message, if it exists)
        if len(tool_response_messages) > 1:
            tool_result = tool_response_messages[1]
            if isinstance(tool_result.get('content', ''), list):
                content = json.dumps(tool_result['content'])
            else:
                content = tool_result.get('content', '')

            # Save the tool result as 'assistant' with a prefix to indicate it was a tool response. This is because Claude
            # does not like you passing in prior messages with a role of tool
            tool_response_content = "[Tool Response] " + content
            await self._save_message_to_session(session_manager, tool_response_content, 'assistant')