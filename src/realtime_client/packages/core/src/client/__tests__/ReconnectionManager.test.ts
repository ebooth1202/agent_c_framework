/**
 * Tests for ReconnectionManager
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ReconnectionManager } from '../ReconnectionManager';
import { ReconnectionConfig } from '../ClientConfig';

// Helper to advance time
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

describe('ReconnectionManager', () => {
  let manager: ReconnectionManager;
  let config: ReconnectionConfig;
  let reconnectFn: vi.Mock;

  beforeEach(() => {
    vi.useFakeTimers();
    
    config = {
      enabled: true,
      maxAttempts: 3,
      initialDelay: 1000,
      maxDelay: 30000,
      backoffMultiplier: 2
    };
    
    reconnectFn = vi.fn().mockResolvedValue(undefined);
    manager = new ReconnectionManager(config);
  });

  afterEach(() => {
    manager.stopReconnection();
    vi.clearAllTimers();
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with config', () => {
      expect(manager).toBeDefined();
      expect(manager.isActive()).toBe(false);
      expect(manager.getCurrentAttempt()).toBe(0);
    });

    it('should handle disabled reconnection', async () => {
      const disabledManager = new ReconnectionManager({
        enabled: false,
        maxAttempts: 3,
        initialDelay: 1000,
        maxDelay: 30000,
        backoffMultiplier: 2
      });
      
      await expect(disabledManager.startReconnection(reconnectFn))
        .rejects.toThrow('Reconnection is disabled');
    });
  });

  describe('Reconnection Process', () => {
    it('should start reconnection process', async () => {
      const promise = manager.startReconnection(reconnectFn);
      
      expect(manager.isActive()).toBe(true);
      expect(reconnectFn).toHaveBeenCalledTimes(1);
      
      // Let it complete
      await vi.runAllTimersAsync();
    });

    it('should prevent multiple concurrent reconnections', async () => {
      const promise1 = manager.startReconnection(reconnectFn);
      
      await expect(manager.startReconnection(reconnectFn))
        .rejects.toThrow('Reconnection already in progress');
      
      manager.stopReconnection();
    });

    it('should emit reconnecting event', async () => {
      const reconnectingHandler = vi.fn();
      manager.on('reconnecting', reconnectingHandler);
      
      const promise = manager.startReconnection(reconnectFn);
      
      // First attempt
      expect(reconnectingHandler).toHaveBeenCalledWith({
        attempt: 1,
        delay: 0
      });
      
      manager.stopReconnection();
    });

    it('should emit reconnected event on success', async () => {
      const reconnectedHandler = vi.fn();
      manager.on('reconnected', reconnectedHandler);
      
      reconnectFn.mockResolvedValueOnce(undefined); // Success
      
      await manager.startReconnection(reconnectFn);
      
      expect(reconnectedHandler).toHaveBeenCalled();
    });

    it('should retry on failure with backoff', async () => {
      reconnectFn
        .mockRejectedValueOnce(new Error('Failed 1'))
        .mockRejectedValueOnce(new Error('Failed 2'))
        .mockResolvedValueOnce(undefined); // Success on third attempt
      
      const promise = manager.startReconnection(reconnectFn);
      
      // First attempt - immediate
      expect(reconnectFn).toHaveBeenCalledTimes(1);
      expect(manager.getCurrentAttempt()).toBe(1);
      
      // Wait for first retry (1000ms delay)
      await vi.advanceTimersByTimeAsync(1000);
      expect(reconnectFn).toHaveBeenCalledTimes(2);
      expect(manager.getCurrentAttempt()).toBe(2);
      
      // Wait for second retry (2000ms delay with backoff)
      await vi.advanceTimersByTimeAsync(2000);
      expect(reconnectFn).toHaveBeenCalledTimes(3);
      
      await promise; // Should succeed
    });

    it('should respect max attempts', async () => {
      const failedHandler = vi.fn();
      manager.on('reconnection_failed', failedHandler);
      
      // Always fail
      reconnectFn.mockRejectedValue(new Error('Always fail'));
      
      const promise = manager.startReconnection(reconnectFn);
      
      // Run through all attempts
      await vi.runAllTimersAsync();
      
      await expect(promise).rejects.toThrow();
      expect(reconnectFn).toHaveBeenCalledTimes(config.maxAttempts);
      expect(failedHandler).toHaveBeenCalled();
    });
  });

  describe('Stop and Reset', () => {
    it('should stop reconnection process', async () => {
      const promise = manager.startReconnection(reconnectFn);
      
      expect(manager.isActive()).toBe(true);
      
      manager.stopReconnection();
      
      expect(manager.isActive()).toBe(false);
      expect(manager.getCurrentAttempt()).toBe(0);
    });

    it('should clear timers on stop', async () => {
      reconnectFn.mockRejectedValueOnce(new Error('Fail first'));
      
      const promise = manager.startReconnection(reconnectFn);
      
      // Wait a bit but not until retry
      await vi.advanceTimersByTimeAsync(500);
      
      manager.stopReconnection();
      
      // Advance time - should not trigger more attempts
      await vi.advanceTimersByTimeAsync(5000);
      expect(reconnectFn).toHaveBeenCalledTimes(1);
    });

    it('should reset state', () => {
      manager.reset();
      
      expect(manager.getCurrentAttempt()).toBe(0);
      expect(manager.isActive()).toBe(false);
    });
  });

  describe('Event Emitter', () => {
    it('should emit events during reconnection', async () => {
      const reconnectingHandler = vi.fn();
      const reconnectedHandler = vi.fn();
      const failedHandler = vi.fn();
      
      manager.on('reconnecting', reconnectingHandler);
      manager.on('reconnected', reconnectedHandler);
      manager.on('reconnection_failed', failedHandler);
      
      // Successful reconnection
      reconnectFn.mockResolvedValueOnce(undefined);
      await manager.startReconnection(reconnectFn);
      
      expect(reconnectingHandler).toHaveBeenCalled();
      expect(reconnectedHandler).toHaveBeenCalled();
      expect(failedHandler).not.toHaveBeenCalled();
    });

    it('should support multiple listeners', async () => {
      const handler1 = vi.fn();
      const handler2 = vi.fn();
      
      manager.on('reconnecting', handler1);
      manager.on('reconnecting', handler2);
      
      const promise = manager.startReconnection(reconnectFn);
      
      expect(handler1).toHaveBeenCalled();
      expect(handler2).toHaveBeenCalled();
      
      manager.stopReconnection();
    });

    it('should support removing listeners', async () => {
      const handler = vi.fn();
      
      manager.on('reconnecting', handler);
      manager.off('reconnecting', handler);
      
      const promise = manager.startReconnection(reconnectFn);
      
      expect(handler).not.toHaveBeenCalled();
      
      manager.stopReconnection();
    });
  });

  describe('Error Handling', () => {
    it('should handle reconnect function errors', async () => {
      reconnectFn.mockRejectedValue(new Error('Connection failed'));
      
      const promise = manager.startReconnection(reconnectFn);
      
      await vi.runAllTimersAsync();
      
      await expect(promise).rejects.toThrow();
    });

    it('should handle synchronous errors in reconnect function', async () => {
      reconnectFn.mockImplementation(() => {
        throw new Error('Sync error');
      });
      
      const promise = manager.startReconnection(reconnectFn);
      
      await vi.runAllTimersAsync();
      
      await expect(promise).rejects.toThrow();
    });
  });

  describe('Backoff Strategy', () => {
    it('should apply exponential backoff', async () => {
      const reconnectingHandler = vi.fn();
      manager.on('reconnecting', reconnectingHandler);
      
      reconnectFn.mockRejectedValue(new Error('Always fail'));
      
      const promise = manager.startReconnection(reconnectFn);
      
      // First attempt - immediate
      expect(reconnectingHandler).toHaveBeenCalledWith({
        attempt: 1,
        delay: 0
      });
      
      // Second attempt - 1000ms delay
      await vi.advanceTimersByTimeAsync(1000);
      expect(reconnectingHandler).toHaveBeenCalledWith({
        attempt: 2,
        delay: 1000
      });
      
      // Third attempt - 2000ms delay (1000 * 2)
      await vi.advanceTimersByTimeAsync(2000);
      expect(reconnectingHandler).toHaveBeenCalledWith({
        attempt: 3,
        delay: 2000
      });
      
      await vi.runAllTimersAsync();
    });

    it('should respect max delay', async () => {
      const fastBackoffManager = new ReconnectionManager({
        enabled: true,
        maxAttempts: 5,
        initialDelay: 1000,
        maxDelay: 3000,
        backoffMultiplier: 10 // Very aggressive
      });
      
      const handler = vi.fn();
      fastBackoffManager.on('reconnecting', handler);
      
      reconnectFn.mockRejectedValue(new Error('Always fail'));
      
      const promise = fastBackoffManager.startReconnection(reconnectFn);
      
      // Run through attempts
      await vi.runAllTimersAsync();
      
      // Check that delays are capped
      const calls = handler.mock.calls;
      calls.forEach((call: any) => {
        if (call[0].delay > 0) {
          expect(call[0].delay).toBeLessThanOrEqual(3000);
        }
      });
      
      fastBackoffManager.stopReconnection();
    });
  });

  describe('Edge Cases', () => {
    it('should handle zero max attempts', async () => {
      const zeroManager = new ReconnectionManager({
        enabled: true,
        maxAttempts: 0,
        initialDelay: 1000,
        maxDelay: 30000,
        backoffMultiplier: 2
      });
      
      const promise = zeroManager.startReconnection(reconnectFn);
      
      await vi.runAllTimersAsync();
      
      await expect(promise).rejects.toThrow();
      expect(reconnectFn).not.toHaveBeenCalled();
    });

    it('should handle immediate stop after start', async () => {
      const promise = manager.startReconnection(reconnectFn);
      manager.stopReconnection();
      
      expect(manager.isActive()).toBe(false);
      expect(reconnectFn).toHaveBeenCalledTimes(1); // Initial attempt
    });

    it('should handle multiple stop calls', () => {
      manager.stopReconnection();
      manager.stopReconnection();
      manager.stopReconnection();
      
      expect(manager.isActive()).toBe(false);
    });
  });
});