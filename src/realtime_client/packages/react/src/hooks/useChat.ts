/**
 * useChat - React hook for chat functionality
 * Provides interface for sending messages and accessing chat history
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import type { ChatSession, Message } from '@agentc/realtime-core';
import { ensureMessagesFormat } from '@agentc/realtime-core';
import { Logger } from '../utils/logger';
import { useRealtimeClientSafe } from '../providers/AgentCContext';

// Extended message type to include sub-session metadata
interface ExtendedMessage extends Message {
  isSubSession?: boolean;
  metadata?: {
    sessionId: string;
    parentSessionId?: string;
    userSessionId?: string;
  };
}

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
  messages: ExtendedMessage[];
  
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
  
  /** Current streaming message from agent */
  streamingMessage: ExtendedMessage | null;
  
  /** Error state */
  error: string | null;
  
  /** Get the last message */
  lastMessage: ExtendedMessage | null;
  
  /** Get messages from a specific role */
  getMessagesByRole: (role: 'user' | 'assistant' | 'system') => ExtendedMessage[];
  
  /** Check if a message is from a sub-session */
  isSubSessionMessage: (message: ExtendedMessage) => boolean;
}

/**
 * React hook for chat functionality
 * Provides interface to SessionManager and text messaging
 */
export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { maxMessages = 100 } = options;
  const client = useRealtimeClientSafe();
  
  // State
  const [messages, setMessages] = useState<ExtendedMessage[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<ExtendedMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Track the current streaming message ID to avoid duplicates
  const streamingMessageIdRef = useRef<string | null>(null);
  
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
  }, [client]);
  
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
      // Use sendText method - EventStreamProcessor will handle the message events
      client.sendText(text);
      
      // Don't add user message locally - EventStreamProcessor will emit message-added event
      // This ensures we get the proper sub-session metadata if applicable
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSending(false);
    }
  }, [client]);
  
  // Clear messages (client-side only)
  const clearMessages = useCallback(() => {
    setMessages([]);
    setStreamingMessage(null);
    streamingMessageIdRef.current = null;
  }, []);
  
  // Get messages by role
  const getMessagesByRole = useCallback((role: 'user' | 'assistant' | 'system'): ExtendedMessage[] => {
    return messages.filter(msg => msg.role === role);
  }, [messages]);
  
  // Check if a message is from a sub-session
  const isSubSessionMessage = useCallback((message: ExtendedMessage): boolean => {
    return message.isSubSession === true;
  }, []);
  
  // Subscribe to chat events
  useEffect(() => {
    if (!client) return;
    
    const sessionManager = client.getSessionManager();
    
    // Initial update
    updateChatInfo();
    
    // Handle message-added events (complete messages from EventStreamProcessor)
    const handleMessageAdded = (event: unknown) => {
      const messageEvent = event as { sessionId: string; message: ExtendedMessage };
      Logger.debug('[useChat] Message added event:', messageEvent);
      
      setMessages(prev => {
        const newMessages = [...prev, messageEvent.message];
        // Limit messages if needed
        if (maxMessages && maxMessages > 0 && newMessages.length > maxMessages) {
          return newMessages.slice(-maxMessages);
        }
        return newMessages;
      });
      
      // Clear streaming state if this was the streaming message
      if (streamingMessageIdRef.current === messageEvent.sessionId) {
        setStreamingMessage(null);
        streamingMessageIdRef.current = null;
        setIsAgentTyping(false);
      }
    };
    
    // Handle message-streaming events (partial messages being built)
    const handleMessageStreaming = (event: unknown) => {
      const streamEvent = event as { sessionId: string; message?: ExtendedMessage };
      Logger.debug('[useChat] Message streaming event:', streamEvent);
      
      // Only update if we have a valid message
      if (streamEvent.message) {
        setIsAgentTyping(true);
        setStreamingMessage(streamEvent.message);
        streamingMessageIdRef.current = streamEvent.sessionId;
      }
    };
    
    // Handle message-complete events (finalized messages)
    const handleMessageComplete = (event: unknown) => {
      const completeEvent = event as { sessionId: string; message: ExtendedMessage };
      Logger.debug('[useChat] Message complete event:', completeEvent);
      
      // Add the completed message to the messages array
      setMessages(prev => {
        const newMessages = [...prev, completeEvent.message];
        // Limit messages if needed
        if (maxMessages && maxMessages > 0 && newMessages.length > maxMessages) {
          return newMessages.slice(-maxMessages);
        }
        return newMessages;
      });
      
      // Clear streaming state
      setStreamingMessage(null);
      streamingMessageIdRef.current = null;
      setIsAgentTyping(false);
    };
    
    // Handle turn events from server for typing indicators
    const handleUserTurnStart = () => {
      setIsAgentTyping(false);
    };
    
    const handleUserTurnEnd = () => {
      // Don't automatically set typing - wait for actual message streaming
      // This prevents false typing indicators
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
        
        // Load messages from the session if present (for backward compatibility)
        if (sessionEvent.chat_session.messages && sessionEvent.chat_session.messages.length > 0) {
          const formattedMessages = ensureMessagesFormat(sessionEvent.chat_session.messages);
          const messagesToSet = maxMessages && maxMessages > 0 
            ? formattedMessages.slice(-maxMessages)
            : formattedMessages;
          setMessages(messagesToSet as ExtendedMessage[]);
        } else {
          // Clear messages if session has no messages
          setMessages([]);
        }
        
        // Clear any streaming state when switching sessions
        setStreamingMessage(null);
        streamingMessageIdRef.current = null;
        setIsAgentTyping(false);
      }
      // If no chat_session provided, don't update state (maintain existing messages)
    };
    
    // Handle session messages loaded event (from EventStreamProcessor)
    const handleSessionMessagesLoaded = (event: unknown) => {
      const messagesEvent = event as { sessionId?: string; messages?: ExtendedMessage[] };
      Logger.debug('[useChat] Session messages loaded event');
      Logger.debug('[useChat] Event data:', messagesEvent);
      
      if (messagesEvent.messages) {
        Logger.debug('[useChat] Messages from event:', messagesEvent.messages.length, 'messages');
        Logger.debug('[useChat] First 3 messages from event:', messagesEvent.messages.slice(0, 3));
        
        // Messages come from EventStreamProcessor already formatted with sub-session metadata
        const messagesToSet = maxMessages && maxMessages > 0
          ? messagesEvent.messages.slice(-maxMessages)
          : messagesEvent.messages;
        Logger.debug('[useChat] After slice for loaded messages:', messagesToSet.length, 'messages');
        Logger.debug('[useChat] Setting loaded messages - first 3:', messagesToSet.slice(0, 3));
        
        setMessages(messagesToSet as ExtendedMessage[]);
        // Clear any streaming state
        setStreamingMessage(null);
        streamingMessageIdRef.current = null;
        setIsAgentTyping(false);
      }
    };
    
    // Subscribe to turn events on client for typing indicators
    // These are always subscribed if client exists
    client.on('user_turn_start', handleUserTurnStart);
    client.on('user_turn_end', handleUserTurnEnd);
    client.on('chat_session_changed', handleSessionChanged);
    
    // Subscribe to SessionManager events for message handling (only if sessionManager exists)
    if (sessionManager) {
      sessionManager.on('message-added', handleMessageAdded);
      sessionManager.on('message-streaming', handleMessageStreaming);
      sessionManager.on('message-complete', handleMessageComplete);
      sessionManager.on('session-messages-loaded', handleSessionMessagesLoaded);
    }
    
    return () => {
      // client and sessionManager must be accessible in closure
      if (client) {
        client.off('user_turn_start', handleUserTurnStart);
        client.off('user_turn_end', handleUserTurnEnd);
        client.off('chat_session_changed', handleSessionChanged);
      }
      
      // Get sessionManager again in cleanup to ensure it's available
      const cleanupSessionManager = client?.getSessionManager();
      if (cleanupSessionManager) {
        cleanupSessionManager.off('message-added', handleMessageAdded);
        cleanupSessionManager.off('message-streaming', handleMessageStreaming);
        cleanupSessionManager.off('message-complete', handleMessageComplete);
        cleanupSessionManager.off('session-messages-loaded', handleSessionMessagesLoaded);
      }
    };
  }, [client, maxMessages, updateChatInfo]);
  
  // Computed properties
  const lastMessage: ExtendedMessage | null = messages.length > 0 ? messages[messages.length - 1]! : null;
  
  return {
    messages,
    currentSession,
    currentSessionId,
    sendMessage,
    clearMessages,
    isSending,
    isAgentTyping,
    streamingMessage,
    error,
    lastMessage,
    getMessagesByRole,
    isSubSessionMessage
  };
}