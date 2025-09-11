/**
 * AudioAgentCBridge Unit Tests
 * Level 1 Simplicity - Focus on bridging behavior and turn management
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { AudioAgentCBridge } from '../AudioAgentCBridge';
import { AudioService } from '../AudioService';
import type { RealtimeClient } from '../../client/RealtimeClient';
import type { TurnManager } from '../../session/TurnManager';

// Mock AudioService
vi.mock('../AudioService', () => ({
  AudioService: {
    getInstance: vi.fn()
  }
}));

describe('AudioAgentCBridge', () => {
  let bridge: AudioAgentCBridge;
  let mockAudioService: {
    onAudioChunk: ReturnType<typeof vi.fn>;
    getStatus: ReturnType<typeof vi.fn>;
  };
  let mockRealtimeClient: {
    isConnected: ReturnType<typeof vi.fn>;
    sendBinaryFrame: ReturnType<typeof vi.fn>;
    getTurnManager: ReturnType<typeof vi.fn>;
  };
  let mockTurnManager: {
    canSendInput: boolean;
    on: ReturnType<typeof vi.fn>;
    off: ReturnType<typeof vi.fn>;
  };
  let audioChunkCallback: ((chunk: ArrayBuffer) => void) | null = null;
  let unsubscribeAudio: ReturnType<typeof vi.fn>;

  // Helper to simulate audio chunks
  const simulateAudioChunk = (size: number = 1024) => {
    const chunk = new ArrayBuffer(size);
    audioChunkCallback?.(chunk);
  };

  // Helper to simulate turn state change
  const simulateTurnChange = (canSendInput: boolean) => {
    mockTurnManager.canSendInput = canSendInput;
    const handler = mockTurnManager.on.mock.calls
      .find(call => call[0] === 'turn-state-changed')?.[1];
    handler?.({ canSendInput });
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Reset singleton
    AudioAgentCBridge.resetInstance();
    
    // Setup mock AudioService
    unsubscribeAudio = vi.fn();
    mockAudioService = {
      onAudioChunk: vi.fn((callback) => {
        audioChunkCallback = callback;
        return unsubscribeAudio;
      }),
      getStatus: vi.fn().mockReturnValue({
        isRecording: false,
        state: 'idle'
      })
    };
    
    // Setup mock TurnManager
    mockTurnManager = {
      canSendInput: false,
      on: vi.fn(),
      off: vi.fn()
    };
    
    // Setup mock RealtimeClient
    mockRealtimeClient = {
      isConnected: vi.fn().mockReturnValue(true),
      sendBinaryFrame: vi.fn(),
      getTurnManager: vi.fn().mockReturnValue(mockTurnManager)
    };
    
    // Configure AudioService mock
    vi.mocked(AudioService.getInstance).mockReturnValue(mockAudioService as any);
    
    // Get bridge instance
    bridge = AudioAgentCBridge.getInstance();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    AudioAgentCBridge.resetInstance();
  });

  describe('Singleton Pattern', () => {
    it('should return same instance', () => {
      const instance1 = AudioAgentCBridge.getInstance();
      const instance2 = AudioAgentCBridge.getInstance();
      
      expect(instance1).toBe(instance2);
    });

    it('should reset instance properly', () => {
      const instance1 = AudioAgentCBridge.getInstance();
      AudioAgentCBridge.resetInstance();
      const instance2 = AudioAgentCBridge.getInstance();
      
      expect(instance1).not.toBe(instance2);
    });

    it('should cleanup on reset', () => {
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      bridge.startStreaming();
      
      AudioAgentCBridge.resetInstance();
      
      expect(unsubscribeAudio).toHaveBeenCalled();
      expect(mockTurnManager.off).toHaveBeenCalled();
    });
  });

  describe('Client Management', () => {
    describe('setClient()', () => {
      it('should set client and subscribe to turn manager', () => {
        bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
        
        expect(mockRealtimeClient.getTurnManager).toHaveBeenCalled();
        expect(mockTurnManager.on).toHaveBeenCalledWith(
          'turn-state-changed',
          expect.any(Function)
        );
      });

      it('should handle null client as disconnect', () => {
        // First set a client
        bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
        bridge.startStreaming();
        
        // Then set null
        bridge.setClient(null);
        
        expect(unsubscribeAudio).toHaveBeenCalled();
        expect(mockTurnManager.off).toHaveBeenCalled();
      });

      it('should replace existing client', () => {
        // Set first client
        bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
        
        // Create second client
        const mockClient2 = {
          ...mockRealtimeClient,
          getTurnManager: vi.fn().mockReturnValue(mockTurnManager)
        };
        
        // Replace client
        bridge.setClient(mockClient2 as unknown as RealtimeClient);
        
        // Should unsubscribe from first and subscribe to second
        expect(mockTurnManager.off).toHaveBeenCalled();
        expect(mockClient2.getTurnManager).toHaveBeenCalled();
      });

      it('should handle client without turn manager', () => {
        mockRealtimeClient.getTurnManager.mockReturnValue(null);
        
        // Should not throw
        expect(() => {
          bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
        }).not.toThrow();
      });
    });
  });

  describe('Streaming Control', () => {
    beforeEach(() => {
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
    });

    describe('startStreaming()', () => {
      it('should subscribe to audio chunks', () => {
        bridge.startStreaming();
        
        expect(mockAudioService.onAudioChunk).toHaveBeenCalledWith(
          expect.any(Function)
        );
      });

      it('should throw error when no client', () => {
        bridge.setClient(null);
        
        expect(() => bridge.startStreaming()).toThrow('No client connected');
      });

      it('should be idempotent', () => {
        bridge.startStreaming();
        bridge.startStreaming(); // Second call
        
        // Should only subscribe once
        expect(mockAudioService.onAudioChunk).toHaveBeenCalledTimes(1);
      });

      it('should emit status event', () => {
        const statusSpy = vi.fn();
        bridge.on('status', statusSpy);
        
        bridge.startStreaming();
        
        expect(statusSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            isStreaming: true,
            isConnected: true
          })
        );
      });
    });

    describe('stopStreaming()', () => {
      beforeEach(() => {
        bridge.startStreaming();
      });

      it('should unsubscribe from audio chunks', () => {
        bridge.stopStreaming();
        
        expect(unsubscribeAudio).toHaveBeenCalled();
      });

      it('should be idempotent', () => {
        bridge.stopStreaming();
        
        unsubscribeAudio.mockClear();
        
        bridge.stopStreaming(); // Second call
        
        // Should not try to unsubscribe again
        expect(unsubscribeAudio).not.toHaveBeenCalled();
      });

      it('should log statistics', () => {
        const consoleLog = vi.spyOn(console, 'log').mockImplementation();
        
        // Send some chunks
        simulateAudioChunk();
        simulateAudioChunk();
        
        bridge.stopStreaming();
        
        expect(consoleLog).toHaveBeenCalledWith(
          expect.stringContaining('Audio streaming stopped'),
          expect.objectContaining({
            streamed_chunks: expect.any(Number),
            suppressed_chunks: expect.any(Number)
          })
        );
      });

      it('should emit status event', () => {
        const statusSpy = vi.fn();
        bridge.on('status', statusSpy);
        
        bridge.stopStreaming();
        
        expect(statusSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            isStreaming: false
          })
        );
      });
    });
  });

  describe('Audio Chunk Bridging', () => {
    beforeEach(() => {
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      bridge.startStreaming();
    });

    it('should send chunks when user has turn', () => {
      mockTurnManager.canSendInput = true;
      
      simulateAudioChunk(1024);
      
      expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalledWith(
        expect.any(ArrayBuffer)
      );
    });

    it('should suppress chunks when user does not have turn', () => {
      mockTurnManager.canSendInput = false;
      
      simulateAudioChunk(1024);
      
      expect(mockRealtimeClient.sendBinaryFrame).not.toHaveBeenCalled();
    });

    it('should handle zero-byte chunks', () => {
      mockTurnManager.canSendInput = true;
      
      simulateAudioChunk(0);
      
      expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalledWith(
        expect.any(ArrayBuffer)
      );
    });

    it('should handle large chunks', () => {
      mockTurnManager.canSendInput = true;
      
      simulateAudioChunk(1024 * 1024); // 1MB
      
      expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalledWith(
        expect.any(ArrayBuffer)
      );
    });

    it('should check connection before sending', () => {
      mockTurnManager.canSendInput = true;
      mockRealtimeClient.isConnected.mockReturnValue(false);
      
      simulateAudioChunk(1024);
      
      expect(mockRealtimeClient.sendBinaryFrame).not.toHaveBeenCalled();
    });
  });

  describe('Turn State Management', () => {
    beforeEach(() => {
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      bridge.startStreaming();
    });

    describe('respectTurnState enabled (default)', () => {
      it('should respect turn state changes', () => {
        // Start with no turn
        mockTurnManager.canSendInput = false;
        simulateAudioChunk();
        expect(mockRealtimeClient.sendBinaryFrame).not.toHaveBeenCalled();
        
        // Get turn
        simulateTurnChange(true);
        simulateAudioChunk();
        expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalledTimes(1);
        
        // Lose turn
        simulateTurnChange(false);
        simulateAudioChunk();
        expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalledTimes(1); // No new calls
      });

      it('should track suppressed chunks', () => {
        mockTurnManager.canSendInput = false;
        
        simulateAudioChunk();
        simulateAudioChunk();
        
        const status = bridge.getStatus();
        expect(status.statistics.suppressed_chunks).toBe(2);
        expect(status.statistics.streamed_chunks).toBe(0);
      });
    });

    describe('respectTurnState disabled', () => {
      beforeEach(() => {
        bridge.updateConfig({ respectTurnState: false });
      });

      it('should ignore turn state', () => {
        mockTurnManager.canSendInput = false;
        
        simulateAudioChunk();
        
        expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalled();
      });

      it('should not track suppressed chunks', () => {
        mockTurnManager.canSendInput = false;
        
        simulateAudioChunk();
        simulateAudioChunk();
        
        const status = bridge.getStatus();
        expect(status.statistics.suppressed_chunks).toBe(0);
        expect(status.statistics.streamed_chunks).toBe(2);
      });
    });

    describe('configuration changes', () => {
      it('should apply config changes immediately', () => {
        // Start with respectTurnState enabled
        mockTurnManager.canSendInput = false;
        simulateAudioChunk();
        expect(mockRealtimeClient.sendBinaryFrame).not.toHaveBeenCalled();
        
        // Disable respectTurnState
        bridge.updateConfig({ respectTurnState: false });
        simulateAudioChunk();
        expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalled();
      });

      it('should emit status on config change', () => {
        const statusSpy = vi.fn();
        bridge.on('status', statusSpy);
        
        bridge.updateConfig({ respectTurnState: false });
        
        expect(statusSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            config: expect.objectContaining({
              respectTurnState: false
            })
          })
        );
      });
    });
  });

  describe('Status and Events', () => {
    describe('getStatus()', () => {
      it('should return complete status', () => {
        bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
        bridge.startStreaming();
        
        const status = bridge.getStatus();
        
        expect(status).toEqual({
          isStreaming: true,
          isConnected: true,
          hasClient: true,
          audioServiceStatus: {
            isRecording: false,
            state: 'idle'
          },
          statistics: {
            streamed_chunks: 0,
            suppressed_chunks: 0
          },
          config: {
            respectTurnState: true,
            debug: false
          }
        });
      });

      it('should update audio service status', () => {
        mockAudioService.getStatus.mockReturnValue({
          isRecording: true,
          state: 'recording'
        });
        
        const status = bridge.getStatus();
        
        expect(status.audioServiceStatus).toEqual({
          isRecording: true,
          state: 'recording'
        });
      });

      it('should reflect connection state', () => {
        bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
        mockRealtimeClient.isConnected.mockReturnValue(false);
        
        const status = bridge.getStatus();
        
        expect(status.isConnected).toBe(false);
      });
    });

    describe('resetStats()', () => {
      it('should reset statistics', () => {
        bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
        bridge.startStreaming();
        
        // Generate some stats
        mockTurnManager.canSendInput = true;
        simulateAudioChunk();
        mockTurnManager.canSendInput = false;
        simulateAudioChunk();
        
        let status = bridge.getStatus();
        expect(status.statistics.streamed_chunks).toBe(1);
        expect(status.statistics.suppressed_chunks).toBe(1);
        
        // Reset
        bridge.resetStats();
        
        status = bridge.getStatus();
        expect(status.statistics.streamed_chunks).toBe(0);
        expect(status.statistics.suppressed_chunks).toBe(0);
      });

      it('should emit status event on reset', () => {
        const statusSpy = vi.fn();
        bridge.on('status', statusSpy);
        
        bridge.resetStats();
        
        expect(statusSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            statistics: {
              streamed_chunks: 0,
              suppressed_chunks: 0
            }
          })
        );
      });
    });
  });

  describe('Error Handling', () => {
    beforeEach(() => {
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      bridge.startStreaming();
    });

    it('should handle send errors gracefully', () => {
      mockTurnManager.canSendInput = true;
      mockRealtimeClient.sendBinaryFrame.mockImplementation(() => {
        throw new Error('Send failed');
      });
      
      // Should not throw
      expect(() => simulateAudioChunk()).not.toThrow();
      
      // Should still track as streamed (attempted)
      const status = bridge.getStatus();
      expect(status.statistics.streamed_chunks).toBe(1);
    });

    it('should handle missing turn manager', () => {
      // Create client without turn manager
      const clientNoTurn = {
        isConnected: vi.fn().mockReturnValue(true),
        sendBinaryFrame: vi.fn(),
        getTurnManager: vi.fn().mockReturnValue(null)
      };
      
      bridge.setClient(clientNoTurn as unknown as RealtimeClient);
      bridge.startStreaming();
      
      // Should still work, always send chunks
      simulateAudioChunk();
      
      expect(clientNoTurn.sendBinaryFrame).toHaveBeenCalled();
    });

    it('should handle client disconnection during streaming', () => {
      mockTurnManager.canSendInput = true;
      
      // Disconnect client
      bridge.setClient(null);
      
      // Should have stopped streaming
      expect(unsubscribeAudio).toHaveBeenCalled();
      
      // New chunks should not cause errors
      expect(() => simulateAudioChunk()).not.toThrow();
    });
  });

  describe('Debug Mode', () => {
    it('should log debug messages when enabled', () => {
      const consoleLog = vi.spyOn(console, 'log').mockImplementation();
      
      bridge.updateConfig({ debug: true });
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      bridge.startStreaming();
      
      mockTurnManager.canSendInput = true;
      simulateAudioChunk(1024);
      
      expect(consoleLog).toHaveBeenCalledWith(
        expect.stringContaining('[AudioAgentCBridge]'),
        expect.stringContaining('Audio chunk')
      );
    });

    it('should not log debug messages when disabled', () => {
      const consoleLog = vi.spyOn(console, 'log').mockImplementation();
      
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      bridge.startStreaming();
      
      mockTurnManager.canSendInput = true;
      simulateAudioChunk(1024);
      
      // Only end-of-streaming log, no debug logs
      bridge.stopStreaming();
      
      expect(consoleLog).toHaveBeenCalledTimes(1);
      expect(consoleLog).toHaveBeenCalledWith(
        expect.stringContaining('Audio streaming stopped')
      );
    });
  });

  describe('Integration Scenarios', () => {
    it('should handle full streaming lifecycle', () => {
      // Connect
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      
      // Start streaming
      bridge.startStreaming();
      
      // User gets turn
      simulateTurnChange(true);
      
      // Stream some chunks
      simulateAudioChunk();
      simulateAudioChunk();
      
      expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalledTimes(2);
      
      // Agent takes turn
      simulateTurnChange(false);
      
      // Chunks suppressed
      simulateAudioChunk();
      
      expect(mockRealtimeClient.sendBinaryFrame).toHaveBeenCalledTimes(2);
      
      // Stop streaming
      bridge.stopStreaming();
      
      const status = bridge.getStatus();
      expect(status.statistics.streamed_chunks).toBe(2);
      expect(status.statistics.suppressed_chunks).toBe(1);
    });

    it('should handle reconnection scenario', () => {
      // Initial connection
      bridge.setClient(mockRealtimeClient as unknown as RealtimeClient);
      bridge.startStreaming();
      
      // Disconnect
      bridge.setClient(null);
      
      // Reconnect with new client
      const newClient = {
        isConnected: vi.fn().mockReturnValue(true),
        sendBinaryFrame: vi.fn(),
        getTurnManager: vi.fn().mockReturnValue(mockTurnManager)
      };
      
      bridge.setClient(newClient as unknown as RealtimeClient);
      bridge.startStreaming();
      
      // Should work with new client
      mockTurnManager.canSendInput = true;
      simulateAudioChunk();
      
      expect(newClient.sendBinaryFrame).toHaveBeenCalled();
    });
  });
});