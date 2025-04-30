import json
from typing import Any, Optional

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema

from .xml_navigator import XMLNavigator
from agent_c_tools.tools.workspace.tool import WorkspaceTools


class XmlExplorerTools(Toolset):
    """
    XMLExplorerTools provides methods for working with XML files in workspaces.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(name='xml', **kwargs)
        self.workspace_tool: Optional[WorkspaceTools] = None

    async def post_init(self):
        self.workspace_tool = self.tool_chest.active_tools['WorkspaceTools']

    @json_schema(
        'Get structure information about a large XML file without loading the entire file.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to update',
                'required': True
            },
            'max_depth': {
                'type': 'integer',
                'description': 'Maximum depth to traverse in the XML structure.',
                'required': False
            },
            'sample_count': {
                'type': 'integer',
                'description': 'Number of sample elements to include at each level.',
                'required': False
            }
        }
    )
    async def structure(self, **kwargs: Any) -> str:
        """Asynchronously retrieves structure information about a large XML file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to analyze
            max_depth (int, optional): Maximum depth to traverse in the XML structure. Defaults to 3.
            sample_count (int, optional): Number of sample elements to include at each level. Defaults to 5.

        Returns:
            str: JSON string with structure information or an error message.
        """
        max_depth: int = kwargs.get('max_depth', 3)
        sample_count: int = kwargs.get('sample_count', 5)
        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        navigator = XMLNavigator(workspace)
        return await navigator.get_structure(relative_path, max_depth, sample_count)

    @json_schema(
        'Execute an XPath query on an XML file using lxml and return matching elements as YAML.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to update',
                'required': True
            },
            'xpath': {
                'type': 'string',
                'description': 'XPath query to execute',
                'required': True
            },
            'limit': {
                'type': 'integer',
                'description': 'Max results to return.',
                'required': False
            }
        }
    )
    async def query(self, **kwargs: Any) -> str:
        """Asynchronously executes an XPath query on an XML file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to query
            xpath (str): XPath query to execute on the XML file.
            limit (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            str: JSON string with query results or an error message.
        """
        xpath: str = kwargs['xpath']
        limit: int = kwargs.get('limit', 10)
        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        navigator = XMLNavigator(workspace)
        return await navigator.xpath_query(relative_path, xpath, limit)

    @json_schema(
        'Extract a subtree from an XML file as YAML using lxml.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to update',
                'required': True
            },
            'xpath': {
                'type': 'string',
                'description': 'XPath to the root element of the subtree to extract.',
                'required': True
            },
            'output_path': {
                'type': 'string',
                'description': 'Optional path to save the extracted subtree.',
                'required': False
            }
        }
    )
    async def extract(self, **kwargs: Any) -> str:
        """Asynchronously extracts a subtree from an XML file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to extract from
            xpath (str): XPath to the root element of the subtree to extract.
            output_path (str, optional): UNC-style path to save the extracted subtree.

        Returns:
            str: JSON string with the extracted subtree or a status message.
        """
        xpath: str = kwargs['xpath']
        output_path: Optional[str] = kwargs.get('output_path')
        unc_path = kwargs.get('path', '')
        
        # Validate input path
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        # Validate output path if provided
        output_relative_path = None
        output_workspace = None
        if output_path:
            if output_path.startswith('//'):
                # UNC path for output
                error, output_workspace, output_relative_path = self.workspace_tool.validate_and_get_workspace_path(output_path)
                if error:
                    return json.dumps({'error': f'Invalid output path: {error}'})
            else:
                # Assume relative path in same workspace
                output_workspace = workspace
                output_relative_path = output_path

        navigator = XMLNavigator(workspace)
        result = await navigator.extract_subtree(relative_path, xpath, output_relative_path)
        
        return result


# Register the toolset
Toolset.register(XmlExplorerTools)