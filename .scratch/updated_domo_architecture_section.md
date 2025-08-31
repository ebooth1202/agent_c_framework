# SDK Architecture Components (CURRENT REALITY)

Agent C is a production-ready Python framework for building sophisticated AI agents with advanced coordination capabilities. The architecture is built on proven technologies with clear separation of concerns.

## Core Architecture Overview

### Technology Foundation
- **Backend Runtime**: Python 3.12+ with AsyncIO for concurrent operations
- **Web Framework**: FastAPI providing RESTful API with automatic documentation
- **Frontend Interface**: React 18+ with TypeScript and Vite build system
- **Data Layer**: Redis for session management and state persistence
- **Deployment**: Docker containerization with multi-service orchestration
- **Testing**: pytest (backend) and Vitest (frontend) with comprehensive coverage

### Agent Runtime Model
- **Stateless Operations**: No persistent state in runtime, all context provided per-call
- **Event-Driven Communication**: Non-blocking async operations with event streaming
- **Vendor Agnostic**: Support for Anthropic Claude, OpenAI, Azure OpenAI, Google Gemini
- **Tool Ecosystem**: Interconnected tools with dependency injection and token optimization

## Production Components

### 1. agent_c_core (Agent Runtime Engine)
**Technology**: Python with AsyncIO
**Responsibility**: Core agent orchestration and execution
**Key Capabilities**:
- Agent prompt processing and response generation  
- Tool execution coordination and result management
- Multi-vendor AI model integration with fallback handling
- Event stream management for real-time user interaction
- Context window management and token optimization

### 2. agent_c_tools (Agent Tool Ecosystem)
**Technology**: Python with specialized libraries (Playwright, etc.)
**Responsibility**: Comprehensive toolset for agent capabilities
**Key Capabilities**:
- **Workspace Management**: Multi-backend support (Local, AWS S3, Azure Blob)
- **Web Integration**: Content scraping with readability conversion to markdown
- **Multi-Agent Coordination**: Clone delegation, team management, assistant agents
- **Planning System**: Hierarchical task management with completion signoff
- **File Operations**: Advanced file manipulation with grep, tree, code inspection
- **Metadata Management**: Structured data storage for agent coordination

### 3. agent_c_api (Web Service Layer)
**Technology**: FastAPI with Uvicorn server
**Responsibility**: HTTP API for agent interactions and management
**Key Capabilities**:
- RESTful endpoints for agent chat and configuration
- Real-time WebSocket connections for streaming responses
- File upload and workspace integration
- User authentication and session management
- Agent configuration and deployment management
- Automatic OpenAPI documentation generation

### 4. agent_c_react_client (Web User Interface)
**Technology**: React, TypeScript, Vite, Tailwind CSS, Radix UI
**Responsibility**: Modern web interface for agent interactions
**Key Capabilities**:
- Real-time chat interface with streaming responses
- Agent selection and configuration management
- Workspace and file management interface
- Planning tool integration with visual task tracking
- Responsive design with accessibility features
- Dark/light theme support with user preferences

## Development and Deployment Architecture

### Python Development Environment
- **Package Management**: pip with setup.py and namespace packages
- **Virtual Environment**: Python venv or conda for dependency isolation
- **Development Mode**: Editable installs with `pip install -e .`
- **Code Structure**: Modular namespace packages for extensibility

### Testing Architecture
```
test/
├── Unit/                    # Isolated unit tests
│   └── agent_c_tools/      
│       └── tools/          # Tool-specific unit tests
└── Integration/            # Integration tests
    └── agent_c_tools/      
        └── tools/          # End-to-end tool testing
```

**Backend Testing**: 
- Framework: pytest with asyncio support
- Execution: `pytest -m unit` or `pytest -m integration`
- Coverage: Built-in coverage reporting
- Mocking: pytest-mock for external service isolation

**Frontend Testing**:
- Framework: Vitest with React Testing Library
- Execution: `npm run test` (frontend directory only)
- Coverage: `npm run test:coverage`
- Components: Jest DOM assertions with user event simulation

### Docker Deployment Architecture
```
docker-compose.yml
├── redis         # Session and state persistence
├── api           # FastAPI application container
└── frontend      # React development server container
```

**Production Deployment**:
- Multi-stage Docker builds for optimization
- Environment-based configuration injection
- Volume mounts for workspace and configuration persistence
- Health checks and restart policies
- Network isolation with service discovery

## Agent Coordination Architecture

### Multi-Agent Patterns
1. **Clone Delegation**: Prime agents spawn focused execution clones
2. **Team Coordination**: Supervisor agents manage specialist teams  
3. **Assistant Integration**: Non-interactive specialized agents for specific tasks
4. **Sequential Orchestration**: Coordinated workflows across multiple agents

### Planning System Integration
- **Hierarchical Tasks**: Parent/child task relationships with dependency tracking
- **Completion Signoff**: Required validation gates for quality assurance
- **Recovery Protocols**: Resumable workflows after failures or context exhaustion
- **Progress Tracking**: Real-time status with completion reporting

### Context Management Strategy
- **Progressive Summarization**: Key insight extraction to prevent context burnout
- **Metadata Preservation**: Valuable outputs stored for cross-agent access
- **Workspace Integration**: Persistent storage for large content and results
- **Token Optimization**: YAML serialization and content compression

## Integration and Extension Points

### Tool Development Framework
- **Dependency Declaration**: Tools can require other tools as dependencies
- **Direct User Communication**: Media and large content bypass agent context
- **Workspace Abstraction**: Pluggable storage backends (Local, S3, Azure)
- **Event Integration**: Tools can emit events for user notification

### Agent Configuration System
- **YAML-Based Definitions**: Human-readable agent configurations
- **Tool Assignment**: Flexible tool combinations per agent
- **Model Selection**: Per-agent AI model and parameter configuration
- **Category System**: Agent grouping and discovery mechanisms

### API Extension Architecture
- **Plugin System**: Modular API extensions through FastAPI routers
- **Middleware Integration**: Request/response processing customization
- **Authentication Hooks**: Pluggable authentication and authorization
- **Event Publishing**: WebSocket and HTTP callback integration

## Performance and Scaling Characteristics

### Runtime Performance
- **Async Operations**: Non-blocking I/O for concurrent request handling
- **Connection Pooling**: Efficient database and external service connections
- **Caching Strategy**: Redis-based caching for frequently accessed data
- **Memory Management**: Context window monitoring and proactive management

### Horizontal Scaling
- **Stateless Design**: API servers can be load-balanced without session affinity
- **Database Separation**: Redis can be clustered independently
- **Container Orchestration**: Docker services can be scaled independently
- **Workspace Abstraction**: Cloud storage backends support distributed deployment

## Security Architecture

### Authentication and Authorization
- **User Management**: Built-in user registration and authentication
- **Session Security**: Secure session handling with Redis persistence
- **API Security**: Request validation and rate limiting
- **Workspace Isolation**: User-specific workspace access controls

### Data Protection
- **Configuration Security**: Sensitive API keys stored in secure configuration
- **File System Security**: Workspace access restricted to authorized users
- **Network Security**: HTTPS/TLS encryption for all communications
- **Container Security**: Minimal attack surface through Alpine-based images

This architecture represents the current production state of the Agent C Framework, providing a robust foundation for building sophisticated multi-agent systems with real-world enterprise capabilities.