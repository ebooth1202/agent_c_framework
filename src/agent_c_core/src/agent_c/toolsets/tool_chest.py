import copy
import asyncio
import copy
import json
import logging
from typing import Type, List, Union, Dict, Any, Tuple

from pyarrow.ipc import new_stream

from agent_c.prompting.basic_sections.tool_guidelines import EndToolGuideLinesSection, BeginToolGuideLinesSection
from agent_c.prompting.prompt_section import PromptSection
from agent_c.toolsets.tool_set import Toolset


class ToolChest:
    """
    A class representing a collection of toolsets that can be used by an agent.
    
    Attributes:
        __tool_instances (dict[str, Toolset]): A private dictionary to store instances of toolsets.
        __tool_classes (list[Type[Toolset]]): A private list to store the classes of the toolsets.
        __tool_sections (List[PromptSection]): A private list to store sections of the prompt.
        logger (logging.Logger): An instance of a logger.
        
    Methods:
        activate_tool(tool_name: str) -> bool: Placeholder method to activate a tool by name.
        add_tool_class(cls: Type[Toolset]): Add a new tool class to the tool chest.
        add_tool_instance(instance: Toolset): Add a new instance of a tool to the tool chest.
        init_tools(**kwargs): Asynchronously initialize the toolsets in the tool chest.
        call_tools(tool_calls: List[dict], format_type: str) -> List[dict]: Execute multiple tool calls concurrently.
        _execute_tool_call(function_id: str, function_args: Dict) -> Any: Execute a single tool call.
        init_tools(**kwargs): Asynchronously initialize the toolsets in the tool chest.
    """

    def __init__(self, **kwargs):
        """
        Initializes the ToolChest with tool instances, tool classes, and a logger.
        
        Args:
            **kwargs: Arbitrary keyword arguments, expects 'tool_classes' to be provided to override default.
        """
        self.__tool_instances: dict[str, Toolset] = {}
        self.__tool_classes = kwargs.get('tool_classes', Toolset.tool_registry)

        self.logger = logging.getLogger(__name__)
        self.__tool_sections: List[PromptSection] = []
        self.__active_open_ai_schemas: List[dict] = []

    # Placeholder
    def activate_tool(self, tool_name: str) -> bool:
        """
        Activates a tool by name. Currently, this is a placeholder method.
        
        Args:
            tool_name (str): The name of the tool to activate.
        
        Returns:
            bool: Returns True if the tool is activated, otherwise False.  For now.
        """
        if self.active_tools.get(tool_name):
            return True

        return False

    @property
    def active_tools(self) -> dict[str, Toolset]:
        """
        Property that returns the active tool instances.
        Currently, all toolsets are the active toolsets but that will change.
        
        Returns:
            dict[str, Toolset]: Dictionary of active tool instances.
        """
        return self.__tool_instances

    @property
    def active_open_ai_schemas(self) -> List[dict]:
        """
        Property that returns the active tool instances in Open AI format.

        Returns:
            dict[str, Toolset]: Dictionary of active tool instances.
        """
        return self.__active_open_ai_schemas

    @property
    def active_claude_schemas(self) -> List[dict]:
        """
        Property that returns the active tool instances in Claude format

        Returns:
            dict[str, Toolset]: Dictionary of active tool instances.
        """
        oai_schemas = self.__active_open_ai_schemas
        claude_schemas = []
        for schema in oai_schemas:
            new_schema = copy.deepcopy(schema['function'])
            new_schema['input_schema'] = new_schema.pop('parameters')
            claude_schemas.append(new_schema)

        return claude_schemas


    @property
    def active_tool_sections(self) -> List[PromptSection]:
        """
        Property that returns the `PromptSection` for each active tool.
        Currently, all toolsets are the active toolsets but that will chang.
        
        Returns:
            List[PromptSection]: List of active tool sections.
        """
        if len(self.__tool_sections) == 0:
            return []

        return [BeginToolGuideLinesSection()] + self.__tool_sections + [EndToolGuideLinesSection()]

    def add_tool_class(self, cls: Type[Toolset]):
        """
        Adds a new tool class to the list of classes to be instantiated in init_tools
        
        Args:
            cls (Type[Toolset]): The class of the tool to add.
        """
        self.__tool_classes.append(cls)

    def add_tool_instance(self, instance: Toolset):
        """
        Adds a new instance of a tool to the tool chest.
        
        Args:
            instance (Toolset): The instance of the tool to add.
        """
        self.__tool_instances[instance.name] = instance
        self.__active_open_ai_schemas += instance.openai_schemas

    async def init_tools(self, **kwargs):
        """
        Asynchronously initializes the toolsets in the tool chest.
        
        This method will initialize each tool one at a time, allowing toolsets that depend on others to access them during their initialization.
        
        Args:
            **kwargs: Arbitrary keyword arguments to pass to the tool instances during initialization.
        """
        for tool_class in self.__tool_classes:
            tool_obj: Union[Toolset, None] = None
            try:
                tool_obj = tool_class(tool_chest=self, **kwargs)
            except Exception as e:
                self.logger.warning(f"Error initializing tool {tool_class.__name__}: {str(e)}")

            if tool_obj is not None and tool_obj.tool_valid:
                self.__tool_instances[tool_obj.name] = tool_obj
                await tool_obj.post_init()

        self.__tool_sections = [toolbelt.section for toolbelt in self.__tool_instances.values() if toolbelt.section is not None]
        for toolset in self.__tool_instances.values():
            self.__active_open_ai_schemas += toolset.openai_schemas

    async def call_tools(self, tool_calls: List[dict], format_type: str = "claude") -> List[dict]:
        """
        Execute multiple tool calls concurrently and return the results.
        
        Args:
            tool_calls (List[dict]): List of tool calls to execute
            format_type (str): The format to use for the results ("claude" or "gpt")
            
        Returns:
            List[dict]: Tool call results formatted according to the agent type
        """
        async def make_call(tool_call: dict) -> Tuple[dict, dict]:
            # Common logic for executing a tool call
            # TODO: refactor this to common model and push the format back down
            if format_type == "claude":
                fn = tool_call['name']
                args = tool_call['input']
                ai_call = copy.deepcopy(tool_call)
            else:  # gpt
                fn = tool_call['name']
                # Handle the case where the test provides Claude format but expects GPT processing
                if 'arguments' in tool_call:
                    args = json.loads(tool_call['arguments'])
                elif 'input' in tool_call:
                    # Fallback to 'input' if 'arguments' is not available
                    args = tool_call['input']
                    # Add 'arguments' field to the tool_call for compatibility
                    tool_call['arguments'] = json.dumps(args)
                ai_call = {
                    "id": tool_call['id'],
                    "function": {"name": fn, "arguments": tool_call['arguments']},
                    'type': 'function'
                }
                
            try:
                function_response = await self._execute_tool_call(fn, args)
                
                if format_type == "claude":
                    call_resp = {
                        "type": "tool_result", 
                        "tool_use_id": tool_call['id'],
                        "content": function_response
                    }
                else:  # gpt
                    call_resp = {
                        "role": "tool", 
                        "tool_call_id": tool_call['id'], 
                        "name": fn,
                        "content": function_response
                    }
            except Exception as e:
                if format_type == "claude":
                    call_resp = {
                        "type": "tool_result", 
                        "tool_use_id": tool_call['id'],
                        "content": f"Exception: {e}"
                    }
                else:  # gpt
                    call_resp = {
                        "role": "tool", 
                        "tool_call_id": tool_call['id'], 
                        "name": fn,
                        "content": f"Exception: {e}"
                    }
                    
            return ai_call, call_resp

        # Schedule all the calls concurrently
        tasks = [make_call(tool_call) for tool_call in tool_calls]
        completed_calls = await asyncio.gather(*tasks)

        # Unpack the resulting ai_calls and resp_calls
        ai_calls, results = zip(*completed_calls)
        
        # Format the final result based on agent type
        if format_type == "claude":
            return [
                {'role': 'assistant', 'content': list(ai_calls)},
                {'role': 'user', 'content': list(results)}
            ]
        else:  # gpt
            return [
                {'role': 'assistant', 'tool_calls': list(ai_calls), 'content': ''}
            ] + list(results)
            
    async def _execute_tool_call(self, function_id: str, function_args: Dict) -> Any:
        """
        Execute a single tool call.
        This method is similar to BaseAgent._call_function but lives in ToolChest.
        
        Args:
            function_id (str): The function identifier
            function_args (Dict): Arguments to pass to the function
            
        Returns:
            Any: The result of the function call
        """
        # Handle the special case for the think tool
        if function_id.lower() == "think":
            toolset = "think"
            function_name = "think"
        else:
            toolset, function_name = function_id.split(Toolset.tool_sep, 1)
        
        try:
            src_obj: Toolset = self.active_tools[toolset]
            if src_obj is None:
                return f"{toolset} is not a valid toolset."

            function_to_call: Any = getattr(src_obj, function_name)
            return await function_to_call(**function_args)
        except Exception as e:
            logging.exception(f"Failed calling {function_name} on {toolset}. {e}")
            return f"Important! Tell the user an error occurred calling {function_name} on {toolset}. {e}"


