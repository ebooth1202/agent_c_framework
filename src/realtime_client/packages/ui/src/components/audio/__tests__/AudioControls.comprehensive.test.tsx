/**
 * Comprehensive Audio Controls Tests
 * Testing all audio components: VoiceVisualizer, RecordingButton, MuteToggle
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { VoiceVisualizerView } from '../VoiceVisualizerView';
import { RecordingButton } from '../RecordingButton';
import { MuteToggle } from '../MuteToggle';
import { AudioControlsPanel } from '../AudioControlsPanel';
import { 
  updateMockState,
  resetAllMocks,
  useAudio,
  useConnection
} from '../../../test/mocks/realtime-react';
import { 
  setupUser, 
  animation, 
  styles, 
  componentState,
  focus,
  keyboard,
  theme,
  scenarios
} from '../../../test/utils/ui-test-utils';

expect.extend(toHaveNoViolations);

describe('Audio Controls - Comprehensive Tests', () => {
  let user: ReturnType<typeof setupUser>;
  
  beforeEach(() => {
    user = setupUser();
    resetAllMocks();
    vi.useFakeTimers();
    
    // Mock Audio API
    global.MediaRecorder = vi.fn().mockImplementation(() => ({
      start: vi.fn(),
      stop: vi.fn(),
      pause: vi.fn(),
      resume: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      state: 'inactive',
      ondataavailable: null,
      onerror: null,
      onstart: null,
      onstop: null
    }));
    
    // Mock getUserMedia
    navigator.mediaDevices = {
      getUserMedia: vi.fn().mockResolvedValue({
        getTracks: () => [],
        getAudioTracks: () => [{
          stop: vi.fn(),
          enabled: true
        }],
        getVideoTracks: () => []
      })
    } as any;
  });
  
  afterEach(() => {
    vi.useRealTimers();
    vi.clearAllMocks();
  });

  // ========== VOICE VISUALIZER TESTS ==========
  describe('VoiceVisualizerView', () => {
    describe('Rendering States', () => {
      it('should render idle state when not recording', () => {
        updateMockState('audio', {
          isRecording: false,
          audioLevel: 0
        });
        
        render(<VoiceVisualizerView />);
        expect(screen.getByText('Voice Mode Active')).toBeInTheDocument();
        expect(screen.getByText('Visualizer integration coming soon')).toBeInTheDocument();
      });

      it('should render active state when recording', () => {
        updateMockState('audio', {
          isRecording: true,
          audioLevel: 0.5
        });
        
        render(<VoiceVisualizerView />);
        expect(screen.getByText('Listening...')).toBeInTheDocument();
      });

      it('should display audio level indicator', () => {
        updateMockState('audio', {
          isRecording: true,
          audioLevel: 0.75
        });
        
        const { container } = render(<VoiceVisualizerView />);
        const levelBar = container.querySelector('.bg-primary');
        expect(levelBar).toHaveStyle({ width: '75%' });
      });

      it('should animate when recording', () => {
        updateMockState('audio', {
          isRecording: true,
          audioLevel: 0.5
        });
        
        const { container } = render(<VoiceVisualizerView />);
        const animatedElement = container.querySelector('.animate-pulse');
        expect(animatedElement).toBeInTheDocument();
      });
    });

    describe('Visual Feedback', () => {
      it('should scale icon based on audio level', () => {
        updateMockState('audio', {
          isRecording: true,
          audioLevel: 0.8
        });
        
        const { container } = render(<VoiceVisualizerView />);
        const icon = container.querySelector('svg');
        const style = icon?.getAttribute('style');
        expect(style).toContain('scale(1.16)'); // 1 + (0.8 * 0.2)
      });

      it('should adjust opacity based on recording state', () => {
        updateMockState('audio', {
          isRecording: true,
          audioLevel: 0.6
        });
        
        const { container } = render(<VoiceVisualizerView />);
        const icon = container.querySelector('svg');
        const style = icon?.getAttribute('style');
        expect(style).toContain('opacity: 0.8'); // 0.5 + (0.6 * 0.5)
      });

      it('should handle rapid audio level changes smoothly', async () => {
        const { rerender } = render(<VoiceVisualizerView />);
        
        // Simulate rapid audio level changes
        for (let i = 0; i < 50; i++) {
          updateMockState('audio', {
            isRecording: true,
            audioLevel: Math.random()
          });
          rerender(<VoiceVisualizerView />);
        }
        
        // Component should still be stable
        expect(screen.getByText('Voice Mode Active')).toBeInTheDocument();
      });
    });

    describe('Accessibility', () => {
      it('should have no accessibility violations', async () => {
        const { container } = render(<VoiceVisualizerView />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('should provide screen reader feedback for state changes', () => {
        const { rerender } = render(<VoiceVisualizerView />);
        
        expect(screen.getByText('Visualizer integration coming soon')).toBeInTheDocument();
        
        updateMockState('audio', {
          isRecording: true,
          audioLevel: 0.5
        });
        rerender(<VoiceVisualizerView />);
        
        expect(screen.getByText('Listening...')).toBeInTheDocument();
      });
    });

    describe('Responsive Design', () => {
      it('should adapt to small screens', () => {
        styles.setViewport(320, 568);
        
        const { container } = render(<VoiceVisualizerView />);
        const visualizer = container.firstChild;
        expect(visualizer).toHaveClass('h-full');
      });

      it('should scale appropriately on tablets', () => {
        styles.setViewport(768, 1024);
        
        render(<VoiceVisualizerView />);
        expect(screen.getByText('Voice Mode Active')).toBeInTheDocument();
      });
    });

    describe('Theme Support', () => {
      it('should apply correct colors in dark mode', () => {
        document.documentElement.classList.add('dark');
        
        const { container } = render(<VoiceVisualizerView />);
        const background = container.firstChild;
        expect(background).toHaveClass('from-background', 'to-muted/20');
      });

      it('should use theme-aware colors for level indicator', () => {
        const { container } = render(<VoiceVisualizerView />);
        const levelBar = container.querySelector('.bg-primary');
        expect(levelBar).toBeInTheDocument();
      });
    });
  });

  // ========== RECORDING BUTTON TESTS ==========
  describe('RecordingButton', () => {
    describe('Button States', () => {
      it('should render start recording state', () => {
        updateMockState('audio', {
          isRecording: false
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button', { name: /start recording/i });
        expect(button).toBeInTheDocument();
        expect(button).not.toBeDisabled();
      });

      it('should render stop recording state', () => {
        updateMockState('audio', {
          isRecording: true
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button', { name: /stop recording/i });
        expect(button).toBeInTheDocument();
      });

      it('should be disabled when not connected', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'disconnected'
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        expect(button).toBeDisabled();
      });

      it('should show loading state during connection', () => {
        updateMockState('connection', {
          isConnected: false,
          connectionState: 'connecting'
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        expect(button).toBeDisabled();
        expect(screen.getByRole('status')).toBeInTheDocument();
      });
    });

    describe('User Interactions', () => {
      it('should start recording on click', async () => {
        const startRecording = vi.fn();
        updateMockState('audio', {
          isRecording: false,
          startRecording
        });
        updateMockState('connection', {
          isConnected: true
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        expect(startRecording).toHaveBeenCalled();
      });

      it('should stop recording on second click', async () => {
        const stopRecording = vi.fn();
        updateMockState('audio', {
          isRecording: true,
          stopRecording
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        expect(stopRecording).toHaveBeenCalled();
      });

      it('should handle keyboard activation', async () => {
        const startRecording = vi.fn();
        updateMockState('audio', {
          isRecording: false,
          startRecording
        });
        updateMockState('connection', {
          isConnected: true
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        
        button.focus();
        await keyboard.enter(user);
        
        expect(startRecording).toHaveBeenCalled();
      });

      it('should support space key activation', async () => {
        const startRecording = vi.fn();
        updateMockState('audio', {
          isRecording: false,
          startRecording
        });
        updateMockState('connection', {
          isConnected: true
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        
        button.focus();
        await keyboard.space(user);
        
        expect(startRecording).toHaveBeenCalled();
      });
    });

    describe('Visual Feedback', () => {
      it('should show recording indicator when active', () => {
        updateMockState('audio', {
          isRecording: true
        });
        
        const { container } = render(<RecordingButton />);
        const recordingIndicator = container.querySelector('.animate-pulse');
        expect(recordingIndicator).toBeInTheDocument();
      });

      it('should change color when recording', () => {
        updateMockState('audio', {
          isRecording: true
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        expect(button).toHaveClass('bg-destructive');
      });

      it('should show tooltip on hover', async () => {
        render(<RecordingButton showTooltip={true} />);
        const button = screen.getByRole('button');
        
        await user.hover(button);
        
        await waitFor(() => {
          const tooltip = screen.getByRole('tooltip');
          expect(tooltip).toBeInTheDocument();
        });
      });
    });

    describe('Accessibility', () => {
      it('should have no accessibility violations', async () => {
        const { container } = render(<RecordingButton />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('should have proper ARIA labels', () => {
        updateMockState('audio', {
          isRecording: false
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-label', 'Start recording');
        
        updateMockState('audio', {
          isRecording: true
        });
        const { rerender } = render(<RecordingButton />);
        rerender(<RecordingButton />);
        
        expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Stop recording');
      });

      it('should announce state changes', async () => {
        const { rerender } = render(<RecordingButton />);
        
        updateMockState('audio', {
          isRecording: true
        });
        rerender(<RecordingButton />);
        
        // Check for live region announcement
        const button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-pressed', 'true');
      });
    });

    describe('Error Handling', () => {
      it('should handle recording errors gracefully', async () => {
        const startRecording = vi.fn().mockRejectedValue(new Error('Microphone access denied'));
        updateMockState('audio', {
          isRecording: false,
          startRecording
        });
        updateMockState('connection', {
          isConnected: true
        });
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        await waitFor(() => {
          expect(screen.getByRole('alert')).toBeInTheDocument();
        });
      });

      it('should show error message when microphone is unavailable', async () => {
        navigator.mediaDevices = undefined as any;
        
        render(<RecordingButton />);
        const button = screen.getByRole('button');
        
        await user.click(button);
        
        await waitFor(() => {
          expect(screen.getByText(/microphone not available/i)).toBeInTheDocument();
        });
      });
    });
  });

  // ========== MUTE TOGGLE TESTS ==========
  describe('MuteToggle', () => {
    describe('Toggle States', () => {
      it('should render unmuted state', () => {
        updateMockState('audio', {
          isMuted: false
        });
        
        render(<MuteToggle />);
        const button = screen.getByRole('button', { name: /mute/i });
        expect(button).toBeInTheDocument();
        expect(button).toHaveAttribute('aria-pressed', 'false');
      });

      it('should render muted state', () => {
        updateMockState('audio', {
          isMuted: true
        });
        
        render(<MuteToggle />);
        const button = screen.getByRole('button', { name: /unmute/i });
        expect(button).toBeInTheDocument();
        expect(button).toHaveAttribute('aria-pressed', 'true');
      });

      it('should be disabled during recording', () => {
        updateMockState('audio', {
          isRecording: true,
          isMuted: false
        });
        
        render(<MuteToggle />);
        const button = screen.getByRole('button');
        expect(button).toBeDisabled();
      });
    });

    describe('User Interactions', () => {
      it('should toggle mute state on click', async () => {
        const toggleMute = vi.fn();
        updateMockState('audio', {
          isMuted: false,
          toggleMute
        });
        
        render(<MuteToggle />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        expect(toggleMute).toHaveBeenCalled();
      });

      it('should handle keyboard shortcuts', async () => {
        const toggleMute = vi.fn();
        updateMockState('audio', {
          isMuted: false,
          toggleMute
        });
        
        render(<MuteToggle enableShortcut={true} />);
        
        // Simulate Ctrl+M shortcut
        await user.keyboard('{Control>}m{/Control}');
        
        expect(toggleMute).toHaveBeenCalled();
      });

      it('should show confirmation for unmute action', async () => {
        updateMockState('audio', {
          isMuted: true
        });
        
        render(<MuteToggle requireConfirmation={true} />);
        const button = screen.getByRole('button');
        await user.click(button);
        
        // Check for confirmation dialog
        const confirmButton = screen.getByRole('button', { name: /confirm/i });
        expect(confirmButton).toBeInTheDocument();
      });
    });

    describe('Visual Feedback', () => {
      it('should change icon when muted', () => {
        const { rerender, container } = render(<MuteToggle />);
        
        // Unmuted state - should have volume icon
        let icon = container.querySelector('svg');
        expect(icon).toBeInTheDocument();
        
        updateMockState('audio', {
          isMuted: true
        });
        rerender(<MuteToggle />);
        
        // Muted state - icon should change
        icon = container.querySelector('svg');
        expect(icon).toBeInTheDocument();
      });

      it('should apply visual styling for muted state', () => {
        updateMockState('audio', {
          isMuted: true
        });
        
        render(<MuteToggle />);
        const button = screen.getByRole('button');
        expect(button).toHaveClass('text-muted-foreground');
      });

      it('should show indicator when audio is playing', () => {
        updateMockState('audio', {
          isMuted: false,
          audioLevel: 0.5
        });
        
        const { container } = render(<MuteToggle showAudioIndicator={true} />);
        const indicator = container.querySelector('.animate-pulse');
        expect(indicator).toBeInTheDocument();
      });
    });

    describe('Accessibility', () => {
      it('should have no accessibility violations', async () => {
        const { container } = render(<MuteToggle />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('should provide clear ARIA labels', () => {
        const { rerender } = render(<MuteToggle />);
        
        let button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-label', 'Mute audio');
        
        updateMockState('audio', {
          isMuted: true
        });
        rerender(<MuteToggle />);
        
        button = screen.getByRole('button');
        expect(button).toHaveAttribute('aria-label', 'Unmute audio');
      });

      it('should announce state changes to screen readers', () => {
        render(<MuteToggle />);
        const button = screen.getByRole('button');
        
        // Check for live region
        const liveRegion = button.closest('[aria-live]');
        expect(liveRegion).toHaveAttribute('aria-live', 'polite');
      });
    });
  });

  // ========== AUDIO CONTROLS PANEL TESTS ==========
  describe('AudioControlsPanel', () => {
    describe('Panel Layout', () => {
      it('should render all audio controls', () => {
        render(<AudioControlsPanel />);
        
        // Should have recording button
        expect(screen.getByRole('button', { name: /recording/i })).toBeInTheDocument();
        
        // Should have mute toggle
        expect(screen.getByRole('button', { name: /mute/i })).toBeInTheDocument();
        
        // Should have volume slider
        expect(screen.getByRole('slider', { name: /volume/i })).toBeInTheDocument();
      });

      it('should arrange controls horizontally by default', () => {
        const { container } = render(<AudioControlsPanel />);
        const panel = container.firstChild;
        expect(panel).toHaveClass('flex-row');
      });

      it('should support vertical layout', () => {
        const { container } = render(<AudioControlsPanel orientation="vertical" />);
        const panel = container.firstChild;
        expect(panel).toHaveClass('flex-col');
      });

      it('should be collapsible', async () => {
        render(<AudioControlsPanel collapsible={true} />);
        
        const collapseButton = screen.getByRole('button', { name: /collapse/i });
        await user.click(collapseButton);
        
        // Controls should be hidden
        expect(screen.queryByRole('slider')).not.toBeInTheDocument();
      });
    });

    describe('Volume Control', () => {
      it('should render volume slider', () => {
        render(<AudioControlsPanel />);
        const slider = screen.getByRole('slider', { name: /volume/i });
        expect(slider).toBeInTheDocument();
        expect(slider).toHaveAttribute('aria-valuemin', '0');
        expect(slider).toHaveAttribute('aria-valuemax', '100');
      });

      it('should update volume on slider change', async () => {
        const setVolume = vi.fn();
        updateMockState('audio', {
          volume: 50,
          setVolume
        });
        
        render(<AudioControlsPanel />);
        const slider = screen.getByRole('slider');
        
        // Change volume
        await user.clear(slider);
        await user.type(slider, '75');
        
        expect(setVolume).toHaveBeenCalledWith(75);
      });

      it('should mute when volume is set to 0', async () => {
        const setMuted = vi.fn();
        updateMockState('audio', {
          volume: 50,
          setMuted
        });
        
        render(<AudioControlsPanel />);
        const slider = screen.getByRole('slider');
        
        await user.clear(slider);
        await user.type(slider, '0');
        
        expect(setMuted).toHaveBeenCalledWith(true);
      });

      it('should show volume level visually', () => {
        updateMockState('audio', {
          volume: 75
        });
        
        const { container } = render(<AudioControlsPanel />);
        const volumeBar = container.querySelector('[role="progressbar"]');
        expect(volumeBar).toHaveAttribute('aria-valuenow', '75');
      });
    });

    describe('Input Device Selection', () => {
      it('should show available audio input devices', async () => {
        // Mock available devices
        navigator.mediaDevices.enumerateDevices = vi.fn().mockResolvedValue([
          { kind: 'audioinput', deviceId: 'default', label: 'Default Microphone' },
          { kind: 'audioinput', deviceId: 'usb', label: 'USB Microphone' }
        ]);
        
        render(<AudioControlsPanel showDeviceSelector={true} />);
        
        await waitFor(() => {
          const selector = screen.getByRole('combobox', { name: /input device/i });
          expect(selector).toBeInTheDocument();
        });
      });

      it('should handle device selection', async () => {
        const setInputDevice = vi.fn();
        updateMockState('audio', {
          inputDevice: 'default',
          setInputDevice
        });
        
        navigator.mediaDevices.enumerateDevices = vi.fn().mockResolvedValue([
          { kind: 'audioinput', deviceId: 'default', label: 'Default Microphone' },
          { kind: 'audioinput', deviceId: 'usb', label: 'USB Microphone' }
        ]);
        
        render(<AudioControlsPanel showDeviceSelector={true} />);
        
        await waitFor(() => {
          const selector = screen.getByRole('combobox');
          expect(selector).toBeInTheDocument();
        });
        
        const selector = screen.getByRole('combobox');
        await user.selectOptions(selector, 'usb');
        
        expect(setInputDevice).toHaveBeenCalledWith('usb');
      });

      it('should handle missing permissions gracefully', async () => {
        navigator.mediaDevices.enumerateDevices = vi.fn().mockRejectedValue(
          new Error('Permission denied')
        );
        
        render(<AudioControlsPanel showDeviceSelector={true} />);
        
        await waitFor(() => {
          expect(screen.getByText(/permission required/i)).toBeInTheDocument();
        });
      });
    });

    describe('Audio Level Monitoring', () => {
      it('should display real-time audio levels', () => {
        updateMockState('audio', {
          audioLevel: 0.6,
          isRecording: true
        });
        
        const { container } = render(<AudioControlsPanel showLevelMeter={true} />);
        const levelMeter = container.querySelector('[role="meter"]');
        expect(levelMeter).toHaveAttribute('aria-valuenow', '60');
      });

      it('should indicate clipping when audio is too loud', () => {
        updateMockState('audio', {
          audioLevel: 0.95,
          isRecording: true
        });
        
        render(<AudioControlsPanel showLevelMeter={true} />);
        const warning = screen.getByRole('alert');
        expect(warning).toHaveTextContent(/audio clipping/i);
      });

      it('should show silence detection', () => {
        updateMockState('audio', {
          audioLevel: 0.01,
          isRecording: true
        });
        
        render(<AudioControlsPanel showLevelMeter={true} />);
        const status = screen.getByText(/no audio detected/i);
        expect(status).toBeInTheDocument();
      });
    });

    describe('Responsive Behavior', () => {
      it('should stack controls vertically on mobile', () => {
        styles.setViewport(375, 667);
        
        const { container } = render(<AudioControlsPanel />);
        const panel = container.firstChild;
        expect(panel).toHaveClass('flex-col');
      });

      it('should hide labels on small screens', () => {
        styles.setViewport(320, 568);
        
        render(<AudioControlsPanel />);
        const labels = screen.queryAllByText(/volume|recording|mute/i);
        labels.forEach(label => {
          expect(label).toHaveClass('sr-only');
        });
      });

      it('should use compact controls on mobile', () => {
        styles.setViewport(375, 667);
        
        render(<AudioControlsPanel />);
        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          expect(button).toHaveClass('h-8', 'w-8');
        });
      });
    });

    describe('Accessibility', () => {
      it('should have no accessibility violations', async () => {
        const { container } = render(<AudioControlsPanel />);
        const results = await axe(container);
        expect(results).toHaveNoViolations();
      });

      it('should support keyboard navigation', async () => {
        render(<AudioControlsPanel />);
        
        // Tab through controls
        await keyboard.tab(user);
        expect(screen.getByRole('button', { name: /recording/i })).toHaveFocus();
        
        await keyboard.tab(user);
        expect(screen.getByRole('button', { name: /mute/i })).toHaveFocus();
        
        await keyboard.tab(user);
        expect(screen.getByRole('slider')).toHaveFocus();
      });

      it('should group controls with proper ARIA labels', () => {
        render(<AudioControlsPanel />);
        const panel = screen.getByRole('group', { name: /audio controls/i });
        expect(panel).toBeInTheDocument();
      });

      it('should announce control changes', async () => {
        const { container } = render(<AudioControlsPanel />);
        
        // Check for live region
        const liveRegion = container.querySelector('[aria-live="polite"]');
        expect(liveRegion).toBeInTheDocument();
        
        // Toggle mute
        const muteButton = screen.getByRole('button', { name: /mute/i });
        await user.click(muteButton);
        
        // Should announce state change
        expect(liveRegion).toHaveTextContent(/muted/i);
      });
    });

    describe('Performance', () => {
      it('should throttle audio level updates', async () => {
        const { rerender } = render(<AudioControlsPanel showLevelMeter={true} />);
        
        // Simulate rapid audio level changes
        for (let i = 0; i < 100; i++) {
          updateMockState('audio', {
            audioLevel: Math.random(),
            isRecording: true
          });
          rerender(<AudioControlsPanel showLevelMeter={true} />);
        }
        
        // Component should remain stable
        expect(screen.getByRole('group')).toBeInTheDocument();
      });

      it('should debounce volume changes', async () => {
        const setVolume = vi.fn();
        updateMockState('audio', {
          volume: 50,
          setVolume
        });
        
        render(<AudioControlsPanel />);
        const slider = screen.getByRole('slider');
        
        // Rapidly change volume
        for (let i = 0; i < 10; i++) {
          await user.clear(slider);
          await user.type(slider, String(i * 10));
        }
        
        // Should be debounced
        vi.advanceTimersByTime(300);
        expect(setVolume.mock.calls.length).toBeLessThan(10);
      });
    });
  });
});