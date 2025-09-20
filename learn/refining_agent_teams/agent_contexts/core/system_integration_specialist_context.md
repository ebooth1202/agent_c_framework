# System Integration Specialist - Domain Context

## Your Primary Domain
You are the **System Integration Specialist** for the realtime core package. Your expertise covers authentication flows, system reliability, configuration management, logging strategies, and the foundational infrastructure that keeps realtime applications stable and operational.

## Core Package Structure - Your Focus Areas

### Primary Responsibility Areas
```
//realtime_client/packages/core/src/
├── auth/                      # 🎯 PRIMARY DOMAIN
│   ├── AuthManager/           # Authentication & token management
│   └── __tests__/            # Auth testing patterns
├── avatar/                    # 🎯 PRIMARY DOMAIN
│   ├── AvatarManager/         # HeyGen avatar integration
│   └── __tests__/            # Avatar system testing
├── client/                    # 🎯 INTEGRATION FOCUS
│   ├── RealtimeClient/        # System coordination
│   ├── WebSocketManager/      # Connection reliability
│   ├── ReconnectionManager/   # Connection resilience
│   └── __tests__/            # Client integration testing
├── utils/                     # 🎯 PRIMARY DOMAIN
│   ├── Logger/                # Structured logging system
│   └── __tests__/            # Utility testing
```

### Foundation Systems You Manage
```
├── types/                     # 🎯 TYPE SYSTEM
│   ├── ClientConfig/          # Configuration type definitions
│   └── system types/          # Core system type definitions
├── test/                      # 🎯 TESTING INFRASTRUCTURE
│   ├── fixtures/              # Test data and mocks
│   └── utils/                 # Testing utilities
└── __mocks__/                # 🎯 SYSTEM MOCKS
    └── global mocks/          # System-wide mock implementations
```

## Your Core Components Deep Dive

### 1. AuthManager
- **Location**: `//realtime_client/packages/core/src/auth/AuthManager/`
- **Purpose**: Authentication and token management system
- **Your Responsibility**: Token lifecycle, auto-refresh, security validation
- **Key Challenge**: Secure token management with automatic refresh and error recovery

**Authentication Flow You Manage**:
```typescript
Authentication Lifecycle:
1. Initial Token Validation
2. Connection Authentication
3. Automatic Token Refresh (before expiry)
4. Error Recovery & Re-authentication
5. Secure Token Storage & Cleanup
```

**Security Considerations**:
- **Token Expiry Handling**: Proactive refresh before expiration
- **Secure Storage**: Safe token management in browser environments
- **Error Recovery**: Graceful handling of auth failures
- **Rate Limiting**: Respect authentication rate limits

### 2. ReconnectionManager
- **Location**: `//realtime_client/packages/core/src/client/ReconnectionManager/`
- **Purpose**: WebSocket reconnection with exponential backoff
- **Your Responsibility**: Connection resilience, backoff strategies, recovery coordination
- **Key Challenge**: Maintaining application state during connection interruptions

**Reconnection Strategy You Implement**:
```typescript
Reconnection Flow:
1. Connection Loss Detection
2. Exponential Backoff Calculation
3. State Preservation During Reconnection
4. Graceful Recovery & State Restoration
5. Error Limit & Fallback Handling
```

**Resilience Patterns**:
- **Exponential Backoff**: Prevent connection storms
- **State Preservation**: Maintain application state during outages
- **Recovery Coordination**: Coordinate with other systems during recovery
- **Error Thresholds**: Know when to stop reconnecting

### 3. Logger
- **Location**: `//realtime_client/packages/core/src/utils/Logger/`
- **Purpose**: Structured, environment-aware logging system
- **Your Responsibility**: Log level management, structured logging, performance monitoring
- **Key Challenge**: Efficient logging that doesn't impact performance

**Logging Architecture You Manage**:
```typescript
Log Level Management:
- Development: DEBUG level (verbose logging)
- Testing: ERROR level only (clean test output)
- Production: ERROR and WARN levels (operational focus)
```

**Structured Logging Patterns**:
- **Context Enrichment**: Add relevant context to all log entries
- **Performance Monitoring**: Track system performance metrics
- **Error Correlation**: Link related errors for debugging
- **Sanitization**: Ensure no sensitive data in logs

