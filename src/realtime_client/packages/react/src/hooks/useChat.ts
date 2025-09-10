/**
 * useChat - React hook for chat functionality
 * Provides interface for sending messages and accessing chat history
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import type { ChatSession, Message } from '@agentc/realtime-core';
import { ensureMessagesFormat } from '@agentc/realtime-core';
import { Logger } from '../utils/logger';

// Define ChatMessage as alias for Message for consistency
type ChatMessage = Message;
import { useRealtimeClientSafe } from '../providers/AgentCContext';

/**
 * Options for the useChat hook
 */
export interface UseChatOptions {
  /** Maximum number of messages to keep in memory */
  maxMessages?: number;
  
  /** Whether to auto-scroll to new messages */
  autoScroll?: boolean;
}

/**
 * Return type for the useChat hook
 */
export interface UseChatReturn {
  /** Current chat messages */
  messages: ChatMessage[];
  
  /** Current session information */
  currentSession: ChatSession | null;
  
  /** Current session ID */
  currentSessionId: string | null;
  
  /** Send a text message */
  sendMessage: (text: string) => Promise<void>;
  
  /** Clear chat history (client-side only) */
  clearMessages: () => void;
  
  /** Whether a message is currently being sent */
  isSending: boolean;
  
  /** Whether the agent is currently typing/processing */
  isAgentTyping: boolean;
  
  /** Current partial message from agent (if streaming) */
  partialMessage: string;
  
  /** Error state */
  error: string | null;
  
  /** Get the last message */
  lastMessage: ChatMessage | null;
  
  /** Get messages from a specific role */
  getMessagesByRole: (role: 'user' | 'assistant' | 'system') => ChatMessage[];
}

/**
 * React hook for chat functionality
 * Provides interface to SessionManager and text messaging
 */
