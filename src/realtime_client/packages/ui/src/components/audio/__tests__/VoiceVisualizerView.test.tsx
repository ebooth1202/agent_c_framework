import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { VoiceVisualizerView } from '../VoiceVisualizerView';
import { axe, toHaveNoViolations } from 'jest-axe';
import { updateMockState } from '../../../test/mocks/realtime-react';

expect.extend(toHaveNoViolations);

describe('VoiceVisualizerView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the voice visualizer component', () => {
      render(<VoiceVisualizerView />);
      const title = screen.getByText('Voice Mode Active');
      expect(title).toBeInTheDocument();
    });

    it('should apply custom className when provided', () => {
      const { container } = render(<VoiceVisualizerView className="custom-class" />);
      expect(container.firstChild).toHaveClass('custom-class');
    });
  });

  describe('Visual States', () => {
    it('should show active state when audio is detected', () => {
      updateMockState('audio', {
        isRecording: true,
        audioLevel: 0.8,
      });

      const { container } = render(<VoiceVisualizerView />);
      const listeningText = screen.getByText('Listening...');
      expect(listeningText).toBeInTheDocument();
      
      // Check audio level bar
      const levelBar = container.querySelector('.bg-primary');
      expect(levelBar).toBeTruthy();
    });

    it('should show inactive state when no audio is detected', () => {
      updateMockState('audio', {
        isRecording: false,
        audioLevel: 0,
      });

      render(<VoiceVisualizerView />);
      const inactiveText = screen.getByText('Visualizer integration coming soon');
      expect(inactiveText).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have no accessibility violations', async () => {
      const { container } = render(<VoiceVisualizerView />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('should have descriptive text for screen readers', () => {
      render(<VoiceVisualizerView />);
      const title = screen.getByText('Voice Mode Active');
      expect(title).toBeInTheDocument();
      
      // Check status text changes based on recording state
      const statusText = screen.getByText('Visualizer integration coming soon');
      expect(statusText).toBeInTheDocument();
    });

    it('should announce state changes to screen readers', () => {
      const { rerender } = render(<VoiceVisualizerView />);
      
      // Initial state - not recording
      expect(screen.getByText('Visualizer integration coming soon')).toBeInTheDocument();
      
      // Update to recording state
      updateMockState('audio', {
        isRecording: true,
        audioLevel: 0.9,
      });
      
      rerender(<VoiceVisualizerView />);
      expect(screen.getByText('Listening...')).toBeInTheDocument();
    });
  });

  describe('Performance', () => {
    it('should handle rapid level updates efficiently', () => {
      const { rerender } = render(<VoiceVisualizerView />);

      // Simulate rapid audio level changes
      for (let i = 0; i < 100; i++) {
        updateMockState('audio', {
          audioLevel: Math.random(),
          isRecording: Math.random() > 0.5,
        });
        rerender(<VoiceVisualizerView />);
      }

      // Component should still be in the document
      const title = screen.getByText('Voice Mode Active');
      expect(title).toBeInTheDocument();
    });
  });
});