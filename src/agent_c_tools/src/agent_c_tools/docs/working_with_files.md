# File-Based Tools Best Practices

A comprehensive guide for creating reliable, maintainable file operation tools for Agent C.

## JSON Schema Best Practices

### Read Operations Pattern

```python
@json_schema(
    description="Read and process a file from workspace",
    params={
        "workspace": {
            "type": "string",
            "description": "Workspace name",
            "required": True
        },
        "input_path": {
            "type": "string",
            "description": "Relative path within workspace (e.g., 'reports/analysis.md')",
            "required": True
        }
    }
)
```

### Write Operations Pattern

```python
@json_schema(
    description="Process file and write output",
    params={
        "input_workspace": {
            "type": "string",
            "description": "Source workspace name",
            "required": True
        },
        "input_path": {
            "type": "string",
            "description": "Source file path within input workspace",
            "required": True
        },
        "output_workspace": {
            "type": "string",
            "description": "Output workspace name (defaults to input_workspace if not specified)",
            "required": False
        },
        "output_path": {
            "type": "string",
            "description": "Output file path within output workspace",
            "required": True
        }
    }
)
```

### Parameter Naming Conventions

**Consistent naming across all tools:**
- `workspace` - for single workspace operations (reads)
- `input_workspace` / `output_workspace` - for cross-workspace operations (writes)
- `input_path` / `output_path` - for file paths within workspaces

## Tool Setup Pattern

### Standard Tool Class Structure

```python
import json
import logging
import yaml
from typing import Optional

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from ... import WorkspaceTools
from ...helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path, has_file_extension
from ...helpers.validation_helper import validate_required_fields

logger = logging.getLogger(__name__)

class YourFileTools(Toolset):
    """Template for file-based tools."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name="your_file_tools")
        self.workspace_tool: Optional[WorkspaceTools] = None
        
    async def post_init(self):
        self.workspace_tool = self.tool_chest.available_tools.get("WorkspaceTools")
    
    def _format_response(self, success: bool, message: str = None, **additional_data) -> str:
        """Return consistent YAML response format."""
        response = {"success": success}
        if message:
            response["message"] = message
        response.update(additional_data)
        return yaml.dump(response, default_flow_style=False, sort_keys=False, allow_unicode=True)
```

## Input Validation Pattern

### Standard Validation Approach

```python
async def your_method(self, **kwargs) -> str:
    # Validate required fields
    success, message = validate_required_fields(kwargs=kwargs, required_fields=['workspace', 'input_path'])
    if not success:
        return self._format_response(False, message)
    
    # Extract parameters
    workspace = kwargs.get('workspace')
    input_path = kwargs.get('input_path')
    
    # Create UNC path
    input_unc_path = create_unc_path(workspace, input_path)
```

### Write Operation Validation

```python
async def write_method(self, **kwargs) -> str:
    # Validate required fields
    success, message = validate_required_fields(kwargs=kwargs, required_fields=['input_workspace', 'input_path', 'output_path'])
    if not success:
        return self._format_response(False, message)
    
    # Extract parameters with workspace defaulting
    input_workspace = kwargs.get('input_workspace')
    output_workspace = kwargs.get('output_workspace', input_workspace)  # Default to input_workspace
    input_path = kwargs.get('input_path')
    output_path = kwargs.get('output_path')
    
    # Create UNC paths
    input_unc_path = create_unc_path(input_workspace, input_path)
    output_unc_path = create_unc_path(output_workspace, output_path)
```

## File and Directory Operations

### Directory Listing and Validation

```python
# Check if directory exists and list contents
ls_result = await self.workspace_tool.ls(path=input_unc_path)
ls_data = json.loads(ls_result)

if 'error' in ls_data:
    return self._format_response(False, f"Input path '{input_path}' is not accessible: {ls_data['error']}")

# Process directory contents
for item in ls_data.get('items', []):
    if item['type'] == 'file' and item['name'].endswith('.md'):
        # Process markdown files
        pass
    elif item['type'] == 'directory':
        # Process subdirectories
        subdir_unc_path = f"{input_unc_path}/{item['name']}"
```

### File Extension Validation

```python
# Validate file type before processing
if not has_file_extension(input_path, ['.md', '.markdown']):
    return self._format_response(False, f"File '{input_path}' is not a markdown file")
```

## File Reading

### Text File Reading Pattern

