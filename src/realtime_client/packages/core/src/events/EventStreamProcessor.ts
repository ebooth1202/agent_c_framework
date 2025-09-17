/**
 * EventStreamProcessor - Central coordinator for processing incoming events and building messages
 * Routes events to appropriate handlers and coordinates message building
 */

import { SessionManager } from '../session/SessionManager';
import { MessageBuilder } from './MessageBuilder';
import { ToolCallManager } from './ToolCallManager';
import { RichMediaHandler } from './RichMediaHandler';
import { 
  ServerEvent,
  TextDeltaEvent, 
  ThoughtDeltaEvent,
  CompletionEvent,
  ToolSelectDeltaEvent,
  ToolCallEvent,
  RenderMediaEvent,
  InteractionEvent,
  SystemMessageEvent,
  ErrorEvent,
  HistoryDeltaEvent,
  ChatSessionChangedEvent,
  UserMessageEvent,
  OpenAIUserMessageEvent,
  AnthropicUserMessageEvent,
  SubsessionStartedEvent,
  SubsessionEndedEvent
} from './types/ServerEvents';
import { Message, MessageContent, ContentPart, ToolCall } from './types/CommonTypes';
import { ChatSession } from '../types/chat-session';
import { 
  MessageParam,
  ContentBlockParam,
  isTextBlockParam,
  isImageBlockParam,
  isToolUseBlockParam,
  isDocumentBlockParam,
  isThinkingBlockParam
} from '../types/message-params';
import { Logger } from '../utils/logger';

/**
 * Central event processor that routes server events to appropriate handlers
 */
export class EventStreamProcessor {
  private messageBuilder: MessageBuilder;
  private toolCallManager: ToolCallManager;
  private richMediaHandler: RichMediaHandler;
  private sessionManager: SessionManager;
  private userSessionId: string | null = null;
  
  constructor(sessionManager: SessionManager) {
    this.sessionManager = sessionManager;
    this.messageBuilder = new MessageBuilder();
    this.toolCallManager = new ToolCallManager();
    this.richMediaHandler = new RichMediaHandler();
  }
  
  /**
   * Set the user session ID for sub-session detection
   */
  setUserSessionId(id: string): void {
    this.userSessionId = id;
    Logger.debug(`[EventStreamProcessor] User session ID set: ${id}`);
  }
  
  /**
   * Check if an event represents a sub-session
   */
  private isSubSession(event: any): boolean {
    // Primary check: use event fields if available
    if (event.user_session_id && event.session_id) {
      return event.session_id !== event.user_session_id;
    }
    
    // Fallback: use stored user session ID
    if (this.userSessionId && event.session_id) {
      return event.session_id !== this.userSessionId;
    }
    
    return false;
  }
  
  /**
   * Normalize MessageParam content to MessageContent format for UI compatibility
   * Handles the conversion from Anthropic ContentBlockParam[] to simplified ContentPart[]
   */
  private normalizeMessageContent(content: string | ContentBlockParam[]): MessageContent {
    // Handle simple string content
    if (typeof content === 'string') {
      return content;
    }
    
    // Handle array of content blocks
    if (Array.isArray(content)) {
      // First, check if all blocks are text blocks
      // If so, concatenate them into a single string for proper markdown rendering
      const allTextBlocks = content.every(block => isTextBlockParam(block));
      
      if (allTextBlocks) {
        // Concatenate all text blocks into a single string
        const concatenatedText = content
          .filter(isTextBlockParam)
          .map(block => block.text)
          .join('');
        
        return concatenatedText;
      }
      
      // For mixed content, convert ContentBlockParam[] to ContentPart[]
      const normalizedParts: ContentPart[] = [];
      
      for (const block of content) {
        if (isTextBlockParam(block)) {
          normalizedParts.push({
            type: 'text',
            text: block.text
          });
        } else if (isImageBlockParam(block)) {
          normalizedParts.push({
            type: 'image',
            source: block.source
          });
        } else if (isToolUseBlockParam(block)) {
          normalizedParts.push({
            type: 'tool_use',
            id: block.id,
            name: block.name,
            input: block.input
          });
        } else if ('type' in block && block.type === 'tool_result') {
          // Handle tool result blocks
          normalizedParts.push({
            type: 'tool_result',
            tool_use_id: (block as any).tool_use_id,
            content: typeof (block as any).content === 'string' ? (block as any).content : '',
            is_error: (block as any).is_error
          });
        } else if (isThinkingBlockParam(block)) {
          // Convert thinking blocks to text for now
          normalizedParts.push({
            type: 'text',
            text: `[Thinking] ${block.thinking}`
          });
        } else if (isDocumentBlockParam(block)) {
          // For documents, create a text representation
          normalizedParts.push({
            type: 'text',
            text: `[Document: ${block.title || 'Untitled'}]`
          });
        } else {
          // For any other block types, try to extract text or skip
          Logger.debug(`[EventStreamProcessor] Skipping unsupported content block type: ${(block as any).type}`);
        }
      }
      
      // If we have normalized parts, return them
      if (normalizedParts.length > 0) {
        return normalizedParts;
      }
    }
    
    // Return empty string as fallback
    return '';
  }
  
