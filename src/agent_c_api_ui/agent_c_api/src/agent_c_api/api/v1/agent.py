from fastapi import APIRouter, HTTPException, Form, Depends
import json
import logging

from agent_c_api.api.dependencies import get_agent_manager
from agent_c_api.config.env_config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/update_settings")
async def update_agent_settings(
        session_id: str = Form(...),
        custom_prompt: str = Form(None),
        temperature: float = Form(None),
        reasoning_effort: str = Form(None),
        persona_name: str = Form(None),
        model_name: str = Form(None),
        backend: str = Form(None),
        agent_manager=Depends(get_agent_manager)
):
    """
    Update agent settings for a given session.
    Handles both temperature-based and reasoning-based models.
    The react front end is handling the model change, that code path is not executed here, but left in place in case we need it.
    """
    logger.debug(f"Updating settings for session {session_id} with params: custom prompt - {custom_prompt},\n"
                 f"temp - {temperature},\nreasoning_effort - {reasoning_effort},\n"
                 f"persona- {persona_name},\nmodel - {model_name},\nbackend {backend}")

    session_data = agent_manager.get_session_data(session_id)
    if not session_data:
        return {"error": "Invalid session_id"}

    agent = session_data["agent"]
    updates_made = False

    try:
        # Handle model change first - this will reinitialize the agent
        if model_name is not None and model_name != agent.model_name:
            logger.info(f"Model change requested for session {session_id}: {agent.model_name} -> {model_name}")

            # Load model config to determine correct parameters
            with open(settings.MODEL_CONFIG_PATH, 'r') as f:
                config = json.load(f)

            # Find the model configuration
            model_config = None
            for vendor in config["vendors"]:
                for model in vendor["models"]:
                    if model["id"] == model_name:
                        model_config = model
                        break
                if model_config:
                    break

            if not model_config:
                raise ValueError(f"Model configuration not found for {model_name}")

            # Determine the correct parameter to use
            model_params = {}
            if "temperature" in model_config["parameters"]:
                model_params["temperature"] = temperature if temperature is not None else \
                    model_config["parameters"]["temperature"]["default"]
            elif "reasoning_effort" in model_config["parameters"]:
                model_params["reasoning_effort"] = reasoning_effort if reasoning_effort is not None else \
                    model_config["parameters"]["reasoning_effort"]["default"]

            # Reuse create_session with existing session ID and appropriate parameters
            session_id = await agent_manager.create_session(
                llm_model=model_name,
                backend=backend,
                **model_params,
                persona_name=persona_name if persona_name is not None else agent.persona_name,
                existing_session_id=session_id
            )
            updates_made = True

        else:
            # Update other settings if no model change
            if temperature is not None and hasattr(agent, 'temperature'):
                agent.temperature = temperature
                updates_made = True
            if reasoning_effort is not None and hasattr(agent, 'reasoning_effort'):
                agent.reasoning_effort = reasoning_effort
                updates_made = True
            if custom_prompt is not None:
                agent.custom_persona_text = custom_prompt
                updates_made = True
            if persona_name is not None:
                agent.persona_name = persona_name
                updates_made = True

        if updates_made:
            logger.info(f"Settings updated for session {session_id}")
            return {
                "status": "Settings updated successfully",
                "changes": "Agent reinitialized" if model_name else "Settings modified",
                "agent_c_session_id": agent_manager.get_session_data(session_id).get('agent_c_session_id', "Unknown")
            }
        else:
            logger.info(f"No changes required for session {session_id}")
            return {"status": "No changes required"}

    except Exception as e:
        logger.error(f"Error updating settings for session {session_id}: {str(e)}")
        return {"error": f"Failed to update settings: {str(e)}"}


@router.get("/get_agent_config/{session_id}")
async def get_agent_config(session_id: str, agent_manager=Depends(get_agent_manager)):
    try:
        # logger.info(f"get_agent_config called for session: {session_id}")
        session_data = agent_manager.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        agent = session_data["agent"]
        config = agent._get_agent_config()

        # Add additional configuration info
        config.update({
            "user_id": config["user_id"],
            "custom_prompt": config["custom_prompt"],
            "session_id": session_id,
            "agent_c_session_id": session_data.get("agent_c_session_id"),
            "backend": config["backend"],
            "model_info": {
                "name": config["model_name"],
                "temperature": config["model_parameters"]["temperature"],
                "reasoning_effort": config["model_parameters"]["reasoning_effort"]
            },
            "initialized_tools": config["initialized_tools"]
        })

        logger.info(f"Session {session_id} requested agent config: {config}")
        return {
            "config": config,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Session {session_id} - Error getting agent config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_tools")
async def update_agent_tools(
        session_id: str = Form(...),
        tools: str = Form(...),  # JSON string of tool names
        agent_manager=Depends(get_agent_manager)
):
    try:
        session_data = agent_manager.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Invalid session ID")

        tool_list = json.loads(tools)
        agent = session_data["agent"]
        await agent.update_tools(tool_list)
        session_data["active_tools"] = tool_list

        return {
            "status": "success",
            "message": "Tools updated successfully",
            "active_tools": tool_list,
            "session_id": session_id,
            "agent_c_session_id": session_data.get('agent_c_session_id', "Unknown")
        }
    except Exception as e:
        logger.error(f"Error updating tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_agent_tools/{session_id}")
async def get_agent_tools(session_id: str, agent_manager=Depends(get_agent_manager)):
    try:
        session_data = agent_manager.get_session_data(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        agent = session_data["agent"]
        config = agent._get_agent_config()
        logger.info(f"Session {session_id} requested tools config: {config['initialized_tools']}")

        return {
            "initialized_tools": config["initialized_tools"],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error getting agent tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))
