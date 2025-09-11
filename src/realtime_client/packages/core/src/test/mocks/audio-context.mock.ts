/**
 * Simple Level 1 AudioContext mock - just stubs for testing
 */
import { vi } from 'vitest';

export const createMockAudioContext = () => ({
  createMediaStreamSource: vi.fn(() => ({ connect: vi.fn(), disconnect: vi.fn() })),
  createScriptProcessor: vi.fn(() => ({ 
    connect: vi.fn(),
    disconnect: vi.fn(),
    onaudioprocess: null
  })),
  createAnalyser: vi.fn(() => ({ connect: vi.fn() })),
  destination: {},
  sampleRate: 24000,
  currentTime: 0,
  state: 'running' as AudioContextState,
  close: vi.fn().mockResolvedValue(undefined),
  resume: vi.fn().mockResolvedValue(undefined)
});