```python
async def read_text_file(self, workspace: str, input_path: str) -> str:
    """Read a text file from workspace."""
    try:
        input_unc_path = create_unc_path(workspace, input_path)
        
        # Read file content
        file_content = await self.workspace_tool.read(path=input_unc_path)
        
        # Check for errors
        if file_content.startswith('{"error":'):
            error_data = json.loads(file_content)
            raise ValueError(f"Error reading file: {error_data['error']}")
        
        return file_content
        
    except Exception as e:
        return self._format_response(False, f"Failed to read file '{input_path}': {str(e)}")
```

### Complete Read Method Example

```python
@json_schema(
    description="Read and analyze a file",
    params={
        "workspace": {
            "type": "string",
            "description": "Workspace name",
            "required": True
        },
        "input_path": {
            "type": "string",
            "description": "File path within workspace",
            "required": True
        }
    }
)
async def analyze_file(self, **kwargs) -> str:
    """Analyze a file and return insights."""
    try:
        # Validate required fields
        success, message = validate_required_fields(kwargs=kwargs, required_fields=['workspace', 'input_path'])
        if not success:
            return self._format_response(False, message)
        
        # Extract parameters
        workspace = kwargs.get('workspace')
        input_path = kwargs.get('input_path')
        
        # Create UNC path
        input_unc_path = create_unc_path(workspace, input_path)
        
        # Read file
        file_content = await self.workspace_tool.read(path=input_unc_path)
        if file_content.startswith('{"error":'):
            error_data = json.loads(file_content)
            return self._format_response(False, f"Error reading file: {error_data['error']}")
        
        # Process content (your logic here)
        analysis_result = f"File has {len(file_content)} characters"
        
        return self._format_response(True, "File analyzed successfully", 
                                   file_path=input_unc_path, 
                                   analysis=analysis_result)
        
    except Exception as e:
        logger.exception("Error analyzing file")
        return self._format_response(False, f"Error analyzing file: {str(e)}")
```

## File Writing - Text

### Standard Text Writing Pattern

```python
async def write_text_file(self, input_workspace: str, input_path: str, 
                         output_workspace: str, output_path: str, content: str) -> str:
    """Write text content to a file."""
    try:
        # Ensure proper file extension
        output_path = ensure_file_extension(output_path, 'txt')
        output_unc_path = create_unc_path(output_workspace, output_path)
        
        # Write file
        write_result = await self.workspace_tool.write(
            path=output_unc_path,
            data=content,
            mode="write"  # "write" or "append"
        )
        
        # Check for write errors
        write_data = json.loads(write_result)
        if 'error' in write_data:
            return self._format_response(False, f"Failed to write file: {write_data['error']}")
        
        return self._format_response(True, f"Successfully wrote file to {output_path}",
                                   file_path=output_unc_path)
        
    except Exception as e:
        return self._format_response(False, f"Error writing file: {str(e)}")
```

### Complete Write Method Example

```python
@json_schema(
    description="Process file and save result",
    params={
        "input_workspace": {
            "type": "string",
            "description": "Source workspace name",
            "required": True
        },
        "input_path": {
            "type": "string",
            "description": "Source file path within input workspace",
            "required": True
        },
        "output_workspace": {
            "type": "string",
            "description": "Output workspace name (defaults to input_workspace if not specified)",
            "required": False
        },
        "output_path": {
            "type": "string",
            "description": "Output file path within output workspace",
            "required": True
        }
    }
)
async def process_and_save(self, **kwargs) -> str:
    """Process a file and save the result."""
    try:
        # Validate required fields
        success, message = validate_required_fields(kwargs=kwargs, required_fields=['input_workspace', 'input_path', 'output_path'])
        if not success:
            return self._format_response(False, message)
        
        # Extract parameters with workspace defaulting
        input_workspace = kwargs.get('input_workspace')
        output_workspace = kwargs.get('output_workspace', input_workspace)
        input_path = kwargs.get('input_path')
        output_path = kwargs.get('output_path')
        
        # Create UNC paths
        input_unc_path = create_unc_path(input_workspace, input_path)
        output_unc_path = create_unc_path(output_workspace, output_path)
        
        # Read input file
        file_content = await self.workspace_tool.read(path=input_unc_path)
        if file_content.startswith('{"error":'):
            error_data = json.loads(file_content)
            return self._format_response(False, f"Error reading file: {error_data['error']}")
        
        # Process content (your logic here)
        processed_content = file_content.upper()  # Example processing
        
        # Ensure proper file extension
        output_path = ensure_file_extension(output_path, 'txt')
        output_unc_path = create_unc_path(output_workspace, output_path)
        
        # Write processed content
        write_result = await self.workspace_tool.write(
            path=output_unc_path,
            data=processed_content,
            mode="write"
        )
        
        # Check for write errors
        write_data = json.loads(write_result)
        if 'error' in write_data:
            return self._format_response(False, f"Failed to write file: {write_data['error']}")
        
        return self._format_response(True, "File processed and saved successfully",
                                   input_file=input_unc_path,
                                   output_file=output_unc_path,
                                   input_workspace=input_workspace,
                                   output_workspace=output_workspace)
        
    except Exception as e:
        logger.exception("Error processing and saving file")
        return self._format_response(False, f"Error processing file: {str(e)}")
```

