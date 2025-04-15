# Agent C Web UI - User Guide

## Overview
This guide explains how to run the Agent C web UI for users who want to work WITH Agent C. The recommended approach for users is to use the Docker-based deployment. The web UI provides a flexible interface for configuring and working with AI agents.

## Using Docker (Recommended for Users)

The easiest way to use Agent C is through the provided Docker Compose configuration.

### Prerequisites
- Docker and Docker Compose installed on your system
- Minimal knowledge of command-line operations

### Running Agent C with Docker

**On Linux/macOS:**
```bash
# Navigate to the project directory and run
./dockerfiles/start_agent_c.sh
```

**On Windows:**
```batch
# Navigate to the project directory and run
dockerfiles\start_agent_c.bat
```

**Important First Run Configuration:**

1. On first run, a configuration file will be created in:
   - Windows: `%USERPROFILE%\.agent_c\agent_c.config`
   - Mac/Linux: `~/.agent_c/agent_c.config`
2. You **must** edit this configuration file to add your API keys and set your username before Agent C will function properly
3. Run the startup script again after editing the configuration

This will start both the API server and the frontend in one command. Once started, you can access the Agent C web interface by opening `http://localhost:3000` in your browser.

### Agent Configuration Screen

The Options Panel allows you to customize your agent's behavior and capabilities:

### Settings

- **Load Persona Prompt**: Select from pre-configured agent personas that define the agent's role, personality, and expertise.
- **Customize Persona Instructions**: View and customize the instructions that shape your agent's behavior and capabilities.
- **Model Selection**: Choose the AI model to power your agent (e.g., Claude 3.7 Sonnet).
- **Extended Thinking**: Toggle to enable deeper reasoning for complex problems, with an adjustable thinking budget to control the depth of analysis.

### Available Tools

The Tools section allows you to equip your agent with capabilities:

- **Essential Tools**: Basic capabilities every agent has, including ThinkTools for reasoning and WorkspaceTools for file operations.
- **Core Tools**: Additional specialized tools that extend your agent's capabilities, such as:
  - Web search tools (DallE, DuckDuckGo, Google)
  - Information gathering (News API, RSS feeds, research tools)
  - Utility tools (Memory, Random Number Generator, etc.)

Select the tools your agent needs based on the tasks you want it to perform. Click "Equip Selected Tools" to apply your choices.

## Persona System

### What are Personas?

Personas are predefined sets of instructions that shape an agent's:
- **Identity and purpose**: What the agent is and what it's designed to do
- **Personality**: How the agent communicates and presents itself
- **Knowledge and expertise**: Specialized information the agent possesses
- **Operating guidelines**: Rules and procedures the agent follows

Personas effectively transform a general-purpose AI into a specialized assistant optimized for specific tasks.

### How Personas Work

A persona is essentially a structured prompt that provides the agent with:

1. A clear understanding of its role and limitations
2. Guidelines for how to interact with users
3. Specialized knowledge and processes relevant to its domain
4. Instructions on which tools to use and how to use them
5. Error handling procedures

The system processes this prompt when initializing the agent, creating a consistent and predictable behavior pattern.

### Creating Custom Personas

To create a custom persona, you can:

1. Use the "Customize Persona Instructions" field to directly edit an existing persona
2. Work with Bobb the Steward (a specialized persona creator agent) to craft a new persona from scratch

#### How Bobb Can Help

Bobb the Steward is a specialized agent that can help you design effective agent personas. When working with Bobb:

1. Describe the purpose and function of your desired agent
2. Answer Bobb's questions about domain knowledge and specific requirements
3. Review and provide feedback on the persona draft
4. Implement the final persona in your Agent C configuration

Bobb will provide guidance on which tools your agent will need and how to structure its instructions for optimal performance.

## Workspace Collaboration

The Docker version of Agent C maps several key directories from your local system as workspaces, allowing agents to access and manipulate files:

### Mapped Workspaces in Docker

In the Docker Compose configuration, the following folders from your local system are automatically mapped as workspaces:

- **Desktop**: Your system's desktop folder is mapped as the `Desktop` workspace
- **Downloads**: Your downloads folder is mapped as the `Downloads` workspace
- **Documents**: Your documents folder is mapped as the `Documents` workspace

These mappings allow agents to:
- Access and modify files in these locations
- Maintain persistence between sessions
- Collaborate with you through shared file access

### Workspace Collaboration Patterns

Agents can collaborate with users and other agents through workspaces by:

1. **Scratchpad Approach**: Using a designated location (like `//Desktop/.scratch`) to leave notes, track progress, and maintain state between sessions
2. **Plan Tracking**: Maintaining files that document current plans and progress
3. **File Exchange**: Reading files you place in specific locations and writing output to agreed-upon destinations

When an agent is instructed to "bring itself up to speed," it typically checks the contents of the scratchpad to understand the current state and prepare for the next request.

## Configuration

When you first run Agent C, it will create a configuration file that needs to be modified before Agent C will function properly.

### Essential Configuration

These settings are required for basic functionality:

```
# Required: OpenAI API key (you MUST set this)
OPENAI_API_KEY=your-openai-api-key-here

# Required: Set your user ID (default is "default")
CLI_CHAT_USER_ID=YourName

# Required: Zep API key for memory management
# Create a free Zep Cloud account at: https://app.getzep.com/api/auth/register
# Zep API keys are specific to a project. Visit "Project Settings" in the Zep dashboard to manage your keys.
ZEP_API_KEY=your-zep-api-key-here
```

### Optional Configuration

The configuration file includes sections for additional functionality if you have these services:

- Claude/Anthropic API key (for Claude models)
- Azure OpenAI credentials (if using Azure instead of OpenAI)
- AWS Storage credentials
- Local Zep CE configuration
- Debug settings
- API keys for various tools (SERPAPI, SEC API, Tavili, NewsAPI, etc.)

### Example Configuration

A minimal configuration to get started would look like:

```
OPENAI_API_KEY=sk-abcd1234567890abcdefg
CLI_CHAT_USER_ID=JaneDoe
ZEP_API_KEY=zep-cloud-api-key-12345abcde
```

After updating your configuration file, run the startup script again to launch Agent C with your settings.

## Troubleshooting

### Common Issues

1. **Port conflicts**: If you already have services running on ports 3000 or 5000, you may need to stop those services or modify the configuration.

2. **Docker permission issues**: On Linux systems, you might need to use `sudo` with Docker commands or add your user to the Docker group.

3. **Connectivity problems**: Make sure your firewall settings allow the required ports.

4. **Configuration issues**: If Agent C isn't working properly, check that you've correctly updated the configuration file with valid API keys.

## Advanced Configuration

For advanced configuration options or if you need to develop for Agent C, please refer to the [Developer Guide](./developer/web_ui_developer_README.md).

## Getting Help

If you encounter issues not covered in this guide, please refer to the project's issue tracker or contact the support team.