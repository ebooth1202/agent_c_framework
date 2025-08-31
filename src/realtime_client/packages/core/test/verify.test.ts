/**
 * Simple verification test
 */

import { describe, it, expect } from 'vitest';

describe('Verification Test', () => {
  it('should complete immediately', () => {
    console.log('Core package test running');
    expect(true).toBe(true);
  });

  it('should do basic math', () => {
    expect(1 + 1).toBe(2);
  });
});