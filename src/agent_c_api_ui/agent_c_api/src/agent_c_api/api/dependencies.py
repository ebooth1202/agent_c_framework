from fastapi import Request, Depends
from agent_c_api.core.agent_manager import AgentManager

def get_agent_manager(request: Request) -> AgentManager:
    return request.app.state.agent_manager