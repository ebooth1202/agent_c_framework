from typing import Optional
import yaml
import markdown

from agent_c.toolsets import json_schema, Toolset
import logging

from ...helpers.validate_kwargs import validate_required_fields
from ... import WorkspaceTools
from ...helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path, has_file_extension, normalize_path


class SarsTools(Toolset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='sars', use_prefix=False)
        self.logger: logging.Logger = logging.getLogger(__name__)
        self.workspace_tool: Optional[WorkspaceTools] = None
        self.file_collector = None

    async def post_init(self):
        self.workspace_tool = self.tool_chest.available_tools.get("WorkspaceTools")

    async def _read_workspace_file(self, filename: str, **kwargs) -> str:
        """
        Helper method to read a file from the workspace with common validation logic.

        Args:
            filename: The name of the file to read
            **kwargs: Must contain 'workspace' and optionally 'tool_context'

        Returns:
            File contents or error message
        """
        tool_context = kwargs.get("tool_context")

        success, message = validate_required_fields(kwargs=kwargs, required_fields=['workspace'])
        if not success:
            return message

        workspace = kwargs['workspace']

        unc_path = create_unc_path(workspace, filename)
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)

        if error:
            return f"Invalid path: {error}"

        contents = await self.workspace_tool.read(path=unc_path, tool_context=tool_context)
        return contents

    @json_schema(
        'Get branch referral report',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the branch referral report is located',
                'required': True
            }
        }
    )
    async def get_branch_referral(self, **kwargs) -> str:
        tool_context = kwargs.get("tool_context")

        contents = await self._read_workspace_file("branch_referral.md", **kwargs)

        # If there's an error, contents will be the error message
        if not contents or contents.startswith("Invalid path:") or "required" in contents:
            return contents

        if contents:
            await self._render_media_markdown(markdown.markdown(contents), sent_by="get_branch_referral", tool_context=tool_context)

        return contents

    @json_schema(
        'Get external_intelligence referral report',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the external_intelligence is located',
                'required': True
            }
        }
    )
    async def get_external_intelligence_referral(self, **kwargs) -> str:
        tool_context = kwargs.get("tool_context")

        contents = await self._read_workspace_file("external_intelligence.md", **kwargs)

        # If there's an error, contents will be the error message
        if not contents or contents.startswith("Invalid path:") or "required" in contents:
            return contents

        if contents:
            await self._render_media_markdown(markdown.markdown(contents), sent_by="get_external_intelligence", tool_context=tool_context)

        return contents

    @json_schema(
        'Get SARS scoring rubric for reference',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the sars scoring rubric is located',
                'required': True
            }
        }
    )
    async def get_scoring_rubric(self, **kwargs) -> str:
        return await self._read_workspace_file("sar_scoring_rubric.md", **kwargs)

    @json_schema(
        'Get transactions to evaluate',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the transactions are located',
                'required': True
            }
        }
    )
    async def get_transactions(self, **kwargs) -> str:
        return await self._read_workspace_file("transactions_alert.json", **kwargs)

    @json_schema(
        'Get the cdd report to consider',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the cdd_report are located',
                'required': True
            }
        }
    )
    async def get_cdd_report(self, **kwargs) -> str:
        return await self._read_workspace_file("cdd_report.json", **kwargs)



Toolset.register(SarsTools, required_tools=['WorkspaceTools'])