  /**
   * Convert a MessageParam to a Message with proper content normalization
   */
  private convertMessageParam(param: MessageParam): Message {
    const normalizedContent = this.normalizeMessageContent(param.content);
    
    return {
      role: param.role as Message['role'],
      content: normalizedContent,
      timestamp: new Date().toISOString(),
      format: 'text' as const
    };
  }
  
  /**
   * Convert ServerChatSession to ChatSession with normalized messages
   */
  private convertServerSession(serverSession: any): ChatSession {
    // Check if this is already a ChatSession (has Message[]) or needs conversion
    const needsConversion = serverSession.messages && 
      serverSession.messages.length > 0 && 
      serverSession.messages[0] && 
      !('timestamp' in serverSession.messages[0]);
    
    if (!needsConversion) {
      // Already in the correct format
      return serverSession as ChatSession;
    }
    
    // Convert messages from MessageParam[] to Message[]
    const convertedMessages: Message[] = [];
    
    if (serverSession.messages && Array.isArray(serverSession.messages)) {
      for (const msg of serverSession.messages) {
        try {
          const convertedMessage = this.convertMessageParam(msg);
          convertedMessages.push(convertedMessage);
        } catch (error) {
          Logger.error('[EventStreamProcessor] Failed to convert message:', error);
          // Create a fallback message
          convertedMessages.push({
            role: msg.role || 'assistant',
            content: '[Message could not be displayed]',
            timestamp: new Date().toISOString(),
            format: 'text'
          });
        }
      }
    }
    
    return {
      ...serverSession,
      messages: convertedMessages
    } as ChatSession;
  }
  
  /**
   * Process incoming server events
   */
  processEvent(event: ServerEvent): void {
    // Filter out ignored events early
    const IGNORED_EVENTS = ['history', 'history_delta', 'complete_thought', 'system_prompt'];
    
    if (IGNORED_EVENTS.includes(event.type)) {
      Logger.debug(`[EventStreamProcessor] Ignoring event type: ${event.type}`);
      return;
    }
    
    Logger.debug(`[EventStreamProcessor] Processing event: ${event.type}`);
    
    switch (event.type) {
      case 'interaction':
        this.handleInteraction(event);
        break;
      case 'text_delta':
        this.handleTextDelta(event);
        break;
      case 'thought_delta':
        this.handleThoughtDelta(event);
        break;
      case 'completion':
        this.handleCompletion(event);
        break;
      case 'tool_select_delta':
        this.handleToolSelect(event);
        break;
      case 'tool_call':
        this.handleToolCall(event);
        break;
      case 'render_media':
        this.handleRenderMedia(event);
        break;
      case 'system_message':
        this.handleSystemMessage(event);
        break;
      case 'error':
        this.handleError(event);
        break;
      case 'history_delta':
        this.handleHistoryDelta(event);
        break;
      case 'chat_session_changed':
        this.handleChatSessionChanged(event);
        break;
      case 'user_message':
        this.handleUserMessage(event as UserMessageEvent);
        break;
      case 'anthropic_user_message':
        this.handleAnthropicUserMessage(event as AnthropicUserMessageEvent);
        break;
      case 'subsession_started':
        this.handleSubsessionStarted(event as SubsessionStartedEvent);
        break;
      case 'subsession_ended':
        this.handleSubsessionEnded(event as SubsessionEndedEvent);
        break;
      // Other events are handled elsewhere or don't require processing here
      default:
        Logger.debug(`[EventStreamProcessor] Event type ${event.type} not handled by EventStreamProcessor`);
    }
  }
  
