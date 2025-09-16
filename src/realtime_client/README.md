# Agent C Realtime Client SDK

A TypeScript SDK and UI component library for building real-time chat applications with Agent C's voice and text AI agents.

## Overview

The Agent C Realtime Client SDK is part of the [Agent C Framework](https://github.com/centricconsulting/agent_c_framework) and provides:

- 🎙️ **Real-time voice conversations** with AI agents using WebRTC audio streaming
- 💬 **Text chat** with streaming responses and rich formatting
- ⚛️ **React components** and hooks for rapid UI development
- 🎨 **Pre-built UI components** following the CenSuite design system
- 🔄 **Automatic reconnection** and robust error handling
- 🎭 **Avatar support** with HeyGen integration

## Prerequisites

Before working with the Realtime Client SDK, ensure you have:

1. ✅ Cloned the [Agent C Framework repository](https://github.com/centricconsulting/agent_c_framework)
2. ✅ Set up and running the Agent C API server (see main repo README)
3. ✅ Node.js 18+ installed
4. ✅ Git installed

## Installation

This project uses `pnpm` as its package manager. If you don't have it installed:

```bash
# Install pnpm globally
npm install -g pnpm

# Or using Corepack (recommended if you have Node.js 16.13+)
corepack enable
corepack prepare pnpm@latest --activate
```

## Getting Started

```bash
# Navigate to the realtime client directory
cd realtime_client

# Install dependencies
pnpm install

# Build all packages
pnpm build

# Run the demo application
pnpm dev
```

The demo app will be available at `http://localhost:3000`

## Development Commands

```bash
# Install dependencies (frozen lockfile)
pnpm install:clean

# Build all packages
pnpm build

# Run development mode (watches for changes)
pnpm dev

# Run tests
pnpm test

# Run tests with coverage
pnpm test:coverage

# Run tests in watch mode
pnpm test:watch

# Run tests with UI
pnpm test:ui

# Type checking
pnpm type-check

# Linting
pnpm lint
pnpm lint:fix

# Clean build artifacts and node_modules
pnpm clean
```

## Project Structure

This is a monorepo managed with Lerna and pnpm workspaces:

```
realtime_client/
├── packages/
│   ├── core/          # @agentc/realtime-core - Core SDK functionality
│   ├── react/         # @agentc/realtime-react - React hooks and providers
│   ├── ui/            # @agentc/realtime-ui - Pre-built UI components
│   └── demo/          # Demo application showcasing SDK usage
├── docs/              # Comprehensive documentation
├── ref/               # Reference materials and design system
├── scripts/           # Build and utility scripts
└── test/              # Shared test utilities
```

### Package Overview

#### @agentc/realtime-core
The foundation package containing:
- WebSocket client for real-time communication
- Audio streaming and processing
- Authentication and session management
- Event system and protocol handling

#### @agentc/realtime-react
React integration layer providing:
- AgentCProvider for app-wide state
- Hooks for connection, chat, audio, and UI state
- Automatic cleanup and reconnection handling

#### @agentc/realtime-ui
Production-ready UI components:
- Chat interface with message history
- Audio controls with visual feedback
- Connection status indicators
- Voice and avatar selectors

#### Demo Application
A complete example implementation showing:
- Full chat interface with voice and text
- Authentication flow
- Error handling and recovery
- Best practices for SDK usage

## Quick Example

```tsx
import { AuthManager, RealtimeClient } from '@agentc/realtime-core';
import { AgentCProvider, useChat, useAudio } from '@agentc/realtime-react';

// Initialize authentication
const authManager = new AuthManager();
await authManager.login({ username: 'user', password: 'pass' });

// Create client
const client = new RealtimeClient({
  apiUrl: authManager.getWebSocketUrl(),
  authManager
});

// Use in React
function ChatApp() {
  return (
    <AgentCProvider client={client}>
      <ChatInterface />
    </AgentCProvider>
  );
}

function ChatInterface() {
  const { messages, sendMessage } = useChat();
  const { isRecording, startRecording, stopRecording } = useAudio();
  
  // Your UI implementation
}
```

## Testing

The project uses Vitest for testing with comprehensive coverage requirements:

```bash
# Run all tests
pnpm test

# Run tests for a specific package
cd packages/core && pnpm test

# Generate coverage report (output in .scratch/coverage)
pnpm test:coverage

# Interactive test UI
pnpm test:ui
```

### Testing Standards
- Minimum 80% code coverage required
- Tests co-located with source in `__tests__` directories
- Unit tests: `.test.ts` files
- Integration tests: `.integration.test.ts` files

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Getting Started Guide](./docs/getting-started.md)
- [API Reference](./docs/api-reference/introduction.md)
- [Architecture Overview](./docs/architecture.md)
- [Testing Standards](./docs/testing/testing_standards_and_architecture.md)
- [Audio System Guide](./docs/AUDIO_QUICK_REFERENCE.md)

## API Server Integration

This SDK connects to the Agent C Realtime API. Ensure your API server is running:

```bash
# In the main agent_c_framework directory
cd api
python -m uvicorn app:app --reload
```

The API provides:
- WebSocket endpoint for real-time communication
- JWT-based authentication
- Binary audio streaming protocol
- Event-driven message system

See the [Realtime API Implementation Guide](../api/docs/realtime_api_implementation_guide.md) for protocol details.

## Browser Requirements

- Chrome 90+, Firefox 88+, Safari 14.1+, Edge 90+
- HTTPS required for microphone access
- WebRTC support for audio streaming

## Contributing

This project follows specific development standards:

1. **Package Management**: Use `pnpm` exclusively (no npm/yarn)
2. **Code Quality**: All code must pass linting and type checking
3. **Testing**: Maintain minimum 80% test coverage
4. **Documentation**: Update relevant docs with any API changes
5. **Design System**: Follow CenSuite design patterns for UI components

## Troubleshooting

### Common Issues

**pnpm: command not found**
- Install pnpm following the instructions above

**WebSocket connection fails**
- Ensure the API server is running
- Check authentication credentials
- Verify HTTPS is being used in production

**Audio not working**
- Check browser microphone permissions
- Ensure HTTPS connection
- Verify browser compatibility

**Build failures**
- Clear node_modules and reinstall: `pnpm clean && pnpm install`
- Check Node.js version (18+ required)

## Support

For issues specific to the Realtime Client SDK:
- Review the [documentation](./docs/README.md)
- Check existing issues in the [main repository](https://github.com/centricconsulting/agent_c_framework/issues)

## License

Part of the Agent C Framework. See the [main repository](https://github.com/centricconsulting/agent_c_framework) for license information.

---

*For more information about the Agent C Framework, visit the [main repository](https://github.com/centricconsulting/agent_c_framework)*