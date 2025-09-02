/**
 * Server-to-client event definitions for the Agent C Realtime API
 * These events are sent from the server to update the client
 */

import {
  Agent,
  AgentConfiguration,
  Avatar,
  AvatarSessionRequest,
  AvatarSession,
  ChatSession,
  ChatSessionQueryResponse,
  Voice,
  Message,
  ToolCall,
  ToolResult,
  CompletionOptions,
  StopReason,
  Severity,
  MessageFormat
} from './CommonTypes';

/**
 * Base interface for all server events
 */
export interface BaseServerEvent {
  type: string;
}

/**
 * Response to get_agents with available agents
 */
export interface AgentListEvent extends BaseServerEvent {
  type: 'agent_list';
  agents: Agent[];
}

/**
 * Notification that agent configuration has changed
 */
export interface AgentConfigurationChangedEvent extends BaseServerEvent {
  type: 'agent_configuration_changed';
  agent_config: AgentConfiguration;
}

/**
 * Response to get_avatars with available avatars
 */
export interface AvatarListEvent extends BaseServerEvent {
  type: 'avatar_list';
  avatars: Avatar[];
}

/**
 * Notification that avatar connection status has changed
 */
export interface AvatarConnectionChangedEvent extends BaseServerEvent {
  type: 'avatar_connection_changed';
  avatar_session_request: AvatarSessionRequest;
  avatar_session: AvatarSession;
}

/**
 * Notification that chat session has been updated
 */
export interface ChatSessionChangedEvent extends BaseServerEvent {
  type: 'chat_session_changed';
  chat_session: ChatSession;
}

/**
 * Notification that session name was updated
 */
export interface ChatSessionNameChangedEvent extends BaseServerEvent {
  type: 'chat_session_name_changed';
  session_name: string;
}

/**
 * Notification that session metadata was updated
 */
export interface SessionMetadataChangedEvent extends BaseServerEvent {
  type: 'session_metadata_changed';
  meta: Record<string, any>;
}

/**
 * Streaming text content from the agent
 */
export interface TextDeltaEvent extends BaseServerEvent {
  type: 'text_delta';
  session_id: string;
  role: 'assistant';
  content: string;
  format: MessageFormat;
}

/**
 * Streaming thought content from the agent
 */
export interface ThoughtDeltaEvent extends BaseServerEvent {
  type: 'thought_delta';
  session_id: string;
  role: 'assistant (thought)';
  content: string;
  format: MessageFormat;
}

/**
 * Completion status updates
 */
export interface CompletionEvent extends BaseServerEvent {
  type: 'completion';
  session_id: string;
  role: 'assistant';
  running: boolean;
  completion_options: CompletionOptions;
  stop_reason?: StopReason;
  input_tokens?: number;
  output_tokens?: number;
}

/**
 * Interaction lifecycle events
 */
export interface InteractionEvent extends BaseServerEvent {
  type: 'interaction';
  session_id: string;
  role: 'assistant';
  started: boolean;
  id: string;
}

/**
 * Complete message history update
 */
export interface HistoryEvent extends BaseServerEvent {
  type: 'history';
  session_id: string;
  role: 'system';
  messages: Message[];
}

/**
 * Tool execution events
 */
export interface ToolCallEvent extends BaseServerEvent {
  type: 'tool_call';
  session_id: string;
  role: 'assistant';
  active: boolean;
  vendor: string;
  tool_calls: ToolCall[];
  tool_results?: ToolResult[];
}

/**
 * System notifications and errors
 */
export interface SystemMessageEvent extends BaseServerEvent {
  type: 'system_message';
  session_id: string;
  role: 'system';
  content: string;
  format: MessageFormat;
  severity?: Severity;
}

/**
 * Notification that the server is ready to accept user input
 */
export interface UserTurnStartEvent extends BaseServerEvent {
  type: 'user_turn_start';
}

/**
 * Notification that the server has received user input and is no longer accepting input
 */
export interface UserTurnEndEvent extends BaseServerEvent {
  type: 'user_turn_end';
}

/**
 * Notification that the agent's voice has been updated
 */
export interface AgentVoiceChangedEvent extends BaseServerEvent {
  type: 'agent_voice_changed';
  voice: Voice;
}

/**
 * Error notifications
 */
export interface ErrorEvent extends BaseServerEvent {
  type: 'error';
  message: string;
  source?: string;
}

/**
 * Response to get_user_sessions request with paginated session list
 */
export interface GetUserSessionsResponseEvent extends BaseServerEvent {
  type: 'get_user_sessions_response';
  sessions: ChatSessionQueryResponse;
}

/**
 * Union type of all server events
 */
export type ServerEvent =
  | AgentListEvent
  | AgentConfigurationChangedEvent
  | AvatarListEvent
  | AvatarConnectionChangedEvent
  | ChatSessionChangedEvent
  | ChatSessionNameChangedEvent
  | SessionMetadataChangedEvent
  | TextDeltaEvent
  | ThoughtDeltaEvent
  | CompletionEvent
  | InteractionEvent
  | HistoryEvent
  | ToolCallEvent
  | SystemMessageEvent
  | UserTurnStartEvent
  | UserTurnEndEvent
  | AgentVoiceChangedEvent
  | ErrorEvent
  | GetUserSessionsResponseEvent;

/**
 * Type guard to check if an object is a server event
 */
export function isServerEvent(obj: unknown): obj is ServerEvent {
  return !!obj && typeof obj === 'object' && 'type' in obj && typeof (obj as any).type === 'string' && [
    'agent_list',
    'agent_configuration_changed',
    'avatar_list',
    'avatar_connection_changed',
    'chat_session_changed',
    'chat_session_name_changed',
    'session_metadata_changed',
    'text_delta',
    'thought_delta',
    'completion',
    'interaction',
    'history',
    'tool_call',
    'system_message',
    'user_turn_start',
    'user_turn_end',
    'agent_voice_changed',
    'error',
    'get_user_sessions_response'
  ].includes((obj as any).type);
}