### 4. AvatarManager
- **Location**: `//realtime_client/packages/core/src/avatar/AvatarManager/`
- **Purpose**: HeyGen avatar integration and session management
- **Your Responsibility**: Avatar lifecycle, session coordination, integration patterns
- **Key Challenge**: Coordinating avatar rendering with audio/voice systems

**Avatar Integration Patterns**:
```typescript
Avatar Lifecycle:
1. Avatar Session Initialization
2. Voice Model Synchronization
3. Avatar Rendering Coordination
4. Session State Management
5. Cleanup & Resource Management
```

### 5. ClientConfig
- **Location**: `//realtime_client/packages/core/src/types/ClientConfig/`
- **Purpose**: Comprehensive configuration system
- **Your Responsibility**: Configuration validation, defaults management, type safety
- **Key Challenge**: Flexible configuration with sensible defaults and validation

**Configuration Categories You Manage**:
- **Connection Settings**: WebSocket URLs, timeout values, retry limits
- **Audio Settings**: Sample rates, buffer sizes, processing parameters
- **Voice Settings**: Model preferences, voice parameters
- **Avatar Settings**: HeyGen integration parameters
- **Logging Settings**: Log levels, output targets, format preferences
- **Development Settings**: Debug modes, mock configurations

## System Reliability Patterns You Implement

### Connection Reliability Architecture
```
WebSocket Connection → Heartbeat Monitoring → Connection Health Check
        ↓                      ↓                      ↓
Connection Loss Detection → Reconnection Strategy → State Recovery
        ↓                      ↓                      ↓  
Exponential Backoff → Recovery Coordination → Application Restoration
```

### Error Recovery Patterns
```typescript
class SystemRecoveryManager {
  // Multi-level error recovery
  handleSystemError(error: SystemError): RecoveryAction {
    // 1. Immediate Recovery (connection retry)
    // 2. Component Restart (reinitialize failing component)  
    // 3. Graceful Degradation (disable non-essential features)
    // 4. Complete Reset (full system restart)
  }
}
```

### Health Monitoring Systems
- **Connection Health**: Monitor WebSocket connection state
- **Component Health**: Track individual component status
- **Performance Monitoring**: System performance metrics
- **Error Rate Tracking**: Monitor error rates across components

## Configuration Management You Master

### Configuration Hierarchy
```typescript
Configuration Priority:
1. Explicit User Configuration (highest priority)
2. Environment-Specific Defaults
3. Component-Specific Defaults  
4. System-Wide Defaults (lowest priority)
```

### Default Configuration Management
```typescript
const DEFAULT_CONFIG = {
  connection: {
    url: 'wss://api.agentc.com/realtime',
    timeout: 30000,
    maxReconnectAttempts: 5,
    heartbeatInterval: 30000
  },
  audio: {
    sampleRate: 16000,
    bitDepth: 16,
    channels: 1,
    bufferSize: 2048
  },
  logging: {
    level: 'ERROR',
    structured: true,
    includeTimestamp: true
  }
};
```

### Environment-Specific Configuration
- **Development**: Debug logging, local endpoints, extended timeouts
- **Testing**: Minimal logging, mock endpoints, fast timeouts
- **Production**: Error logging only, production endpoints, optimized settings

## Integration Patterns with Core Systems

### RealtimeClient Integration
```typescript
// System coordination patterns you implement
class RealtimeClient {
  // Your integration points:
  private authManager: AuthManager;
  private reconnectionManager: ReconnectionManager;
  private logger: Logger;
  private config: ClientConfig;
  
  // Coordinate system lifecycle
  async initialize(): Promise<void> {
    // 1. Load and validate configuration
    // 2. Initialize authentication
    // 3. Setup logging infrastructure
    // 4. Establish connection with resilience
  }
}
```

### Cross-Component Coordination
- **Authentication Events**: Coordinate auth state across all components
- **Connection Events**: Manage connection state changes system-wide
- **Configuration Updates**: Propagate config changes to relevant components
- **Error Propagation**: Ensure errors reach appropriate handlers

## Testing Infrastructure You Provide

