import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RealtimeClient } from '../RealtimeClient';
import { ClientEventMap } from '../../events';
import { MockWebSocket, mockWebSocketConstructor } from '../../test/mocks/mock-websocket';

describe('RealtimeClient.sendEvent', () => {
    let client: RealtimeClient;
    let mockWS: ReturnType<typeof mockWebSocketConstructor>;
    let wsInstance: MockWebSocket;

    beforeEach(() => {
        // Mock WebSocket globally
        mockWS = mockWebSocketConstructor();
        global.WebSocket = mockWS as any;

        // Create client with test config
        client = new RealtimeClient({
            apiUrl: 'ws://localhost:8080/realtime',
            authToken: 'test-token',
            autoReconnect: false,
            debug: false
        });
    });

    afterEach(() => {
        client.destroy();
        vi.clearAllMocks();
    });

    it('should be a public method', () => {
        // Verify sendEvent is accessible as a public method
        expect(client.sendEvent).toBeDefined();
        expect(typeof client.sendEvent).toBe('function');
    });

    it('should throw error when not connected', () => {
        // Try to send event without connecting
        expect(() => {
            client.sendEvent({ type: 'ping' });
        }).toThrow('Not connected to server');
    });

    it('should send event when connected', async () => {
        // Connect first
        const connectPromise = client.connect();
        wsInstance = mockWS.lastInstance();
        
        // Set readyState to OPEN to simulate connected state
        wsInstance.readyState = MockWebSocket.OPEN;
        
        // Trigger open event
        if (wsInstance.onopen) {
            wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
        }
        await connectPromise;

        // Send a test event
        const testEvent: ClientEventMap['ping'] = { type: 'ping' };
        client.sendEvent(testEvent);

        // Verify the event was sent
        expect(wsInstance.send).toHaveBeenCalledWith(JSON.stringify(testEvent));
    });

    it('should accept various event types from ClientEventMap', async () => {
        // Connect first
        const connectPromise = client.connect();
        wsInstance = mockWS.lastInstance();
        
        // Set readyState to OPEN to simulate connected state
        wsInstance.readyState = MockWebSocket.OPEN;
        
        // Trigger open event
        if (wsInstance.onopen) {
            wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
        }
        await connectPromise;

        // Test different event types
        const events: Array<ClientEventMap[keyof ClientEventMap]> = [
            { type: 'ping' },
            { type: 'get_agents' },
            { type: 'set_agent', agent_key: 'test-agent' },
            { type: 'get_voices' },
            { type: 'text_input', text: 'Hello' },
            { type: 'new_chat_session' },
            { type: 'resume_chat_session', session_id: 'test-session' }
        ];

        events.forEach(event => {
            (wsInstance.send as any).mockClear();
            client.sendEvent(event);
            expect(wsInstance.send).toHaveBeenCalledWith(JSON.stringify(event));
        });
    });

    it('should maintain type safety with TypeScript generics', async () => {
        // Connect first
        const connectPromise = client.connect();
        wsInstance = mockWS.lastInstance();
        
        // Set readyState to OPEN to simulate connected state
        wsInstance.readyState = MockWebSocket.OPEN;
        
        // Trigger open event
        if (wsInstance.onopen) {
            wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
        }
        await connectPromise;

        // This should compile without errors
        client.sendEvent<'text_input'>({ type: 'text_input', text: 'Test message' });
        client.sendEvent<'set_agent'>({ type: 'set_agent', agent_key: 'agent-1' });
        
        // Verify that the method signature enforces correct event types
        // (This is a compile-time check, but we can verify runtime behavior)
        expect(() => {
            client.sendEvent({ type: 'text_input', text: 'Valid' });
        }).not.toThrow();
    });
});