import glob
import os
from typing import List, Dict
from fastapi import APIRouter, HTTPException, Depends

import logging


from agent_c_api.config.env_config import settings


router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/personas")
async def list_personas() -> List[Dict[str, str]]:
    """Get list of available personas from personas directory"""
    personas = []
    # persona_dir = os.path.join(os.getcwd(), "personas")
    persona_dir = settings.PERSONA_DIR
    # print(f"Persona directory: {persona_dir}")
    # Ensure directory exists
    if not os.path.isdir(persona_dir):
        logger.warning(f"Persona directory does not exist: {persona_dir}")
        return personas

    # Get all .md files in personas directory
    for file_path in glob.glob(os.path.join(persona_dir, "*.md")):
        name = os.path.basename(file_path)[:-3]  # Remove .md extension

        # Read persona content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            continue

        personas.append({
            "name": name,
            "content": content,
            "file": os.path.basename(file_path)
        })

    logger.info(f"Found {len(personas)} personas: {[p['name'] for p in personas]}")
    return personas