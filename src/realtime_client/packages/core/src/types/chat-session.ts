/**
 * Agent C ChatSession TypeScript Definitions
 * 
 * This file contains comprehensive type definitions for the Agent C ChatSession
 * model and all related types, converted from the Python implementation.
 * 
 * These types match the actual server data structures exactly.
 */

import type { MessageParam } from './message-params';

// Re-import Message type from CommonTypes for compatibility
// The Message type is the runtime version with additional fields
// MessageParam is the server data structure
import type { Message } from '../events/types/CommonTypes';

// Core ChatSession Interfaces
export interface ChatSessionIndexEntry {
  session_id: string; // Unique identifier for the chat session
  session_name?: string | null; // The name of the session, if any (can be null)
  created_at?: string | null; // ISO timestamp, defaults to current time (can be null)
  updated_at?: string | null; // ISO timestamp, defaults to current time (can be null)
  user_id?: string | null; // The user ID associated with the session (defaults to "admin", can be null)
  agent_key?: string; // The key of the agent associated with the session
  agent_name?: string; // The name of the agent associated with the session
}

export interface ChatSessionQueryResponse {
  chat_sessions: ChatSessionIndexEntry[]; // List of chat session index entries (defaults to empty array)
  total_sessions: number; // Total number of sessions available for the query (defaults to 0)
  offset: number; // The offset used in the query (defaults to 0)
}

export interface ChatSession {
  version: number; // Version of the chat session schema (defaults to 1)
  session_id: string; // Unique identifier generated using mnemonic slugs (defaults to 2-word slug)
  token_count: number; // The number of tokens used in the session (defaults to 0)
  context_window_size: number; // The number of tokens in the context window (defaults to 0)
  session_name?: string | null; // The name of the session, if any
  created_at?: string; // ISO timestamp when created (defaults to current time)
  updated_at?: string; // ISO timestamp when last updated (defaults to current time)
  deleted_at?: string | null; // Timestamp when the session was deleted
  user_id?: string; // The user ID associated with the session (defaults to "admin")
  metadata?: Record<string, any>; // Metadata associated with the session (defaults to empty object)
  messages: Message[]; // List of messages in the session (runtime type with additional fields)
  agent_config?: CurrentAgentConfiguration; // Configuration for the agent associated with the session
  vendor: string; // Computed field: Returns "anthropic", "openai", or "none" based on model_id
  display_name: string; // Computed field: Returns session_name or generated name with agent
}

/**
 * Server version of ChatSession with MessageParam[]
 * Used when receiving raw data from the server
 */
export interface ServerChatSession {
  version: number;
  session_id: string;
  token_count: number;
  context_window_size: number;
  session_name?: string | null;
  created_at?: string;
  updated_at?: string;
  deleted_at?: string | null;
  user_id?: string;
  metadata?: Record<string, any>;
  messages: MessageParam[]; // Server sends MessageParam structure
  agent_config?: CurrentAgentConfiguration;
  vendor: string;
  display_name: string;
}

// Agent Configuration Types
export interface AgentCatalogEntry {
  name: string; // Name of the agent configuration
  key: string; // Key for the agent configuration, used for identification
  agent_description?: string; // A description of the agent's purpose and capabilities
  category: string[]; // List of categories this agent belongs to (from most to least general)
}

// Legacy V1 Configuration (for compatibility)
export interface AgentConfigurationV1 {
  version: 1;
  name: string;
  key: string;
  model_id: string;
  agent_description?: string;
  tools: string[];
  agent_params?: CompletionParams;
  prompt_metadata?: Record<string, any>;
  persona: string;
  uid?: string;
  category: string[];
}

// Current V2 Configuration
export interface AgentConfigurationV2 {
  version: 2; // Configuration version
  name: string; // Name of the persona file
  key: string; // Key for the agent configuration, used for identification (defaults to name if not provided)
  model_id: string; // ID of the LLM model being used by the agent
  agent_description?: string; // A description of the agent's purpose and capabilities
  tools: string[]; // List of enabled toolset names the agent can use (defaults to empty array)
  agent_params?: CompletionParams; // Parameters for the interaction with the agent
  prompt_metadata?: Record<string, any>; // Metadata for the prompt
  persona: string; // Persona prompt defining the agent's behavior
  uid?: string; // Unique identifier for the configuration
  category: string[]; // List of categories this agent belongs to (from most to least general)
}

// Type aliases for convenience
export type AgentConfiguration = AgentConfigurationV1 | AgentConfigurationV2;
export type CurrentAgentConfiguration = AgentConfigurationV2;

// Completion Parameters Types
export interface CommonCompletionParams {
  model_name: string; // The name of the model to use for the interaction
  max_tokens?: number; // The maximum number of tokens to generate (defaults to backend defaults)
  user_name?: string; // The name of the user interacting with the agent
  auth?: ApiAuthInfo; // The vendor API key or authentication info to use for the agent
}

// Claude Completion Parameters
export interface ClaudeNonReasoningParams extends CommonCompletionParams {
  type: "claude_non_reasoning"; // The type of the completion params
  temperature?: number; // The temperature to use for the interaction (do not combine with top_p)
}

export interface ClaudeReasoningParams extends CommonCompletionParams {
  type: "claude_reasoning"; // The type of the completion params
  budget_tokens?: number; // The budget tokens to use for the interaction (must be higher than max tokens)
  max_searches?: number; // The maximum number of web searches for the claude models to perform
}

