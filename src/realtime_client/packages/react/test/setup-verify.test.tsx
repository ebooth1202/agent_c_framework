/**
 * Test to verify setup file is loading correctly
 */

import { describe, it, expect, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, cleanup } from '@testing-library/react';
import React from 'react';

describe('Setup File Verification', () => {
  let mockFnFromPreviousTest: any;
  
  it('should have vitest globals available', () => {
    expect(vi).toBeDefined();
    expect(afterEach).toBeDefined();
  });

  it('should have React Testing Library available', () => {
    expect(render).toBeDefined();
    expect(screen).toBeDefined();
    expect(cleanup).toBeDefined();
  });

  it('should clean up mocks between tests - test 1', () => {
    const mockFn = vi.fn();
    mockFn('test1');
    expect(mockFn).toHaveBeenCalledWith('test1');
    expect(mockFn).toHaveBeenCalledTimes(1);
    
    // Store reference for next test
    mockFnFromPreviousTest = mockFn;
  });
  
  it('should clean up mocks between tests - test 2', () => {
    // Previous mock should be cleared
    if (mockFnFromPreviousTest) {
      expect(mockFnFromPreviousTest.mock.calls.length).toBe(0);
    }
    
    const newMockFn = vi.fn();
    newMockFn('test2');
    expect(newMockFn).toHaveBeenCalledWith('test2');
    expect(newMockFn).toHaveBeenCalledTimes(1);
  });

  it('should handle async operations', async () => {
    const promise = Promise.resolve('test');
    const result = await promise;
    expect(result).toBe('test');
  });

  it('should handle timers properly - fake timers', () => {
    vi.useFakeTimers();
    const callback = vi.fn();
    
    setTimeout(callback, 1000);
    vi.advanceTimersByTime(1000);
    
    expect(callback).toHaveBeenCalled();
    // Real timers will be restored by afterEach in setup.ts
  });
  
  it('should restore real timers after fake timer test', () => {
    // This test verifies that real timers are restored
    // If fake timers were still active, this would fail
    const startTime = Date.now();
    const endTime = Date.now();
    
    // Should be able to get real time
    expect(endTime).toBeGreaterThanOrEqual(startTime);
    expect(vi.isFakeTimers()).toBe(false);
  });

  it('should handle React component rendering', () => {
    const TestComponent = () => <div data-testid="test">Hello</div>;
    
    const { container } = render(<TestComponent />);
    expect(screen.getByTestId('test')).toBeInTheDocument();
    expect(container.querySelector('[data-testid="test"]')).toBeInTheDocument();
    
    // Component will be cleaned up by afterEach
  });
  
  it('should clean up React components between tests', () => {
    // Previous component should be cleaned up
    expect(screen.queryByTestId('test')).not.toBeInTheDocument();
    
    // Render new component
    const NewComponent = () => <div data-testid="new-test">New</div>;
    render(<NewComponent />);
    
    expect(screen.getByTestId('new-test')).toBeInTheDocument();
  });
  
  it('should handle async cleanup properly', async () => {
    let cleanupCalled = false;
    
    const asyncOperation = new Promise<void>((resolve) => {
      setTimeout(() => {
        cleanupCalled = true;
        resolve();
      }, 10);
    });
    
    await asyncOperation;
    expect(cleanupCalled).toBe(true);
  });
});