## File Writing - Binary

### Binary File Writing Pattern

```python
async def write_binary_file(self, input_workspace: str, output_workspace: str, 
                           output_path: str, binary_data: bytes) -> str:
    """Write binary content to a file."""
    try:
        # Ensure proper file extension
        output_path = ensure_file_extension(output_path, 'docx')
        output_unc_path = create_unc_path(output_workspace, output_path)
        
        # Use internal binary write method
        write_result = await self.workspace_tool.internal_write_bytes(
            path=output_unc_path,
            data=binary_data,
            mode="write"
        )
        
        # Check for write errors
        write_data = json.loads(write_result)
        if 'error' in write_data:
            return self._format_response(False, f"Failed to write binary file: {write_data['error']}")
        
        return self._format_response(True, f"Successfully wrote binary file to {output_path}",
                                   file_path=output_unc_path)
        
    except Exception as e:
        return self._format_response(False, f"Error writing binary file: {str(e)}")
```

### Complete Binary Write Example

```python
@json_schema(
    description="Convert markdown to DOCX format",
    params={
        "input_workspace": {
            "type": "string",
            "description": "Source workspace name",
            "required": True
        },
        "input_path": {
            "type": "string",
            "description": "Source markdown file path",
            "required": True
        },
        "output_workspace": {
            "type": "string",
            "description": "Output workspace name (defaults to input_workspace if not specified)",
            "required": False
        },
        "output_path": {
            "type": "string",
            "description": "Output DOCX file path",
            "required": True
        }
    }
)
async def markdown_to_docx(self, **kwargs) -> str:
    """Convert markdown to DOCX format."""
    try:
        # Validate required fields
        success, message = validate_required_fields(kwargs=kwargs, required_fields=['input_workspace', 'input_path', 'output_path'])
        if not success:
            return self._format_response(False, message)
        
        # Extract parameters with workspace defaulting
        input_workspace = kwargs.get('input_workspace')
        output_workspace = kwargs.get('output_workspace', input_workspace)
        input_path = kwargs.get('input_path')
        output_path = kwargs.get('output_path')
        
        # Validate input file type
        if not has_file_extension(input_path, ['.md', '.markdown']):
            return self._format_response(False, f"Input file '{input_path}' is not a markdown file")
        
        # Create UNC paths
        input_unc_path = create_unc_path(input_workspace, input_path)
        
        # Read markdown file
        file_content = await self.workspace_tool.read(path=input_unc_path)
        if file_content.startswith('{"error":'):
            error_data = json.loads(file_content)
            return self._format_response(False, f"Error reading file: {error_data['error']}")
        
        # Convert to DOCX bytes (your conversion logic here)
        docx_content_bytes = await self.convert_markdown_to_docx_bytes(file_content)
        
        # Ensure proper file extension and create output path
        output_path = ensure_file_extension(output_path, 'docx')
        output_unc_path = create_unc_path(output_workspace, output_path)
        
        # Write binary content
        write_result = await self.workspace_tool.internal_write_bytes(
            path=output_unc_path,
            data=docx_content_bytes,
            mode="write"
        )
        
        # Check for write errors
        write_data = json.loads(write_result)
        if 'error' in write_data:
            return self._format_response(False, f"Failed to write DOCX file: {write_data['error']}")
        
        return self._format_response(True, "Successfully converted markdown to DOCX",
                                   input_file=input_unc_path,
                                   output_file=output_unc_path,
                                   input_workspace=input_workspace,
                                   output_workspace=output_workspace)
        
    except Exception as e:
        logger.exception("Error converting markdown to DOCX")
        return self._format_response(False, f"Error converting to DOCX: {str(e)}")
```

## Getting OS Path for Media Events

### OS Path and Media Event Pattern

