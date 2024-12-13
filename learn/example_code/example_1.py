import asyncio

from agent_c import GPTChatAgent


async def main():
    agent = GPTChatAgent()
    result: str = await agent.one_shot(user_message="What is the capital of France?")

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
