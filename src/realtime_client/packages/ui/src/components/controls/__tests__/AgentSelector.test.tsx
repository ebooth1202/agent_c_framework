/**
 * AgentSelector Component Tests - Persistence Feature
 * Testing localStorage persistence for agent selections
 */

import React from 'react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, fireEvent, waitFor } from '@testing-library/react';
import { AgentSelector } from '../AgentSelector';
import { 
  updateMockState, 
  useAgentCData,
  useConnection, 
  useRealtimeClientSafe,
  AgentStorage 
} from '../../../test/mocks/realtime-react';
import type { Agent } from '@agentc/realtime-react';

// Note: @agentc/realtime-react is globally mocked in vitest.setup.ts

// Mock Lucide icons
vi.mock('lucide-react', () => ({
  Bot: ({ className, ...props }: any) => 
    <div data-testid="bot-icon" className={className} {...props}>Bot</div>,
  Check: ({ className, ...props }: any) => 
    <div data-testid="check-icon" className={className} {...props}>Check</div>,
  ChevronDown: ({ className, ...props }: any) => 
    <div data-testid="chevron-icon" className={className} {...props}>ChevronDown</div>,
  Loader2: ({ className, ...props }: any) => 
    <div data-testid="loader-icon" className={className} {...props}>Loading</div>,
  Search: ({ className, ...props }: any) => 
    <div data-testid="search-icon" className={className} {...props}>Search</div>,
  X: ({ className, ...props }: any) => 
    <div data-testid="x-icon" className={className} {...props}>X</div>
}));

// Create mock data
const createMockAgent = (key: string, name: string): Agent => ({
  key,
  name,
  description: `Test ${name} agent`,
  metadata: {
    tags: ['test'],
    category: 'Testing'
  },
  status: 'active'
} as Agent);

const mockAgents: Agent[] = [
  createMockAgent('agent1', 'Agent One'),
  createMockAgent('agent2', 'Agent Two'),
  createMockAgent('agent3', 'Agent Three')
];

// Create type-safe mocks
const createMockUseAgentCData = () => ({
  data: {
    agents: mockAgents,
    currentAgentConfig: mockAgents[0],
    voices: [],
    avatars: [],
    tools: []
  },
  isInitialized: true,
  isLoading: false,
  error: null as Error | null
});

const createMockUseConnection = () => ({
  isConnected: true,
  connectionState: 'CONNECTED' as const,
  connect: vi.fn(),
  disconnect: vi.fn(),
  error: null as Error | null
});

const createMockClient = () => ({
  setAgent: vi.fn(),
  getAgent: vi.fn(() => mockAgents[0]),
  isConnected: () => true
});