// GPT Completion Parameters
export interface GPTNonReasoningCompletionParams extends CommonCompletionParams {
  type: "g_p_t_non_reasoning"; // The type of the completion params
  tool_choice?: string | Record<string, any>; // The tool choice to use for the interaction (see OpenAI API docs)
  voice?: string; // Voice parameter for audio generation
  presence_penalty?: number; // Number between -2.0 and 2.0 for penalizing new tokens (defaults to 0)
  seed?: number; // For deterministic sampling (Beta feature)
  service_tier?: string; // See OpenAI Docs for details
  stop?: string | string[]; // Up to 4 sequences where the API will stop generating tokens
  temperature?: number; // The temperature to use for the interaction (do not combine with top_p)
}

export interface GPTReasoningCompletionParams extends CommonCompletionParams {
  type: "g_p_t_reasoning"; // The type of the completion params
  tool_choice?: string | Record<string, any>; // The tool choice to use for the interaction (see OpenAI API docs)
  voice?: string; // Voice parameter for audio generation
  presence_penalty?: number; // Number between -2.0 and 2.0 for penalizing new tokens (defaults to 0)
  seed?: number; // For deterministic sampling (Beta feature)
  service_tier?: string; // See OpenAI Docs for details
  stop?: string | string[]; // Up to 4 sequences where the API will stop generating tokens
  reasoning_effort?: string; // The reasoning effort to use for the interaction (must be low, medium, or high)
}

// Union type for all completion parameter variants
export type CompletionParams = 
  | ClaudeNonReasoningParams
  | ClaudeReasoningParams
  | GPTNonReasoningCompletionParams
  | GPTReasoningCompletionParams;

// Authentication Types
export interface SimpleAuthInfo {
  api_key: string; // The API key to use for the interaction
}

export interface AzureAuthInfo {
  endpoint: string; // The Azure OpenAI endpoint to use for the interaction
  api_key: string; // The Azure OpenAI API key to use for the interaction
  api_version?: string; // The Azure OpenAI API version to use (defaults to "2024-08-01-preview")
}

export interface BedrockAuthInfo {
  aws_access_key?: string; // The AWS access key to use for the interaction
  aws_secret_key?: string; // The AWS secret key to use for the interaction
  aws_region?: string; // The AWS region to use for the interaction
  aws_session_token?: string; // Temporary credentials can be used with aws_session_token
}

export type ApiAuthInfo = SimpleAuthInfo | AzureAuthInfo | BedrockAuthInfo;

// Type guards for runtime type checking
export function isAgentConfigurationV2(config: AgentConfiguration): config is AgentConfigurationV2 {
  return config.version === 2;
}

export function isClaudeNonReasoningParams(params: CompletionParams): params is ClaudeNonReasoningParams {
  return params.type === 'claude_non_reasoning';
}

export function isClaudeReasoningParams(params: CompletionParams): params is ClaudeReasoningParams {
  return params.type === 'claude_reasoning';
}

export function isGPTNonReasoningParams(params: CompletionParams): params is GPTNonReasoningCompletionParams {
  return params.type === 'g_p_t_non_reasoning';
}

export function isGPTReasoningParams(params: CompletionParams): params is GPTReasoningCompletionParams {
  return params.type === 'g_p_t_reasoning';
}

export function isSimpleAuthInfo(auth: ApiAuthInfo): auth is SimpleAuthInfo {
  return 'api_key' in auth && !('endpoint' in auth) && !('aws_access_key' in auth);
}

export function isAzureAuthInfo(auth: ApiAuthInfo): auth is AzureAuthInfo {
  return 'endpoint' in auth && 'api_key' in auth;
}

export function isBedrockAuthInfo(auth: ApiAuthInfo): auth is BedrockAuthInfo {
  return 'aws_access_key' in auth || 'aws_secret_key' in auth || 'aws_region' in auth;
}

// Helper function to compute vendor from model_id
export function getVendorFromModelId(modelId?: string): string {
  if (!modelId) return 'none';
  
  const modelIdLower = modelId.toLowerCase();
  
  if (modelIdLower.includes('claude') || modelIdLower.includes('anthropic')) {
    return 'anthropic';
  } else if (modelIdLower.includes('gpt') || modelIdLower.includes('openai')) {
    return 'openai';
  }
  
  return 'none';
}

// Helper function to compute display name
export function getDisplayName(session: Partial<ChatSession>): string {
  if (session.session_name) {
    return session.session_name;
  }
  
  const agentName = session.agent_config?.name || 'Agent';
  return `New chat with ${agentName}`;
}

/**
 * Convert a MessageParam to a Message (runtime type)
 * Adds runtime fields like timestamp and format
 */
export function messageParamToMessage(param: MessageParam): Message {
  return {
    role: param.role,
    content: param.content as any, // The types are compatible at runtime
    timestamp: new Date().toISOString(),
    format: 'text' as const
  };
}

/**
 * Convert a Message to a MessageParam (server type)
 * Strips runtime-only fields
 */
export function messageToMessageParam(message: Message): MessageParam {
  return {
    role: message.role as 'user' | 'assistant',
    content: message.content === null ? '' : message.content as any
  };
}

/**
 * Convert a ServerChatSession to a ChatSession
 * Transforms MessageParam[] to Message[] and adds runtime fields
 */
export function serverChatSessionToRuntimeSession(serverSession: ServerChatSession): ChatSession {
  return {
    ...serverSession,
    messages: serverSession.messages.map(messageParamToMessage)
  };
}

/**
 * Convert a ChatSession to a ServerChatSession
 * Transforms Message[] to MessageParam[] for server communication
 */
export function runtimeSessionToServerChatSession(session: ChatSession): ServerChatSession {
  return {
    ...session,
    messages: session.messages.map(messageToMessageParam)
  };
}