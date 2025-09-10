/**
 * Tests for main index exports
 */

import { describe, it, expect } from 'vitest';
import * as CoreExports from '../index';

describe('Core Package Exports', () => {
  it('should export VERSION constant', () => {
    expect(CoreExports.VERSION).toBe('0.1.0');
    expect(typeof CoreExports.VERSION).toBe('string');
  });

  describe('Client exports', () => {
    it('should export RealtimeClient', () => {
      expect(CoreExports.RealtimeClient).toBeDefined();
      expect(typeof CoreExports.RealtimeClient).toBe('function');
    });

    it('should export WebSocketManager', () => {
      expect(CoreExports.WebSocketManager).toBeDefined();
      expect(typeof CoreExports.WebSocketManager).toBe('function');
    });

    it('should export ReconnectionManager', () => {
      expect(CoreExports.ReconnectionManager).toBeDefined();
      expect(typeof CoreExports.ReconnectionManager).toBe('function');
    });
  });

  describe('Event exports', () => {
    it('should export EventEmitter', () => {
      expect(CoreExports.EventEmitter).toBeDefined();
      expect(typeof CoreExports.EventEmitter).toBe('function');
    });

    it('should export EventStreamProcessor', () => {
      expect(CoreExports.EventStreamProcessor).toBeDefined();
      expect(typeof CoreExports.EventStreamProcessor).toBe('function');
    });

    it('should export MessageBuilder', () => {
      expect(CoreExports.MessageBuilder).toBeDefined();
      expect(typeof CoreExports.MessageBuilder).toBe('function');
    });

    it('should export RichMediaHandler', () => {
      expect(CoreExports.RichMediaHandler).toBeDefined();
      expect(typeof CoreExports.RichMediaHandler).toBe('function');
    });

    it('should export ToolCallManager', () => {
      expect(CoreExports.ToolCallManager).toBeDefined();
      expect(typeof CoreExports.ToolCallManager).toBe('function');
    });
  });

  describe('Auth exports', () => {
    it('should export AuthManager', () => {
      expect(CoreExports.AuthManager).toBeDefined();
      expect(typeof CoreExports.AuthManager).toBe('function');
    });
  });

  describe('Audio exports', () => {
    it('should export AudioService', () => {
      expect(CoreExports.AudioService).toBeDefined();
      expect(typeof CoreExports.AudioService).toBe('function');
    });

    it('should export AudioAgentCBridge', () => {
      expect(CoreExports.AudioAgentCBridge).toBeDefined();
      expect(typeof CoreExports.AudioAgentCBridge).toBe('function');
    });

    it('should export AudioOutputService', () => {
      expect(CoreExports.AudioOutputService).toBeDefined();
      expect(typeof CoreExports.AudioOutputService).toBe('function');
    });

    it('should export AudioOutputService', () => {
      expect(CoreExports.AudioOutputService).toBeDefined();
      expect(typeof CoreExports.AudioOutputService).toBe('function');
    });
  });

  describe('Session exports', () => {
    it('should export SessionManager', () => {
      expect(CoreExports.SessionManager).toBeDefined();
      expect(typeof CoreExports.SessionManager).toBe('function');
    });

    it('should export TurnManager', () => {
      expect(CoreExports.TurnManager).toBeDefined();
      expect(typeof CoreExports.TurnManager).toBe('function');
    });
  });

  describe('Voice exports', () => {
    it('should export VoiceManager', () => {
      expect(CoreExports.VoiceManager).toBeDefined();
      expect(typeof CoreExports.VoiceManager).toBe('function');
    });
  });

  describe('Avatar exports', () => {
    it('should export AvatarManager', () => {
      expect(CoreExports.AvatarManager).toBeDefined();
      expect(typeof CoreExports.AvatarManager).toBe('function');
    });
  });

  describe('Utility exports', () => {
    it('should export messageUtils', () => {
      expect(CoreExports.normalizeMessage).toBeDefined();
      expect(typeof CoreExports.normalizeMessage).toBe('function');
      expect(CoreExports.normalizeMessages).toBeDefined();
      expect(typeof CoreExports.normalizeMessages).toBe('function');
    });

    it('should export isChatMessage helper', () => {
      expect(CoreExports.isChatMessage).toBeDefined();
      expect(typeof CoreExports.isChatMessage).toBe('function');
    });

    it('should export sanitizeHtml utility', () => {
      expect(CoreExports.sanitizeHtml).toBeDefined();
      expect(typeof CoreExports.sanitizeHtml).toBe('function');
    });
  });

  describe('Type exports', () => {
    // Type exports are compile-time only, but we can verify the module structure
    it('should have proper module structure', () => {
      // Check that core types can be accessed (they'll be undefined at runtime but shouldn't throw)
      expect(() => {
        // These won't have runtime values but accessing them shouldn't throw
        const _types = {
          RealtimeClientConfig: CoreExports.RealtimeClient,
          EventMap: CoreExports.EventEmitter,
        };
      }).not.toThrow();
    });
  });
});