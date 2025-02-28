from fastapi import Request, Depends, HTTPException
from typing import Dict, Any, Optional, List, Tuple, Set
from pydantic import create_model
import logging
import re
from collections import defaultdict

from agent_c_api.core.agent_manager import AgentManager
from agent_c_api.config.config_loader import get_allowed_params
from agent_c_api.core.util.logging_utils import LoggingManager

logging_manager = LoggingManager(__name__)
logger = logging_manager.get_logger()


def get_agent_manager(request: Request) -> AgentManager:
    return request.app.state.agent_manager


def build_fields_from_config(config: dict) -> dict:
    """
    Recursively build a dictionary of fields for create_model.
    For nested configurations (i.e. those without a top-level "default"),
    create a sub-model.
    """
    fields = {}
    for param, spec in config.items():
        # If spec is a dict but has no "default" key, treat it as nested.
        if isinstance(spec, dict) and "default" not in spec:
            # Extract a required flag if present; assume True if not specified.
            required_flag = spec.get("required", True)
            # Remove keys that aren't actual sub-fields (e.g. "required").
            nested_spec = {k: v for k, v in spec.items() if k != "required"}
            sub_fields = build_fields_from_config(nested_spec)
            # Create a nested model.
            sub_model = create_model(param.capitalize() + "Model", **sub_fields)
            default = ... if required_flag else None
            fields[param] = (sub_model, default)
        else:
            # Flat field: determine the field type based on the parameter name.
            if param == "temperature":
                field_type = float
            elif param in ["max_tokens", "budget_tokens"]:
                field_type = int
            elif param in ["reasoning_effort"]:
                field_type = str
            elif param in ["extended_thinking", "enabled"]:
                field_type = bool
            else:
                field_type = str

            # If spec is a dict, get its "default" value; otherwise, mark as required.
            default = spec.get("default", ...) if isinstance(spec, dict) else ...
            fields[param] = (field_type, default)
    return fields


def analyze_config_structure(config: Dict[str, Any], prefix: str = "", result: Dict[str, Dict] = None) -> Dict[
    str, Dict]:
    """
    Analyze configuration structure to create a mapping of parameter paths.

    Args:
        config: The configuration dictionary
        prefix: Current path prefix for recursive calls
        result: Dictionary to store results

    Returns:
        Dictionary mapping parameter paths to metadata about that path
    """
    if result is None:
        result = {}

    for key, value in config.items():
        current_path = f"{prefix}.{key}" if prefix else key

        # If this is a nested structure (dict without 'default')
        if isinstance(value, dict) and "default" not in value:
            # Mark this as a parent node
            result[current_path] = {
                "is_parent": True,
                "children": [],
                "required": value.get("required", True)
            }

            # Get children but exclude metadata keys like 'required'
            nested_config = {k: v for k, v in value.items() if k != "required"}

            # Recursively process children
            analyze_config_structure(nested_config, current_path, result)

            # Add children to parent's children list
            for child_path in list(result.keys()):
                if child_path.startswith(f"{current_path}.") and "." not in child_path[len(current_path) + 1:]:
                    result[current_path]["children"].append(child_path)
        else:
            # This is a leaf node (actual parameter)
            param_type = None
            if key == "temperature":
                param_type = float
            elif key in ["max_tokens", "budget_tokens"]:
                param_type = int
            elif key in ["reasoning_effort"]:
                param_type = str
            elif key in ["extended_thinking", "enabled"]:
                param_type = bool
            else:
                param_type = str

            result[current_path] = {
                "is_parent": False,
                "type": param_type,
                "default": value.get("default", None) if isinstance(value, dict) else None
            }

    return result


def convert_value_to_type(value: str, target_type: type) -> Any:
    """
    Convert string values from request to appropriate Python types.

    Args:
        value: The value to convert
        target_type: The type to convert to

    Returns:
        Converted value
    """
    if value is None:
        return None

    if target_type == bool:
        return str(value).lower() in ("true", "1", "yes", "y", "on")
    elif target_type == int:
        return int(value)
    elif target_type == float:
        return float(value)
    else:
        return value


