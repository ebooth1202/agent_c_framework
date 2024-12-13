# Chat Events in Agent C

Regardless of which completion method you're using on the agent, `ChatEvent`s via the `streaming_callback` you provide. It allows us to completely decouple the agent and tools from the UI.  The UI can consume events via direct callback like the reference client, or they can be shoved into a queue and processed by a separate thread or process.

Another benefit is that the events can be used by tools to bypass the agent and provide data directly to the UI.  This is useful for tools that are token dense, need to render media, or want to stream data.  By bypassing the agent, for and presenting the data directly to the UI, we can both save tokens and allow the  agent to work with data indirectly. Fore example, a waveform tool could use `render_media` to present a waveform to the user, and return some much smaller string to the agent.


## Overview

`src/agent_c/modelrs/chat_event.py` contains the `ChatEvent` model and sub-models.

## Models

- `FunctionCall` - This is the same the Open AI model for function calls it will be part of `ToolCall`s 
- `ToolCall` - This the the same an Open AI model for a `tool_call`. It may be part of a `Message`
- `Message` - An individual message with a role and content. It can also include tool calls and other metadata. This model is used to represent messages that are sent or received in a chat.
- `RenderMedia` - Defines the details for media rendering, mapping traditional HTTP-style 'content-type' to a model field. It allows the UI to render different types of media based on the content provided.
- `ChatEvent` - The central model that represents a chat event.


## Chat Events
This model represents a chat event, which could be any number of things so most fields are optional.

- `session_id` and `role` are mandatory fields and will always be present. Everything else is either optional, or dependent on something that it optional.

### Fields
- `session_id` - The ID of the chat session, which in the reference client comes from Zep.
- `role` - The role that originated the event. `assistant`, `user`, `system`, and `tool` are predefined roles. Some tools may have their own roles, for example tools that are themselves agents might send their name as the role.
- `completed` - A boolean indicating that the current interaction is complete. This is used to signal the end of a chat message so that any buffered content can be flushed. Note: This `start`, `completed` refer to the interaction i.e. Until `agent.chat` returns.  Any given interaction may have multiple completions and tool calls.
- `completion_running` - A boolean indicating that a completion is currently running or not. If present and True, the client should display a message indicating that a completion is running. If present and False, the client should display a message indicating that the completion has completed. This, combined with the other flags can help identify if a performance problem exists at different points in the chain.
- `content` - A chunk of of text content (if set).  This can be as small as a token or as large as a full chat message.
- `output_format` - The format of the content.  This is used to signal the client how to interpret the content. The default is `markdown`, `raw` is also supported.
    - Clients should interpret `raw` as plain text (that might still be in Markdown format), `raw` is essentially a flag that indicates: Display every token as it comes in even if that means fancy rendering doesn't happen.
- `messages` - Populated by agents and the end of an interaction to provide the complete list of messages, including any tool calls and returns.
    - This array can be passed to the agent during the next interaction so that it doesn't need to repeat a tool call to answer a follow-up question.  This ends up consuming more and more tokens over time, but it's a trade-off for not needing to re-run the tool calls.
    - When you don't pass the message array, back around the loop the message array will be constructed from the Zep memory if a ZepCache has been provided.
    - The reference client has the `!compact` command which takes advantage of this by resetting the copy of the message array it was holding onto and then caching it again after the next interaction.  But that could be made WAAAAY smarter.
- `render_media` - If present, this field will contain details for media to be rendered in the client.
    - The reference client just goes "it it has content and name, write it to a temp file and ask the OS to open it. If not and it has a URL ask the default browser to open it. Anything else complain."
- `start` - A boolean indicating that an interaction in beginning. And would single a client to start displaying a response from the `event.role`.

- `tool_use_active` - A boolean indicating that a tool is currently active.
    - If present and `True`, an agent is executing tool calls and the client should display a message to that effect.
    - If present and `False`, the client should display a message indicating that the tool has completed.
- `tool_calls` - If `tool_use_active` is `True`, this field will contain a list of `ToolCall` models that are currently being executed.

## Rendering Media
The RenderMedia event is used by tools to provide non-text content to the client. It's a fairly straightforward model with a few fields:

- `content_type` - The type of media to be rendered. In familiar HTTP content type syntax, for example `image/png` or `audio/wav`.
- `url` - The URL of the media to be rendered. This will be set when a tool wants to show media or web content that has a URL already.
- `name` - The name of the media to be rendered.  Tools SHOULD set this to a filename
- `content` - The bytes of the media to be rendered. 

A RenderMedia model will always have a content type, a URL, content or both a URL and content.  For example the Mermaid chart tool will give and SVG both as savable content and a share.

The reference client handles this in the UI layer by either saving the content to a temp file and hav ing the OS open it,
or by asking the default browser to open the URL if there's no content.

## Notes

- Clients should be prepared to handle any combination of fields, and should be prepared to handle role changes mid-interaction.
  - Tools can and will send messages to the client directly, and the client should be prepared to handle them.
  