export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { maxMessages = 100 } = options;
  const client = useRealtimeClientSafe();
  
  // State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const [partialMessage, setPartialMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  
  // Refs for tracking message assembly
  const messageBufferRef = useRef<string>('');
  const currentMessageIdRef = useRef<string | null>(null);
  
  // Update session and messages from client
  const updateChatInfo = useCallback(() => {
    if (!client) {
      setCurrentSession(null);
      setCurrentSessionId(null);
      setMessages([]);
      return;
    }
    
    const sessionManager = client.getSessionManager();
    if (!sessionManager) {
      setCurrentSession(null);
      setCurrentSessionId(null);
      setMessages([]);
      return;
    }
    
    try {
      const session = sessionManager.getCurrentSession();
      setCurrentSession(session);
      setCurrentSessionId(session?.session_id || null);
      
      if (session) {
        // SessionManager doesn't have getMessageHistory, we'll track messages ourselves
        // Messages are accumulated from events
      }
      
      setError(null);
    } catch (err) {
      console.error('Failed to get chat information:', err);
      setError(err instanceof Error ? err.message : 'Failed to get chat information');
    }
  }, [client, maxMessages]);
  
  // Send message
  const sendMessage = useCallback(async (text: string): Promise<void> => {
    if (!client) {
      throw new Error('Client not available');
    }
    
    if (!client.isConnected()) {
      throw new Error('Not connected to server');
    }
    
    if (!text.trim()) {
      throw new Error('Message cannot be empty');
    }
    
    setIsSending(true);
    setError(null);
    
    try {
      // Use sendText method instead of textInput
      client.sendText(text);
      
      // Add user message to local state immediately for responsiveness
      const userMessage: ChatMessage = {
        role: 'user',
        content: text,
        timestamp: new Date().toISOString(),
        format: 'text'
      };
      
      setMessages(prev => {
        const newMessages = [...prev, userMessage];
        // Limit messages if needed
        if (maxMessages && newMessages.length > maxMessages) {
          return newMessages.slice(-maxMessages);
        }
        return newMessages;
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSending(false);
    }
  }, [client, maxMessages]);
  
  // Clear messages (client-side only)
  const clearMessages = useCallback(() => {
    setMessages([]);
    setPartialMessage('');
    messageBufferRef.current = '';
    currentMessageIdRef.current = null;
  }, []);
  
  // Get messages by role
  const getMessagesByRole = useCallback((role: 'user' | 'assistant' | 'system'): ChatMessage[] => {
    return messages.filter(msg => msg.role === role);
  }, [messages]);
  
  // Subscribe to chat events
  useEffect(() => {
    if (!client) return;
    
    // Initial update
    updateChatInfo();
    
    // Handle text delta events (streaming text from agent)
    const handleTextDelta = (event: unknown) => {
      setIsAgentTyping(true);
      
      // Type guard for event properties
      const textEvent = event as { text?: string; item_id?: string };
      
      // Update partial message
      messageBufferRef.current += textEvent.text || '';
      setPartialMessage(messageBufferRef.current);
      
      // Store message ID for completion
      if (textEvent.item_id) {
        currentMessageIdRef.current = textEvent.item_id;
      }
    };
    
    // Handle completion events (when agent is done)
    const handleCompletion = (event: unknown) => {
      // Type guard for event properties
      const completionEvent = event as { running?: boolean };
      
      if (completionEvent.running === false && messageBufferRef.current) {
        setIsAgentTyping(false);
        
        // Create complete message
        const agentMessage: ChatMessage = {
          role: 'assistant',
          content: messageBufferRef.current,
          timestamp: new Date().toISOString(),
          format: 'text'
        };
        
        setMessages(prev => {
          const newMessages = [...prev, agentMessage];
          // Limit messages if needed
          if (maxMessages && newMessages.length > maxMessages) {
            return newMessages.slice(-maxMessages);
          }
          return newMessages;
        });
        
        // Clear partial message
        setPartialMessage('');
        messageBufferRef.current = '';
        currentMessageIdRef.current = null;
      }
    };
    
    // Handle turn events from server
    const handleUserTurnStart = () => {
      setIsAgentTyping(false);
    };
    
    const handleUserTurnEnd = () => {
      setIsAgentTyping(true);
      
      // Agent is now typing
    };
    
    // Handle session change events
    const handleSessionChanged = (event: unknown) => {
      const sessionEvent = event as { chat_session?: ChatSession };
      if (sessionEvent.chat_session) {
        Logger.debug('[useChat] Session changed event received');
        Logger.debug('[useChat] Session ID:', sessionEvent.chat_session.session_id);
        Logger.debug('[useChat] Raw messages from server:', sessionEvent.chat_session.messages?.length || 0, 'messages');
        
        setCurrentSession(sessionEvent.chat_session);
        setCurrentSessionId(sessionEvent.chat_session.session_id);
        
        // Load existing messages from the session and ensure proper format
        if (sessionEvent.chat_session.messages && sessionEvent.chat_session.messages.length > 0) {
          Logger.debug('[useChat] First 3 raw messages:', sessionEvent.chat_session.messages.slice(0, 3));
          
          const formattedMessages = ensureMessagesFormat(sessionEvent.chat_session.messages);
          Logger.debug('[useChat] After ensureMessagesFormat:', formattedMessages.length, 'messages');
          Logger.debug('[useChat] First 3 formatted messages:', formattedMessages.slice(0, 3));
          
          const messagesToSet = formattedMessages.slice(-maxMessages);
          Logger.debug('[useChat] After slice(-maxMessages):', messagesToSet.length, 'messages');
          Logger.debug('[useChat] maxMessages value:', maxMessages);
          Logger.debug('[useChat] Setting messages - first 3:', messagesToSet.slice(0, 3));
          
          setMessages(messagesToSet);
          // Clear any partial message when switching sessions
          setPartialMessage('');
          messageBufferRef.current = '';
          currentMessageIdRef.current = null;
        } else {
          Logger.debug('[useChat] No messages in session, clearing');
          // Clear messages if new session has no messages
          clearMessages();
        }
      }
    };
    
    // Handle session messages loaded event (from EventStreamProcessor)
    const handleSessionMessagesLoaded = (event: unknown) => {
      const messagesEvent = event as { sessionId?: string; messages?: Message[] };
      Logger.debug('[useChat] Session messages loaded event');
      Logger.debug('[useChat] Event data:', messagesEvent);
      
      if (messagesEvent.messages) {
        Logger.debug('[useChat] Messages from event:', messagesEvent.messages.length, 'messages');
        Logger.debug('[useChat] First 3 messages from event:', messagesEvent.messages.slice(0, 3));
        
        // Update messages with the loaded messages, ensuring proper format
        const formattedMessages = ensureMessagesFormat(messagesEvent.messages);
        Logger.debug('[useChat] After format:', formattedMessages.length, 'messages');
        
        const messagesToSet = formattedMessages.slice(-maxMessages);
        Logger.debug('[useChat] After slice for loaded messages:', messagesToSet.length, 'messages');
        Logger.debug('[useChat] Setting loaded messages - first 3:', messagesToSet.slice(0, 3));
        
        setMessages(messagesToSet);
        // Clear any partial message
        setPartialMessage('');
        messageBufferRef.current = '';
        currentMessageIdRef.current = null;
      }
    };
    
    // Subscribe to events
    client.on('text_delta', handleTextDelta);
    client.on('completion', handleCompletion);
    client.on('user_turn_start', handleUserTurnStart);
    client.on('user_turn_end', handleUserTurnEnd);
    client.on('chat_session_changed', handleSessionChanged);
    
    // Subscribe to SessionManager events if available
    const sessionManager = client.getSessionManager();
    if (sessionManager) {
      sessionManager.on('session-messages-loaded', handleSessionMessagesLoaded);
    }
    
    return () => {
      client.off('text_delta', handleTextDelta);
      client.off('completion', handleCompletion);
      client.off('user_turn_start', handleUserTurnStart);
      client.off('user_turn_end', handleUserTurnEnd);
      client.off('chat_session_changed', handleSessionChanged);
      
      // Unsubscribe from SessionManager events
      const sessionManager = client.getSessionManager();
      if (sessionManager) {
        sessionManager.off('session-messages-loaded', handleSessionMessagesLoaded);
      }
    };
  }, [client, maxMessages, updateChatInfo, clearMessages]);
  
  // Computed properties
  const lastMessage: ChatMessage | null = messages.length > 0 ? messages[messages.length - 1]! : null;
  
  return {
    messages,
    currentSession,
    currentSessionId,
    sendMessage,
    clearMessages,
    isSending,
    isAgentTyping,
    partialMessage,
    error,
    lastMessage,
    getMessagesByRole
  };
}