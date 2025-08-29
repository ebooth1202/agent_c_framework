/**
 * Common type definitions used throughout the Agent C Realtime API
 * These types are shared between client and server events
 */

/**
 * User information returned from authentication
 */
export interface User {
  user_id: string;
  user_name: string;
  email: string | null;
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  roles: string[];
  groups: string[];
  created_at: string | null;
  last_login: string | null;
}

/**
 * Agent configuration information
 */
export interface Agent {
  name: string;
  key: string;
  agent_description: string | null;
  category: string[];
}

/**
 * Extended agent configuration with runtime details
 */
export interface AgentConfiguration {
  version: number;
  name: string;
  key: string;
  model_id: string;
  agent_description: string | null;
  tools: string[];
  agent_params: Record<string, any>;
  prompt_metadata: Record<string, any>;
  persona: string;
  uid: string | null;
  category: string[];
}

/**
 * Avatar information from HeyGen
 */
export interface Avatar {
  avatar_id: string;
  created_at: number;
  default_voice: string;
  is_public: boolean;
  normal_preview: string;
  pose_name: string;
  status: string;
}

/**
 * Avatar session request configuration
 */
export interface AvatarSessionRequest {
  avatar_id: string | null;
  quality: string | null;
  voice: Record<string, any> | null;
  language: string | null;
  version: string | null;
  video_encoding: string | null;
  source: string | null;
  stt_settings: Record<string, any> | null;
  ia_is_livekit_transport: boolean | null;
  knowledge_base: string | null;
  knowledge_base_id: string | null;
  disable_idle_timeout: boolean | null;
  activity_idle_timeout: number | null;
}

/**
 * Avatar session information
 */
export interface AvatarSession {
  session_id: string;
  url: string;
  access_token: string;
  session_duration_limit: number;
  is_paid: boolean;
  realtime_endpoint: string;
  sdp: string | null;
  ice_servers: any[] | null;
  ice_servers2: any[] | null;
}

/**
 * Voice model configuration
 */
export interface Voice {
  voice_id: string;
  vendor: string;
  description: string;
  output_format: string;
}

/**
 * Toolset information
 */
export interface Toolset {
  name: string;
  description: string;
  schemas: Record<string, ToolSchema>;
}

/**
 * Tool schema definition
 */
export interface ToolSchema {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: Record<string, any>;
      required?: string[];
    };
  };
}

/**
 * Chat message structure
 */
export interface Message {
  role: 'user' | 'assistant' | 'system' | 'assistant (thought)';
  content: string;
  timestamp?: string;
  format?: 'text' | 'markdown';
}

/**
 * Chat session information
 */
export interface ChatSession {
  session_id: string;
  token_count: number;
  context_window_size: number;
  session_name: string | null;
  created_at: string | null;
  updated_at: string | null;
  deleted_at: string | null;
  user_id: string | null;
  metadata: Record<string, any>;
  messages: Message[];
  agent_config: AgentConfiguration;
}

/**
 * Tool call structure for function calling
 */
export interface ToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

/**
 * Tool result structure
 */
export interface ToolResult {
  call_id: string;
  output: string;
}

/**
 * Completion options from various vendors
 */
export interface CompletionOptions {
  [key: string]: any;
}

/**
 * Stop reason for completions
 */
export type StopReason = 'stop' | 'length' | 'tool_calls';

/**
 * Severity levels for system messages
 */
export type Severity = 'info' | 'warning' | 'error';

/**
 * Message format types
 */
export type MessageFormat = 'text' | 'markdown';

/**
 * Login response structure
 */
export interface LoginResponse {
  agent_c_token: string;
  heygen_token: string;
  user: User;
  agents: Agent[];
  avatars: Avatar[];
  toolsets: Toolset[];
  voices: Voice[];
  ui_session_id: string;
}

/**
 * Token refresh response
 */
export interface RefreshTokenResponse {
  agent_c_token: string;
  heygen_token: string;
}