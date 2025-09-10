/**
 * Basic test to verify test setup
 */

import { describe, it, expect } from 'vitest';

describe('Basic Test Setup', () => {
  it('should run a simple test', () => {
    expect(1 + 1).toBe(2);
  });

  it('should check for globals safely', () => {
    // Just check they exist or don't exist, don't fail either way
    const hasWebSocket = typeof WebSocket !== 'undefined';
    const hasAudioContext = typeof AudioContext !== 'undefined';
    
    console.log('WebSocket available:', hasWebSocket);
    console.log('AudioContext available:', hasAudioContext);
    
    // This test always passes, just logs the state
    expect(true).toBe(true);
  });
});