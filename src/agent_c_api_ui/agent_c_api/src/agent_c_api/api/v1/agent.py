from fastapi import APIRouter, HTTPException, Form, Depends, Request
import json
import logging
from pydantic import create_model

from agent_c_api.api.dependencies import get_agent_manager, get_dynamic_form_params, build_fields_from_config
from agent_c_api.config.config_loader import get_allowed_params
from agent_c_api.config.env_config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/update_settings")
async def update_agent_settings(
        session_id: str = Form(...),
        custom_prompt: str = Form(None),
        persona_name: str = Form(None),
        dynamic_form_data=Depends(get_dynamic_form_params),
        agent_manager=Depends(get_agent_manager)
):
    """
    Update agent settings for a given session.
    """
    # Get current session and agent
    session_data = agent_manager.get_session_data(session_id)
    if not session_data:
        return {"error": "Invalid session_id"}

    agent = session_data["agent"]
    original_form = dynamic_form_data["original_form"]
    updates_made = False

    try:
        # Get model info either from form or from current agent
        model_name = dynamic_form_data["model_name"] or agent.model_name
        backend = dynamic_form_data["backend"] or agent.backend

        # Add defensive checks
        if not model_name or not backend:
            logger.error(f"Missing model_name or backend: {model_name}, {backend}")
            return {"error": "Missing model name or backend information"}

        # If we don't have validated params yet, create them now with agent's model info
        dynamic_params = dynamic_form_data["params"]
        if dynamic_params is None:
            # Fill in model_name and backend in the form data
            form_dict = original_form.copy()
            form_dict["model_name"] = model_name
            form_dict["backend"] = backend

            # Get parameter configuration for this model
            allowed_params = get_allowed_params(backend, model_name)
            fields = build_fields_from_config(allowed_params)
            DynamicFormParams = create_model("DynamicFormParams", **fields)

            # Parse the parameters
            try:
                dynamic_params = DynamicFormParams.parse_obj(form_dict)
            except Exception as e:
                logger.error(f"Parameter validation error: {e}")
                return {"error": f"Invalid parameters: {str(e)}"}

        # Check if this is an intentional model change
        model_explicitly_changed = "model_name" in original_form and model_name != agent.model_name

        if model_explicitly_changed:
            logger.info(f"Model change requested for session {session_id}: {agent.model_name} -> {model_name}")

            # Create kwargs dictionary with all parameters
            session_kwargs = {}

            # Add all dynamic parameters
            if dynamic_params:
                session_kwargs.update(dynamic_params.dict())

            # Add custom_prompt with proper parameter name
            if custom_prompt is not None:
                session_kwargs['custom_persona_text'] = custom_prompt
            elif agent.custom_persona_text is not None:
                session_kwargs['custom_persona_text'] = agent.custom_persona_text

            # Create a new session using the parameters
            new_session_id = await agent_manager.create_session(
                llm_model=model_name,
                backend=backend,
                persona_name=persona_name if persona_name is not None else agent.persona_name,
                **session_kwargs
            )
            session_id = new_session_id  # Update session_id to the new session.
            updates_made = True
        else:
            # Update existing agent settings using the dynamic parameters.
            # Process each parameter that was explicitly provided in the original form
            for param_name in original_form:
                if param_name in ["temperature", "reasoning_effort", "extended_thinking", "budget_tokens"]:
                    if hasattr(dynamic_params, param_name):
                        setattr(agent, param_name, getattr(dynamic_params, param_name))
                        updates_made = True

            # Handle custom_prompt and persona_name separately
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
                "changes": "Agent reinitialized" if model_explicitly_changed else "Settings modified",
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
                "reasoning_effort": config["model_parameters"]["reasoning_effort"],
                "extended_thinking": getattr(agent, "extended_thinking", False),
                "budget_tokens": getattr(agent, "budget_tokens", 0)
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
