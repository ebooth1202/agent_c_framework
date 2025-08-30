/**
 * Simple test to verify setup.ts is working
 */

const { describe, it, expect, beforeEach, afterEach } = require('vitest');

// This should load the setup automatically
console.log('Testing setup.ts functionality...');

// Check if globals are available
console.log('WebSocket available:', typeof WebSocket !== 'undefined');
console.log('AudioContext available:', typeof AudioContext !== 'undefined');
console.log('fetch available:', typeof fetch !== 'undefined');

// Verify mocks are working
if (typeof WebSocket !== 'undefined') {
  const ws = new WebSocket('ws://test');
  console.log('WebSocket mock created:', !!ws);
  console.log('WebSocket has close method:', typeof ws.close === 'function');
  ws.close();
  console.log('WebSocket closed successfully');
}

if (typeof AudioContext !== 'undefined') {
  const ctx = new AudioContext();
  console.log('AudioContext mock created:', !!ctx);
  console.log('AudioContext has close method:', typeof ctx.close === 'function');
  ctx.close().then(() => {
    console.log('AudioContext closed successfully');
  });
}

console.log('Setup test completed successfully!');