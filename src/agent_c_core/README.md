# Agent C - Core

This package implements a fairly thin abstraction layer over chat completion APIs to support rapid development of AI agents. An AI agent can be looked at as model + prompt + tools.  Agent C was designed to make building both those tools, and the prompts to drive them trivial to create.



## Chat Agents

There are two main agent classes: `GPTChatAgent` and `ClaudeChatAgent`.  As of right now only the GPT agent supports tools.  Anthropic only recently added tool support and I've not had a burning need to build support for it... Someone could pitch in here fairly easily.

Each of the agents has a couple of ways to use them for completion calls and that's simply based on if your use-case is chat, or data processing.

- `chat` is the interface for chatting and deals with arrays of messages

- `one-shot` is for data processing tasks where each is it's own thing.