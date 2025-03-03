import asyncio
import unittest
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
from agent_c_api.core.agent_bridge import AgentBridge
from agent_c_api.core.agent_manager import UItoAgentBridgeManager


class TestCustomPersonaPersistence(unittest.TestCase):
    """Tests to verify custom persona text is properly maintained during agent operations."""

    def setUp(self):
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)

        self.agent_manager = UItoAgentBridgeManager()
        self.custom_prompt = "This is a test custom persona prompt that should persist."
        # Use new_event_loop instead of get_event_loop to avoid deprecation warning
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    @patch('agent_c.agents.gpt.AsyncOpenAI')
    @patch('agent_c_api.core.reactjs_agent.GPTChatAgent')
    def test_custom_prompt_persists_during_initialization(self, mock_gpt_agent, mock_openai):
        """Test that custom prompt persists through agent initialization."""
        # Setup mocks
        mock_agent_instance = MagicMock()
        mock_gpt_agent.return_value = mock_agent_instance

        # Create agent with test prompt
        agent = AgentBridge(
            user_id="test_user",
            backend="openai",
            model_name="gpt-4o",
            persona_name="default",
            custom_persona_text=self.custom_prompt
        )

        # Mock private methods correctly - using the name-mangled version
        with patch.object(AgentBridge, '_ReactJSAgent__init_session', new_callable=AsyncMock) as mock_init_session:
            with patch.object(AgentBridge, '_ReactJSAgent__init_tool_chest',
                              new_callable=AsyncMock) as mock_init_tools:
                with patch.object(AgentBridge, '_ReactJSAgent__init_agent', new_callable=AsyncMock) as mock_init_agent:
                    # Check initial state
                    self.assertEqual(agent.custom_persona_text, self.custom_prompt)

                    # Run initialization with mocked dependencies
                    self.loop.run_until_complete(agent.initialize())

                    # Verify custom prompt still exists after initialization
                    self.assertEqual(agent.custom_persona_text, self.custom_prompt)

                    # Verify our mocks were called
                    mock_init_session.assert_called_once()
                    mock_init_tools.assert_called_once()
                    mock_init_agent.assert_called_once()

    @patch('agent_c.agents.gpt.AsyncOpenAI')
    def test_custom_prompt_persists_during_model_change(self, mock_openai):
        """Test that custom prompt persists when changing models."""

        # Create a simpler test that directly tests AgentManager's handling of custom_persona_text

        # Create a more complete mock ReactJSAgent that includes required methods
        class MockReactJSAgent:
            def __init__(self, **kwargs):
                self.custom_persona_text = kwargs.get('custom_persona_text')
                self.session_manager = None
                self.model_name = kwargs.get('model_name')
                self.persona_name = kwargs.get('persona_name', 'default')
                self.backend = kwargs.get('backend', 'openai')
                self.session_id = "mock-session-id"

            async def initialize(self):
                # Do nothing
                pass

            def _current_timestamp(self):
                """Return current UTC timestamp in ISO format."""
                return datetime.now(timezone.utc).isoformat()

            def _get_agent_config(self):
                """Mock the agent config method."""
                return {
                    'user_id': 'test_user',
                    'backend': self.backend,
                    'model_name': self.model_name,
                    'persona_name': self.persona_name,
                    'initialized_tools': [],
                    'agent_name': 'MockAgent',
                    'session_id': self.session_id,
                    'custom_prompt': self.custom_persona_text,
                    'output_format': 'raw',
                    'created_time': self._current_timestamp(),
                    'temperature': None,
                    'reasoning_effort': None,
                    'model_parameters': {
                        'temperature': None,
                        'reasoning_effort': None,
                        'extended_thinking': False,
                        'budget_tokens': 0
                    }
                }

        # Patch the ReactJSAgent with our mock
        with patch('agent_c_api.core.agent_manager.ReactJSAgent', MockReactJSAgent):
            # Create initial session
            session_id = self.loop.run_until_complete(
                self.agent_manager.create_session(
                    llm_model="gpt-4o",
                    backend="openai",
                    persona_name="default",
                    custom_persona_text=self.custom_prompt
                )
            )

            # Verify initial state
            session_data = self.agent_manager.get_session_data(session_id)
            self.assertIsNotNone(session_data)
            agent = session_data["agent"]
            self.assertEqual(agent.custom_persona_text, self.custom_prompt)

            # Change model - without specifying custom_persona_text again
            new_session_id = self.loop.run_until_complete(
                self.agent_manager.create_session(
                    llm_model="gpt-3.5-turbo",
                    backend="openai",
                    persona_name="default",
                    existing_ui_session_id=session_id
                )
            )

            # Verify custom prompt persisted in AgentManager's create_session method
            new_session_data = self.agent_manager.get_session_data(new_session_id)
            self.assertIsNotNone(new_session_data)
            new_agent = new_session_data["agent"]

            # This is the key assertion - verify the custom prompt was maintained
            self.assertEqual(new_agent.custom_persona_text, self.custom_prompt)

    @patch('agent_c.agents.gpt.AsyncOpenAI')
    def test_real_agent_persists_custom_prompt_during_model_change(self, mock_openai):
        """Test that custom prompt persists when changing models using the real ReactJSAgent."""

        # This test uses the actual ReactJSAgent with minimal mocking

        # Define a custom mock for __init_session that sets the session_id
        async def mock_init_session(self):
            self.session_id = "test-session-123"

        # Define mocks for the other initialization methods
        async def mock_init_tool_chest(self):
            pass

        async def mock_init_agent(self):
            pass

        # Setup patches for the initialization methods
        with patch.object(AgentBridge, '_ReactJSAgent__init_session', mock_init_session):
            with patch.object(AgentBridge, '_ReactJSAgent__init_tool_chest', mock_init_tool_chest):
                with patch.object(AgentBridge, '_ReactJSAgent__init_agent', mock_init_agent):
                    # Create initial session
                    session_id = self.loop.run_until_complete(
                        self.agent_manager.create_session(
                            llm_model="gpt-4o",
                            backend="openai",
                            persona_name="default",
                            custom_persona_text=self.custom_prompt
                        )
                    )

                    # Verify initial state
                    session_data = self.agent_manager.get_session_data(session_id)
                    self.assertIsNotNone(session_data)
                    agent = session_data["agent"]
                    self.assertEqual(agent.custom_persona_text, self.custom_prompt)

                    # Change model - without specifying custom_persona_text again
                    new_session_id = self.loop.run_until_complete(
                        self.agent_manager.create_session(
                            llm_model="gpt-3.5-turbo",
                            backend="openai",
                            persona_name="default",
                            existing_ui_session_id=session_id
                        )
                    )

                    # Verify custom prompt persisted in the real agent
                    new_session_data = self.agent_manager.get_session_data(new_session_id)
                    self.assertIsNotNone(new_session_data)
                    new_agent = new_session_data["agent"]

                    # This checks that the real ReactJSAgent properly maintains the prompt
                    self.assertEqual(new_agent.custom_persona_text, self.custom_prompt)


if __name__ == "__main__":
    unittest.main()