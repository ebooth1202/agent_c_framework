/**
 * @fileoverview Unit tests for OutputSelector component
 * @module @agentc/realtime-ui/test/controls
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { OutputSelector } from '../../src/components/controls/OutputSelector'
import type { RealtimeClient } from '@agentc/realtime-core'

// Mock the hooks from @agentc/realtime-react
vi.mock('@agentc/realtime-react', () => ({
  useAgentCData: vi.fn(),
  useInitializationStatus: vi.fn(),
  useVoiceModel: vi.fn(),
  useRealtimeClientSafe: vi.fn(),
  useConnection: vi.fn()
}))

// Import the mocked functions
import { 
  useAgentCData, 
  useInitializationStatus, 
  useVoiceModel, 
  useRealtimeClientSafe,
  useConnection 
} from '@agentc/realtime-react'

describe('OutputSelector Component', () => {
  let mockClient: Partial<RealtimeClient>
  let mockSetAgentVoice: ReturnType<typeof vi.fn>
  let mockOn: ReturnType<typeof vi.fn>
  let mockOff: ReturnType<typeof vi.fn>
  
  const mockVoices = [
    { 
      voice_id: 'voice1', 
      vendor: 'OpenAI', 
      description: 'Professional male voice' 
    },
    { 
      voice_id: 'voice2', 
      vendor: 'ElevenLabs', 
      description: 'Friendly female voice' 
    },
    { 
      voice_id: 'alloy', 
      vendor: 'OpenAI', 
      description: 'Neutral assistant voice' 
    }
  ]
  
  const mockAvatars = [
    {
      avatar_id: 'avatar1',
      pose_name: 'Standing',
      status: 'active',
      is_public: true
    },
    {
      avatar_id: 'avatar2',
      pose_name: 'Sitting',
      status: 'active',
      is_public: true
    },
    {
      avatar_id: 'avatar3',
      pose_name: 'Private',
      status: 'active',
      is_public: false // Should be filtered out
    }
  ]

  beforeEach(() => {
    mockSetAgentVoice = vi.fn()
    mockOn = vi.fn()
    mockOff = vi.fn()
    
    mockClient = {
      setAgentVoice: mockSetAgentVoice,
      on: mockOn,
      off: mockOff,
      getAvatarManager: vi.fn(() => ({
        getAvatarId: vi.fn(() => null)
      }))
    }
    
    // Default mock implementations
    ;(useRealtimeClientSafe as any).mockReturnValue(mockClient)
    ;(useAgentCData as any).mockReturnValue({
      data: {
        voices: mockVoices,
        avatars: mockAvatars
      },
      isInitialized: true,
      isLoading: false
    })
    ;(useInitializationStatus as any).mockReturnValue({
      isInitialized: true
    })
    ;(useVoiceModel as any).mockReturnValue({
      currentVoice: null,
      isLoading: false,
      error: null
    })
    ;(useConnection as any).mockReturnValue({
      isConnected: true
    })
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('Display and Menu Options', () => {
    it('should render with default text mode when no voice is selected', () => {
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toBeInTheDocument()
      expect(button).toHaveTextContent('Text Only')
    })

    it('should display all menu options in correct hierarchical format', async () => {
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      // Check root level items
      expect(screen.getByText('Output Mode')).toBeInTheDocument()
      expect(screen.getByRole('menuitem', { name: /text only/i })).toBeInTheDocument()
      
      // Check submenu triggers
      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options/i })
      expect(voicesSubmenu).toBeInTheDocument()
      expect(voicesSubmenu).toHaveTextContent('3') // Voice count
      
      const avatarSubmenu = screen.getByRole('menuitem', { name: /avatar options/i })
      expect(avatarSubmenu).toBeInTheDocument()
      expect(avatarSubmenu).toHaveTextContent('2') // Active public avatars only
    })

    it('should show voice options when voices submenu is opened', async () => {
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options/i })
      await userEvent.click(voicesSubmenu)
      
      // Check all voices are displayed with vendor and description
      expect(screen.getByText('Available Voices')).toBeInTheDocument()
      expect(screen.getByText(/OpenAI - voice1/)).toBeInTheDocument()
      expect(screen.getByText(/Professional male voice/)).toBeInTheDocument()
      expect(screen.getByText(/ElevenLabs - voice2/)).toBeInTheDocument()
      expect(screen.getByText(/Friendly female voice/)).toBeInTheDocument()
    })

    it('should filter out non-public avatars', async () => {
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const avatarSubmenu = screen.getByRole('menuitem', { name: /avatar options/i })
      await userEvent.click(avatarSubmenu)
      
      // Only public avatars should be shown
      expect(screen.getByText(/avatar1 - Standing/)).toBeInTheDocument()
      expect(screen.getByText(/avatar2 - Sitting/)).toBeInTheDocument()
      expect(screen.queryByText(/avatar3/)).not.toBeInTheDocument()
    })

    it('should show current voice selection with check mark', async () => {
      ;(useVoiceModel as any).mockReturnValue({
        currentVoice: { 
          voice_id: 'voice1', 
          vendor: 'OpenAI',
          description: 'Professional male voice'
        },
        isLoading: false,
        error: null
      })
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toHaveTextContent('Professional male voice')
      
      await userEvent.click(button)
      
      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options/i })
      await userEvent.click(voicesSubmenu)
      
      // Check that the current voice has a check mark
      const selectedVoice = screen.getByRole('menuitem', { 
        name: /OpenAI voice1.*currently selected/i 
      })
      expect(selectedVoice).toBeInTheDocument()
    })

    it('should show text mode as selected when voice_id is none', async () => {
      ;(useVoiceModel as any).mockReturnValue({
        currentVoice: { voice_id: 'none' },
        isLoading: false,
        error: null
      })
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only.*currently selected/i })
      expect(textOption).toBeInTheDocument()
    })
  })

  describe('Event Firing', () => {
    it('should fire setAgentVoice with "none" when text mode is selected', async () => {
      mockSetAgentVoice.mockResolvedValue(undefined)
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)
      
      await waitFor(() => {
        expect(mockSetAgentVoice).toHaveBeenCalledWith('none')
      })
    })

    it('should fire setAgentVoice with voice_id when voice is selected', async () => {
      mockSetAgentVoice.mockResolvedValue(undefined)
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options/i })
      await userEvent.click(voicesSubmenu)
      
      const voice2 = screen.getByRole('menuitem', { name: /ElevenLabs voice2/i })
      await userEvent.click(voice2)
      
      await waitFor(() => {
        expect(mockSetAgentVoice).toHaveBeenCalledWith('voice2')
      })
    })

    it('should announce avatar selection as not yet available', async () => {
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const avatarSubmenu = screen.getByRole('menuitem', { name: /avatar options/i })
      await userEvent.click(avatarSubmenu)
      
      const avatar1 = screen.getByRole('menuitem', { name: /avatar avatar1/i })
      await userEvent.click(avatar1)
      
      // Check that announcement is made for deferred implementation
      const liveRegion = document.querySelector('[role="status"][aria-live="polite"]')
      expect(liveRegion).toHaveTextContent('Avatar avatar1 - Standing selection is not yet available')
    })

    it('should register and cleanup voice change event listeners', () => {
      const { unmount } = render(<OutputSelector />)
      
      // Check that event listener was registered
      expect(mockOn).toHaveBeenCalledWith('agent_voice_changed', expect.any(Function))
      
      unmount()
      
      // Check that event listener was cleaned up
      expect(mockOff).toHaveBeenCalledWith('agent_voice_changed', expect.any(Function))
    })
  })

  describe('State Management', () => {
    it('should be disabled when not connected', () => {
      ;(useConnection as any).mockReturnValue({
        isConnected: false
      })
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toBeDisabled()
      expect(button).toHaveClass('opacity-50', 'cursor-not-allowed')
    })

    it('should be disabled when not initialized', () => {
      ;(useInitializationStatus as any).mockReturnValue({
        isInitialized: false
      })
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toBeDisabled()
    })

    it('should show loading state during voice changes', async () => {
      mockSetAgentVoice.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)
      
      // Check loading state
      const loadingButton = screen.getByRole('button', { name: /output mode selector/i })
      expect(loadingButton).toHaveTextContent('Loading...')
      expect(loadingButton).toBeDisabled()
      
      // Wait for async operation to complete
      await waitFor(() => {
        expect(loadingButton).toHaveTextContent('Text Only')
        expect(loadingButton).not.toBeDisabled()
      })
    })

    it('should show loading spinner icon during transitions', async () => {
      ;(useVoiceModel as any).mockReturnValue({
        currentVoice: null,
        isLoading: true,
        error: null
      })
      
      render(<OutputSelector showIcon />)
      
      // Look for spinner animation class
      const button = screen.getByRole('button', { name: /output mode selector/i })
      const spinner = within(button).getByTestId('lucide-loader-2')
      expect(spinner).toHaveClass('animate-spin')
    })

    it('should disable menu items during state changes', async () => {
      mockSetAgentVoice.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      fireEvent.click(textOption)
      
      // Quickly reopen menu to check disabled state
      await userEvent.click(button)
      
      const allMenuItems = screen.getAllByRole('menuitem')
      // Text option should be disabled during change
      expect(allMenuItems[0]).toHaveAttribute('aria-disabled', 'true')
    })
  })

  describe('Error Handling', () => {
    it('should display error alert when voice change fails', async () => {
      mockSetAgentVoice.mockRejectedValue(new Error('Network error'))
      
      render(<OutputSelector showErrorAlerts />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)
      
      await waitFor(() => {
        const alert = screen.getByRole('alert')
        expect(alert).toHaveTextContent('Failed to set text mode')
      })
    })

    it('should not show error alert when showErrorAlerts is false', async () => {
      mockSetAgentVoice.mockRejectedValue(new Error('Network error'))
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      
      render(<OutputSelector showErrorAlerts={false} />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalled()
      })
      
      expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      
      consoleSpy.mockRestore()
    })

    it('should clear error after 5 seconds', async () => {
      vi.useFakeTimers()
      mockSetAgentVoice.mockRejectedValue(new Error('Network error'))
      
      render(<OutputSelector showErrorAlerts />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)
      
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      })
      
      // Fast forward 5 seconds
      vi.advanceTimersByTime(5000)
      
      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      })
      
      vi.useRealTimers()
    })

    it('should show error icon when in error state', () => {
      ;(useVoiceModel as any).mockReturnValue({
        currentVoice: null,
        isLoading: false,
        error: 'Voice service unavailable'
      })
      
      render(<OutputSelector showIcon />)
      
      // Look for AlertCircle icon
      const button = screen.getByRole('button', { name: /output mode selector/i })
      const alertIcon = within(button).getByTestId('lucide-alert-circle')
      expect(alertIcon).toBeInTheDocument()
      
      expect(button).toHaveClass('destructive')
    })

    it('should handle missing client gracefully', () => {
      ;(useRealtimeClientSafe as any).mockReturnValue(null)
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toBeDisabled()
    })

    it('should handle empty voices list', async () => {
      ;(useAgentCData as any).mockReturnValue({
        data: {
          voices: [],
          avatars: []
        },
        isInitialized: true,
        isLoading: false
      })
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const voicesSubmenu = screen.getByRole('menuitem', { name: /voice options.*0/i })
      await userEvent.click(voicesSubmenu)
      
      expect(screen.getByText('No voices available')).toBeInTheDocument()
    })
  })

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      render(<OutputSelector ariaLabel="Choose agent output format" />)
      
      const button = screen.getByRole('button', { name: /choose agent output format/i })
      expect(button).toHaveAttribute('aria-expanded', 'false')
      expect(button).toHaveAttribute('aria-haspopup', 'menu')
    })

    it('should update aria-expanded when menu opens', async () => {
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toHaveAttribute('aria-expanded', 'false')
      
      await userEvent.click(button)
      
      expect(button).toHaveAttribute('aria-expanded', 'true')
    })

    it('should announce changes to screen readers', async () => {
      mockSetAgentVoice.mockResolvedValue(undefined)
      
      const { container } = render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)
      
      // Check for live region announcement
      const liveRegion = container.querySelector('[role="status"][aria-live="polite"]')
      expect(liveRegion).toBeInTheDocument()
      
      await waitFor(() => {
        expect(liveRegion).toHaveTextContent('Text-only mode activated')
      })
    })

    it('should support keyboard navigation', async () => {
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      
      // Focus the button
      button.focus()
      expect(button).toHaveFocus()
      
      // Open menu with Enter key
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' })
      
      await waitFor(() => {
        expect(screen.getByText('Output Mode')).toBeInTheDocument()
      })
      
      // Navigate with arrow keys would be handled by DropdownMenu component
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      expect(textOption).toBeInTheDocument()
    })

    it('should have screen reader only content for status', () => {
      const { container } = render(<OutputSelector />)
      
      const srOnlyElements = container.querySelectorAll('.sr-only')
      expect(srOnlyElements.length).toBeGreaterThan(0)
      
      // Check for live region
      const liveRegion = container.querySelector('[role="status"]')
      expect(liveRegion).toHaveClass('sr-only')
    })
  })

  describe('Props and Customization', () => {
    it('should accept custom className', () => {
      render(<OutputSelector className="custom-class w-[300px]" />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toHaveClass('custom-class', 'w-[300px]')
    })

    it('should respect disabled prop', () => {
      render(<OutputSelector disabled />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toBeDisabled()
    })

    it('should hide icon when showIcon is false', () => {
      const { container } = render(<OutputSelector showIcon={false} />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      const icons = within(button).queryAllByRole('img', { hidden: true })
      // Should only have the chevron icon, not the mode icon
      expect(icons).toHaveLength(1)
    })

    it('should forward ref to button element', () => {
      const ref = vi.fn()
      render(<OutputSelector ref={ref} />)
      
      expect(ref).toHaveBeenCalledWith(expect.any(HTMLButtonElement))
    })
  })

  describe('Integration with SDK', () => {
    it('should clear errors when voice change is confirmed', async () => {
      mockSetAgentVoice.mockRejectedValue(new Error('Initial error'))
      
      render(<OutputSelector showErrorAlerts />)
      
      // Trigger an error
      const button = screen.getByRole('button', { name: /output mode selector/i })
      await userEvent.click(button)
      
      const textOption = screen.getByRole('menuitem', { name: /text only/i })
      await userEvent.click(textOption)
      
      await waitFor(() => {
        expect(screen.getByRole('alert')).toBeInTheDocument()
      })
      
      // Simulate successful voice change event
      const voiceChangedHandler = mockOn.mock.calls.find(
        call => call[0] === 'agent_voice_changed'
      )?.[1]
      
      voiceChangedHandler?.({ voice_id: 'voice2' })
      
      await waitFor(() => {
        expect(screen.queryByRole('alert')).not.toBeInTheDocument()
      })
    })

    it('should display loading state from SDK hooks', () => {
      ;(useAgentCData as any).mockReturnValue({
        data: { voices: [], avatars: [] },
        isInitialized: true,
        isLoading: true
      })
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toHaveTextContent('Loading...')
      expect(button).toBeDisabled()
    })

    it('should handle voice model with missing description', async () => {
      ;(useVoiceModel as any).mockReturnValue({
        currentVoice: { 
          voice_id: 'custom_voice',
          vendor: 'Custom',
          description: null
        },
        isLoading: false,
        error: null
      })
      
      render(<OutputSelector />)
      
      const button = screen.getByRole('button', { name: /output mode selector/i })
      expect(button).toHaveTextContent('Custom - custom_voice')
    })
  })
})