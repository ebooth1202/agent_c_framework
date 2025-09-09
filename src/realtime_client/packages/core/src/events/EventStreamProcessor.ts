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
  ChatSessionChangedEvent
} from './types/ServerEvents';
import { Logger } from '../utils/logger';

/**
 * Central event processor that routes server events to appropriate handlers
 */
export class EventStreamProcessor {
  private messageBuilder: MessageBuilder;
  private toolCallManager: ToolCallManager;
  private richMediaHandler: RichMediaHandler;
  private sessionManager: SessionManager;
  private logger: Logger;
  
  constructor(sessionManager: SessionManager) {
    this.sessionManager = sessionManager;
    this.messageBuilder = new MessageBuilder();
    this.toolCallManager = new ToolCallManager();
    this.richMediaHandler = new RichMediaHandler();
    this.logger = new Logger('EventStreamProcessor');
  }
  
  /**
   * Process incoming server events
   */
  processEvent(event: ServerEvent): void {
    this.logger.debug(`Processing event: ${event.type}`);
    
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
      // Other events are handled elsewhere or don't require processing here
      default:
        this.logger.debug(`Event type ${event.type} not handled by EventStreamProcessor`);
    }
  }
  
  /**
   * Handle interaction lifecycle events
   */
  private handleInteraction(event: InteractionEvent): void {
    if (event.started) {
      this.logger.info(`Interaction started: ${event.id}`);
      
      // Reset state for new interaction
      this.messageBuilder.reset();
      this.toolCallManager.reset();
    } else {
      this.logger.info(`Interaction ended: ${event.id}`);
    }
  }
  
  /**
   * Handle streaming text delta events
   */
  private handleTextDelta(event: TextDeltaEvent): void {
    // Start a new message if needed
    if (!this.messageBuilder.hasCurrentMessage()) {
      this.messageBuilder.startMessage('assistant');
    }
    
    // Append the text delta
    this.messageBuilder.appendText(event.content);
    
    // Update the streaming message in session manager
    const currentMessage = this.messageBuilder.getCurrentMessage();
    if (currentMessage) {
      this.sessionManager.emit('message-streaming', {
        sessionId: event.session_id,
        message: currentMessage
      });
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
      // Get any completed tool calls
      const toolCalls = this.toolCallManager.getCompletedToolCalls();
      
      // Finalize the message with metadata
      const message = this.messageBuilder.finalize({
        inputTokens: event.input_tokens,
        outputTokens: event.output_tokens,
        stopReason: event.stop_reason,
        toolCalls: toolCalls.length > 0 ? toolCalls : undefined
      });
      
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
    this.sessionManager.emit('tool-notification', notification);
  }
  
  /**
   * Handle tool call events (during/after execution)
   */
  private handleToolCall(event: ToolCallEvent): void {
    if (event.active) {
      // Tool is executing
      const notification = this.toolCallManager.onToolCallActive(event);
      if (notification) {
        this.sessionManager.emit('tool-notification', notification);
      }
    } else {
      // Tool completed
      this.toolCallManager.onToolCallComplete(event);
      
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
      // Add the new messages to the session
      event.messages.forEach(msg => {
        session.messages.push(msg);
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
      this.logger.warn('ChatSessionChangedEvent received without chat_session');
      return;
    }
    
    const session = event.chat_session;
    this.logger.info(`Processing session change: ${session.session_id} with ${session.messages?.length || 0} messages`);
    
    // Reset the message builder for new session context
    this.messageBuilder.reset();
    
    // Process existing messages to emit proper events for UI
    if (session.messages && session.messages.length > 0) {
      // Emit a session-messages-loaded event for bulk updates
      // This is more appropriate for pre-existing messages
      this.sessionManager.emit('session-messages-loaded', {
        sessionId: session.session_id,
        messages: session.messages
      });
    }
  }
  
  /**
   * Reset the processor state
   */
  reset(): void {
    this.messageBuilder.reset();
    this.toolCallManager.reset();
    this.logger.info('EventStreamProcessor reset');
  }
  
  /**
   * Clean up resources
   */
  destroy(): void {
    this.reset();
    this.logger.info('EventStreamProcessor destroyed');
  }
}