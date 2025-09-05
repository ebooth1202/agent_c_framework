import { describe, it, expect, beforeEach } from 'vitest';
import { RealtimeClient } from '../src/client/RealtimeClient';
import type { Agent, AgentConfiguration } from '../src/events/types/CommonTypes';

describe('Agent Tools Field', () => {
  let client: RealtimeClient;

  beforeEach(() => {
    client = new RealtimeClient({
      url: 'ws://localhost:8080',
      apiUrl: 'http://localhost:3000/api',
      authToken: 'test-token',
      debug: false
    });
  });

  it('should preserve tools field in Agent interface', () => {
    const mockAgent: Agent = {
      name: 'Test Agent',
      key: 'test-agent',
      agent_description: 'Test description',
      category: ['category1', 'category2'],
      tools: ['tool1', 'tool2', 'tool3']
    };

    expect(mockAgent.tools).toBeDefined();
    expect(mockAgent.tools).toHaveLength(3);
    expect(mockAgent.tools).toContain('tool1');
    expect(mockAgent.tools).toContain('tool2');
    expect(mockAgent.tools).toContain('tool3');
  });

  it('should preserve tools field in AgentConfiguration interface', () => {
    const mockAgentConfig: AgentConfiguration = {
      version: 1,
      name: 'Test Agent',
      key: 'test-agent',
      model_id: 'gpt-4',
      agent_description: 'Test description',
      tools: ['search', 'calculator', 'weather'],
      agent_params: {},
      prompt_metadata: {},
      persona: 'Helpful assistant',
      uid: 'unique-id-123',
      category: ['ai', 'assistant']
    };

    expect(mockAgentConfig.tools).toBeDefined();
    expect(mockAgentConfig.tools).toHaveLength(3);
    expect(mockAgentConfig.tools).toEqual(['search', 'calculator', 'weather']);
  });

  it('should handle agent_list event with tools field', () => {
    const mockAgents: Agent[] = [
      {
        name: 'Agent 1',
        key: 'agent-1',
        agent_description: 'First agent',
        category: ['cat1'],
        tools: ['tool-a', 'tool-b']
      },
      {
        name: 'Agent 2',
        key: 'agent-2',
        agent_description: 'Second agent',
        category: ['cat2'],
        tools: ['tool-c', 'tool-d', 'tool-e']
      }
    ];

    // Simulate receiving agent_list event
    const eventHandler = (event: any) => {
      if (event.agents) {
        expect(event.agents).toHaveLength(2);
        expect(event.agents[0].tools).toEqual(['tool-a', 'tool-b']);
        expect(event.agents[1].tools).toEqual(['tool-c', 'tool-d', 'tool-e']);
      }
    };

    client.on('agent_list', eventHandler);
    
    // Emit mock event
    client.emit('agent_list', { type: 'agent_list', agents: mockAgents });
  });

  it('should expose agents list through getAgentsList method', () => {
    // Initially should be empty
    expect(client.getAgentsList()).toEqual([]);

    // Simulate agents being set (normally happens in setupInitializationHandlers)
    const mockAgents: Agent[] = [
      {
        name: 'Test Agent',
        key: 'test-key',
        agent_description: 'Description',
        category: ['test'],
        tools: ['tool1', 'tool2']
      }
    ];

    // Emit agent_list event to populate agents
    client.emit('agent_list', { type: 'agent_list', agents: mockAgents });

    // Now getAgentsList should return the agents with tools field
    const agents = client.getAgentsList();
    expect(agents).toHaveLength(1);
    expect(agents[0].tools).toEqual(['tool1', 'tool2']);
  });

  it('should handle agent_configuration_changed event with tools field', () => {
    const mockAgentConfig: AgentConfiguration = {
      version: 1,
      name: 'Updated Agent',
      key: 'updated-agent',
      model_id: 'gpt-4-turbo',
      agent_description: 'Updated description',
      tools: ['new-tool-1', 'new-tool-2'],
      agent_params: { temperature: 0.7 },
      prompt_metadata: {},
      persona: 'Updated persona',
      uid: 'uid-456',
      category: ['updated']
    };

    const eventHandler = (event: any) => {
      if (event.agent_config) {
        expect(event.agent_config.tools).toBeDefined();
        expect(event.agent_config.tools).toEqual(['new-tool-1', 'new-tool-2']);
      }
    };

    client.on('agent_configuration_changed', eventHandler);
    
    // Emit mock event
    client.emit('agent_configuration_changed', { 
      type: 'agent_configuration_changed', 
      agent_config: mockAgentConfig 
    });
  });
});