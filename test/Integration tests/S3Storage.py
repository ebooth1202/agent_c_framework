import os
import asyncio

from dotenv import load_dotenv

from agent_c_core.agent_c.toolsets.tool_chest import ToolChest
from agent_c_core.agent_c.agents.gpt import GPTChatAgent
from agent_c_tools.tools.workspaces.s3_storage import S3StorageWorkspace

load_dotenv(override=True)


async def main():
    tool_chest = ToolChest()

    path = os.path.join(os.getcwd(), 'learn/lab_code')
    lab_workspace = S3StorageWorkspace(bucket_name="lab", prefix=path)

    await tool_chest.init_tools(workspaces=[lab_workspace])

    prompt: str = "create a poem and save it as poem.md in the workspace"

    agent = GPTChatAgent()
    await agent.one_shot(model_name="gpt-4-turbo-preview",
                         prompt=prompt,
                         tool_chest=tool_chest)


if __name__ == "__main__":
    asyncio.run(main())