```python
async def your_file_operation_with_media(self, **kwargs) -> str:
    """Perform file operation and raise media event."""
    try:
        # ... your file operations ...
        
        # Get OS file system path for media events
        file_system_path = os_file_system_path(self.workspace_tool, output_unc_path)
        
        # Raise media event
        await self._raise_render_media(
            sent_by_class=self.__class__.__name__,
            sent_by_function='your_file_operation_with_media',
            content_type="text/html",
            content=f"<p>File created: <a href='file://{file_system_path}'>{output_path}</a></p>"
        )
        
        return self._format_response(True, "File operation completed successfully",
                                   file_path=output_unc_path,
                                   os_path=file_system_path)
        
    except Exception as e:
        return self._format_response(False, str(e))
```

## Complete Tool Template

```python
import json
import logging
import yaml
from typing import Optional

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from ... import WorkspaceTools
from ...helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path, has_file_extension
from ...helpers.validation_helper import validate_required_fields

logger = logging.getLogger(__name__)

class YourFileTools(Toolset):
    """Template for file-based tools following best practices."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs, name="your_file_tools")
        self.workspace_tool: Optional[WorkspaceTools] = None
        
    async def post_init(self):
        self.workspace_tool = self.tool_chest.available_tools.get("WorkspaceTools")
    
    def _format_response(self, success: bool, message: str = None, **additional_data) -> str:
        """Return consistent YAML response format."""
        response = {"success": success}
        if message:
            response["message"] = message
        response.update(additional_data)
        return yaml.dump(response, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    @json_schema(
        description="Process a file and create output",
        params={
            "input_workspace": {
                "type": "string",
                "description": "Source workspace name",
                "required": True
            },
            "input_path": {
                "type": "string",
                "description": "Source file path within input workspace",
                "required": True
            },
            "output_workspace": {
                "type": "string",
                "description": "Output workspace name (defaults to input_workspace if not specified)",
                "required": False
            },
            "output_path": {
                "type": "string",
                "description": "Output file path within output workspace",
                "required": True
            }
        }
    )
    async def process_file(self, **kwargs) -> str:
        """Process a file and create output following best practices."""
        try:
            # Validate required fields
            success, message = validate_required_fields(kwargs=kwargs, required_fields=['input_workspace', 'input_path', 'output_path'])
            if not success:
                return self._format_response(False, message)
            
            # Extract parameters with workspace defaulting
            input_workspace = kwargs.get('input_workspace')
            output_workspace = kwargs.get('output_workspace', input_workspace)
            input_path = kwargs.get('input_path')
            output_path = kwargs.get('output_path')
            
            # Create UNC paths
            input_unc_path = create_unc_path(input_workspace, input_path)
            
            # Read file
            file_content = await self.workspace_tool.read(path=input_unc_path)
            if file_content.startswith('{"error":'):
                error_data = json.loads(file_content)
                return self._format_response(False, f"Error reading file: {error_data['error']}")
            
            # Process content (your logic here)
            processed_content = file_content.upper()  # Example processing
            
            # Prepare output
            output_path = ensure_file_extension(output_path, 'txt')
            output_unc_path = create_unc_path(output_workspace, output_path)
            
            # Write processed content
            write_result = await self.workspace_tool.write(
                path=output_unc_path,
                data=processed_content,
                mode="write"
            )
            
            # Check for write errors
            write_data = json.loads(write_result)
            if 'error' in write_data:
                return self._format_response(False, f"Failed to write file: {write_data['error']}")
            
            # Get OS path and raise media event
            file_system_path = os_file_system_path(self.workspace_tool, output_unc_path)
            await self._raise_render_media(
                sent_by_class=self.__class__.__name__,
                sent_by_function='process_file',
                content_type="text/html",
                content=f"<p>Processed file saved: <a href='file://{file_system_path}'>{output_path}</a></p>"
            )
            
            return self._format_response(True, "File processed successfully",
                                       input_file=input_unc_path,
                                       output_file=output_unc_path,
                                       input_workspace=input_workspace,
                                       output_workspace=output_workspace,
                                       os_path=file_system_path)
            
        except Exception as e:
            logger.exception("Error processing file")
            return self._format_response(False, f"Error processing file: {str(e)}")

# Register the toolset
Toolset.register(YourFileTools, required_tools=['WorkspaceTools'])
```

## Summary

**Key Patterns:**
- **Read operations:** `workspace` + `input_path`
- **Write operations:** `input_workspace` + `output_workspace` (defaults to input_workspace) + `input_path` + `output_path`
- **Response format:** Consistent YAML using `_format_response()` helper
- **Validation:** Direct import and tuple return pattern `validate_required_fields()`
- **Path handling:** Always use helper functions with consistent `*_unc_path` variable naming
- **Error handling:** Consistent exception logging and response formatting
- **Imports:** Use relative imports wherever possible