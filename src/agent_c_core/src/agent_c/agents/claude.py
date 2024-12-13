import logging

from typing import Any, List, Union
from anthropic import AsyncAnthropic, APITimeoutError, Anthropic

from agent_c.agents.base import BaseAgent
from agent_c.chat.session_manager import ChatSessionManager
from agent_c.models.image_input import ImageInput
from agent_c.util.token_counter import TokenCounter

class ClaudeChatAgent(BaseAgent):
    class TokenCounter(TokenCounter):

        def __init__(self):
            self.anthropic: Anthropic = Anthropic()

        def count_tokens(self, text: str) -> int:
            return self.anthropic.count_tokens(text)


    def __init__(self, **kwargs) -> None:
        """
        Initialize ChatAgent object.

        Non-Base Parameters:
        client: AsyncAnthropic, default is AsyncAnthropic()
            The client to use for making requests to the Anthropic API.
        """
        kwargs['token_counter'] = kwargs.get('token_counter', ClaudeChatAgent.TokenCounter())
        super().__init__(**kwargs)
        self.client: AsyncAnthropic = kwargs.get("client", AsyncAnthropic())
        self.supports_multimodal = True



    async def __interaction_setup(self, **kwargs) -> dict[str, Any]:
        model_name: str = kwargs.get("model_name", self.model_name)
        sys_prompt: str = await self._render_system_prompt(**kwargs)
        temperature: float = kwargs.get("temperature", self.temperature)
        max_tokens: int = kwargs.get("max_tokens", 4096)

        messages = await self._construct_message_array(**kwargs)
        callback_opts = self._callback_opts(**kwargs)

        completion_opts = {"model": model_name, "messages": messages, "system": sys_prompt, "stream": True, "max_tokens": max_tokens, 'temperature': temperature}

        session_manager: Union[ChatSessionManager, None] = kwargs.get("session_manager", None)
        if session_manager is not None:
            completion_opts["metadata"] = {'user_id': session_manager.user.user_id}

        opts = {"callback_opts": callback_opts, "completion_opts": completion_opts}
        return opts

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

        session_manager: Union[ChatSessionManager, None] = kwargs.get("session_manager", None)
        messages = opts["completion_opts"]["messages"]

        delay = 1  # Initial delay between retries
        async with self.semaphore:
            await self._cb_completion(True, **callback_opts)
            while delay <= self.max_delay:
                try:
                    stream = await self.client.messages.create(**opts["completion_opts"])
                except APITimeoutError as e:
                    await self._cb_system(content=f"Timeout error calling `client.messages.create`. Delaying for {delay} seconds.\n")
                    await self._exponential_backoff(delay)
                    delay *= 2
                except Exception as e:
                    await self._cb_system(content=f"Exception calling `client.messages.create`.\n\n{e}\n")
                    await self._cb_completion(False, **callback_opts)
                    return []

            await self._cb_completion(False, **callback_opts)

            collected_messages = []

            async for event in stream:
                if event.type == "content_block_start":
                    content_type = event.content_block.type
                    await self._cb_start(True, **callback_opts)
                    if content_type == "text":
                        content = event.content_block.text
                        if len(content) > 0:
                            collected_messages.append(content)
                            await self._cb_token(content, **callback_opts)
                    else:
                        await self._cb_system(content=f"content_block_start Unknown content type: {content_type}")

                elif event.type == 'content_block_delta':
                    collected_messages.append(event.delta.text)
                    await self._cb_token(event.delta.text, **callback_opts)
                elif event.type == "content_block_stop":
                    await self._cb_start(False, **callback_opts)
                elif event.type == 'message_delta':
                    stop_reason = event.delta.stop_reason
                elif event.type == 'message_stop':
                    output_text = "".join(collected_messages)
                    messages.append(await self._save_interaction_to_session(session_manager, output_text))
                    await self._cb_messages(messages, **callback_opts)

        return messages

    def _generate_multi_modal_user_message(self, user_input: str, images: List[ImageInput]) -> Union[List[dict[str, Any]], None]:
        contents = []
        for image in images:
            if image.content is None and image.url is not None:
                logging.warning(f"ImageInput has no content and Claude doesn't support image URLs. Skipping image {image.url}")
                continue

            img_source = {"type": "base64", "media_type": image.content_type, "data": image.content}
            contents.append({"type": "image", "source": img_source})

        if self.mitigate_image_prompt_injection:
            text = f"User: {user_input}{BaseAgent.IMAGE_PI_MITIGATION}"
        else:
            text = user_input

        contents.append({"type": "text", "text": text})

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
