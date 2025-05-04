import pytest

from agent_c_api.api.v1.llm_models.agent_params import (
    AgentInitializationParams,
    AgentUpdateParams
)
from agent_c_api.api.v2.models.session_models import (
    SessionCreate,
    SessionUpdate
)
from agent_c_api.api.v2.utils.model_converters import (
    v1_to_v2_session_create,
    v1_to_v2_session_update,
    v2_to_v1_session_params
)


class TestV1ToV2Converters:
    
    def test_v1_to_v2_session_create_minimal(self):
        # Test with minimal required parameters
        v1_params = AgentInitializationParams(
            model_name="gpt-4o",
            backend="openai"
        )
        
        v2_model = v1_to_v2_session_create(v1_params)
        
        assert v2_model.model_id == "gpt-4o"
        assert v2_model.persona_id == "default"
        assert v2_model.metadata == {"backend": "openai"}
    
    def test_v1_to_v2_session_create_full(self):
        # Test with all parameters
        v1_params = AgentInitializationParams(
            model_name="claude-3-5-sonnet-latest",
            backend="anthropic",
            persona_name="researcher",
            custom_prompt="Act as a helpful researcher",
            temperature=0.7,
            max_tokens=4000,
            reasoning_effort="high",
            budget_tokens=1000,
            ui_session_id="existing-session-id"
        )
        
        v2_model = v1_to_v2_session_create(v1_params)
        
        assert v2_model.model_id == "claude-3-5-sonnet-latest"
        assert v2_model.persona_id == "researcher"
        assert v2_model.metadata == {"backend": "anthropic", "custom_prompt": "Act as a helpful researcher"}
        # Parameters are no longer directly stored in the session model
    
    def test_v1_to_v2_session_update(self):
        # Test update parameters conversion
        v1_params = AgentUpdateParams(
            ui_session_id="session-to-update",
            persona_name="coder",
            custom_prompt="Act as a code reviewer",
            temperature=0.5,
            reasoning_effort="medium"
        )
        
        v2_model = v1_to_v2_session_update(v1_params)
        
        assert v2_model.name is None  # Name update not present in v1
        assert v2_model.metadata == {"custom_prompt": "Act as a code reviewer"}


class TestV2ToV1Converters:
    
    def test_v2_to_v1_session_params_minimal(self):
        # Test with minimal required parameters
        v2_model = SessionCreate(
            model_id="gpt-4o",
            persona_id="default",
            metadata={"backend": "openai"}
        )
        
        v1_params = v2_to_v1_session_params(v2_model)
        
        assert v1_params.model_name == "gpt-4o"
        assert v1_params.backend == "openai"
        assert v1_params.persona_name == "default"
        assert v1_params.ui_session_id is None
    
    def test_v2_to_v1_session_params_full(self):
        # Test with all parameters
        v2_model = SessionCreate(
            model_id="claude-3-5-sonnet-latest",
            persona_id="researcher",
            metadata={
                "backend": "anthropic",
                "custom_prompt": "Act as a helpful researcher"
            }
        )
        
        v1_params = v2_to_v1_session_params(v2_model)
        
        assert v1_params.model_name == "claude-3-5-sonnet-latest"
        assert v1_params.backend == "anthropic"
        assert v1_params.persona_name == "researcher"
        assert v1_params.custom_prompt == "Act as a helpful researcher"
        # Other parameters are now None by default
        assert v1_params.temperature is None
        assert v1_params.max_tokens is None
        assert v1_params.reasoning_effort is None
        assert v1_params.budget_tokens is None