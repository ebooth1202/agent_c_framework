# Claude 3 support

The `CaludeChatAgent` allows us to use Anthropic's Claude 3 as a chat agent.  Currently ONLY chat is supports

You can enable it by passing `--claude` on the command line to the reference agent app.  This will enable the `ClaudeChatAgent` and disable the `GPTChatAgent` agent.

With Claude 3 your model name should be a full claude 3 model name like: 
- `claude-3-opus-20240229`  - Smart, slow, expensive
- `claude-3-sonnet-20240229` - mid tier
- `claude-3-haiku-20240307` - fast, dumb, cheap
