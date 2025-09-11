/**
 * Simple Level 1 MediaStream and getUserMedia mocks - just stubs for testing
 */
import { vi } from 'vitest';

export const createMockMediaStream = () => ({
  getTracks: vi.fn(() => []),
  getAudioTracks: vi.fn(() => [{ 
    stop: vi.fn(),
    enabled: true,
    kind: 'audio'
  }]),
  getVideoTracks: vi.fn(() => []),
  active: true,
  id: 'mock-stream-id'
});

export const createMockGetUserMedia = () => 
  vi.fn().mockResolvedValue(createMockMediaStream());