def transform_flat_to_nested(params: Dict[str, Any], param_map: Dict[str, Dict]) -> Dict[str, Any]:
    """
    Transform flat parameters to nested structure based on parameter mapping.

    Args:
        params: Dictionary of flat parameters
        param_map: Parameter mapping from analyze_config_structure

    Returns:
        Transformed parameters with nested structure
    """
    result = {}
    processed_params = set()

    # Find all parent nodes in the parameter map
    parent_nodes = {k: v for k, v in param_map.items() if v.get("is_parent", False)}

    # Create a map of dot-notation keys to their parent paths
    parent_for_child = {}
    for parent_path in parent_nodes:
        parent_name = parent_path.split(".")[-1]
        for child_path in parent_nodes[parent_path].get("children", []):
            child_key = child_path.split(".")[-1]
            flat_key = f"{parent_name}.{child_key}"
            parent_for_child[flat_key] = parent_name

    # Process simple (non-nested) parameters first
    for param, value in params.items():
        if "." not in param and param not in parent_nodes:
            # Direct parameter, add to result
            if param in param_map:
                param_type = param_map[param].get("type", str)
                result[param] = convert_value_to_type(value, param_type)
            else:
                # Parameter not in mapping, keep as is
                result[param] = value
            processed_params.add(param)

    # Track which parent objects need to be created
    parents_to_create = set()
    for param in params:
        if "." in param:
            parent, child = param.split(".", 1)
            parents_to_create.add(parent)

    # Process nested parameters
    for parent_path, parent_info in parent_nodes.items():
        parent_name = parent_path.split(".")[-1]  # e.g., "extended_thinking"

        # Skip if we don't need this parent
        if parent_name not in parents_to_create and parent_name not in params:
            # Check if this is a required parent for validation
            if parent_info.get("required", True) and parent_name not in result:
                # Add an empty object for required parents
                logger.debug(f"Adding empty object for required parent: {parent_name}")
                result[parent_name] = {"enabled": False}
            continue

        # Initialize nested object if any child param exists or parent itself exists
        nested_obj = {}
        needs_parent = False

        # Check for directly provided parent parameter (e.g., "extended_thinking=true")
        if parent_name in params:
            parent_value = params[parent_name]
            processed_params.add(parent_name)

            # Check if any of the children is named "enabled"
            has_enabled_child = any(
                path.split(".")[-1] == "enabled" for path in parent_info.get("children", [])
            )

            if has_enabled_child:
                # If we have an "enabled" child, set it from the parent value
                nested_obj["enabled"] = convert_value_to_type(parent_value, bool)
                needs_parent = True
            else:
                # Otherwise, try to parse as JSON if it's a string that looks like JSON
                try:
                    if isinstance(parent_value, str) and (
                            parent_value.startswith("{") or parent_value.startswith("[")):
                        import json
                        json_value = json.loads(parent_value)
                        nested_obj.update(json_value)
                        needs_parent = True
                except:
                    # If we can't parse as JSON, treat as a direct value
                    pass

        # Process dot-notation parameters (e.g., "extended_thinking.enabled")
        for param, value in params.items():
            if "." in param:
                parent, child = param.split(".", 1)
                if parent == parent_name:
                    # Find the child's path in the param_map
                    child_type = None
                    for child_path in parent_info.get("children", []):
                        if child_path.split(".")[-1] == child:
                            child_type = param_map[child_path].get("type", str)
                            break

                    nested_obj[child] = convert_value_to_type(value, child_type or str)
                    processed_params.add(param)
                    needs_parent = True

        # If parent is required and children have been processed, ensure parent exists
        if parent_info.get("required", True) and needs_parent:
            result[parent_name] = nested_obj
        # If parent is not required but we have child values, add it
        elif not parent_info.get("required", True) and needs_parent:
            result[parent_name] = nested_obj
        # If parent is required but no children were processed, create an empty object with defaults
        elif parent_info.get("required", True) and parent_name not in result:
            # For extended_thinking, provide a default of {enabled: false}
            if parent_name == "extended_thinking":
                result[parent_name] = {"enabled": False}
            else:
                result[parent_name] = {}

    # Add any remaining parameters that weren't processed
    for param, value in params.items():
        if param not in processed_params:
            result[param] = value
    logger.debug(f"Transformed flat params: {result}")
    return result


