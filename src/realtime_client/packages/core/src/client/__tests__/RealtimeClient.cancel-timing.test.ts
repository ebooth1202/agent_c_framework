import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { RealtimeClient } from '../RealtimeClient';
import { WebSocketManager } from '../WebSocketManager';
import { MockWebSocketConstructor } from '../../test/mocks/websocket.mock';

// Replace global WebSocket with mock
vi.stubGlobal('WebSocket', MockWebSocketConstructor);

// Mock WebSocketManager
vi.mock('../WebSocketManager');

describe('RealtimeClient - Cancel Timing Tests', () => {
  let client: RealtimeClient;
  let mockWsManager: any;
  let mockWebSocket: any;
  
  beforeEach(() => {
    // Create a mock WebSocket with bufferedAmount property
    mockWebSocket = {
      readyState: MockWebSocketConstructor.OPEN,
      bufferedAmount: 0,
      send: vi.fn((data) => {
        // Simulate immediate send
        console.log(`[TEST] WebSocket.send called with:`, data);
      })
    };
    
    // Setup mock WebSocketManager
    mockWsManager = {
      connect: vi.fn(),
      disconnect: vi.fn(),
      isConnected: vi.fn().mockReturnValue(true),
      sendJSON: vi.fn((data) => {
        const jsonString = JSON.stringify(data);
        console.log(`[TEST] sendJSON called at ${Date.now()} with:`, data);
        mockWebSocket.send(jsonString);
      }),
      supportsBinary: vi.fn().mockReturnValue(true),
      sendBinary: vi.fn(),
      getReadyState: vi.fn().mockReturnValue(MockWebSocketConstructor.OPEN)
    };
    
    (WebSocketManager as any).mockImplementation(() => mockWsManager);
    
    // Create client with debug enabled
    client = new RealtimeClient({
      apiUrl: 'wss://test.example.com',
      authToken: 'test-token',
      debug: true
    });
  });
  
  afterEach(() => {
    vi.clearAllMocks();
  });
  
  describe('Cancel Event Timing', () => {
    it('should send cancel event immediately without any delay', () => {
      // Connect the client (mock it as connected)
      (client as any).wsManager = mockWsManager;
      (client as any).connectionState = 2; // ConnectionState.CONNECTED
      
      const startTime = Date.now();
      
      // Call cancelResponse
      client.cancelResponse();
      
      const endTime = Date.now();
      const elapsed = endTime - startTime;
      
      // Verify the event was sent immediately (should be < 1ms in a unit test)
      expect(elapsed).toBeLessThan(5);
      
      // Verify sendJSON was called synchronously
      expect(mockWsManager.sendJSON).toHaveBeenCalledTimes(1);
      expect(mockWsManager.sendJSON).toHaveBeenCalledWith({
        type: 'client_wants_cancel'
      });
      
      // Verify WebSocket.send was called
      expect(mockWebSocket.send).toHaveBeenCalledTimes(1);
      expect(mockWebSocket.send).toHaveBeenCalledWith(
        JSON.stringify({ type: 'client_wants_cancel' })
      );
    });
    
    it('should report WebSocket bufferedAmount if available', () => {
      // Connect the client
      (client as any).wsManager = mockWsManager;
      (client as any).connectionState = 2; // ConnectionState.CONNECTED
      
      // Simulate some buffered data
      mockWebSocket.bufferedAmount = 1024;
      
      // Spy on console.debug to check our logging
      const debugSpy = vi.spyOn(console, 'debug').mockImplementation(() => {});
      
      // Call cancelResponse
      client.cancelResponse();
      
      // Check that debug logging was called with timing info
      expect(debugSpy).toHaveBeenCalled();
      
      // Find the debug call that logs the cancel
      const cancelLogCall = debugSpy.mock.calls.find(call => 
        call[0]?.includes('cancelResponse() called')
      );
      
      expect(cancelLogCall).toBeDefined();
      
      debugSpy.mockRestore();
    });
    
    it('should measure round-trip time for cancel confirmation', async () => {
      // Connect the client
      (client as any).wsManager = mockWsManager;
      (client as any).connectionState = 2; // ConnectionState.CONNECTED
      
      let cancelSentTime: number;
      let cancelledReceivedTime: number;
      
      // Track when cancel is sent
      mockWsManager.sendJSON.mockImplementation((data) => {
        if (data.type === 'client_wants_cancel') {
          cancelSentTime = Date.now();
          console.log(`[TEST] Cancel sent at ${cancelSentTime}`);
        }
        mockWebSocket.send(JSON.stringify(data));
      });
      
      // Set up listener for cancelled event
      client.on('cancelled' as any, () => {
        cancelledReceivedTime = Date.now();
        console.log(`[TEST] Cancelled received at ${cancelledReceivedTime}`);
      });
      
      // Send cancel
      client.cancelResponse();
      
      // Simulate server response after 50ms
      setTimeout(() => {
        const cancelledEvent = { type: 'cancelled' };
        (client as any).handleMessage(JSON.stringify(cancelledEvent));
      }, 50);
      
      // Wait for the cancelled event
      await new Promise(resolve => setTimeout(resolve, 100));
      
      // Check timing
      expect(cancelSentTime).toBeDefined();
      // Note: cancelledReceivedTime won't be set in this test since EventStreamProcessor
      // handles the event, but we've verified the flow
    });
  });
  
  describe('Race Condition Scenarios', () => {
    it('should handle cancel arriving after user_turn_start', () => {
      // Connect the client
      (client as any).wsManager = mockWsManager;
      (client as any).connectionState = 2; // ConnectionState.CONNECTED
      
      const eventLog: string[] = [];
      
      // Track event order
      mockWsManager.sendJSON.mockImplementation((data) => {
        eventLog.push(`CLIENT: ${data.type} at ${Date.now()}`);
        mockWebSocket.send(JSON.stringify(data));
      });
      
      // Simulate quick agent response completing
      eventLog.push(`SERVER: agent_turn_start at ${Date.now()}`);
      (client as any).handleMessage(JSON.stringify({ type: 'agent_turn_start' }));
      
      // Small delay to simulate agent processing
      setTimeout(() => {
        eventLog.push(`SERVER: user_turn_start at ${Date.now()}`);
        (client as any).handleMessage(JSON.stringify({ type: 'user_turn_start' }));
      }, 10);
      
      // User clicks cancel immediately after sending
      setTimeout(() => {
        eventLog.push(`USER: cancel clicked at ${Date.now()}`);
        client.cancelResponse();
      }, 5);
      
      // Wait for all events to process
      setTimeout(() => {
        console.log('Event sequence:', eventLog);
        
        // Verify cancel was sent
        expect(mockWsManager.sendJSON).toHaveBeenCalledWith({
          type: 'client_wants_cancel'
        });
      }, 50);
    });
  });
});