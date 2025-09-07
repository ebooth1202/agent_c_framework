/**
 * Type verification test for useChat hook currentSessionId
 */

import { describe, it, expect } from 'vitest';
import type { UseChatReturn } from '../../src/hooks/useChat';

describe('useChat - currentSessionId types', () => {
  it('should include currentSessionId in the return type', () => {
    // This is a compile-time test to verify the type includes currentSessionId
    const mockReturn: UseChatReturn = {
      messages: [],
      currentSession: null,
      currentSessionId: null, // This should be required now
      sendMessage: async () => {},
      clearMessages: () => {},
      isSending: false,
      isAgentTyping: false,
      partialMessage: '',
      error: null,
      lastMessage: null,
      getMessagesByRole: () => []
    };
    
    // Verify the type allows string | null
    const testId1: UseChatReturn['currentSessionId'] = 'session-123';
    const testId2: UseChatReturn['currentSessionId'] = null;
    
    expect(mockReturn.currentSessionId).toBeDefined();
    expect(testId1).toBe('session-123');
    expect(testId2).toBeNull();
  });
  
  it('should maintain backward compatibility with existing properties', () => {
    const mockReturn: UseChatReturn = {
      messages: [],
      currentSession: null,
      currentSessionId: null,
      sendMessage: async () => {},
      clearMessages: () => {},
      isSending: false,
      isAgentTyping: false,
      partialMessage: '',
      error: null,
      lastMessage: null,
      getMessagesByRole: () => []
    };
    
    // All existing properties should still be present
    expect(mockReturn).toHaveProperty('messages');
    expect(mockReturn).toHaveProperty('currentSession');
    expect(mockReturn).toHaveProperty('sendMessage');
    expect(mockReturn).toHaveProperty('clearMessages');
    expect(mockReturn).toHaveProperty('isSending');
    expect(mockReturn).toHaveProperty('isAgentTyping');
    expect(mockReturn).toHaveProperty('partialMessage');
    expect(mockReturn).toHaveProperty('error');
    expect(mockReturn).toHaveProperty('lastMessage');
    expect(mockReturn).toHaveProperty('getMessagesByRole');
    
    // New property should also be present
    expect(mockReturn).toHaveProperty('currentSessionId');
  });
});