import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { VoiceVisualizerView } from '../VoiceVisualizerView';
// TODO: Uncomment when jest-axe is installed
// import { axe, toHaveNoViolations } from 'jest-axe';
import * as realtimeReact from '@agentc/realtime-react';

// TODO: Uncomment when jest-axe is installed
// expect.extend(toHaveNoViolations);

// Mock the hook from @agentc/realtime-react
vi.mock('@agentc/realtime-react', () => ({
  useAudioLevel: vi.fn(() => ({
    level: 0.5,
    isActive: true,
  })),
  useConnection: vi.fn(() => ({
    isConnected: true,
    connectionState: 'connected',
  })),
}));

describe('VoiceVisualizerView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the voice visualizer component', () => {
      render(<VoiceVisualizerView />);
      const visualizer = screen.getByRole('img', { name: /voice activity/i });
      expect(visualizer).toBeInTheDocument();
    });

    it('should apply custom className when provided', () => {
      const { container } = render(<VoiceVisualizerView className="custom-class" />);
      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Visual States', () => {
    it('should show active state when audio is detected', () => {
      vi.mocked(realtimeReact.useAudioLevel).mockReturnValue({
        level: 0.8,
        isActive: true,
      });

      render(<VoiceVisualizerView />);
      const visualizer = screen.getByRole('img', { name: /voice activity/i });
      expect(visualizer).toHaveAttribute('aria-live', 'polite');
    });

    it('should show inactive state when no audio is detected', () => {
      vi.mocked(realtimeReact.useAudioLevel).mockReturnValue({
        level: 0,
        isActive: false,
      });

      render(<VoiceVisualizerView />);
      const visualizer = screen.getByRole('img', { name: /voice activity/i });
      expect(visualizer).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    // TODO: Uncomment when jest-axe is installed
    it.skip('should have no accessibility violations', async () => {
      // const { container } = render(<VoiceVisualizerView />);
      // const results = await axe(container);
      // expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA attributes', () => {
      render(<VoiceVisualizerView />);
      const visualizer = screen.getByRole('img', { name: /voice activity/i });
      expect(visualizer).toHaveAttribute('aria-label');
      expect(visualizer).toHaveAttribute('aria-live', 'polite');
    });

    it('should announce state changes to screen readers', () => {
      const { rerender } = render(<VoiceVisualizerView />);
      const visualizer = screen.getByRole('img', { name: /voice activity/i });
      
      // Should have live region for announcements
      expect(visualizer).toHaveAttribute('aria-live', 'polite');
      
      // State change should update aria-label
      vi.mocked(realtimeReact.useAudioLevel).mockReturnValue({
        level: 0.9,
        isActive: true,
      });
      
      rerender(<VoiceVisualizerView />);
      expect(visualizer).toHaveAttribute('aria-label', expect.stringContaining('active'));
    });
  });

  describe('Performance', () => {
    it('should handle rapid level updates efficiently', () => {
      const { rerender } = render(<VoiceVisualizerView />);

      // Simulate rapid audio level changes
      for (let i = 0; i < 100; i++) {
        vi.mocked(realtimeReact.useAudioLevel).mockReturnValue({
          level: Math.random(),
          isActive: Math.random() > 0.5,
        });
        rerender(<VoiceVisualizerView />);
      }

      // Component should still be in the document
      const visualizer = screen.getByRole('img', { name: /voice activity/i });
      expect(visualizer).toBeInTheDocument();
    });
  });
});