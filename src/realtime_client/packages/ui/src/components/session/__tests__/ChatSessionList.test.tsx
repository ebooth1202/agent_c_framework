import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatSessionList } from '../ChatSessionList';
import { axe, toHaveNoViolations } from 'jest-axe';
import * as realtimeReact from '@agentc/realtime-react';

expect.extend(toHaveNoViolations);

// Mock the hooks from @agentc/realtime-react
vi.mock('@agentc/realtime-react', () => ({
  useChatSessions: vi.fn(() => ({
    sessions: [],
    currentSessionId: null,
    createSession: vi.fn(),
    deleteSession: vi.fn(),
    selectSession: vi.fn(),
    renameSession: vi.fn(),
  })),
  useConnection: vi.fn(() => ({
    isConnected: true,
    connectionState: 'connected',
  })),
}));

describe('ChatSessionList', () => {
  const user = userEvent.setup();

  const mockSessions = [
    {
      id: 'session-1',
      name: 'Morning Chat',
      createdAt: new Date('2024-01-01T09:00:00'),
      updatedAt: new Date('2024-01-01T10:00:00'),
      messageCount: 5,
    },
    {
      id: 'session-2',
      name: 'Project Discussion',
      createdAt: new Date('2024-01-01T14:00:00'),
      updatedAt: new Date('2024-01-01T15:30:00'),
      messageCount: 12,
    },
    {
      id: 'session-3',
      name: 'Quick Question',
      createdAt: new Date('2024-01-02T11:00:00'),
      updatedAt: new Date('2024-01-02T11:15:00'),
      messageCount: 3,
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the session list', () => {
      render(<ChatSessionList />);
      const list = screen.getByRole('list', { name: /chat sessions/i });
      expect(list).toBeInTheDocument();
    });

    it('should display empty state when no sessions', () => {
      render(<ChatSessionList />);
      expect(screen.getByText(/no chat sessions/i)).toBeInTheDocument();
    });

    it('should display all sessions', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      expect(screen.getByText('Morning Chat')).toBeInTheDocument();
      expect(screen.getByText('Project Discussion')).toBeInTheDocument();
      expect(screen.getByText('Quick Question')).toBeInTheDocument();
    });
  });

  describe('Session Selection', () => {
    it('should highlight current session', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: 'session-2',
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const currentSession = screen.getByText('Project Discussion').closest('li');
      expect(currentSession).toHaveAttribute('aria-current', 'true');
      expect(currentSession).toHaveClass('bg-accent');
    });

    it('should handle session selection', async () => {
      const selectSession = vi.fn();
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession,
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const sessionItem = screen.getByText('Morning Chat');
      await user.click(sessionItem);
      
      expect(selectSession).toHaveBeenCalledWith('session-1');
    });
  });

  describe('Session Creation', () => {
    it('should show create new session button', () => {
      render(<ChatSessionList />);
      const createButton = screen.getByRole('button', { name: /new session/i });
      expect(createButton).toBeInTheDocument();
    });

    it('should handle session creation', async () => {
      const createSession = vi.fn();
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession,
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const createButton = screen.getByRole('button', { name: /new session/i });
      await user.click(createButton);
      
      expect(createSession).toHaveBeenCalled();
    });
  });

  describe('Session Management', () => {
    it('should show session actions menu', async () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const moreButton = screen.getAllByRole('button', { name: /more options/i })[0];
      await user.click(moreButton);
      
      const menu = screen.getByRole('menu');
      expect(menu).toBeInTheDocument();
      expect(within(menu).getByText(/rename/i)).toBeInTheDocument();
      expect(within(menu).getByText(/delete/i)).toBeInTheDocument();
    });

    it('should handle session rename', async () => {
      const renameSession = vi.fn();
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession,
      });

      render(<ChatSessionList />);
      
      const moreButton = screen.getAllByRole('button', { name: /more options/i })[0];
      await user.click(moreButton);
      
      const renameOption = screen.getByText(/rename/i);
      await user.click(renameOption);
      
      // Should show rename dialog
      const input = screen.getByRole('textbox', { name: /session name/i });
      await user.clear(input);
      await user.type(input, 'New Name');
      
      const saveButton = screen.getByRole('button', { name: /save/i });
      await user.click(saveButton);
      
      expect(renameSession).toHaveBeenCalledWith('session-1', 'New Name');
    });

    it('should handle session deletion with confirmation', async () => {
      const deleteSession = vi.fn();
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession,
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const moreButton = screen.getAllByRole('button', { name: /more options/i })[0];
      await user.click(moreButton);
      
      const deleteOption = screen.getByText(/delete/i);
      await user.click(deleteOption);
      
      // Should show confirmation dialog
      const confirmButton = screen.getByRole('button', { name: /confirm/i });
      await user.click(confirmButton);
      
      expect(deleteSession).toHaveBeenCalledWith('session-1');
    });
  });

  describe('Session Metadata', () => {
    it('should display session timestamps', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      // Should show relative timestamps
      expect(screen.getByText(/Jan 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Jan 2/i)).toBeInTheDocument();
    });

    it('should display message count', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      expect(screen.getByText(/5 messages/i)).toBeInTheDocument();
      expect(screen.getByText(/12 messages/i)).toBeInTheDocument();
      expect(screen.getByText(/3 messages/i)).toBeInTheDocument();
    });
  });

  describe('Search and Filter', () => {
    it('should show search input', () => {
      render(<ChatSessionList showSearch />);
      const searchInput = screen.getByRole('searchbox', { name: /search sessions/i });
      expect(searchInput).toBeInTheDocument();
    });

    it('should filter sessions by search term', async () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList showSearch />);
      
      const searchInput = screen.getByRole('searchbox');
      await user.type(searchInput, 'Project');
      
      // Should only show matching session
      expect(screen.getByText('Project Discussion')).toBeInTheDocument();
      expect(screen.queryByText('Morning Chat')).not.toBeInTheDocument();
      expect(screen.queryByText('Quick Question')).not.toBeInTheDocument();
    });

    it('should show no results message when search has no matches', async () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList showSearch />);
      
      const searchInput = screen.getByRole('searchbox');
      await user.type(searchInput, 'NonExistent');
      
      expect(screen.getByText(/no sessions found/i)).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(<ChatSessionList />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: 'session-2',
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const list = screen.getByRole('list');
      expect(list).toHaveAttribute('aria-label', 'Chat sessions');
      
      const currentSession = screen.getByText('Project Discussion').closest('li');
      expect(currentSession).toHaveAttribute('aria-current', 'true');
    });

    it('should support keyboard navigation', async () => {
      const selectSession = vi.fn();
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession,
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      // Tab to first session
      await user.tab();
      const firstSession = screen.getByText('Morning Chat').closest('li');
      expect(firstSession).toHaveFocus();
      
      // Arrow down to next session
      await user.keyboard('{ArrowDown}');
      const secondSession = screen.getByText('Project Discussion').closest('li');
      expect(secondSession).toHaveFocus();
      
      // Enter to select
      await user.keyboard('{Enter}');
      expect(selectSession).toHaveBeenCalledWith('session-2');
    });

    it('should announce session count to screen readers', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const status = screen.getByRole('status');
      expect(status).toHaveTextContent(/3 sessions/i);
    });

    it('should have accessible action buttons', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
      });

      render(<ChatSessionList />);
      
      const moreButtons = screen.getAllByRole('button', { name: /more options/i });
      moreButtons.forEach(button => {
        expect(button).toHaveAttribute('aria-label');
        expect(button).toHaveAttribute('aria-haspopup', 'menu');
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading skeleton', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: [],
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
        isLoading: true,
      });

      render(<ChatSessionList />);
      
      const skeletons = screen.getAllByRole('progressbar');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Error Handling', () => {
    it('should display error message', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: [],
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        renameSession: vi.fn(),
        error: new Error('Failed to load sessions'),
      });

      render(<ChatSessionList />);
      
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent(/failed to load sessions/i);
    });
  });
});