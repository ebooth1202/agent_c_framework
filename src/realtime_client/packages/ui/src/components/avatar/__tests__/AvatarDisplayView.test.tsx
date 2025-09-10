import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AvatarDisplayView } from '../AvatarDisplayView';
// TODO: Uncomment when jest-axe is installed
// import { axe, toHaveNoViolations } from 'jest-axe';
import * as realtimeReact from '@agentc/realtime-react';

// TODO: Uncomment when jest-axe is installed
// expect.extend(toHaveNoViolations);

// Mock the hook from @agentc/realtime-react
vi.mock('@agentc/realtime-react', () => ({
  useAvatar: vi.fn(() => ({
    isAvatarActive: false,
    avatarUrl: null,
    startAvatar: vi.fn(),
    stopAvatar: vi.fn(),
    avatarState: 'idle',
  })),
  useConnection: vi.fn(() => ({
    isConnected: true,
    connectionState: 'connected',
  })),
}));

describe('AvatarDisplayView', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the avatar display component', () => {
      render(<AvatarDisplayView />);
      const avatarContainer = screen.getByRole('region', { name: /avatar display/i });
      expect(avatarContainer).toBeInTheDocument();
    });

    it('should apply custom className when provided', () => {
      const { container } = render(<AvatarDisplayView className="custom-avatar-class" />);
      expect(container.firstChild).toHaveClass('custom-avatar-class');
    });

    it('should show placeholder when avatar is not active', () => {
      render(<AvatarDisplayView />);
      const placeholder = screen.getByText(/avatar not active/i);
      expect(placeholder).toBeInTheDocument();
    });
  });

  describe('Avatar States', () => {
    it('should display avatar when active', () => {
      vi.mocked(realtimeReact.useAvatar).mockReturnValue({
        isAvatarActive: true,
        avatarUrl: 'https://example.com/avatar',
        startAvatar: vi.fn(),
        stopAvatar: vi.fn(),
        avatarState: 'active',
      });

      render(<AvatarDisplayView />);
      const avatarVideo = screen.getByRole('img', { name: /ai avatar/i });
      expect(avatarVideo).toBeInTheDocument();
    });

    it('should show loading state during avatar initialization', () => {
      vi.mocked(realtimeReact.useAvatar).mockReturnValue({
        isAvatarActive: false,
        avatarUrl: null,
        startAvatar: vi.fn(),
        stopAvatar: vi.fn(),
        avatarState: 'loading',
      });

      render(<AvatarDisplayView />);
      const loadingIndicator = screen.getByText(/loading avatar/i);
      expect(loadingIndicator).toBeInTheDocument();
    });

    it('should show error state when avatar fails to load', () => {
      vi.mocked(realtimeReact.useAvatar).mockReturnValue({
        isAvatarActive: false,
        avatarUrl: null,
        startAvatar: vi.fn(),
        stopAvatar: vi.fn(),
        avatarState: 'error',
      });

      render(<AvatarDisplayView />);
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toBeInTheDocument();
      expect(errorMessage).toHaveTextContent(/failed to load avatar/i);
    });
  });

  describe('Interactivity', () => {
    it('should handle avatar toggle', async () => {
      const startAvatar = vi.fn();
      const stopAvatar = vi.fn();
      vi.mocked(realtimeReact.useAvatar).mockReturnValue({
        isAvatarActive: false,
        avatarUrl: null,
        startAvatar,
        stopAvatar,
        avatarState: 'idle',
      });

      render(<AvatarDisplayView />);
      const toggleButton = screen.getByRole('button', { name: /start avatar/i });
      
      await user.click(toggleButton);
      expect(startAvatar).toHaveBeenCalled();
    });

    it('should disable controls when connection is lost', () => {
      vi.mocked(realtimeReact.useConnection).mockReturnValue({
        isConnected: false,
        connectionState: 'disconnected',
      });

      render(<AvatarDisplayView />);
      const toggleButton = screen.getByRole('button');
      expect(toggleButton).toBeDisabled();
    });
  });

  describe('Accessibility', () => {
    // TODO: Uncomment when jest-axe is installed
    it.skip('should have no accessibility violations', async () => {
      // const { container } = render(<AvatarDisplayView />);
      // const results = await axe(container);
      // expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA attributes for avatar region', () => {
      render(<AvatarDisplayView />);
      const avatarRegion = screen.getByRole('region', { name: /avatar display/i });
      expect(avatarRegion).toHaveAttribute('aria-label');
    });

    it('should announce avatar state changes to screen readers', () => {
      const { rerender } = render(<AvatarDisplayView />);
      
      // Check for live region
      const liveRegion = screen.getByRole('status');
      expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      
      // Simulate state change
      vi.mocked(realtimeReact.useAvatar).mockReturnValue({
        isAvatarActive: true,
        avatarUrl: 'https://example.com/avatar',
        startAvatar: vi.fn(),
        stopAvatar: vi.fn(),
        avatarState: 'active',
      });
      
      rerender(<AvatarDisplayView />);
      expect(liveRegion).toHaveTextContent(/avatar active/i);
    });

    it('should support keyboard navigation for controls', async () => {
      render(<AvatarDisplayView />);
      const toggleButton = screen.getByRole('button', { name: /start avatar/i });
      
      // Should be focusable
      await user.tab();
      expect(toggleButton).toHaveFocus();
      
      // Should respond to Enter key
      await user.keyboard('{Enter}');
      expect(vi.mocked(realtimeReact.useAvatar).mock.results[0].value.startAvatar).toHaveBeenCalled();
    });

    it('should provide descriptive labels for all interactive elements', () => {
      render(<AvatarDisplayView />);
      
      const toggleButton = screen.getByRole('button');
      expect(toggleButton).toHaveAttribute('aria-label');
      
      // All buttons should have accessible names
      const allButtons = screen.getAllByRole('button');
      allButtons.forEach(button => {
        expect(button).toHaveAccessibleName();
      });
    });
  });

  describe('Responsive Design', () => {
    it('should adapt to container size', () => {
      const { container } = render(<AvatarDisplayView />);
      const avatarContainer = container.firstChild as HTMLElement;
      
      // Should have responsive classes
      expect(avatarContainer.className).toMatch(/w-full|h-full|flex/);
    });
  });
});