from fastapi import Request, Depends
from agent_c_api.core.agent_manager import AgentManager
from fastapi import Request, HTTPException
from pydantic import create_model
from agent_c_api.config.config_loader import get_allowed_params


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
            # Remove keys that aren’t actual sub-fields (e.g. "required").
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
            elif param in ["extended_thinking"]:
                field_type = bool
            else:
                field_type = str

            # If spec is a dict, get its "default" value; otherwise, mark as required.
            default = spec.get("default", ...) if isinstance(spec, dict) else ...
            fields[param] = (field_type, default)
    return fields


async def get_dynamic_params(request: Request, model_name: str, backend: str):
    # Look up allowed parameters from the configuration.
    allowed_params = get_allowed_params(backend, model_name)
    fields = build_fields_from_config(allowed_params)

    # Dynamically create a Pydantic model.
    DynamicParams = create_model("DynamicParams", **fields)
    try:
        # Convert query parameters to a dict and parse.
        params_dict = dict(request.query_params)
        return DynamicParams.parse_obj(params_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def get_dynamic_form_params(request: Request, agent_manager=Depends(get_agent_manager)):
    # Extract form data as a dict
    form = await request.form()
    form_dict = dict(form)

    # Get model_name and backend from form
    model_name = form_dict.get("model_name")
    backend = form_dict.get("backend")

    # If both are provided, validate parameters normally
    if model_name and backend:
        # Retrieve allowed parameters from the configuration
        allowed_params = get_allowed_params(backend, model_name)
        fields = build_fields_from_config(allowed_params)
        DynamicFormParams = create_model("DynamicFormParams", **fields)

        try:
            validated_params = DynamicFormParams.parse_obj(form_dict)
            return {
                "params": validated_params,
                "original_form": form_dict,
                "model_name": model_name,
                "backend": backend
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    # If we're missing model info, just return the form data
    # We'll handle fetching the model details in the route handler
    return {
        "params": None,
        "original_form": form_dict,
        "model_name": model_name,
        "backend": backend
    }

