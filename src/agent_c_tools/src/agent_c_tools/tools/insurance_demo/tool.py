from typing import Optional
import yaml
import markdown

from agent_c.toolsets import json_schema, Toolset
import logging

from ...helpers.validate_kwargs import validate_required_fields
from ... import WorkspaceTools
from ...helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path, has_file_extension, \
    normalize_path


class InsuranceDemoTools(Toolset):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='new_business_insurance', use_prefix=False)
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
        'Example and template for generating a Quote for New Business Insurance. Requires other processes to be run first.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the quote template is located',
                'required': True
            }
        }
    )
    async def get_policy_quote(self, **kwargs) -> str:
        # tool_context = kwargs.get("tool_context")

        return await self._read_workspace_file("quote_template.md", **kwargs)

        # # If there's an error, contents will be the error message
        # if not contents or contents.startswith("Invalid path:") or "required" in contents:
        #     return contents
        #
        # if contents:
        #     await self._render_media_markdown(markdown.markdown(contents), sent_by="get_branch_referral",
        #                                       tool_context=tool_context)
        #
        # return contents

    @json_schema(
        'Get underwriting guidelines',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the underwriting guidelines is located',
                'required': True
            },
            'guidelines_type': {
                'type': 'string',
                'description': 'The type of underwriting guidelines to retrieve',
                'required': False,
                'default': 'general_liability',
                'enum': ['general_liability', 'workers_compensation', 'commercial_auto']
            }
        }
    )
    async def get_underwriting_guidelines(self, **kwargs) -> str:
        # tool_context = kwargs.get("tool_context")
        #
        return await self._read_workspace_file("underwriting_guidelines.md", **kwargs)

        # # If there's an error, contents will be the error message
        # if not contents or contents.startswith("Invalid path:") or "required" in contents:
        #     return contents
        #
        # if contents:
        #     await self._render_media_markdown(markdown.markdown(contents), sent_by="get_external_intelligence", tool_context=tool_context)
        #
        # return contents

    @json_schema(
        'Get General Liability Risk scoring rubric for reference',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the sars scoring rubric is located',
                'required': True
            }
        }
    )
    async def get_risk_rubric(self, **kwargs) -> str:
        return await self._read_workspace_file("risk_scoring.md", **kwargs)

    @json_schema(
        'Get Applicant Company Loss Information to evaluate',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the transactions are located',
                'required': True
            },
            'tax_id': {
                'type': 'string',
                'description': 'The tax ID of the company to get loss history for',
                'required': False
            }
        }
    )
    async def company_loss_history(self, **kwargs) -> str:
        return await self._read_workspace_file("loss_history.json", **kwargs)

    @json_schema(
        'Extract ACORD data',
        {
            'workspace': {
                'type': 'string',
                'description': 'The workspace where the acord file to process is located',
                'required': True
            }
        }
    )
    async def extract_acord_data(self, **kwargs) -> str:
        return await self._read_workspace_file("acord_125.json", **kwargs)


Toolset.register(InsuranceDemoTools, required_tools=['WorkspaceTools'])