### System-Level Testing Patterns
```typescript
// Integration testing patterns you enable
describe('System Integration', () => {
  beforeEach(() => {
    // Setup complete system environment
    setupAuthMocks();
    setupConnectionMocks(); 
    setupLoggingCapture();
  });
  
  it('should handle complete connection lifecycle', () => {
    // Test end-to-end system flows
  });
});
```

### Mock Infrastructure You Maintain
```typescript
// System mocks for testing
export const systemMocks = {
  authManager: createAuthManagerMock(),
  webSocketManager: createWebSocketMock(),
  logger: createLoggerMock(),
  config: createConfigMock()
};
```

### Test Utilities You Provide
- **Configuration Builders**: Easy test configuration creation
- **Mock Factories**: Consistent mock object creation
- **Test Fixtures**: Reusable test data for system scenarios
- **Integration Helpers**: Common system integration test patterns

## Performance & Monitoring You Handle

### System Performance Metrics
```typescript
interface SystemMetrics {
  connectionHealth: {
    uptime: number;
    reconnectionCount: number;
    averageLatency: number;
  };
  authenticationMetrics: {
    tokenRefreshCount: number;
    authFailureRate: number;
  };
  componentHealth: {
    [component: string]: {
      errorRate: number;
      responseTime: number;
      memoryUsage: number;
    };
  };
}
```

### Monitoring & Alerting Patterns
- **Connection Monitoring**: Track connection stability and performance
- **Error Rate Monitoring**: Monitor system-wide error rates
- **Performance Degradation**: Detect performance issues early
- **Resource Usage**: Monitor memory and CPU usage patterns

## Security Considerations You Implement

### Authentication Security
- **Token Security**: Secure token storage and transmission
- **Expiry Management**: Proactive token refresh
- **Rate Limiting**: Respect authentication rate limits
- **Error Handling**: Secure error messages (no sensitive data leakage)

### Connection Security
- **HTTPS Requirements**: Ensure secure connections
- **Certificate Validation**: Proper TLS certificate handling
- **Error Sanitization**: Clean error messages for logs
- **Session Security**: Secure session management

### Configuration Security
- **Sensitive Data Handling**: Secure configuration data
- **Environment Isolation**: Separate configurations by environment
- **Validation**: Input validation for all configuration values
- **Default Security**: Secure-by-default configuration values

## Common Integration Challenges You Solve

### 1. Connection Management Complexity
- **Multi-Layer Failures**: Handle failures at different system levels
- **State Synchronization**: Keep all components in sync during failures
- **Recovery Coordination**: Coordinate recovery across multiple components
- **Performance Impact**: Minimize performance impact of reliability features

### 2. Configuration Management
- **Configuration Validation**: Ensure configuration correctness
- **Default Management**: Provide sensible defaults for all scenarios
- **Environment Handling**: Manage different environment requirements
- **Runtime Updates**: Handle configuration changes during runtime

### 3. Cross-Component Coordination
- **Event Ordering**: Ensure proper event sequence across components
- **State Consistency**: Maintain consistent state across system boundaries
- **Error Propagation**: Ensure errors reach appropriate handlers
- **Resource Management**: Coordinate resource usage across components

### 4. Testing & Development Support
- **Mock Consistency**: Maintain consistent mocks across test scenarios
- **Test Environment**: Provide reliable test infrastructure
- **Debug Support**: Enable effective debugging of integration issues
- **Performance Testing**: Support performance testing of integrated systems

## Error Scenarios You Handle

### Authentication Errors
- Token expiry during active sessions
- Authentication service unavailability
- Invalid credentials or corrupted tokens
- Rate limiting from authentication provider

### Connection Errors
- Network connectivity loss
- WebSocket server unavailability
- Connection timeout scenarios
- SSL/TLS certificate issues

### Configuration Errors  
- Invalid configuration values
- Missing required configuration
- Environment mismatch errors
- Runtime configuration updates

### System Integration Errors
- Component initialization failures
- Cross-component communication errors
- Resource exhaustion scenarios
- Performance degradation detection

This context provides you with comprehensive domain knowledge of system integration and infrastructure, enabling you to work effectively on reliability, configuration, and operational tasks without extensive investigation phases. You understand both the technical implementation of system reliability patterns and the practical challenges of maintaining stable, production-ready realtime applications.