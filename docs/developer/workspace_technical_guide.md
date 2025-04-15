# Agent C Workspace Tool Guide

## Introduction

The workspace tool in Agent C provides a mechanism for AI agents to interact with file systems in a secure and controlled manner. It allows reading, writing, and listing files within designated workspace areas, enabling file-based operations while maintaining security boundaries.

## Workspace Architecture

The workspace system is designed around a hierarchy of classes:

1. **BaseWorkspace** (`base.py`) - An abstract base class that defines the interface for all workspace implementations with common methods like:
   - `ls()` - List contents of a directory
   - `read()` - Read text from a file
   - `write()` - Write text to a file
   - `read_bytes_internal()` - Read binary data from a file
   - `write_bytes()` - Write binary data to a file

2. **LocalStorageWorkspace** (`local_storage.py`) - A concrete implementation that works with local file system:
   - Maps workspace paths to actual filesystem locations
   - Implements security measures to prevent path traversal attacks
   - Provides symlink control based on environment settings

3. **LocalProjectWorkspace** (`local_storage.py`) - A specialized implementation that:
   - Automatically determines the project workspace path using a fallback strategy
   - Uses environment variables to configure its behavior
   - Supports workspace description customization

## Workspace Tool API

The `WorkspaceTools` class (`tool.py`) exposes the workspace functionality to AI agents through standard tool interfaces:

1. **ls** - Lists contents of a directory
   - Parameters: 
     - `workspace`: Name of the workspace
     - `path`: Path within the workspace to list (optional)

2. **read** - Reads contents of a text file
   - Parameters:
     - `workspace`: Name of the workspace
     - `file_path`: Path to the file within the workspace

3. **write** - Writes or appends text to a file
   - Parameters:
     - `workspace`: Name of the workspace
     - `file_path`: Path to the file within the workspace
     - `data`: Text content to write
     - `mode`: "write" (default) or "append"

## Docker Integration

Workspaces are mapped to Docker containers through volume mounts in the `docker-compose.yml` file. The following workspaces are configured by default:

1. **Documents Workspace** - Maps to the user's Documents folder
2. **Downloads Workspace** - Maps to the user's Downloads folder
3. **Desktop Workspace** - Maps to the user's Desktop folder
4. **Local Personas Workspace** - Maps to the user's personal personas folder
5. **Project Workspace** - Maps to the Agent C project root directory

### Volume Mappings in Docker

```yaml
volumes:
  - ${AGENT_C_IMAGES_PATH}:/app/images
  - ${AGENT_C_PERSONAS_PATH}:/app/personas/local
  - ${DOCUMENTS_WORKSPACE}:/app/workspaces/documents
  - ${DOWNLOADS_WORKSPACE}:/app/workspaces/downloads
  - ${DESKTOP_WORKSPACE}:/app/workspaces/desktop
  - ${PROJECT_WORKSPACE_PATH}:/app/workspaces/project
```

These mappings are configured using environment variables set in the startup scripts (`start_agent_c.sh` and `start_agent_c.bat`).

## Remapping the Project Workspace

The project workspace can be remapped to a different location in two ways:

### Method 1: Using Environment Variables

1. Set the `PROJECT_WORKSPACE_PATH` environment variable to point to your desired directory.
2. Set the `PROJECT_WORKSPACE_DESCRIPTION` environment variable to customize the workspace description.

The `LocalProjectWorkspace` class will use these variables when initializing.

```bash
# Example (Linux/macOS)
export PROJECT_WORKSPACE_PATH=/path/to/your/project
export PROJECT_WORKSPACE_DESCRIPTION="My custom project workspace"

# Example (Windows)
set PROJECT_WORKSPACE_PATH=C:\path\to\your\project
set PROJECT_WORKSPACE_DESCRIPTION="My custom project workspace"
```

### Method 2: Modifying the Start Scripts

Edit the `start_agent_c.sh` (Linux/macOS) or `start_agent_c.bat` (Windows) scripts to change the `PROJECT_WORKSPACE_PATH` variable:

```bash
# In start_agent_c.sh
export PROJECT_WORKSPACE_PATH=/path/to/your/project
```

```batch
:: In start_agent_c.bat
set PROJECT_WORKSPACE_PATH=C:\path\to\your\project
```

### Method 3: Direct Configuration in Docker Compose

You can also modify the `docker-compose.yml` file to directly specify a path:

```yaml
volumes:
  - /path/to/your/project:/app/workspaces/project
```

## Workspace Configuration

Workspaces are defined in `compose_workspaces.json`, which contains the configuration for local workspaces:

```json
{
  "local_workspaces": [
    {
      "name": "Documents",
      "workspace_path": "/app/workspaces/documents",
      "description": "A workspace mapped to the `My Documents` folder of the user."
    },
    ...
  ]
}
```

## Security Considerations

1. **Path Traversal Protection**: The `_is_path_within_workspace()` method prevents accessing files outside the workspace.

2. **Symlink Controls**: Symlinks are only allowed in development/local environments by default.

3. **Token Limits**: Files are checked against token limits to prevent overloading the AI model.

## Best Practices

1. **Use Relative Paths**: Always use paths relative to the workspace root.

2. **Explicit Workspace Names**: Always specify the workspace name explicitly when using tools.

3. **Check for Errors**: Always check for error responses when working with workspace tools.

4. **Permissions**: Be aware that Docker volume mounts may have different permissions than the host system.

## Troubleshooting

1. **File Not Found**: Ensure the path is relative to the workspace root, not the absolute path.

2. **Permission Denied**: Check that the container has appropriate permissions for the mounted volume.

3. **Workspace Not Found**: Verify that the workspace name is correctly specified and matches one in the available workspaces.

4. **File Too Large**: Files that exceed the token limit will generate an error. Consider breaking them into smaller files.