  /**
   * Handle interaction lifecycle events
   */
  private handleInteraction(event: InteractionEvent): void {
    if (event.started) {
      Logger.info(`[EventStreamProcessor] Interaction started: ${event.id}`);
      
      // Reset state for new interaction
      this.messageBuilder.reset();
      this.toolCallManager.reset();
    } else {
      Logger.info(`[EventStreamProcessor] Interaction ended: ${event.id}`);
    }
  }
  
  /**
   * Handle streaming text delta events
   */
  private handleTextDelta(event: TextDeltaEvent): void {
    // Start a new message if needed
    if (!this.messageBuilder.hasCurrentMessage()) {
      Logger.debug('[EventStreamProcessor] Starting new assistant message for text delta');
      this.messageBuilder.startMessage('assistant');
    }
    
    // Append the text delta
    Logger.debug('[EventStreamProcessor] Appending text delta:', {
      deltaContent: event.content,
      deltaLength: event.content.length
    });
    this.messageBuilder.appendText(event.content);
    
    // Update the streaming message in session manager
    const currentMessage = this.messageBuilder.getCurrentMessage();
    if (currentMessage) {
      Logger.debug('[EventStreamProcessor] Emitting message-streaming:', {
        sessionId: event.session_id,
        messageContent: currentMessage.content,
        messageRole: currentMessage.role,
        messageStatus: currentMessage.status
      });
      this.sessionManager.emit('message-streaming', {
        sessionId: event.session_id,
        message: currentMessage
      });
    } else {
      Logger.warn('[EventStreamProcessor] No current message after text delta');
    }
  }
  
  /**
   * Handle streaming thought delta events
   */
  private handleThoughtDelta(event: ThoughtDeltaEvent): void {
    // Start a new thought message if needed
    if (!this.messageBuilder.hasCurrentMessage() || this.messageBuilder.getCurrentMessageType() !== 'thought') {
      // If there's a regular message in progress, finalize it first
      if (this.messageBuilder.hasCurrentMessage()) {
        const message = this.messageBuilder.finalize();
        this.sessionManager.emit('message-complete', {
          sessionId: event.session_id,
          message
        });
      }
      this.messageBuilder.startMessage('thought');
      
      // Remove any "Agent is thinking..." notification when thought deltas start
      // We check all active notifications for the think tool
      const activeNotifications = this.toolCallManager.getActiveNotifications();
      activeNotifications.forEach(notification => {
        if (notification.toolName === 'think') {
          this.sessionManager.emit('tool-notification-removed', notification.id);
        }
      });
    }
    
    // Append the thought delta
    this.messageBuilder.appendText(event.content);
    
    // Update the streaming message
    const currentMessage = this.messageBuilder.getCurrentMessage();
    if (currentMessage) {
      this.sessionManager.emit('message-streaming', {
        sessionId: event.session_id,
        message: currentMessage
      });
    }
  }
  
  /**
   * Handle completion events
   */
  private handleCompletion(event: CompletionEvent): void {
    if (!event.running && this.messageBuilder.hasCurrentMessage()) {
      // Get any completed tool calls (which may include results)
      const completedToolCalls = this.toolCallManager.getCompletedToolCalls();
      
      // Separate tool calls from tool results
      const toolCalls = completedToolCalls.map(tc => ({
        id: tc.id,
        type: tc.type,
        name: tc.name,
        input: tc.input
      })) as ToolCall[];
      
      const toolResults = completedToolCalls
        .filter(tc => tc.result)
        .map(tc => tc.result!);
      
      // Finalize the message with metadata
      const message = this.messageBuilder.finalize({
        inputTokens: event.input_tokens,
        outputTokens: event.output_tokens,
        stopReason: event.stop_reason,
        toolCalls: toolCalls.length > 0 ? toolCalls : undefined,
        toolResults: toolResults.length > 0 ? toolResults : undefined
      });
      
      // Clear the completed tool calls after attaching them to the message
      if (completedToolCalls.length > 0) {
        this.toolCallManager.clearCompleted();
      }
      
      // Add to session and emit completion
      const session = this.sessionManager.getCurrentSession();
      if (session) {
        session.messages.push(message);
        if (event.input_tokens || event.output_tokens) {
          session.token_count += (event.input_tokens || 0) + (event.output_tokens || 0);
        }
        session.updated_at = new Date().toISOString();
      }
      
      this.sessionManager.emit('message-complete', {
        sessionId: event.session_id,
        message
      });
      
      // Reset message builder for next message
      this.messageBuilder.reset();
    }
  }
  
