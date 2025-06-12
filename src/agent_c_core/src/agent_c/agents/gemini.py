import os
from openai import AsyncOpenAI
from agent_c.agents.gpt import GPTChatAgent

class GeminiChatAgent(GPTChatAgent):
    @classmethod
    def client(cls, **opts):
        return AsyncOpenAI(api_key= os.environ.get("GEMINI_API_KEY"),
                           base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
