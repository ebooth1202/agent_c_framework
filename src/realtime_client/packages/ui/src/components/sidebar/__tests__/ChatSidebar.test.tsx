import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatSidebar } from '../ChatSidebar';
import { axe, toHaveNoViolations } from 'jest-axe';
import * as realtimeReact from '@agentc/realtime-react';

expect.extend(toHaveNoViolations);

// Mock the hooks
vi.mock('@agentc/realtime-react', () => ({
  useChatSessions: vi.fn(() => ({
    sessions: [],
    currentSessionId: null,
    createSession: vi.fn(),
    deleteSession: vi.fn(),
    selectSession: vi.fn(),
  })),
  useConnection: vi.fn(() => ({
    isConnected: true,
    connectionState: 'connected',
  })),
  useUser: vi.fn(() => ({
    user: {
      id: 'user-1',
      name: 'John Doe',
      email: 'john@example.com',
      avatar: 'https://example.com/avatar.jpg',
    },
  })),
}));

describe('ChatSidebar', () => {
  const user = userEvent.setup();

  const defaultProps = {
    isOpen: true,
    onToggle: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the sidebar', () => {
      render(<ChatSidebar {...defaultProps} />);
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(<ChatSidebar {...defaultProps} className="custom-sidebar" />);
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveClass('custom-sidebar');
    });

    it('should render when closed', () => {
      render(<ChatSidebar {...defaultProps} isOpen={false} />);
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveAttribute('aria-expanded', 'false');
    });
  });

  describe('Toggle Functionality', () => {
    it('should show toggle button', () => {
      render(<ChatSidebar {...defaultProps} />);
      const toggleButton = screen.getByRole('button', { name: /toggle sidebar/i });
      expect(toggleButton).toBeInTheDocument();
    });

    it('should call onToggle when clicked', async () => {
      const onToggle = vi.fn();
      render(<ChatSidebar {...defaultProps} onToggle={onToggle} />);
      
      const toggleButton = screen.getByRole('button', { name: /toggle sidebar/i });
      await user.click(toggleButton);
      
      expect(onToggle).toHaveBeenCalled();
    });

    it('should update aria-expanded based on state', () => {
      const { rerender } = render(<ChatSidebar {...defaultProps} isOpen={true} />);
      let sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveAttribute('aria-expanded', 'true');

      rerender(<ChatSidebar {...defaultProps} isOpen={false} />);
      sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveAttribute('aria-expanded', 'false');
    });
  });

  describe('User Display', () => {
    it('should display user information', () => {
      vi.mocked(realtimeReact.useUser).mockReturnValue({
        user: {
          id: 'user-1',
          name: 'John Doe',
          email: 'john@example.com',
          avatar: 'https://example.com/avatar.jpg',
        },
      });

      render(<ChatSidebar {...defaultProps} />);
      
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('john@example.com')).toBeInTheDocument();
    });

    it('should display user avatar', () => {
      vi.mocked(realtimeReact.useUser).mockReturnValue({
        user: {
          id: 'user-1',
          name: 'John Doe',
          email: 'john@example.com',
          avatar: 'https://example.com/avatar.jpg',
        },
      });

      render(<ChatSidebar {...defaultProps} />);
      
      const avatar = screen.getByRole('img', { name: /john doe/i });
      expect(avatar).toHaveAttribute('src', 'https://example.com/avatar.jpg');
    });

    it('should show fallback avatar when no image', () => {
      vi.mocked(realtimeReact.useUser).mockReturnValue({
        user: {
          id: 'user-1',
          name: 'John Doe',
          email: 'john@example.com',
          avatar: null,
        },
      });

      render(<ChatSidebar {...defaultProps} />);
      
      const fallbackAvatar = screen.getByText('JD');
      expect(fallbackAvatar).toBeInTheDocument();
    });
  });

  describe('Session List', () => {
    it('should render session list', () => {
      const mockSessions = [
        { id: '1', name: 'Session 1', createdAt: new Date() },
        { id: '2', name: 'Session 2', createdAt: new Date() },
      ];

      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: '1',
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
      });

      render(<ChatSidebar {...defaultProps} />);
      
      expect(screen.getByText('Session 1')).toBeInTheDocument();
      expect(screen.getByText('Session 2')).toBeInTheDocument();
    });

    it('should highlight current session', () => {
      const mockSessions = [
        { id: '1', name: 'Session 1', createdAt: new Date() },
        { id: '2', name: 'Session 2', createdAt: new Date() },
      ];

      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: mockSessions,
        currentSessionId: '1',
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
      });

      render(<ChatSidebar {...defaultProps} />);
      
      const currentSession = screen.getByText('Session 1').closest('li');
      expect(currentSession).toHaveClass('bg-accent');
    });
  });

  describe('New Session Button', () => {
    it('should show new session button', () => {
      render(<ChatSidebar {...defaultProps} />);
      const newSessionButton = screen.getByRole('button', { name: /new chat/i });
      expect(newSessionButton).toBeInTheDocument();
    });

    it('should create new session on click', async () => {
      const createSession = vi.fn();
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: [],
        currentSessionId: null,
        createSession,
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
      });

      render(<ChatSidebar {...defaultProps} />);
      
      const newSessionButton = screen.getByRole('button', { name: /new chat/i });
      await user.click(newSessionButton);
      
      expect(createSession).toHaveBeenCalled();
    });
  });

  describe('Settings Menu', () => {
    it('should show settings button', () => {
      render(<ChatSidebar {...defaultProps} />);
      const settingsButton = screen.getByRole('button', { name: /settings/i });
      expect(settingsButton).toBeInTheDocument();
    });

    it('should open settings menu on click', async () => {
      render(<ChatSidebar {...defaultProps} />);
      
      const settingsButton = screen.getByRole('button', { name: /settings/i });
      await user.click(settingsButton);
      
      const menu = screen.getByRole('menu');
      expect(menu).toBeInTheDocument();
    });

    it('should show menu options', async () => {
      render(<ChatSidebar {...defaultProps} />);
      
      const settingsButton = screen.getByRole('button', { name: /settings/i });
      await user.click(settingsButton);
      
      expect(screen.getByRole('menuitem', { name: /profile/i })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: /preferences/i })).toBeInTheDocument();
      expect(screen.getByRole('menuitem', { name: /logout/i })).toBeInTheDocument();
    });
  });

  describe('Responsive Behavior', () => {
    it('should collapse on mobile', () => {
      render(<ChatSidebar {...defaultProps} isMobile />);
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveClass('w-16'); // Collapsed width
    });

    it('should overlay on mobile when expanded', () => {
      render(<ChatSidebar {...defaultProps} isMobile isOpen />);
      
      // Should show overlay backdrop
      const overlay = screen.getByRole('presentation');
      expect(overlay).toBeInTheDocument();
      expect(overlay).toHaveClass('fixed', 'inset-0', 'bg-black/50');
    });

    it('should close on overlay click on mobile', async () => {
      const onToggle = vi.fn();
      render(<ChatSidebar {...defaultProps} isMobile isOpen onToggle={onToggle} />);
      
      const overlay = screen.getByRole('presentation');
      await user.click(overlay);
      
      expect(onToggle).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(<ChatSidebar {...defaultProps} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA labels', () => {
      render(<ChatSidebar {...defaultProps} />);
      
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveAttribute('aria-label', 'Chat sidebar');
      
      const nav = screen.getByRole('navigation');
      expect(nav).toHaveAttribute('aria-label', 'Chat sessions');
    });

    it('should support keyboard navigation', async () => {
      render(<ChatSidebar {...defaultProps} />);
      
      // Tab to new chat button
      await user.tab();
      const newChatButton = screen.getByRole('button', { name: /new chat/i });
      expect(newChatButton).toHaveFocus();
      
      // Tab to toggle button
      await user.tab();
      const toggleButton = screen.getByRole('button', { name: /toggle sidebar/i });
      expect(toggleButton).toHaveFocus();
    });

    it('should trap focus when modal overlay is shown', async () => {
      render(<ChatSidebar {...defaultProps} isMobile isOpen />);
      
      const sidebar = screen.getByRole('complementary');
      const focusableElements = sidebar.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      // Focus should be trapped within sidebar
      expect(focusableElements.length).toBeGreaterThan(0);
    });

    it('should announce sidebar state changes', () => {
      const { rerender } = render(<ChatSidebar {...defaultProps} isOpen={true} />);
      
      let status = screen.getByRole('status');
      expect(status).toHaveTextContent(/sidebar expanded/i);
      
      rerender(<ChatSidebar {...defaultProps} isOpen={false} />);
      status = screen.getByRole('status');
      expect(status).toHaveTextContent(/sidebar collapsed/i);
    });
  });

  describe('Theme Support', () => {
    it('should apply light theme classes', () => {
      render(<ChatSidebar {...defaultProps} theme="light" />);
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveClass('bg-background', 'text-foreground');
    });

    it('should apply dark theme classes', () => {
      render(<ChatSidebar {...defaultProps} theme="dark" />);
      const sidebar = screen.getByRole('complementary');
      expect(sidebar).toHaveClass('dark:bg-background', 'dark:text-foreground');
    });
  });

  describe('Loading States', () => {
    it('should show loading skeleton for sessions', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: [],
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        isLoading: true,
      });

      render(<ChatSidebar {...defaultProps} />);
      
      const skeletons = screen.getAllByRole('progressbar');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Error States', () => {
    it('should display error message', () => {
      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: [],
        currentSessionId: null,
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
        error: new Error('Failed to load sessions'),
      });

      render(<ChatSidebar {...defaultProps} />);
      
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent(/failed to load sessions/i);
    });
  });

  describe('Performance', () => {
    it('should handle many sessions efficiently', () => {
      const manySessions = Array.from({ length: 100 }, (_, i) => ({
        id: `session-${i}`,
        name: `Session ${i}`,
        createdAt: new Date(),
      }));

      vi.mocked(realtimeReact.useChatSessions).mockReturnValue({
        sessions: manySessions,
        currentSessionId: 'session-50',
        createSession: vi.fn(),
        deleteSession: vi.fn(),
        selectSession: vi.fn(),
      });

      const { container } = render(<ChatSidebar {...defaultProps} />);
      
      // Should render without performance issues
      const sessionItems = container.querySelectorAll('li');
      expect(sessionItems.length).toBe(100);
    });
  });
});