  /**
   * Handle tool selection events (before execution)
   */
  private handleToolSelect(event: ToolSelectDeltaEvent): void {
    const notification = this.toolCallManager.onToolSelect(event);
    
    // Special handling for the "think" tool
    const toolCall = event.tool_calls[0];
    if (toolCall && toolCall.name === 'think') {
      // For the think tool, we emit a special notification
      // The thought deltas will be handled separately
      this.sessionManager.emit('tool-notification', {
        ...notification,
        toolName: 'think',
        status: 'preparing' as const
      });
    } else {
      this.sessionManager.emit('tool-notification', notification);
    }
  }
  
  /**
   * Handle tool call events (during/after execution)
   */
  private handleToolCall(event: ToolCallEvent): void {
    // Check if this is the think tool - if so, ignore it
    const toolCall = event.tool_calls[0];
    if (toolCall && toolCall.name === 'think') {
      // For the think tool, we ignore the tool_call events
      // as the content is already rendered via thought deltas
      Logger.debug('[EventStreamProcessor] Ignoring tool_call event for think tool');
      // Still remove the notification
      this.sessionManager.emit('tool-notification-removed', toolCall.id);
      return;
    }
    
    if (event.active) {
      // Tool is executing
      const notification = this.toolCallManager.onToolCallActive(event);
      if (notification) {
        this.sessionManager.emit('tool-notification', notification);
      }
    } else {
      // Tool completed
      this.toolCallManager.onToolCallComplete(event);
      
      // Emit tool-call-complete event for UI to track results
      this.sessionManager.emit('tool-call-complete', {
        toolCalls: event.tool_calls,
        toolResults: event.tool_results
      });
      
      // Remove notifications for completed tools
      event.tool_calls.forEach(tc => {
        this.sessionManager.emit('tool-notification-removed', tc.id);
      });
    }
  }
  
  /**
   * Handle rich media rendering events
   */
  private handleRenderMedia(event: RenderMediaEvent): void {
    const media = this.richMediaHandler.processRenderMediaEvent(event);
    
    // Emit media event for UI
    this.sessionManager.emit('media-added', {
      sessionId: event.session_id,
      media: {
        id: media.id,
        role: 'assistant',
        type: 'media',
        content: media.content,
        contentType: media.type,
        timestamp: media.metadata.timestamp.toISOString(),
        status: 'complete',
        metadata: {
          ...media.metadata,
          timestamp: media.metadata.timestamp.toISOString()
        }
      }
    });
  }
  
