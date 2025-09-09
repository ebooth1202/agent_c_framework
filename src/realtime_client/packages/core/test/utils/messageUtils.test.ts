/**
 * Tests for message utility functions
 */

import { describe, it, expect } from 'vitest';
import { 
  normalizeMessageContent, 
  normalizeMessage, 
  normalizeMessages,
  isValidMessage 
} from '../../src/utils/messageUtils';

describe('messageUtils', () => {
  describe('normalizeMessageContent', () => {
    it('should return string content as is', () => {
      const content = 'Hello, world!';
      expect(normalizeMessageContent(content)).toBe(content);
    });
    
    it('should return empty string for null or undefined', () => {
      expect(normalizeMessageContent(null)).toBe('');
      expect(normalizeMessageContent(undefined)).toBe('');
    });
    
    it('should extract text property from object', () => {
      const content = { text: 'Hello from object' };
      expect(normalizeMessageContent(content)).toBe('Hello from object');
    });
    
    it('should extract nested content property from object', () => {
      const content = { content: 'Nested content' };
      expect(normalizeMessageContent(content)).toBe('Nested content');
    });
    
    it('should extract value property from object', () => {
      const content = { value: 'Value content' };
      expect(normalizeMessageContent(content)).toBe('Value content');
    });
    
    it('should handle array of strings', () => {
      const content = ['Hello', ' ', 'world'];
      expect(normalizeMessageContent(content)).toBe('Hello world');
    });
    
    it('should handle array of objects with text property', () => {
      const content = [
        { text: 'Part 1' },
        { text: ' ' },
        { text: 'Part 2' }
      ];
      expect(normalizeMessageContent(content)).toBe('Part 1 Part 2');
    });
    
    it('should handle mixed array', () => {
      const content = [
        'Direct text',
        { text: ' with object' },
        null,
        { other: 'ignored' }
      ];
      expect(normalizeMessageContent(content)).toBe('Direct text with object');
    });
    
    it('should stringify unknown object structure', () => {
      const content = { unknown: 'property', nested: { data: 'value' } };
      const result = normalizeMessageContent(content);
      expect(result).toContain('"unknown"');
      expect(result).toContain('"property"');
      expect(result).toContain('"nested"');
    });
    
    it('should handle numbers by converting to string', () => {
      expect(normalizeMessageContent(123)).toBe('123');
      expect(normalizeMessageContent(0)).toBe('0');
    });
    
    it('should handle booleans by converting to string', () => {
      expect(normalizeMessageContent(true)).toBe('true');
      expect(normalizeMessageContent(false)).toBe('false');
    });
  });
  
  describe('normalizeMessage', () => {
    it('should normalize a valid message', () => {
      const message = {
        role: 'assistant' as const,
        content: 'Hello',
        timestamp: '2024-01-01T00:00:00Z',
        format: 'text' as const
      };
      
      const result = normalizeMessage(message);
      expect(result).toEqual(message);
    });
    
    it('should normalize message with object content', () => {
      const message = {
        role: 'assistant' as const,
        content: { text: 'Hello from object' },
        timestamp: '2024-01-01T00:00:00Z'
      };
      
      const result = normalizeMessage(message);
      expect(result.content).toBe('Hello from object');
      expect(result.role).toBe('assistant');
      expect(result.format).toBe('text');
    });
    
    it('should handle invalid message input', () => {
      const result = normalizeMessage(null);
      expect(result.role).toBe('system');
      expect(result.content).toBe('');
      expect(result.format).toBe('text');
    });
    
    it('should provide defaults for missing fields', () => {
      const message = { content: 'Test' };
      const result = normalizeMessage(message);
      
      expect(result.role).toBe('assistant');
      expect(result.content).toBe('Test');
      expect(result.timestamp).toBeDefined();
      expect(result.format).toBe('text');
    });
  });
  
  describe('normalizeMessages', () => {
    it('should normalize an array of messages', () => {
      const messages = [
        { role: 'user' as const, content: 'Hello' },
        { role: 'assistant' as const, content: { text: 'Hi there' } },
        { role: 'user' as const, content: ['How', ' are', ' you?'] }
      ];
      
      const result = normalizeMessages(messages);
      
      expect(result).toHaveLength(3);
      expect(result[0].content).toBe('Hello');
      expect(result[1].content).toBe('Hi there');
      expect(result[2].content).toBe('How are you?');
    });
    
    it('should handle invalid input', () => {
      expect(normalizeMessages(null as any)).toEqual([]);
      expect(normalizeMessages(undefined as any)).toEqual([]);
      expect(normalizeMessages('not an array' as any)).toEqual([]);
    });
  });
  
  describe('isValidMessage', () => {
    it('should validate correct message structure', () => {
      const validMessage = {
        role: 'user',
        content: 'Hello',
        timestamp: '2024-01-01T00:00:00Z',
        format: 'text'
      };
      
      expect(isValidMessage(validMessage)).toBe(true);
    });
    
    it('should accept valid roles', () => {
      expect(isValidMessage({ role: 'user', content: 'test' })).toBe(true);
      expect(isValidMessage({ role: 'assistant', content: 'test' })).toBe(true);
      expect(isValidMessage({ role: 'system', content: 'test' })).toBe(true);
      expect(isValidMessage({ role: 'assistant (thought)', content: 'test' })).toBe(true);
    });
    
    it('should reject invalid roles', () => {
      expect(isValidMessage({ role: 'invalid', content: 'test' })).toBe(false);
    });
    
    it('should reject non-string content', () => {
      expect(isValidMessage({ role: 'user', content: { text: 'object' } })).toBe(false);
      expect(isValidMessage({ role: 'user', content: 123 })).toBe(false);
      expect(isValidMessage({ role: 'user', content: null })).toBe(false);
    });
    
    it('should reject missing required fields', () => {
      expect(isValidMessage({ role: 'user' })).toBe(false);
      expect(isValidMessage({ content: 'test' })).toBe(false);
      expect(isValidMessage({})).toBe(false);
    });
    
    it('should reject non-object inputs', () => {
      expect(isValidMessage(null)).toBe(false);
      expect(isValidMessage(undefined)).toBe(false);
      expect(isValidMessage('string')).toBe(false);
      expect(isValidMessage(123)).toBe(false);
    });
  });
});