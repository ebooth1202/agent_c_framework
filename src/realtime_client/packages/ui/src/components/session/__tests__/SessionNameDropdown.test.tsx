import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor, act, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SessionNameDropdown } from '../SessionNameDropdown'
import type { RealtimeClient } from '@agentc/realtime-core'

// Mock the React hook
vi.mock('@agentc/realtime-react', () => ({
  useRealtimeClientSafe: vi.fn()
}))

// Mock sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}))

import { useRealtimeClientSafe } from '@agentc/realtime-react'
import { toast } from 'sonner'

describe('SessionNameDropdown', () => {
  let mockClient: Partial<RealtimeClient>
  const mockUseRealtimeClientSafe = vi.mocked(useRealtimeClientSafe)
  const mockToast = vi.mocked(toast)
  
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks()
    
    // Create mock client
    mockClient = {
      on: vi.fn(),
      off: vi.fn(),
      sendEvent: vi.fn().mockResolvedValue(undefined)
    }
    
    // Set up default mock return
    mockUseRealtimeClientSafe.mockReturnValue(mockClient as RealtimeClient)
  })
  
  afterEach(() => {
    vi.restoreAllMocks()
  })
  
  it('should render with default session name', () => {
    render(<SessionNameDropdown />)
    expect(screen.getByText('New Chat')).toBeInTheDocument()
  })
  
  it('should render with provided session name', () => {
    render(<SessionNameDropdown sessionName="My Session" />)
    expect(screen.getByText('My Session')).toBeInTheDocument()
  })
  
  it('should open dropdown menu when clicked', async () => {
    render(<SessionNameDropdown />)
    const trigger = screen.getByRole('button', { name: /session options/i })
    
    await userEvent.click(trigger)
    
    expect(screen.getByText('Rename session')).toBeInTheDocument()
    expect(screen.getByText('Delete session')).toBeInTheDocument()
  })
  
  it('should disable menu items when client is not available', async () => {
    mockUseRealtimeClientSafe.mockReturnValue(null)
    
    render(<SessionNameDropdown />)
    const trigger = screen.getByRole('button', { name: /session options/i })
    
    await userEvent.click(trigger)
    
    const renameItem = screen.getByRole('menuitem', { name: /rename session/i })
    const deleteItem = screen.getByRole('menuitem', { name: /delete session/i })
    
    expect(renameItem).toHaveAttribute('aria-disabled', 'true')
    expect(deleteItem).toHaveAttribute('aria-disabled', 'true')
  })
  
  it('should handle session changed events', () => {
    render(<SessionNameDropdown />)
    
    // Verify event listeners were registered
    expect(mockClient.on).toHaveBeenCalledWith('chat_session_changed', expect.any(Function))
    expect(mockClient.on).toHaveBeenCalledWith('chat_session_name_changed', expect.any(Function))
  })
  
  it('should update session name from ChatSessionChangedEvent', async () => {
    const { rerender } = render(<SessionNameDropdown />)
    
    // Get the event handler
    const [[, handler]] = vi.mocked(mockClient.on!).mock.calls.filter(
      ([event]) => event === 'chat_session_changed'
    )
    
    // Simulate event
    await act(async () => {
      handler({
        type: 'chat_session_changed',
        chat_session: {
          session_id: 'test-123',
          session_name: 'Updated Session',
          messages: [],
          version: 1,
          token_count: 0,
          context_window_size: 0,
          vendor: 'openai',
          display_name: 'Display Name'
        }
      })
    })
    
    // Force re-render to see updated state
    rerender(<SessionNameDropdown />)
    
    await waitFor(() => {
      expect(screen.getByText('Updated Session')).toBeInTheDocument()
    })
  })
  
  it('should open rename dialog when rename is clicked', async () => {
    render(<SessionNameDropdown sessionName="Current Name" />)
    
    // Open dropdown
    const trigger = screen.getByRole('button', { name: /session options/i })
    await userEvent.click(trigger)
    
    // Click rename
    const renameItem = screen.getByRole('menuitem', { name: /rename session/i })
    await userEvent.click(renameItem)
    
    // Check dialog opened
    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
    expect(screen.getByText('Rename Session')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Current Name')).toBeInTheDocument()
  })
  
  it('should send rename event when confirmed', async () => {
    render(<SessionNameDropdown sessionName="Old Name" />)
    
    // Open dropdown and click rename
    await userEvent.click(screen.getByRole('button', { name: /session options/i }))
    await userEvent.click(screen.getByRole('menuitem', { name: /rename session/i }))
    
    // Change name in input
    const input = screen.getByLabelText(/session name/i)
    await userEvent.clear(input)
    await userEvent.type(input, 'New Name')
    
    // Click rename button
    const renameButton = screen.getByRole('button', { name: /^rename$/i })
    await userEvent.click(renameButton)
    
    // Verify event was sent
    await waitFor(() => {
      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'set_chat_session_name',
        session_name: 'New Name'
      })
    })
    
    // Verify success toast
    expect(mockToast.success).toHaveBeenCalledWith('Session renamed successfully')
  })
  
  it('should open delete confirmation dialog when delete is clicked', async () => {
    render(<SessionNameDropdown sessionName="Session to Delete" />)
    
    // Open dropdown
    await userEvent.click(screen.getByRole('button', { name: /session options/i }))
    
    // Click delete
    const deleteItem = screen.getByRole('menuitem', { name: /delete session/i })
    await userEvent.click(deleteItem)
    
    // Check confirmation dialog
    const dialog = screen.getByRole('alertdialog')
    expect(dialog).toBeInTheDocument()
    
    // Check dialog content - use within to scope queries to the dialog
    const { getByRole, getByText } = within(dialog)
    expect(getByRole('heading', { name: /delete session/i })).toBeInTheDocument()
    // The session name appears both in the button and in the dialog, so we check within the dialog specifically
    expect(getByText(/Session to Delete/)).toBeInTheDocument()
    expect(getByText(/this action cannot be undone/i)).toBeInTheDocument()
  })
  
  it('should send delete event when confirmed', async () => {
    render(<SessionNameDropdown sessionName="Session to Delete" />)
    
    // Open dropdown and click delete
    await userEvent.click(screen.getByRole('button', { name: /session options/i }))
    await userEvent.click(screen.getByRole('menuitem', { name: /delete session/i }))
    
    // Click delete button in confirmation
    const deleteButton = screen.getByRole('button', { name: /delete session$/i })
    await userEvent.click(deleteButton)
    
    // Verify event was sent
    await waitFor(() => {
      expect(mockClient.sendEvent).toHaveBeenCalledWith({
        type: 'delete_chat_session'
      })
    })
    
    // Verify success toast
    expect(mockToast.success).toHaveBeenCalledWith('Session deleted successfully')
  })
  
  it('should handle errors gracefully', async () => {
    // Make sendEvent reject
    vi.mocked(mockClient.sendEvent!).mockRejectedValue(new Error('Network error'))
    
    render(<SessionNameDropdown sessionName="Test Session" />)
    
    // Try to rename
    await userEvent.click(screen.getByRole('button', { name: /session options/i }))
    await userEvent.click(screen.getByRole('menuitem', { name: /rename session/i }))
    
    const input = screen.getByLabelText(/session name/i)
    await userEvent.clear(input)
    await userEvent.type(input, 'New Name')
    
    await userEvent.click(screen.getByRole('button', { name: /^rename$/i }))
    
    // Verify error toast
    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Failed to rename session')
    })
  })
  
  it('should unsubscribe from events on unmount', () => {
    const { unmount } = render(<SessionNameDropdown />)
    
    // Verify subscriptions
    expect(mockClient.on).toHaveBeenCalled()
    
    // Unmount
    unmount()
    
    // Verify cleanup
    expect(mockClient.off).toHaveBeenCalledWith('chat_session_changed', expect.any(Function))
    expect(mockClient.off).toHaveBeenCalledWith('chat_session_name_changed', expect.any(Function))
  })
})