  /**
   * Handle system messages
   */
  private handleSystemMessage(event: SystemMessageEvent): void {
    this.sessionManager.emit('system-notification', {
      type: 'system',
      severity: event.severity || 'info',
      content: event.content,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Handle error events
   */
  private handleError(event: ErrorEvent): void {
    this.sessionManager.emit('system-notification', {
      type: 'error',
      severity: 'error',
      content: event.message,
      source: event.source,
      timestamp: new Date().toISOString()
    });
  }
  
  /**
   * Handle history delta events (incremental history updates)
   */
  private handleHistoryDelta(event: HistoryDeltaEvent): void {
    const session = this.sessionManager.getCurrentSession();
    if (session) {
      // Convert and add the new messages to the session
      event.messages.forEach(msg => {
        // Check if the message needs conversion
        if (!('timestamp' in msg)) {
          // This is a MessageParam, convert it
          const convertedMessage = this.convertMessageParam(msg as any);
          session.messages.push(convertedMessage);
        } else {
          // Already a proper Message
          session.messages.push(msg);
        }
      });
      session.updated_at = new Date().toISOString();
      
      // Emit update event
      this.sessionManager.emit('sessions-updated', {
        sessions: this.sessionManager.getAllSessions()
      });
    }
  }
  
  /**
   * Handle chat session changed events
   * This is called when resuming an existing session or switching sessions
   */
  private handleChatSessionChanged(event: ChatSessionChangedEvent): void {
    if (!event.chat_session) {
      Logger.warn('[EventStreamProcessor] ChatSessionChangedEvent received without chat_session');
      return;
    }
    
    // Extract user_session_id if available for sub-session detection
    // ChatSessionChangedEvent doesn't extend SessionEvent, so check if it exists
    const eventWithSessionInfo = event as any;
    if (eventWithSessionInfo.user_session_id) {
      this.setUserSessionId(eventWithSessionInfo.user_session_id);
    } else if (event.chat_session.session_id) {
      // If no explicit user_session_id, assume the current session is the user session
      this.setUserSessionId(event.chat_session.session_id);
    }
    
    // Convert the server session to runtime ChatSession with normalized messages
    const session = this.convertServerSession(event.chat_session);
    
    Logger.info(`[EventStreamProcessor] Processing session change: ${session.session_id} with ${session.messages?.length || 0} messages and agent_config: ${session.agent_config?.key || 'none'}`);
    
    // Update the session in SessionManager with the converted version
    this.sessionManager.setCurrentSession(session);
    
    // Reset the message builder for new session context
    this.messageBuilder.reset();
    
    // ALWAYS emit session-messages-loaded event, even if messages array is empty
    // This ensures the UI clears the chat display when switching to a new empty session
    this.sessionManager.emit('session-messages-loaded', {
      sessionId: session.session_id,
      messages: session.messages || []  // Ensure we always pass an array
    });
  }
  
  /**
   * Handle Anthropic-specific user message events with sub-session detection
   */
  private handleAnthropicUserMessage(event: AnthropicUserMessageEvent): void {
    // Convert the Anthropic message to our normalized format
    const messageParam = event.message as any;
    let message: Message;
    
    // Check if it has the expected MessageParam structure
    if (messageParam && messageParam.content !== undefined && messageParam.role !== undefined) {
      message = this.convertMessageParam(messageParam);
    } else {
      // Fallback for malformed messages
      message = {
        role: 'user',
        content: JSON.stringify(messageParam) || '[User message]',
        timestamp: new Date().toISOString(),
        format: 'text'
      };
    }
    
    // Check for sub-session using SessionEvent fields
    if (this.isSubSession(event)) {
      // Add sub-session metadata to the message
      (message as any).isSubSession = true;
      (message as any).metadata = {
        sessionId: event.session_id,
        parentSessionId: event.parent_session_id,
        userSessionId: event.user_session_id
      };
      
      Logger.debug(`[EventStreamProcessor] Sub-session detected: ${event.session_id} (parent: ${event.parent_session_id})`);
    }
    
    // Add to current session
    const session = this.sessionManager.getCurrentSession();
    if (session) {
      session.messages.push(message);
      session.updated_at = new Date().toISOString();
      
      // Emit for UI consumption
      this.sessionManager.emit('message-added', {
        sessionId: session.session_id,
        message
      });
    }
    
    // Also emit the original user-message event for backward compatibility
    this.sessionManager.emit('user-message', {
      vendor: event.vendor,
      message: event.message
    });
  }
  
  /**
   * Handle user message events (vendor-specific format)
   */
  private handleUserMessage(event: UserMessageEvent | OpenAIUserMessageEvent | AnthropicUserMessageEvent): void {
    // Delegate to specific handler if it's an Anthropic message
    if (event.type === 'anthropic_user_message') {
      this.handleAnthropicUserMessage(event as AnthropicUserMessageEvent);
      return;
    }
    
    // Convert based on vendor
    let message: Message;
    
    if ('message' in event && event.vendor === 'openai') {
      // Handle OpenAI format if needed
      const openAiEvent = event as OpenAIUserMessageEvent;
      const openAiMessage = openAiEvent.message;
      
      // Try to extract content from OpenAI format
      if (typeof openAiMessage === 'string') {
        message = {
          role: 'user',
          content: openAiMessage,
          timestamp: new Date().toISOString(),
          format: 'text'
        };
      } else if (openAiMessage && typeof openAiMessage === 'object') {
        // Handle structured OpenAI message
        message = {
          role: 'user',
          content: (openAiMessage as any).content || JSON.stringify(openAiMessage),
          timestamp: new Date().toISOString(),
          format: 'text'
        };
      } else {
        message = {
          role: 'user',
          content: '[User message]',
          timestamp: new Date().toISOString(),
          format: 'text'
        };
      }
    } else {
      // Handle generic user message format
      // The event likely has a message field that's not in the type definition
      const eventWithMessage = event as any;
      
      if (eventWithMessage.message) {
        // Extract content from the message field
        if (typeof eventWithMessage.message === 'string') {
          message = {
            role: 'user',
            content: eventWithMessage.message,
            timestamp: new Date().toISOString(),
            format: 'text'
          };
        } else if (eventWithMessage.message && typeof eventWithMessage.message === 'object') {
          // Handle structured message - could be MessageParam format
          const messageParam = eventWithMessage.message;
          if (messageParam.content !== undefined) {
            message = {
              role: messageParam.role || 'user',
              content: messageParam.content,
              timestamp: new Date().toISOString(),
              format: 'text'
            };
          } else {
            // Fallback to stringifying the object
            message = {
              role: 'user',
              content: JSON.stringify(eventWithMessage.message),
              timestamp: new Date().toISOString(),
              format: 'text'
            };
          }
        } else {
          // Fallback if message field exists but is neither string nor object
          message = {
            role: 'user',
            content: '[User message]',
            timestamp: new Date().toISOString(),
            format: 'text'
          };
        }
      } else if (eventWithMessage.text) {
        // Try text field as fallback (might be present in some events)
        message = {
          role: 'user',
          content: eventWithMessage.text,
          timestamp: new Date().toISOString(),
          format: 'text'
        };
      } else {
        // Last resort fallback
        Logger.warn('[EventStreamProcessor] UserMessageEvent missing message content', event);
        message = {
          role: 'user',
          content: '[User message]',
          timestamp: new Date().toISOString(),
          format: 'text'
        };
      }
    }
    
    // Check for sub-session using SessionEvent fields (all UserMessageEvents extend SessionEvent)
    if (this.isSubSession(event)) {
      // Add sub-session metadata to the message
      (message as any).isSubSession = true;
      (message as any).metadata = {
        sessionId: event.session_id,
        parentSessionId: event.parent_session_id,
        userSessionId: event.user_session_id
      };
      
      Logger.debug(`[EventStreamProcessor] Sub-session detected in generic handler: ${event.session_id}`);
    }
    
    // Add to session
    const session = this.sessionManager.getCurrentSession();
    if (session) {
      session.messages.push(message);
      session.updated_at = new Date().toISOString();
      
      // Emit for UI consumption
      this.sessionManager.emit('message-added', {
        sessionId: session.session_id,
        message
      });
    }
    
    // Also emit the original user-message event for backward compatibility
    this.sessionManager.emit('user-message', {
      vendor: event.vendor,
      message: 'message' in event ? (event as any).message : undefined
    });
  }
  
  /**
   * Handle subsession started events
   */
  private handleSubsessionStarted(event: SubsessionStartedEvent): void {
    // Emit subsession start event for UI tracking
    this.sessionManager.emit('subsession-started', {
      subSessionType: event.sub_session_type,
      subAgentType: event.sub_agent_type,
      primeAgentKey: event.prime_agent_key,
      subAgentKey: event.sub_agent_key
    });
  }
  
  /**
   * Handle subsession ended events
   */
  private handleSubsessionEnded(_event: SubsessionEndedEvent): void {
    // Emit subsession end event for UI tracking
    this.sessionManager.emit('subsession-ended', {});
  }
  
  /**
   * Reset the processor state
   */
  reset(): void {
    this.messageBuilder.reset();
    this.toolCallManager.reset();
    Logger.info('[EventStreamProcessor] EventStreamProcessor reset');
  }
  
  /**
   * Clean up resources
   */
  destroy(): void {
    this.reset();
    Logger.info('[EventStreamProcessor] EventStreamProcessor destroyed');
  }
}