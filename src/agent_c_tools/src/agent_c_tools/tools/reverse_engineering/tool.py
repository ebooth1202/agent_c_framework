import itertools
from typing import Any, Dict, Optional

from agent_c.models.agent_config import AgentConfiguration
from agent_c.toolsets.json_schema import json_schema
from agent_c.toolsets.tool_set import Toolset
from agent_c_tools.tools.agent_assist.base import AgentAssistToolBase
from agent_c_tools.tools.reverse_engineering.prompt import RevEngSection


class ReverseEngineeringTools(AgentAssistToolBase):
    """
    CssExplorerTools provides methods for working with CSS files in workspaces.
    It enables efficient navigation and manipulation of large CSS files with component-based structure.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(name='rev_eng', **kwargs)
        self.section = RevEngSection()
        self.recon_oneshot = self.agent_loader.catalog['recon_oneshot']
        self.recon_revise_oneshot = self.agent_loader.catalog['recon_revise_oneshot']
        self.recon_answers_oneshot = self.agent_loader.catalog['recon_answers_oneshot']

    async def __try_explain_code(self, file: str) -> str:
        try:
            context = await self.workspace_tool.inspect_code(path=file)
            if context.startswith("{"):
                return file

            return context

        except Exception as e:
            return file


    @json_schema(
        'Perform an in depth analysis of all code files matching a glob pattern. Output will be saved to the scratchpad of the workspace containing the code.',
        {
            'glob': {
                'type': 'string',
                'description': 'A glob pattern in workspace workspace UNC format. Equivalent to `glob.glob` in Python with recursive=True. e.g. //workspace/**/*.js',
                'required': True
            }
        }
    )
    async def analyze_source(self, **kwargs) -> str:
        glob: str = kwargs.get('glob')
        batch_size: int = kwargs.get('batch_size', 2)
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(glob)
        if error is not None:
            return f"Error: {error}"

        files = await workspace.glob(relative_path, True)

        await self._pass_one(workspace, files, batch_size, tool_context )
        await self._pass_two(workspace, files, tool_context)

        return f"Processed {len(files)} files. See //{workspace.name}/.scratch/analyze_source/ for results."


    @json_schema(
        'Make a request of and expert on the analysis of the codebase in a given workspace. The expert will be able to ',
        {
            'query': {
                'type': 'string',
                'description': 'A question, or request for information about the codebase and/or the analysis done on it.',
                'required': True
            },
            'workspace': {
                'type': 'string',
                'description': 'The workspace containing the output of `analyze_source` you with to query.',
                'required': True
            },
        }
    )
    async def query_analysis(self, **kwargs) -> str:
        query: str = kwargs.get('query')
        workspace: str = kwargs.get('workspace')
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        ws = self.workspace_tool.find_workspace_by_name(workspace)
        persona_data = self.recon_answers_oneshot.model_dump()
        persona_data['persona'] = persona_data['persona'].replace('[workspace]', workspace).replace('[workspace_tree]', await ws.tree(7, 3))
        new_persona = AgentConfiguration.model_validate(persona_data)
        return await self.agent_oneshot(query,
                                        persona=new_persona,
                                        user_session_id=tool_context['session_id'],
                                        tool_context=tool_context)


    async def _pass_one(self, workspace, files: list[str], batch_size: int = 2, tool_context: Optional[Dict[str, any]] = None) -> list[str]:
        pass_one_results = []
        if batch_size > 1:
            parallel: bool = True
        else:
            parallel: bool = False
            batch_size = 1

        if parallel:
            iterator = iter(files)
            while batch := list(itertools.islice(iterator, batch_size)):
                paths = "\n- ".join([f"//{workspace.name}/{file}" for file in batch])
                await self._raise_text_delta_event(content=f"\n**Processing files (pass 1)**: {paths}... ")
                true_batch = [await self.__try_explain_code(f"//{workspace.name}/{file}") for file in batch]
                results = await self.parallel_agent_oneshots(true_batch,
                                                             persona=self.recon_oneshot,
                                                             user_session_id=tool_context['session_id'],
                                                             tool_context=tool_context)
                await self._raise_text_delta_event(content=f"\nfinished processing files (pass 1):\n- {paths}")
                pass_one_results.extend(results)
        else:
            for file in files:
                await self._raise_text_delta_event(content=f"\n**Processing file (pass 1)**: {file}... ")
                result = await self.agent_oneshot(user_message=await self.__try_explain_code(f"//{workspace.name}/{file}"),
                                                  persona=self.recon_oneshot,
                                                  user_session_id=tool_context['session_id'],
                                                  tool_context=tool_context)
                await self._raise_text_delta_event(content=f"\nDone processing file (pass 1): {file}")
                pass_one_results.append(result)

        return pass_one_results


    async def _pass_two(self, workspace, files: list[str], tool_context: Optional[Dict[str, any]] = None) -> list[str]:
        pass_two_results = []

        for file in files:
            await self._raise_text_delta_event(content=f"\n**Processing file (pass 1)**: {file}... ")
            result = await self.agent_oneshot(user_message=f"//{workspace.name}/{file}",
                                              persona=self.recon_revise_oneshot,
                                              user_session_id=tool_context['session_id'],
                                              tool_context=tool_context)
            pass_two_results.append(result)

        return pass_two_results


# Register the toolset
Toolset.register(ReverseEngineeringTools, required_tools=['WorkspaceTools'])
