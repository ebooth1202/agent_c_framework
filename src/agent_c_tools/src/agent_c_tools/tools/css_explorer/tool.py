from typing import Any, Dict, List, Optional


from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema

from .css_navigator import CssNavigator
from agent_c_tools.tools.workspace.tool import WorkspaceTools


class CssExplorerTools(Toolset):
    """
    CssExplorerTools provides methods for working with CSS files in workspaces.
    It enables efficient navigation and manipulation of large CSS files with component-based structure.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(name='css', **kwargs)
        self.workspace_tool: Optional[WorkspaceTools] = None

    async def post_init(self):
        self.workspace_tool = self.tool_chest.active_tools['workspace']

    @json_schema(
        'Obtain an overview of the CSS file structure and components. In a token efficient manner',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the CSS file',
                'required': True
            }
        }
    )
    async def overview(self, **kwargs: Any) -> str:
        """Asynchronously scans a CSS file to identify components and their styles.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the CSS file

        Returns:
            str: Markdown overview of the CSS file structure.
        """
        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return f"Error: {error}"

        navigator = CssNavigator(workspace)
        return await navigator.scan_css_file(relative_path)

    @json_schema(
        'Get detailed information about a specific component styles from a CSS file.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the CSS file',
                'required': True
            },
            'component': {
                'type': 'string',
                'description': 'Name of the component to extract styles for',
                'required': True
            }
        }
    )
    async def get_component(self, **kwargs: Any) -> str:
        """Asynchronously retrieves styles for a specific component from a CSS file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the CSS file
            component (str): Name of the component to extract styles for

        Returns:
            str: Markdown overview of the component styles.
        """
        unc_path = kwargs.get('path', '')
        component = kwargs.get('component', '')
        
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return f"Error: {error}"

        navigator = CssNavigator(workspace)
        return await navigator.get_component_styles(relative_path, component)

    @json_schema(
        'Update a specific CSS class within a component section.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the CSS file',
                'required': True
            },
            'component': {
                'type': 'string',
                'description': 'Name of the component containing the style',
                'required': True
            },
            'class_name': {
                'type': 'string',
                'description': 'Name of the CSS class to update (selector)',
                'required': True
            },
            'new_style': {
                'type': 'string',
                'description': 'New style definition (including the selector and braces)',
                'required': True
            }
        }
    )
    async def update_style(self, **kwargs: Any) -> str:
        """Asynchronously updates a specific CSS style without rewriting the entire file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the CSS file
            component (str): Name of the component containing the style
            class_name (str): Name of the CSS class to update (selector)
            new_style (str): New style definition (including the selector and braces)

        Returns:
            str: Markdown report of the update operation.
        """
        unc_path = kwargs.get('path', '')
        component = kwargs.get('component', '')
        class_name = kwargs.get('class_name', '')
        new_style = kwargs.get('new_style', '')
        
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return f"Error: {error}"

        navigator = CssNavigator(workspace)
        return await navigator.update_style(relative_path, component, class_name, new_style)
        
    @json_schema(
        'Get the raw CSS source for a component, including its header comment and all styles.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the CSS file',
                'required': True
            },
            'component': {
                'type': 'string',
                'description': 'Name of the component to extract source for',
                'required': True
            }
        }
    )
    async def get_component_source(self, **kwargs: Any) -> str:
        """Asynchronously retrieves raw CSS source for a specific component from a CSS file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the CSS file
            component (str): Name of the component to extract source for

        Returns:
            str: Raw CSS source code for the component including header comment and all styles
        """
        unc_path = kwargs.get('path', '')
        component = kwargs.get('component', '')
        
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return f"Error: {error}"

        navigator = CssNavigator(workspace)
        return await navigator.get_component_source(relative_path, component)

    @json_schema(
        'Get the raw CSS source for a specific style within a component, including its preceding comment.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the CSS file',
                'required': True
            },
            'component': {
                'type': 'string',
                'description': 'Name of the component containing the style',
                'required': True
            },
            'class_name': {
                'type': 'string',
                'description': 'Name of the CSS class to get source for (selector)',
                'required': True
            }
        }
    )
    async def get_style_source(self, **kwargs: Any) -> str:
        """Asynchronously retrieves raw CSS source for a specific style from a CSS file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the CSS file
            component (str): Name of the component containing the style
            class_name (str): Name of the CSS class to get source for (selector)

        Returns:
            str: Raw CSS source code for the style including its preceding comment
        """
        unc_path = kwargs.get('path', '')
        component = kwargs.get('component', '')
        class_name = kwargs.get('class_name', '')
        
        error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
        if error:
            return f"Error: {error}"

        navigator = CssNavigator(workspace)
        return await navigator.get_style_source(relative_path, component, class_name)


# Register the toolset
Toolset.register(CssExplorerTools)