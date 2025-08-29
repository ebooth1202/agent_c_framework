/**
 * Client-to-server event definitions for the Agent C Realtime API
 * These events are sent from the client to control the server
 */

import { Message } from './CommonTypes';

/**
 * Base interface for all client events
 */
export interface BaseClientEvent {
  type: string;
}

/**
 * Request list of available agents
 */
export interface GetAgentsEvent extends BaseClientEvent {
  type: 'get_agents';
}

/**
 * Set the active agent for the session
 */
export interface SetAgentEvent extends BaseClientEvent {
  type: 'set_agent';
  agent_key: string;
}

/**
 * Request list of available avatars
 */
export interface GetAvatarsEvent extends BaseClientEvent {
  type: 'get_avatars';
}

/**
 * Connect to an existing avatar session
 */
export interface SetAvatarSessionEvent extends BaseClientEvent {
  type: 'set_avatar_session';
  session_id: string;  // HeyGen session ID
  avatar_id: string;   // Avatar ID used to create the session
}

/**
 * Clear avatar session when HeyGen session ends
 */
export interface ClearAvatarSessionEvent extends BaseClientEvent {
  type: 'clear_avatar_session';
  session_id: string;
}

/**
 * Set the TTS voice for the current agent
 */
export interface SetAgentVoiceEvent extends BaseClientEvent {
  type: 'set_agent_voice';
  voice_id: string;
}

/**
 * Send text message to agent
 */
export interface TextInputEvent extends BaseClientEvent {
  type: 'text_input';
  text: string;
  file_ids?: string[];
}

/**
 * Create a new chat session
 */
export interface NewChatSessionEvent extends BaseClientEvent {
  type: 'new_chat_session';
  agent_key?: string;
}

/**
 * Resume an existing chat session
 */
export interface ResumeChatSessionEvent extends BaseClientEvent {
  type: 'resume_chat_session';
  session_id: string;
}

/**
 * Set the name/title for the current session
 */
export interface SetChatSessionNameEvent extends BaseClientEvent {
  type: 'set_chat_session_name';
  session_name: string;
}

/**
 * Update session metadata
 */
export interface SetSessionMetadataEvent extends BaseClientEvent {
  type: 'set_session_metadata';
  meta: Record<string, any>;
}

/**
 * Replace all messages in the current session
 */
export interface SetSessionMessagesEvent extends BaseClientEvent {
  type: 'set_session_messages';
  messages: Message[];
}

/**
 * Union type of all client events
 */
export type ClientEvent =
  | GetAgentsEvent
  | SetAgentEvent
  | GetAvatarsEvent
  | SetAvatarSessionEvent
  | ClearAvatarSessionEvent
  | SetAgentVoiceEvent
  | TextInputEvent
  | NewChatSessionEvent
  | ResumeChatSessionEvent
  | SetChatSessionNameEvent
  | SetSessionMetadataEvent
  | SetSessionMessagesEvent;

/**
 * Type guard to check if an object is a client event
 */
export function isClientEvent(obj: unknown): obj is ClientEvent {
  return obj && typeof obj.type === 'string' && [
    'get_agents',
    'set_agent',
    'get_avatars',
    'set_avatar_session',
    'clear_avatar_session',
    'set_agent_voice',
    'text_input',
    'new_chat_session',
    'resume_chat_session',
    'set_chat_session_name',
    'set_session_metadata',
    'set_session_messages'
  ].includes(obj.type);
}