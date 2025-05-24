/**
 * Tests for v1 API Adapters
 * 
 * These tests verify that the v1 adapters correctly transform between
 * v1 and v2 API formats while maintaining backward compatibility.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import * as v1Adapters from './v1-api-adapters';
import * as configService from './config-api';
import * as sessionService from './session-api';

// Mock the v2 services
vi.mock('./config-api');
vi.mock('./session-api');

describe('v1 API Adapters', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Suppress console logs during tests
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // =============================================================================
  // MODEL API ADAPTER TESTS
  // =============================================================================

  describe('Model API Adapters', () => {
    it('should get models using v2 config service', async () => {
      const mockModels = [
        { id: 'gpt-4', name: 'GPT-4', provider: 'openai' },
        { id: 'claude-3', name: 'Claude 3', provider: 'anthropic' }
      ];
      
      configService.getModels.mockResolvedValue(mockModels);
      
      const result = await v1Adapters.getModels();
      
      expect(configService.getModels).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockModels);
    });

    it('should get model details using v2 config service', async () => {
      const mockModelDetails = {
        id: 'gpt-4',
        name: 'GPT-4',
        provider: 'openai',
        parameters: { temperature: 0.7, max_tokens: 4096 }
      };
      
      configService.getModelDetails.mockResolvedValue(mockModelDetails);
      
      const result = await v1Adapters.getModelDetails('gpt-4');
      
      expect(configService.getModelDetails).toHaveBeenCalledWith('gpt-4');
      expect(result).toEqual(mockModelDetails);
    });

    it('should get model parameters using v2 config service', async () => {
      const mockParameters = {
        temperature: { default: 0.7, min: 0, max: 2 },
        max_tokens: { default: 4096, min: 1, max: 8192 }
      };
      
      configService.getModelParameters.mockResolvedValue(mockParameters);
      
      const result = await v1Adapters.getModelParameters('gpt-4');
      
      expect(configService.getModelParameters).toHaveBeenCalledWith('gpt-4');
      expect(result).toEqual(mockParameters);
    });

    it('should set session model using v2 agent config', async () => {
      const sessionId = 'session-123';
      const modelId = 'gpt-4';
      const currentConfig = { persona_id: 'assistant', parameters: {} };
      const updatedConfig = { persona_id: 'assistant', model_id: 'gpt-4', parameters: {} };
      
      sessionService.getAgentConfig.mockResolvedValue(currentConfig);
      sessionService.updateAgentConfig.mockResolvedValue(updatedConfig);
      
      const result = await v1Adapters.setSessionModel(sessionId, modelId);
      
      expect(sessionService.getAgentConfig).toHaveBeenCalledWith(sessionId);
      expect(sessionService.updateAgentConfig).toHaveBeenCalledWith(sessionId, {
        ...currentConfig,
        model_id: modelId
      });
      expect(result).toMatchObject({
        success: true,
        model_id: modelId,
        session_id: sessionId
      });
    });

    it('should update model parameters using v2 agent config', async () => {
      const sessionId = 'session-123';
      const newParams = { temperature: 0.8, max_tokens: 2048 };
      const currentConfig = { 
        model_id: 'gpt-4', 
        parameters: { temperature: 0.7, top_p: 0.9 } 
      };
      const expectedConfig = {
        model_id: 'gpt-4',
        parameters: { temperature: 0.8, top_p: 0.9, max_tokens: 2048 }
      };
      
      sessionService.getAgentConfig.mockResolvedValue(currentConfig);
      sessionService.updateAgentConfig.mockResolvedValue(expectedConfig);
      
      const result = await v1Adapters.updateModelParameters(sessionId, newParams);
      
      expect(sessionService.getAgentConfig).toHaveBeenCalledWith(sessionId);
      expect(sessionService.updateAgentConfig).toHaveBeenCalledWith(sessionId, expectedConfig);
      expect(result).toMatchObject({
        success: true,
        session_id: sessionId
      });
    });

    it('should handle errors in model adapters', async () => {
      const error = new Error('Config service error');
      configService.getModels.mockRejectedValue(error);
      
      await expect(v1Adapters.getModels()).rejects.toThrow('Config service error');
      expect(console.error).toHaveBeenCalledWith('[v1-adapter] getModels failed:', error);
    });
  });

  // =============================================================================
  // TOOLS API ADAPTER TESTS
  // =============================================================================

  describe('Tools API Adapters', () => {
    it('should get tools using v2 config service', async () => {
      const mockTools = [
        { id: 'calculator', name: 'Calculator', category: 'math' },
        { id: 'web-search', name: 'Web Search', category: 'search' }
      ];
      
      configService.getTools.mockResolvedValue(mockTools);
      
      const result = await v1Adapters.getTools();
      
      expect(configService.getTools).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockTools);
    });

    it('should get tool details using v2 config service', async () => {
      const mockToolDetails = {
        id: 'calculator',
        name: 'Calculator',
        description: 'Perform mathematical calculations',
        parameters: { expression: { type: 'string', required: true } }
      };
      
      configService.getToolDetails.mockResolvedValue(mockToolDetails);
      
      const result = await v1Adapters.getToolDetails('calculator');
      
      expect(configService.getToolDetails).toHaveBeenCalledWith('calculator');
      expect(result).toEqual(mockToolDetails);
    });

    it('should get session tools using v2 session service', async () => {
      const sessionId = 'session-123';
      const mockTools = ['calculator', 'web-search'];
      
      sessionService.getSessionTools.mockResolvedValue(mockTools);
      
      const result = await v1Adapters.getSessionTools(sessionId);
      
      expect(sessionService.getSessionTools).toHaveBeenCalledWith(sessionId);
      expect(result).toEqual(mockTools);
    });

    it('should update session tools using v2 session service', async () => {
      const sessionId = 'session-123';
      const tools = ['calculator', 'web-search'];
      const mockResult = { tools };
      
      sessionService.updateSessionTools.mockResolvedValue(mockResult);
      
      const result = await v1Adapters.updateSessionTools(sessionId, tools);
      
      expect(sessionService.updateSessionTools).toHaveBeenCalledWith(sessionId, tools);
      expect(result).toMatchObject({
        success: true,
        tools,
        session_id: sessionId
      });
    });

    it('should derive tool categories from tools list', async () => {
      const mockTools = [
        { id: 'calc', category: 'math' },
        { id: 'search', category: 'web' },
        { id: 'add', category: 'math' },
        { id: 'browse', category: 'web' }
      ];
      
      configService.getTools.mockResolvedValue(mockTools);
      
      const result = await v1Adapters.getToolCategories();
      
      expect(result).toEqual([
        { id: 'math', name: 'math', description: 'Tools in the math category' },
        { id: 'web', name: 'web', description: 'Tools in the web category' }
      ]);
    });

    it('should throw error for tool execution (not implemented)', async () => {
      await expect(v1Adapters.executeTool('calculator', {}))
        .rejects.toThrow('Tool execution adapter not yet implemented');
    });
  });

  // =============================================================================
  // PERSONA API ADAPTER TESTS
  // =============================================================================

  describe('Persona API Adapters', () => {
    it('should get personas using v2 config service', async () => {
      const mockPersonas = [
        { id: 'assistant', name: 'Assistant', category: 'general' },
        { id: 'expert', name: 'Expert', category: 'specialized' }
      ];
      
      configService.getPersonas.mockResolvedValue(mockPersonas);
      
      const result = await v1Adapters.getPersonas();
      
      expect(configService.getPersonas).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockPersonas);
    });

    it('should get persona details using v2 config service', async () => {
      const mockPersonaDetails = {
        id: 'assistant',
        name: 'Assistant',
        description: 'Helpful AI assistant',
        system_prompt: 'You are a helpful assistant.'
      };
      
      configService.getPersonaDetails.mockResolvedValue(mockPersonaDetails);
      
      const result = await v1Adapters.getPersonaDetails('assistant');
      
      expect(configService.getPersonaDetails).toHaveBeenCalledWith('assistant');
      expect(result).toEqual(mockPersonaDetails);
    });

    it('should set session persona using v2 agent config', async () => {
      const sessionId = 'session-123';
      const personaId = 'expert';
      const currentConfig = { model_id: 'gpt-4', parameters: {} };
      const updatedConfig = { model_id: 'gpt-4', persona_id: 'expert', parameters: {} };
      
      sessionService.getAgentConfig.mockResolvedValue(currentConfig);
      sessionService.updateAgentConfig.mockResolvedValue(updatedConfig);
      
      const result = await v1Adapters.setSessionPersona(sessionId, personaId);
      
      expect(sessionService.getAgentConfig).toHaveBeenCalledWith(sessionId);
      expect(sessionService.updateAgentConfig).toHaveBeenCalledWith(sessionId, {
        ...currentConfig,
        persona_id: personaId
      });
      expect(result).toMatchObject({
        success: true,
        persona_id: personaId,
        session_id: sessionId
      });
    });

    it('should get session persona using v2 agent config', async () => {
      const sessionId = 'session-123';
      const agentConfig = { model_id: 'gpt-4', persona_id: 'assistant' };
      const personaDetails = { id: 'assistant', name: 'Assistant' };
      
      sessionService.getAgentConfig.mockResolvedValue(agentConfig);
      configService.getPersonaDetails.mockResolvedValue(personaDetails);
      
      const result = await v1Adapters.getSessionPersona(sessionId);
      
      expect(sessionService.getAgentConfig).toHaveBeenCalledWith(sessionId);
      expect(configService.getPersonaDetails).toHaveBeenCalledWith('assistant');
      expect(result).toEqual({
        session_id: sessionId,
        persona_id: 'assistant',
        persona: personaDetails
      });
    });

    it('should handle session with no persona', async () => {
      const sessionId = 'session-123';
      const agentConfig = { model_id: 'gpt-4' }; // No persona_id
      
      sessionService.getAgentConfig.mockResolvedValue(agentConfig);
      
      const result = await v1Adapters.getSessionPersona(sessionId);
      
      expect(result).toEqual({
        session_id: sessionId,
        persona_id: null,
        persona: null
      });
    });

    it('should derive persona categories from personas list', async () => {
      const mockPersonas = [
        { id: 'assistant', category: 'general' },
        { id: 'expert', category: 'specialized' },
        { id: 'helper', category: 'general' }
      ];
      
      configService.getPersonas.mockResolvedValue(mockPersonas);
      
      const result = await v1Adapters.getPersonaCategories();
      
      expect(result).toEqual([
        { id: 'general', name: 'general', description: 'Personas in the general category' },
        { id: 'specialized', name: 'specialized', description: 'Personas in the specialized category' }
      ]);
    });
  });

  // =============================================================================
  // UTILITY FUNCTION TESTS
  // =============================================================================

  describe('Utility Functions', () => {
    it('should transform v1 parameters to v2 format', () => {
      const v1Params = {
        model_name: 'gpt-4',
        persona_name: 'assistant',
        temperature: 0.7,
        other_param: 'value'
      };
      
      const result = v1Adapters.transformV1ToV2Params(v1Params);
      
      expect(result).toEqual({
        model_id: 'gpt-4',
        persona_id: 'assistant',
        temperature: 0.7,
        other_param: 'value'
      });
      expect(result.model_name).toBeUndefined();
      expect(result.persona_name).toBeUndefined();
    });

    it('should transform v2 response to v1 format', () => {
      const v2Response = {
        model_id: 'gpt-4',
        persona_id: 'assistant',
        temperature: 0.7,
        other_field: 'value'
      };
      
      const result = v1Adapters.transformV2ToV1Response(v2Response);
      
      expect(result).toEqual({
        model_id: 'gpt-4',
        model_name: 'gpt-4',
        persona_id: 'assistant',
        persona_name: 'assistant',
        temperature: 0.7,
        other_field: 'value'
      });
    });

    it('should not add duplicate fields in transformation', () => {
      const v2Response = {
        model_id: 'gpt-4',
        model_name: 'GPT-4 Turbo', // Already has model_name
        persona_id: 'assistant'
      };
      
      const result = v1Adapters.transformV2ToV1Response(v2Response);
      
      expect(result.model_name).toBe('GPT-4 Turbo'); // Should keep existing
      expect(result.persona_name).toBe('assistant'); // Should add this
    });
  });
});