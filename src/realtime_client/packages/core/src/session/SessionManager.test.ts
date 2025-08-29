/**
 * Example usage and test cases for SessionManager
 */

import { SessionManager } from './SessionManager';
import { ChatSession, Message, AgentConfiguration } from '../events/types/CommonTypes';

// Example: Create a mock session
function createMockSession(id: string = 'test-session-1'): ChatSession {
  const mockAgentConfig: AgentConfiguration = {
    version: 1,
    name: 'Test Agent',
    key: 'test-agent',
    model_id: 'gpt-4',
    agent_description: 'Test agent for SessionManager',
    tools: [],
    agent_params: {},
    prompt_metadata: {},
    persona: 'Helpful assistant',
    uid: null,
    category: ['test']
  };

  return {
    session_id: id,
    token_count: 0,
    context_window_size: 4096,
    session_name: 'Test Session',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted_at: null,
    user_id: 'test-user',
    metadata: {},
    messages: [],
    agent_config: mockAgentConfig
  };
}

// Example usage
function demonstrateSessionManager() {
  console.log('=== SessionManager Demo ===\n');

  // Create SessionManager instance
  const sessionManager = new SessionManager({
    maxSessions: 10,
    defaultSessionName: 'Demo Session'
  });

  // Listen to events
  sessionManager.on('session-changed', (event) => {
    console.log('Session changed:', {
      from: event.previousSession?.session_id || 'none',
      to: event.currentSession?.session_id || 'none'
    });
  });

  sessionManager.on('message-added', (event) => {
    console.log('Message added to session:', event.sessionId);
    console.log('Message:', event.message);
  });

  sessionManager.on('sessions-updated', (event) => {
    console.log('Sessions updated, total count:', event.sessions.size);
  });

  // Create and set a session
  const session1 = createMockSession('session-1');
  sessionManager.setCurrentSession(session1);

  // Add user message
  console.log('\n--- Adding user message ---');
  sessionManager.addUserMessage('Hello, how are you?');

  // Simulate receiving assistant response with text deltas
  console.log('\n--- Simulating assistant response ---');
  sessionManager.handleTextDelta('I am doing well, ');
  sessionManager.handleTextDelta('thank you for asking. ');
  sessionManager.handleTextDelta('How can I help you today?');
  
  // Finalize the assistant message
  const assistantMessage = sessionManager.handleTextDone();
  console.log('Finalized assistant message:', assistantMessage?.content);

  // Create and switch to another session
  console.log('\n--- Creating second session ---');
  const session2 = createMockSession('session-2');
  session2.session_name = 'Second Session';
  sessionManager.setCurrentSession(session2);

  // Add messages to second session
  sessionManager.addUserMessage('What is the weather like?');
  sessionManager.handleTextDelta('I don\'t have access to real-time weather data.');
  sessionManager.handleTextDone();

  // Get statistics
  console.log('\n--- Session Statistics ---');
  const stats = sessionManager.getStatistics();
  console.log('Statistics:', stats);

  // List all sessions
  console.log('\n--- All Sessions ---');
  const allSessions = sessionManager.getAllSessions();
  for (const [id, session] of allSessions) {
    console.log(`Session ${id}:`, {
      name: session.session_name,
      messages: session.messages.length,
      tokens: session.token_count
    });
  }

  // Update session metadata
  console.log('\n--- Updating session metadata ---');
  sessionManager.updateSessionMetadata('session-1', {
    topic: 'greeting',
    language: 'en'
  });

  // Update session name
  sessionManager.updateSessionName('session-1', 'Greeting Conversation');

  // Get specific session
  console.log('\n--- Getting specific session ---');
  const retrievedSession = sessionManager.getSession('session-1');
  console.log('Retrieved session:', {
    id: retrievedSession?.session_id,
    name: retrievedSession?.session_name,
    metadata: retrievedSession?.metadata
  });

  // Clear a session
  console.log('\n--- Clearing session-2 ---');
  const cleared = sessionManager.clearSession('session-2');
  console.log('Session cleared:', cleared);
  console.log('Remaining sessions:', sessionManager.getSessionIds());

  // Reset all sessions
  console.log('\n--- Resetting all sessions ---');
  sessionManager.reset();
  console.log('Total sessions after reset:', sessionManager.getAllSessions().size);

  // Cleanup
  sessionManager.cleanup();
  console.log('\n=== Demo Complete ===');
}

// Export for testing
export { demonstrateSessionManager, createMockSession };