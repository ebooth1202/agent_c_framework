/**
 * Tests for TurnManager
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { TurnManager } from '../../src/session/TurnManager';
import { RealtimeClient } from '../../src/client/RealtimeClient';
import { MockWebSocket, mockWebSocketConstructor } from '../../../../test/utils/mock-websocket';
import { sleep } from '../../../../test/utils/test-helpers';

describe('TurnManager', () => {
  let turnManager: TurnManager;
  let realtimeClient: RealtimeClient;
  let mockWS: any;

  beforeEach(() => {
    // Mock WebSocket globally
    mockWS = mockWebSocketConstructor();
    global.WebSocket = mockWS as any;
    
    // Create RealtimeClient instance
    realtimeClient = new RealtimeClient({
      apiUrl: 'ws://localhost:8080/realtime',
      authToken: 'test-token',
      autoReconnect: false
    });
    
    // Create TurnManager instance
    turnManager = new TurnManager(realtimeClient);
  });

  afterEach(() => {
    // Cleanup
    turnManager.destroy();
    realtimeClient.destroy();
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with canSendInput as false', () => {
      expect(turnManager.canSendInput).toBe(false);
    });

    it('should register event listeners on client', () => {
      const onSpy = vi.spyOn(realtimeClient, 'on');
      
      // Create new turn manager to capture registration
      const newTurnManager = new TurnManager(realtimeClient);
      
      expect(onSpy).toHaveBeenCalledWith('user_turn_start', expect.any(Function));
      expect(onSpy).toHaveBeenCalledWith('user_turn_end', expect.any(Function));
      
      newTurnManager.destroy();
    });
  });

  describe('Turn State Management', () => {
    it('should update state to true on user_turn_start event', () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // Initial state should be false
      expect(turnManager.canSendInput).toBe(false);
      
      // Emit user_turn_start event
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      // State should now be true
      expect(turnManager.canSendInput).toBe(true);
      
      // Event should have been emitted
      expect(stateChangeHandler).toHaveBeenCalledWith({ canSendInput: true });
    });

    it('should update state to false on user_turn_end event', () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // First set state to true
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      expect(turnManager.canSendInput).toBe(true);
      stateChangeHandler.mockClear();
      
      // Emit user_turn_end event
      realtimeClient.emit('user_turn_end', {
        type: 'user_turn_end',
        timestamp: new Date().toISOString()
      });
      
      // State should now be false
      expect(turnManager.canSendInput).toBe(false);
      
      // Event should have been emitted
      expect(stateChangeHandler).toHaveBeenCalledWith({ canSendInput: false });
    });

    it('should not emit event if state does not change', () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // Initial state is false
      expect(turnManager.canSendInput).toBe(false);
      
      // Emit user_turn_end when already false
      realtimeClient.emit('user_turn_end', {
        type: 'user_turn_end',
        timestamp: new Date().toISOString()
      });
      
      // State should still be false
      expect(turnManager.canSendInput).toBe(false);
      
      // Event should NOT have been emitted
      expect(stateChangeHandler).not.toHaveBeenCalled();
    });

    it('should handle multiple state transitions correctly', () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // Sequence of events
      const events = [
        { type: 'user_turn_start', expectedState: true },
        { type: 'user_turn_end', expectedState: false },
        { type: 'user_turn_start', expectedState: true },
        { type: 'user_turn_start', expectedState: true }, // No change
        { type: 'user_turn_end', expectedState: false },
        { type: 'user_turn_end', expectedState: false }, // No change
      ];
      
      let expectedCallCount = 0;
      
      events.forEach(({ type, expectedState }) => {
        const previousState = turnManager.canSendInput;
        
        // Emit event
        realtimeClient.emit(type as any, {
          type,
          timestamp: new Date().toISOString()
        });
        
        // Check state
        expect(turnManager.canSendInput).toBe(expectedState);
        
        // Check if event was emitted (only if state changed)
        if (previousState !== expectedState) {
          expectedCallCount++;
          expect(stateChangeHandler).toHaveBeenCalledTimes(expectedCallCount);
          expect(stateChangeHandler).toHaveBeenLastCalledWith({ canSendInput: expectedState });
        }
      });
      
      // Total calls should be 4 (state changed 4 times)
      expect(stateChangeHandler).toHaveBeenCalledTimes(4);
    });
  });

  describe('Event Handling', () => {
    it('should handle events from different sources correctly', () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // Simulate event with additional data
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString(),
        session_id: 'session-123',
        reason: 'user_input_requested'
      });
      
      expect(turnManager.canSendInput).toBe(true);
      expect(stateChangeHandler).toHaveBeenCalledWith({ canSendInput: true });
    });

    it('should maintain correct state through rapid event changes', async () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // Rapid fire events
      for (let i = 0; i < 10; i++) {
        realtimeClient.emit('user_turn_start', {
          type: 'user_turn_start',
          timestamp: new Date().toISOString()
        });
        
        realtimeClient.emit('user_turn_end', {
          type: 'user_turn_end',
          timestamp: new Date().toISOString()
        });
      }
      
      // Final state should be false (last event was turn_end)
      expect(turnManager.canSendInput).toBe(false);
      
      // Should have received 20 state change events
      expect(stateChangeHandler).toHaveBeenCalledTimes(20);
    });
  });

  describe('Event Subscription', () => {
    it('should allow multiple listeners for turn-state-changed event', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      const handler3 = vi.fn();
      
      turnManager.on('turn-state-changed', handler1);
      turnManager.on('turn-state-changed', handler2);
      turnManager.on('turn-state-changed', handler3);
      
      // Trigger state change
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      // All handlers should have been called
      expect(handler1).toHaveBeenCalledWith({ canSendInput: true });
      expect(handler2).toHaveBeenCalledWith({ canSendInput: true });
      expect(handler3).toHaveBeenCalledWith({ canSendInput: true });
    });

    it('should support removing specific listeners', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      
      turnManager.on('turn-state-changed', handler1);
      turnManager.on('turn-state-changed', handler2);
      
      // Remove first handler
      turnManager.off('turn-state-changed', handler1);
      
      // Trigger state change
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      // Only handler2 should have been called
      expect(handler1).not.toHaveBeenCalled();
      expect(handler2).toHaveBeenCalledWith({ canSendInput: true });
    });
  });

  describe('Integration with RealtimeClient', () => {
    it('should work correctly with connected client', async () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // Connect the client
      const connectPromise = realtimeClient.connect();
      const wsInstance = mockWS.mock.results[0].value as MockWebSocket;
      
      // Trigger open event
      if (wsInstance.onopen) {
        wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
      }
      await connectPromise;
      
      // Simulate receiving turn events from server
      const turnStartEvent = {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      };
      
      if (wsInstance.onmessage) {
        wsInstance.onmessage({
          type: 'message',
          target: wsInstance,
          data: JSON.stringify(turnStartEvent)
        } as MessageEvent);
      }
      
      // Wait for event processing
      await sleep(10);
      
      // Turn state should have changed
      expect(turnManager.canSendInput).toBe(true);
      expect(stateChangeHandler).toHaveBeenCalledWith({ canSendInput: true });
      
      // Simulate turn end from server
      const turnEndEvent = {
        type: 'user_turn_end',
        timestamp: new Date().toISOString()
      };
      
      if (wsInstance.onmessage) {
        wsInstance.onmessage({
          type: 'message',
          target: wsInstance,
          data: JSON.stringify(turnEndEvent)
        } as MessageEvent);
      }
      
      // Wait for event processing
      await sleep(10);
      
      // Turn state should have changed back
      expect(turnManager.canSendInput).toBe(false);
      expect(stateChangeHandler).toHaveBeenLastCalledWith({ canSendInput: false });
    });

    it('should handle disconnection gracefully', async () => {
      // Connect the client
      const connectPromise = realtimeClient.connect();
      const wsInstance = mockWS.mock.results[0].value as MockWebSocket;
      
      // Trigger open event
      if (wsInstance.onopen) {
        wsInstance.onopen({ type: 'open', target: wsInstance } as Event);
      }
      await connectPromise;
      
      // Set turn state to true
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      expect(turnManager.canSendInput).toBe(true);
      
      // Disconnect client
      realtimeClient.disconnect();
      
      // Turn manager should still maintain its state
      expect(turnManager.canSendInput).toBe(true);
      
      // But should still respond to events if client reconnects
      realtimeClient.emit('user_turn_end', {
        type: 'user_turn_end',
        timestamp: new Date().toISOString()
      });
      
      expect(turnManager.canSendInput).toBe(false);
    });
  });

  describe('Cleanup', () => {
    it('should remove event listeners on cleanup', () => {
      const offSpy = vi.spyOn(realtimeClient, 'off');
      
      turnManager.cleanup();
      
      expect(offSpy).toHaveBeenCalledWith('user_turn_start', expect.any(Function));
      expect(offSpy).toHaveBeenCalledWith('user_turn_end', expect.any(Function));
    });

    it('should remove all listeners on cleanup', () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      
      turnManager.on('turn-state-changed', handler1);
      turnManager.on('turn-state-changed', handler2);
      
      // Cleanup
      turnManager.cleanup();
      
      // Try to emit event (should not call handlers)
      turnManager.emit('turn-state-changed', { canSendInput: true });
      
      expect(handler1).not.toHaveBeenCalled();
      expect(handler2).not.toHaveBeenCalled();
    });

    it('should handle multiple cleanup calls gracefully', () => {
      // First cleanup
      turnManager.cleanup();
      
      // Second cleanup should not throw
      expect(() => turnManager.cleanup()).not.toThrow();
    });

    it('should work correctly after destroy is called', () => {
      const handler = vi.fn();
      turnManager.on('turn-state-changed', handler);
      
      // Destroy (alias for cleanup)
      turnManager.destroy();
      
      // Events should not be processed
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      // Handler should not have been called
      expect(handler).not.toHaveBeenCalled();
      
      // State should not have changed
      expect(turnManager.canSendInput).toBe(false);
    });

    it('should not affect client after cleanup', () => {
      turnManager.cleanup();
      
      // Client should still work
      const clientHandler = vi.fn();
      realtimeClient.on('test_event', clientHandler);
      realtimeClient.emit('test_event', { data: 'test' });
      
      expect(clientHandler).toHaveBeenCalledWith({ data: 'test' });
    });
  });

  describe('Edge Cases', () => {
    it('should handle undefined or null events gracefully', () => {
      const stateChangeHandler = vi.fn();
      turnManager.on('turn-state-changed', stateChangeHandler);
      
      // Emit events with undefined data
      realtimeClient.emit('user_turn_start', undefined as any);
      
      // Should still update state
      expect(turnManager.canSendInput).toBe(true);
      expect(stateChangeHandler).toHaveBeenCalledWith({ canSendInput: true });
      
      // Emit with null
      realtimeClient.emit('user_turn_end', null as any);
      
      // Should still update state
      expect(turnManager.canSendInput).toBe(false);
      expect(stateChangeHandler).toHaveBeenCalledWith({ canSendInput: false });
    });

    it('should maintain correct state if created after client events', () => {
      // Emit event before creating turn manager
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      // Create new turn manager
      const newTurnManager = new TurnManager(realtimeClient);
      
      // Should start with default state (false), not affected by previous events
      expect(newTurnManager.canSendInput).toBe(false);
      
      // But should respond to new events
      realtimeClient.emit('user_turn_start', {
        type: 'user_turn_start',
        timestamp: new Date().toISOString()
      });
      
      expect(newTurnManager.canSendInput).toBe(true);
      
      newTurnManager.destroy();
    });
  });
});