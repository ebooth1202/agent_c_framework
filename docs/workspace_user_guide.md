# Agent C User's Guide to Workspaces

## Introduction

Workspaces in Agent C provide a secure and controlled way for the AI assistant to interact with your file system. They allow me (the Agent C assistant) to read, write, and list files in designated areas of your system, making it possible to manage documents, create content, analyze code, and more.

This guide will help you understand how to effectively use workspaces when interacting with me.

## Available Workspaces

By default, Agent C provides these standard workspaces:

1. **Documents** - Maps to your computer's Documents folder
2. **Downloads** - Maps to your computer's Downloads folder
3. **Desktop** - Maps to your computer's Desktop folder
4. **Local Personas** - Maps to your personal personas folder (for saving custom personas)
5. **Project** - Maps to the Agent C source code directory

These workspaces are available for me to use when you request file operations.

## How Docker Maps Your Workspaces

Under the hood, Agent C uses Docker to create a secure environment. Your computer's folders are mapped to locations inside the Docker container using volume mounts in the docker-compose configuration:

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

## Common Workspace Operations

Here are the main operations I can perform with workspaces:

### Listing Files and Directories

To see what files exist in a workspace, you can ask me to list them:

```
Show me what files are in my Documents workspace
List the contents of my Desktop workspace
What's in the docs folder of the project workspace?
```

### Reading Files

You can ask me to read files from any workspace:

```
Read the README.md file from the project workspace
Show me the content of my resume.docx in the Documents workspace
What's in the meeting_notes.txt on my Desktop?
```

### Writing or Creating Files

You can ask me to write or create new files in any writable workspace:

```
Create a new file called notes.txt in my Documents workspace with the following content: [content]
Save this Python code to a script.py file in my Downloads workspace
Append this paragraph to my report.md file on the Desktop
```

## Tips for Effective Workspace Usage

### 1. Always Specify the Workspace

When requesting file operations, always explicitly mention which workspace you want to use. This helps avoid confusion and ensures I operate in the correct location.

**Good Example**: "List the files in my Documents workspace"
**Less Clear**: "List my files"

### 2. Use Relative Paths

When referring to files or directories, use paths that are relative to the workspace root. Absolute paths (starting with '/') aren't supported and will result in errors.

**Good Example**: "Read meeting_notes/january/minutes.txt from the Documents workspace"
**Will Not Work**: "Read /Users/myname/Documents/meeting_notes/january/minutes.txt"

### 3. Be Aware of File Size Limitations

The workspace tool has a token limit (approximately 50,000 tokens) for reading files. Very large files might be rejected to prevent overloading the AI model. Consider breaking large files into smaller chunks if you need to work with them.

### 4. Creating Directories Automatically

When writing files, the workspace tool automatically creates any necessary directories in the path. You don't need to explicitly create folders before saving files to them.

### 5. Checking for Errors

If a file operation fails, I'll explain the reason. Common errors include:
- File not found
- Path outside workspace
- File too large
- Permission issues

## Advanced Workspace Configuration

### Remapping the Project Workspace

If you want to change where the Project workspace points to, you have several options:

#### Using Environment Variables

1. Set the `PROJECT_WORKSPACE_PATH` environment variable to your desired directory.
2. Set the `PROJECT_WORKSPACE_DESCRIPTION` environment variable to customize the description.

```bash
# Example (Linux/macOS)
export PROJECT_WORKSPACE_PATH=/path/to/your/project
export PROJECT_WORKSPACE_DESCRIPTION="My custom project"

# Example (Windows)
set PROJECT_WORKSPACE_PATH=C:\path\to\your\project
set PROJECT_WORKSPACE_DESCRIPTION="My custom project"
```

#### Editing the Start Scripts

You can modify the startup scripts to permanently change the workspace path:

```bash
# In start_agent_c.sh
export PROJECT_WORKSPACE_PATH=/path/to/your/project
```

```batch
:: In start_agent_c.bat
set PROJECT_WORKSPACE_PATH=C:\path\to\your\project
```

#### Direct Configuration in Docker Compose

For advanced users, you can modify the `docker-compose.yml` file directly:

```yaml
volumes:
  - /path/to/your/project:/app/workspaces/project
```

## Troubleshooting

### Common Issues and Solutions

1. **"File not found" error**
   - Check that you're using the correct workspace name
   - Verify the file path is relative to the workspace root
   - Check for typos in the file name or path

2. **"Path is not within the workspace" error**
   - Ensure you're using relative paths, not absolute paths
   - Avoid using "../" path traversal syntax

3. **"The file exceeds the token limit" error**
   - The file is too large for the AI to process
   - Break the file into smaller chunks or extract only the relevant portions

4. **"This workspace is read-only" error**
   - Some workspaces may be configured as read-only for security
   - Try writing to another workspace instead

## Best Practices

1. **Organize your files logically** - Keep related files in the same directory structure to make them easier to work with.

2. **Use descriptive file names** - Clear, descriptive file names make it easier to reference files in conversations.

3. **Specify file formats explicitly** - When creating new files, specify the file extension to ensure proper formatting and handling.

4. **Use the Desktop workspace for temporary files** - The Desktop workspace is ideal for quick, temporary files you want to see immediately.

5. **Use the Documents workspace for persistent files** - Store important documents you want to keep in the Documents workspace.

6. **Save all AI-generated personas to the Local Personas workspace** - Keep your custom personas organized in the designated workspace.

## Conclusion

Workspaces provide a powerful way for you to interact with files through Agent C. By understanding how to effectively use workspaces and following these best practices, you can leverage the full potential of file-based operations to enhance your productivity.

Remember to explicitly refer to workspaces by name when making requests to ensure I understand exactly where you want me to perform operations.