async def get_dynamic_params(request: Request, model_name: str, backend: str):
    """
    Dynamically validate request parameters based on model configuration.

    Args:
        request: FastAPI request
        model_name: Name of the model to get parameters for
        backend: Backend provider (e.g., 'openai', 'claude')

    Returns:
        Validated parameter object

    Raises:
        HTTPException: If parameters fail validation
    """
    # Look up allowed parameters from the configuration
    allowed_params = get_allowed_params(backend, model_name)
    fields = build_fields_from_config(allowed_params)

    # Analyze the parameter structure
    param_map = analyze_config_structure(allowed_params)

    # Dynamically create a Pydantic model
    DynamicParams = create_model("DynamicParams", **fields)

    try:
        # Convert query parameters to a dict
        params_dict = dict(request.query_params)

        # Transform flat params to nested structure
        transformed_params = transform_flat_to_nested(params_dict, param_map)

        # Validate with the dynamic model
        logger.debug(f"Validating params for {model_name}: {transformed_params}")
        validated_params = DynamicParams.parse_obj(transformed_params)
        return validated_params
    except Exception as e:
        logger.error(f"Parameter validation error for {model_name}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")


async def get_dynamic_form_params(request: Request, agent_manager=Depends(get_agent_manager)):
    """
    Process form parameters with dynamic validation.

    Args:
        request: FastAPI request
        agent_manager: Dependency that provides the agent manager

    Returns:
        Dict containing validated parameters, original form data, and model info
    """
    # Extract form data as a dict
    form = await request.form()
    form_dict = dict(form)

    logger.debug(f"RAW FORM DATA RECEIVED: {form_dict}")

    # Get model_name and backend from form
    model_name = form_dict.get("model_name")
    backend = form_dict.get("backend")

    logger.debug(f"EXTRACTED model_name: {model_name}, backend: {backend}")

    # If both are provided, validate parameters normally
    if model_name and backend:
        try:
            # Retrieve allowed parameters from the configuration
            allowed_params = get_allowed_params(backend, model_name)
            logger.debug(f"ALLOWED PARAMS: {allowed_params}")

            # Analyze the parameter structure
            param_map = analyze_config_structure(allowed_params)
            logger.debug(f"PARAMETER STRUCTURE MAP: {param_map}")

            # Transform the form data to match expected nested structure
            logger.debug(f"BEFORE TRANSFORM: {form_dict}")
            transformed_form = transform_flat_to_nested(form_dict, param_map)
            logger.debug(f"AFTER TRANSFORM: {transformed_form}")

            # Debug the transformation
            logger.debug(f"Original form: {form_dict}")
            logger.debug(f"Transformed: {transformed_form}")

            fields = build_fields_from_config(allowed_params)
            DynamicFormParams = create_model("DynamicFormParams", **fields)

            try:
                logger.debug(f"MODEL SCHEMA: {DynamicFormParams.model_json_schema()}")
                validated_params = DynamicFormParams.parse_obj(transformed_form)
                logger.debug(f"VALIDATED PARAMS: {validated_params}")
                return {
                    "params": validated_params,
                    "original_form": form_dict,
                    "model_name": model_name,
                    "backend": backend
                }
            except Exception as e:
                logger.error(f"Form parameter validation error: {str(e)}")
                import traceback
                logger.error(f"VALIDATION ERROR DETAILS: {traceback.format_exc()}")
                raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing form parameters: {str(e)}")
            import traceback
            logger.error(f"PROCESSING ERROR DETAILS: {traceback.format_exc()}")
            raise HTTPException(status_code=400, detail=f"Error processing parameters: {str(e)}")

    # If we're missing model info, just return the form data
    # We'll handle fetching the model details in the route handler
    return {
        "params": None,
        "original_form": form_dict,
        "model_name": model_name,
        "backend": backend
    }