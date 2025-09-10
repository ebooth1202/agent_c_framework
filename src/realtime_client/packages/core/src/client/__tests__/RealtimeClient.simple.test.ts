/**
 * Simplified tests for RealtimeClient
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { RealtimeClient } from '../RealtimeClient';

describe('RealtimeClient - Simple Tests', () => {
  let client: RealtimeClient;

  beforeEach(() => {
    // Create client instance without connecting
    client = new RealtimeClient({
      apiUrl: 'ws://localhost:8080/realtime',
      authToken: 'test-token',
      autoReconnect: false,
    });
  });

  describe('Client Creation', () => {
    it('should create a client instance', () => {
      expect(client).toBeDefined();
      expect(client).toBeInstanceOf(RealtimeClient);
    });

    it('should initialize with correct config', () => {
      expect(client.isConnected()).toBe(false);
    });
  });

  describe('Event Emitter', () => {
    it('should add and remove event listeners', () => {
      const handler = vi.fn();
      
      client.on('test_event', handler);
      client.emit('test_event' as any, { data: 'test' });
      
      expect(handler).toHaveBeenCalledWith({ data: 'test' });
      
      client.off('test_event', handler);
      client.emit('test_event' as any, { data: 'test2' });
      
      expect(handler).toHaveBeenCalledTimes(1);
    });

    it('should support once listeners', () => {
      const handler = vi.fn();
      
      client.once('test_event', handler);
      client.emit('test_event' as any, { data: 'test1' });
      client.emit('test_event' as any, { data: 'test2' });
      
      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith({ data: 'test1' });
    });
  });
});