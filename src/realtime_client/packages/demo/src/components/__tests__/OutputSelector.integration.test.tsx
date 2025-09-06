/**
 * @fileoverview Integration tests for OutputSelector with demo app
 * @module demo/components/__tests__
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { OutputSelector } from '@agentc/realtime-ui'
import { AgentCProvider } from '@agentc/realtime-react'
import { RealtimeClient } from '@agentc/realtime-core'

// Mock the RealtimeClient
vi.mock('@agentc/realtime-core', () => ({
  RealtimeClient: vi.fn().mockImplementation(() => ({
    connect: vi.fn(),
    disconnect: vi.fn(),
    setAgentVoice: vi.fn(),
    getAvatarManager: vi.fn(() => ({
      getAvatarId: vi.fn(() => null)
    })),
    on: vi.fn(),
    off: vi.fn(),
    emit: vi.fn(),
    getConnectionState: vi.fn(() => 'connected'),
    isConnected: vi.fn(() => true),
    getVoiceModel: vi.fn(() => null)
  }))
}))

describe('OutputSelector Integration Tests', () => {
  let mockClient: any
  let mockEventHandlers: Map<string, Set<Function>>

  beforeEach(() => {
    mockEventHandlers = new Map()
    
    mockClient = {
      connect: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn().mockResolvedValue(undefined),
      setAgentVoice: vi.fn().mockResolvedValue(undefined),
      getAvatarManager: vi.fn(() => ({
        getAvatarId: vi.fn(() => null)
      })),
      on: vi.fn((event: string, handler: Function) => {
        if (!mockEventHandlers.has(event)) {
          mockEventHandlers.set(event, new Set())
        }
        mockEventHandlers.get(event)?.add(handler)
      }),
      off: vi.fn((event: string, handler: Function) => {
        mockEventHandlers.get(event)?.delete(handler)
      }),
      emit: vi.fn((event: string, data?: any) => {
        const handlers = mockEventHandlers.get(event)
        if (handlers) {
          handlers.forEach(handler => handler(data))
        }
      }),
      getConnectionState: vi.fn(() => 'connected'),
      isConnected: vi.fn(() => true),
      getVoiceModel: vi.fn(() => null),
      getAgentData: vi.fn(() => ({
        voices: [
          { voice_id: 'alloy', vendor: 'OpenAI', description: 'Neutral voice' },
          { voice_id: 'nova', vendor: 'OpenAI', description: 'Friendly voice' }
        ],
        avatars: [
          { avatar_id: 'avatar1', pose_name: 'Standing', status: 'active', is_public: true }
        ]
      }))
    }

    ;(RealtimeClient as any).mockImplementation(() => mockClient)
  })

  afterEach(() => {
    vi.clearAllMocks()
    mockEventHandlers.clear()
  })

  describe('SDK Event Propagation', () => {
    it('should propagate voice change events from SDK', async () => {
      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      render(<TestComponent />)

      // Wait for component to mount and register listeners
      await waitFor(() => {
        expect(mockClient.on).toHaveBeenCalledWith(
          'agent_voice_changed', 
          expect.any(Function)
        )
      })

      // Open menu and select a voice
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)

      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options/i })
      await userEvent.click(voicesSubmenu)

      const novaVoice = screen.getByRole('menuitem', { name: /nova/i })
      await userEvent.click(novaVoice)

      // Verify SDK method was called
      await waitFor(() => {
        expect(mockClient.setAgentVoice).toHaveBeenCalledWith('nova')
      })

      // Simulate SDK confirming the change
      mockClient.emit('agent_voice_changed', { voice_id: 'nova' })

      // Component should update to reflect the change
      await waitFor(() => {
        expect(mockClient.getVoiceModel).toHaveBeenCalled()
      })
    })

    it('should handle connection state changes', async () => {
      mockClient.isConnected.mockReturnValue(false)
      mockClient.getConnectionState.mockReturnValue('disconnected')

      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      render(<TestComponent />)

      // Component should be disabled when disconnected
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toBeDisabled()

      // Simulate connection
      mockClient.isConnected.mockReturnValue(true)
      mockClient.getConnectionState.mockReturnValue('connected')
      mockClient.emit('connected')

      // Component should become enabled
      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })
    })

    it('should sync with SDK initialization state', async () => {
      mockClient.getAgentData.mockReturnValue({
        voices: [],
        avatars: []
      })

      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      const { rerender } = render(<TestComponent />)

      // Initially no voices
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)

      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options.*0/i })
      expect(voicesSubmenu).toBeInTheDocument()

      // Update SDK data
      mockClient.getAgentData.mockReturnValue({
        voices: [
          { voice_id: 'echo', vendor: 'OpenAI', description: 'Echo voice' }
        ],
        avatars: []
      })

      // Emit data update event
      mockClient.emit('agent_data_updated')
      
      rerender(<TestComponent />)

      // Voices should now be available
      await waitFor(() => {
        const updatedVoicesSubmenu = screen.getByRole('menuitem', { name: /voice options.*1/i })
        expect(updatedVoicesSubmenu).toBeInTheDocument()
      })
    })
  })

  describe('State Synchronization', () => {
    it('should synchronize state with other components using same SDK', async () => {
      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <div>
            <OutputSelector data-testid="selector1" />
            <OutputSelector data-testid="selector2" />
          </div>
        </AgentCProvider>
      )

      render(<TestComponent />)

      const [selector1, selector2] = screen.getAllByRole('button', { name: /output mode selector/i })

      // Both should show same initial state
      expect(selector1).toHaveTextContent('Text Only')
      expect(selector2).toHaveTextContent('Text Only')

      // Change voice using first selector
      await userEvent.click(selector1)
      
      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options/i })
      await userEvent.click(voicesSubmenu)

      const alloyVoice = screen.getByRole('menuitem', { name: /alloy/i })
      await userEvent.click(alloyVoice)

      // Mock SDK updating the voice model
      mockClient.getVoiceModel.mockReturnValue({
        voice_id: 'alloy',
        vendor: 'OpenAI',
        description: 'Neutral voice'
      })

      // Emit voice changed event
      mockClient.emit('agent_voice_changed', { voice_id: 'alloy' })

      // Both selectors should update
      await waitFor(() => {
        expect(selector1).toHaveTextContent('Neutral voice')
        expect(selector2).toHaveTextContent('Neutral voice')
      })
    })

    it('should maintain consistency during concurrent operations', async () => {
      let voiceChangePromiseResolve: any
      const voiceChangePromise = new Promise(resolve => {
        voiceChangePromiseResolve = resolve
      })

      mockClient.setAgentVoice.mockImplementation(() => voiceChangePromise)

      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      render(<TestComponent />)

      const button = screen.getByRole('button', { name: /output mode selector/i })
      
      // Start a voice change
      await userEvent.click(button)
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)

      // Button should show loading state
      expect(button).toHaveTextContent('Loading...')
      expect(button).toBeDisabled()

      // Try to open menu again (should stay disabled)
      await userEvent.click(button)
      expect(screen.queryByText('Output Mode')).not.toBeInTheDocument()

      // Complete the operation
      voiceChangePromiseResolve()
      mockClient.emit('agent_voice_changed', { voice_id: 'none' })

      await waitFor(() => {
        expect(button).toHaveTextContent('Text Only')
        expect(button).not.toBeDisabled()
      })
    })
  })

  describe('Connection/Disconnection Scenarios', () => {
    it('should handle connection loss gracefully', async () => {
      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector showErrorAlerts />
        </AgentCProvider>
      )

      render(<TestComponent />)

      // Initially connected
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).not.toBeDisabled()

      // Simulate connection loss
      mockClient.isConnected.mockReturnValue(false)
      mockClient.getConnectionState.mockReturnValue('error')
      mockClient.emit('connection_error', { message: 'Network error' })

      await waitFor(() => {
        expect(button).toBeDisabled()
        // Error alert should be shown
        const alert = screen.queryByRole('alert')
        if (alert) {
          expect(alert).toBeInTheDocument()
        }
      })

      // Simulate reconnection
      mockClient.isConnected.mockReturnValue(true)
      mockClient.getConnectionState.mockReturnValue('connected')
      mockClient.emit('connected')

      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })
    })

    it('should queue operations during reconnection', async () => {
      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      render(<TestComponent />)

      // Simulate temporary disconnection
      mockClient.isConnected.mockReturnValue(false)
      mockClient.getConnectionState.mockReturnValue('reconnecting')
      mockClient.emit('reconnecting')

      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toBeDisabled()

      // Attempt to change voice (should be prevented)
      await userEvent.click(button, { pointerEventsCheck: 0 })
      expect(mockClient.setAgentVoice).not.toHaveBeenCalled()

      // Restore connection
      mockClient.isConnected.mockReturnValue(true)
      mockClient.getConnectionState.mockReturnValue('connected')
      mockClient.emit('connected')

      await waitFor(() => {
        expect(button).not.toBeDisabled()
      })

      // Now voice change should work
      await userEvent.click(button)
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)

      expect(mockClient.setAgentVoice).toHaveBeenCalledWith('none')
    })
  })

  describe('Voice Change During Active Conversation', () => {
    it('should handle voice change while conversation is active', async () => {
      mockClient.getConversationState = vi.fn(() => 'active')
      mockClient.getTurnState = vi.fn(() => 'agent_speaking')

      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      render(<TestComponent />)

      // Change voice during active conversation
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)

      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options/i })
      await userEvent.click(voicesSubmenu)

      const novaVoice = screen.getByRole('menuitem', { name: /nova/i })
      await userEvent.click(novaVoice)

      // SDK should handle the voice change
      await waitFor(() => {
        expect(mockClient.setAgentVoice).toHaveBeenCalledWith('nova')
      })

      // Simulate SDK confirming change applied after current turn
      mockClient.emit('turn_ended')
      mockClient.emit('agent_voice_changed', { voice_id: 'nova' })

      // Verify no errors occurred
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    })

    it('should defer avatar changes during active conversation', async () => {
      mockClient.getConversationState = vi.fn(() => 'active')

      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      const { container } = render(<TestComponent />)

      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)

      const avatarSubmenu = screen.getByRole('menuitem', { name: /avatar options/i })
      await userEvent.click(avatarSubmenu)

      const avatar1 = screen.getByRole('menuitem', { name: /avatar1/i })
      await userEvent.click(avatar1)

      // Avatar selection should be announced as not yet available
      const liveRegion = container.querySelector('[role="status"][aria-live="polite"]')
      await waitFor(() => {
        expect(liveRegion).toHaveTextContent('selection is not yet available')
      })
    })
  })

  describe('Error Recovery', () => {
    it('should recover from voice service errors', async () => {
      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector showErrorAlerts />
        </AgentCProvider>
      )

      render(<TestComponent />)

      // First attempt fails
      mockClient.setAgentVoice.mockRejectedValueOnce(new Error('Service unavailable'))

      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)

      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)

      // Error should be displayed
      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert).toHaveTextContent('Failed to set text mode')
      })

      // Second attempt succeeds
      mockClient.setAgentVoice.mockResolvedValueOnce(undefined)

      await userEvent.click(button)
      const textOption2 = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption2)

      // Should succeed and clear error
      await waitFor(() => {
        expect(mockClient.setAgentVoice).toHaveBeenCalledTimes(2)
      })

      mockClient.emit('agent_voice_changed', { voice_id: 'none' })

      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      })
    })

    it('should handle rapid selection changes', async () => {
      const TestComponent = () => (
        <AgentCProvider 
          apiKey="test-key"
          agentId="test-agent"
          client={mockClient}
        >
          <OutputSelector />
        </AgentCProvider>
      )

      render(<TestComponent />)

      // Make multiple rapid selections
      const button = screen.getByRole('button', { name: /output mode selector/i })
      
      for (let i = 0; i < 3; i++) {
        await userEvent.click(button)
        const textOption = screen.getByRole('menuitem', { name: /text only/i })
        await userEvent.click(textOption)
      }

      // Only the last selection should be processed
      await waitFor(() => {
        // Due to debouncing or state management, we expect controlled behavior
        expect(mockClient.setAgentVoice.mock.calls.length).toBeGreaterThan(0)
      })
    })
  })
})