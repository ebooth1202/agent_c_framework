import os
from fastapi import APIRouter, HTTPException, Depends
import json
import logging
from agent_c_api.core.agent_manager import AgentManager
from agent_c_api.config.env_config import settings


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/models")
async def list_models():
    """Get list of available models from model_configs.json"""
    try:
        # Ensure file exists
        if not settings.MODEL_CONFIG_PATH.is_file():
            logger.warning(f"Model config file does not exist: {settings.MODEL_CONFIG_PATH}")
            return {"models": []}

        # Read and parse model config
        with open(settings.MODEL_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # Transform the data for frontend consumption
        models = []
        for vendor in config.get("vendors", []):
            vendor_name = vendor.get("vendor")
            for model in vendor.get("models", []):
                models.append({
                    "id": model["id"],
                    "label": model["ui_name"],
                    "description": model["description"],
                    "model_type": model["model_type"],
                    "backend": vendor_name,
                    "parameters": model["parameters"],
                    "capabilities": model["capabilities"],
                    "allowed_inputs": model["allowed_inputs"]
                })

        logger.info(f"Found {len(models)} models in configuration")
        return {"models": models}

    except Exception as e:
        logger.error(f"Error reading model config: {e}")
        raise HTTPException(status_code=500, detail=str(e))