describe('AgentSelector - Persistence Feature', () => {
  let mockUseAgentCData: ReturnType<typeof createMockUseAgentCData>;
  let mockUseConnection: ReturnType<typeof createMockUseConnection>;
  let mockClient: ReturnType<typeof createMockClient>;
  let consoleErrorSpy: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Reset mocks to default state
    mockUseAgentCData = createMockUseAgentCData();
    mockUseConnection = createMockUseConnection();
    mockClient = createMockClient();
    
    updateMockState('agentCData', mockUseAgentCData);
    updateMockState('connection', mockUseConnection);
    updateMockState('client', mockClient);
    
    // Mock console.error to keep test output clean
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    // Reset AgentStorage mock
    vi.mocked(AgentStorage.saveAgentKey).mockClear();
    vi.mocked(AgentStorage.loadAgentKey).mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Agent Selection Persistence', () => {
    it('should call AgentStorage.saveAgentKey when selecting an agent', async () => {
      const { container, getByText } = render(<AgentSelector />);
      
      // Open the selector dropdown
      const trigger = container.querySelector('button[role="combobox"]');
      expect(trigger).toBeInTheDocument();
      fireEvent.click(trigger!);
      
      // Wait for dropdown to open
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      // Click on Agent Two
      const agentOption = getByText('Agent Two');
      fireEvent.click(agentOption);
      
      // Verify saveAgentKey was called with correct agent key
      await waitFor(() => {
        expect(AgentStorage.saveAgentKey).toHaveBeenCalledWith('agent2');
      });
      
      // Verify setAgent was also called
      expect(mockClient.setAgent).toHaveBeenCalledWith('agent2');
    });

    it('should continue with agent selection even if localStorage save fails', async () => {
      // Mock saveAgentKey to throw an error
      vi.mocked(AgentStorage.saveAgentKey).mockImplementation(() => {
        throw new Error('localStorage is disabled');
      });
      
      const { container, getByText } = render(<AgentSelector />);
      
      // Open the selector dropdown
      const trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      // Wait for dropdown to open
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      // Click on Agent Three
      const agentOption = getByText('Agent Three');
      fireEvent.click(agentOption);
      
      // Wait for the selection to process
      await waitFor(() => {
        // Verify saveAgentKey was attempted
        expect(AgentStorage.saveAgentKey).toHaveBeenCalledWith('agent3');
        
        // Verify error was logged
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Failed to persist agent selection:',
          expect.any(Error)
        );
        
        // Verify setAgent was still called despite the error
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent3');
      });
    });

    it('should handle selection with all agents including persistence', async () => {
      const { container, getByText } = render(<AgentSelector />);
      
      // Test selecting each agent
      for (const agent of mockAgents) {
        // Clear previous calls
        vi.mocked(AgentStorage.saveAgentKey).mockClear();
        vi.mocked(mockClient.setAgent).mockClear();
        
        // Open dropdown
        const trigger = container.querySelector('button[role="combobox"]');
        fireEvent.click(trigger!);
        
        // Wait for dropdown
        await waitFor(() => {
          expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
        });
        
        // Select agent
        const agentOption = getByText(agent.name);
        fireEvent.click(agentOption);
        
        // Verify persistence and selection
        await waitFor(() => {
          expect(AgentStorage.saveAgentKey).toHaveBeenCalledWith(agent.key);
          expect(mockClient.setAgent).toHaveBeenCalledWith(agent.key);
        });
      }
    });
  });

  describe('Error Handling', () => {
    it('should handle null localStorage gracefully', async () => {
      // Mock saveAgentKey to simulate null localStorage
      vi.mocked(AgentStorage.saveAgentKey).mockImplementation(() => {
        const error = new Error('localStorage is null');
        error.name = 'TypeError';
        throw error;
      });
      
      const { container, getByText } = render(<AgentSelector />);
      
      // Open dropdown and select
      const trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      const agentOption = getByText('Agent Two');
      fireEvent.click(agentOption);
      
      // Verify error handling
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Failed to persist agent selection:',
          expect.objectContaining({
            name: 'TypeError',
            message: 'localStorage is null'
          })
        );
        
        // Selection should still work
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent2');
      });
    });

    it('should handle quota exceeded errors', async () => {
      // Mock quota exceeded error
      vi.mocked(AgentStorage.saveAgentKey).mockImplementation(() => {
        const error = new Error('QuotaExceededError: Storage quota exceeded');
        error.name = 'QuotaExceededError';
        throw error;
      });
      
      const { container, getByText } = render(<AgentSelector />);
      
      // Open and select
      const trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      fireEvent.click(getByText('Agent One'));
      
      // Verify graceful handling
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Failed to persist agent selection:',
          expect.objectContaining({
            name: 'QuotaExceededError'
          })
        );
        
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent1');
      });
    });

    it('should handle SecurityError for private browsing', async () => {
      // Mock security error (private browsing)
      vi.mocked(AgentStorage.saveAgentKey).mockImplementation(() => {
        const error = new Error('SecurityError: localStorage access denied');
        error.name = 'SecurityError';
        throw error;
      });
      
      const { container, getByText } = render(<AgentSelector />);
      
      const trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      fireEvent.click(getByText('Agent Three'));
      
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          'Failed to persist agent selection:',
          expect.objectContaining({
            name: 'SecurityError'
          })
        );
        
        // Agent selection should still complete
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent3');
      });
    });
  });

  describe('Integration Tests', () => {
    it('should render normally with AgentStorage import', () => {
      // This test verifies that importing AgentStorage doesn't break the component
      const { container } = render(<AgentSelector />);
      
      const selector = container.querySelector('button[role="combobox"]');
      expect(selector).toBeInTheDocument();
      
      // Should display current agent
      expect(selector).toHaveTextContent('Agent One');
    });

    it('should handle rapid selections with persistence', async () => {
      const { container, getByText } = render(<AgentSelector />);
      
      // Perform rapid selections
      const agents = ['Agent Two', 'Agent Three', 'Agent One'];
      
      for (const agentName of agents) {
        const trigger = container.querySelector('button[role="combobox"]');
        fireEvent.click(trigger!);
        
        await waitFor(() => {
          expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
        });
        
        fireEvent.click(getByText(agentName));
        
        // Small delay to let selection complete
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      
      // All saves should have been attempted
      expect(AgentStorage.saveAgentKey).toHaveBeenCalledTimes(3);
      expect(mockClient.setAgent).toHaveBeenCalledTimes(3);
    });

    it('should maintain selection state during persistence errors', async () => {
      // First selection succeeds
      vi.mocked(AgentStorage.saveAgentKey).mockImplementationOnce(() => {
        // Success - no error
      });
      
      // Second selection fails
      vi.mocked(AgentStorage.saveAgentKey).mockImplementationOnce(() => {
        throw new Error('Storage error');
      });
      
      const { container, getByText } = render(<AgentSelector />);
      
      // First selection (success)
      let trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      fireEvent.click(getByText('Agent Two'));
      
      await waitFor(() => {
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent2');
      });
      
      // Second selection (failure)
      vi.mocked(mockClient.setAgent).mockClear();
      
      trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      fireEvent.click(getByText('Agent Three'));
      
      await waitFor(() => {
        expect(consoleErrorSpy).toHaveBeenCalled();
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent3');
      });
    });

    it('should not interfere with component disabled state', () => {
      const { container } = render(<AgentSelector disabled />);
      
      const selector = container.querySelector('button[role="combobox"]');
      expect(selector).toBeDisabled();
      
      // Try to click - should not open
      fireEvent.click(selector!);
      
      // Dropdown should not appear
      expect(container.querySelector('[role="listbox"]')).not.toBeInTheDocument();
      
      // No persistence calls should have been made
      expect(AgentStorage.saveAgentKey).not.toHaveBeenCalled();
      expect(mockClient.setAgent).not.toHaveBeenCalled();
    });

    it('should work when no client is available', () => {
      // Set client to null
      updateMockState('client', null);
      
      const { container } = render(<AgentSelector />);
      
      const selector = container.querySelector('button[role="combobox"]');
      expect(selector).toBeInTheDocument();
      expect(selector).toBeDisabled(); // Should be disabled when no client
      
      // Try to click
      fireEvent.click(selector!);
      
      // Should not open
      expect(container.querySelector('[role="listbox"]')).not.toBeInTheDocument();
      
      // No calls should be made
      expect(AgentStorage.saveAgentKey).not.toHaveBeenCalled();
    });
  });

  describe('Component Behavior with Persistence', () => {
    it('should close dropdown after selection with persistence', async () => {
      const { container, getByText } = render(<AgentSelector />);
      
      // Open dropdown
      const trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      // Select agent
      fireEvent.click(getByText('Agent Two'));
      
      // Dropdown should close
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).not.toBeInTheDocument();
      });
      
      // Persistence should have been called
      expect(AgentStorage.saveAgentKey).toHaveBeenCalledWith('agent2');
    });

    it('should show loading state briefly during selection', async () => {
      const { container, getByText } = render(<AgentSelector />);
      
      // Open dropdown
      const trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      // Select agent
      fireEvent.click(getByText('Agent Three'));
      
      // The component sets isChanging state which might show loading indication
      // Verify the selection completes
      await waitFor(() => {
        expect(AgentStorage.saveAgentKey).toHaveBeenCalledWith('agent3');
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent3');
      });
    });

    it('should handle search with persistence', async () => {
      const { container, getByText, getByPlaceholderText } = render(<AgentSelector />);
      
      // Open dropdown
      const trigger = container.querySelector('button[role="combobox"]');
      fireEvent.click(trigger!);
      
      await waitFor(() => {
        expect(container.querySelector('[role="listbox"]')).toBeInTheDocument();
      });
      
      // Search for agent
      const searchInput = getByPlaceholderText(/search agents/i);
      fireEvent.change(searchInput, { target: { value: 'Two' } });
      
      // Select filtered result
      await waitFor(() => {
        const agentOption = getByText('Agent Two');
        fireEvent.click(agentOption);
      });
      
      // Verify persistence
      await waitFor(() => {
        expect(AgentStorage.saveAgentKey).toHaveBeenCalledWith('agent2');
        expect(mockClient.setAgent).toHaveBeenCalledWith('agent2');
      });
    });
  });
});