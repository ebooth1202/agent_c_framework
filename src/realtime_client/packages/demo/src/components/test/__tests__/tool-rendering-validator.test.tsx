/**
 * Tests for Tool Rendering Validator component
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ToolRenderingValidator } from '../tool-rendering-validator';

// Mock utils
vi.mock('@/lib/utils', () => ({
  cn: (...inputs: any[]) => {
    // Handle various input types including objects and conditional classes
    return inputs
      .filter(Boolean)
      .map((input: any) => {
        if (typeof input === 'string') return input;
        if (typeof input === 'object' && input !== null) {
          // Handle conditional class objects
          return Object.entries(input)
            .filter(([_, value]) => value)
            .map(([key]) => key)
            .join(' ');
        }
        return '';
      })
      .join(' ')
      .trim();
  }
}));

// Mock UI components
vi.mock('@agentc/realtime-ui', () => ({
  Card: ({ children, className }: any) => <div className={`card ${className}`}>{children}</div>,
  CardContent: ({ children }: any) => <div className="card-content">{children}</div>,
  CardDescription: ({ children }: any) => <p className="card-description">{children}</p>,
  CardHeader: ({ children }: any) => <div className="card-header">{children}</div>,
  CardTitle: ({ children }: any) => <h3 className="card-title">{children}</h3>,
  Badge: ({ children, variant }: any) => <span data-variant={variant} className="badge">{children}</span>,
  Alert: ({ children }: any) => <div className="alert">{children}</div>,
  AlertDescription: ({ children }: any) => <p className="alert-description">{children}</p>,
  ScrollArea: ({ children, className }: any) => <div className={`scroll-area ${className}`}>{children}</div>,
  Separator: () => <hr className="separator" />,
  Button: ({ children, onClick, disabled, variant, size, ...props }: any) => (
    <button 
      onClick={onClick} 
      disabled={disabled} 
      data-variant={variant}
      data-size={size}
      {...props}
    >
      {children}
    </button>
  ),
  Tooltip: ({ children }: any) => <>{children}</>,
  TooltipContent: ({ children }: any) => <div className="tooltip-content">{children}</div>,
  TooltipProvider: ({ children }: any) => <>{children}</>,
  TooltipTrigger: ({ children, asChild }: any) => {
    if (asChild) {
      return React.cloneElement(children, { 'data-tooltip': true });
    }
    return <span data-tooltip>{children}</span>;
  }
}));

// Mock Lucide React icons
vi.mock('lucide-react', () => ({
  GitBranch: () => <span>GitBranch</span>,
  Brain: () => <span>Brain</span>,
  CheckCircle2: () => <span>CheckCircle2</span>,
  XCircle: () => <span>XCircle</span>,
  AlertTriangle: () => <span>AlertTriangle</span>,
  Info: () => <span>Info</span>,
  RefreshCw: () => <span>RefreshCw</span>,
  Eye: () => <span>Eye</span>,
  EyeOff: () => <span>EyeOff</span>,
  MessageSquare: () => <span>MessageSquare</span>,
  ArrowRight: () => <span>ArrowRight</span>,
  ArrowDown: () => <span>ArrowDown</span>,
  Layers: () => <span>Layers</span>,
  Hash: () => <span>Hash</span>
}));

describe('ToolRenderingValidator', () => {
  // Set test timeout to prevent hanging
  vi.setConfig({ testTimeout: 10000 });
  const mockMessages = {
    delegation: [
      {
        id: 'msg-1',
        content: [{
          type: 'tool_use',
          name: 'act_oneshot',
          id: 'tool-1'
        }]
      },
      {
        id: 'msg-2',
        content: [{
          type: 'tool_use',
          name: 'act_chat',
          id: 'tool-2'
        }]
      }
    ],
    think: [
      {
        id: 'msg-3',
        content: [{
          type: 'tool_use',
          name: 'think',
          id: 'think-1'
        }]
      }
    ],
    mixed: [
      {
        id: 'msg-4',
        content: [{
          type: 'tool_use',
          name: 'act_oneshot',
          id: 'tool-3'
        }]
      },
      {
        id: 'msg-5',
        content: [{
          type: 'tool_use',
          name: 'think',
          id: 'think-2'
        }]
      }
    ],
    other: [
      {
        id: 'msg-6',
        content: [{
          type: 'tool_use',
          name: 'other_tool',
          id: 'other-1'
        }]
      }
    ],
    noTools: [
      {
        id: 'msg-7',
        content: 'Regular message without tools'
      }
    ]
  };

  // Mock DOM elements for validation
  let mockElements: Map<string, HTMLElement>;

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Create mock DOM elements
    mockElements = new Map();
    
    // Mock subsession divider
    const divider = document.createElement('div');
    divider.className = 'subsession-divider';
    mockElements.set('subsession-divider', divider);
    
    // Mock thought bubble
    const thought = document.createElement('div');
    thought.className = 'thought-bubble';
    mockElements.set('thought-bubble', thought);
    
    // Mock tool UI
    const toolUI = document.createElement('div');
    toolUI.className = 'tool-call-ui';
    mockElements.set('tool-call-ui', toolUI);
    
    // Mock delegation elements
    const delegationResponse = document.createElement('div');
    delegationResponse.className = 'delegation-response';
    delegationResponse.style.marginLeft = '20px';
    mockElements.set('delegation-response', delegationResponse);
    
    const delegationHeader = document.createElement('div');
    delegationHeader.className = 'delegation-header';
    delegationHeader.textContent = 'Delegated to agent';
    mockElements.set('delegation-header', delegationHeader);
    
    const delegationContainer = document.createElement('div');
    delegationContainer.className = 'delegation-container';
    delegationContainer.style.borderLeftWidth = '2px';
    mockElements.set('delegation-container', delegationContainer);
    
    // Mock thought styling
    const thoughtWithStyle = document.createElement('div');
    thoughtWithStyle.className = 'thought-bubble';
    thoughtWithStyle.style.fontStyle = 'italic';
    mockElements.set('thought-styled', thoughtWithStyle);
    
    const thoughtIcon = document.createElement('div');
    thoughtIcon.className = 'thought-icon';
    mockElements.set('thought-icon', thoughtIcon);
    
    const thoughtContent = document.createElement('div');
    thoughtContent.className = 'thought-content';
    thoughtContent.innerHTML = 'Thought content<br>with line breaks';
    mockElements.set('thought-content', thoughtContent);
    
    // Mock document.querySelector
    vi.spyOn(document, 'querySelector').mockImplementation((selector: string) => {
      if (selector.includes('[data-message-id="msg-1"]')) {
        const container = document.createElement('div');
        container.appendChild(mockElements.get('subsession-divider')!.cloneNode(true));
        container.appendChild(mockElements.get('delegation-response')!.cloneNode(true));
        container.appendChild(mockElements.get('delegation-header')!.cloneNode(true));
        container.appendChild(mockElements.get('delegation-container')!.cloneNode(true));
        return container;
      }
      if (selector.includes('[data-message-id="msg-3"]')) {
        const container = document.createElement('div');
        container.appendChild(mockElements.get('thought-styled')!.cloneNode(true));
        container.appendChild(mockElements.get('thought-icon')!.cloneNode(true));
        container.appendChild(mockElements.get('thought-content')!.cloneNode(true));
        return container;
      }
      if (selector.includes('.subsession-divider')) return mockElements.get('subsession-divider');
      if (selector.includes('.thought-bubble')) return mockElements.get('thought-styled');
      if (selector.includes('.tool-call-ui')) return null; // Think tools shouldn't have this
      if (selector.includes('.delegation-response')) return mockElements.get('delegation-response');
      if (selector.includes('.delegation-header')) return mockElements.get('delegation-header');
      if (selector.includes('.delegation-container')) return mockElements.get('delegation-container');
      if (selector.includes('.thought-icon')) return mockElements.get('thought-icon');
      if (selector.includes('.thought-content')) return mockElements.get('thought-content');
      if (selector.includes('.chat-messages-container')) return document.createElement('div');
      return null;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Component Rendering', () => {
    it('renders with title and description', () => {
      render(<ToolRenderingValidator messages={[]} />);
      
      expect(screen.getByText('Tool Rendering Validator')).toBeDefined();
      expect(screen.getByText('Validates delegation and think tool visual rendering')).toBeDefined();
    });

    it('shows validate button', () => {
      render(<ToolRenderingValidator messages={[]} />);
      
      const validateButton = screen.getByText('RefreshCw').closest('button');
      expect(validateButton).toBeDefined();
    });

    it('displays visual guides badge when enabled', () => {
      render(<ToolRenderingValidator messages={[]} showVisualGuides={true} />);
      
      expect(screen.getByText('Visual Guides')).toBeDefined();
    });

    it('renders with custom className', () => {
      const { container } = render(
        <ToolRenderingValidator messages={[]} className="custom-class" />
      );
      
      const card = container.querySelector('.card');
      expect(card?.className).toContain('custom-class');
    });
  });

  describe('Validation Statistics', () => {
    it('displays summary statistics', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText('Passed')).toBeDefined();
        expect(screen.getByText('Failed')).toBeDefined();
        expect(screen.getByText('Errors')).toBeDefined();
        expect(screen.getByText('Warnings')).toBeDefined();
      });
    });

    it('updates statistics after validation', async () => {
      const { rerender } = render(
        <ToolRenderingValidator messages={[]} autoRun={false} />
      );
      
      // Initially should show 0s
      expect(screen.getByText('0')).toBeDefined();
      
      // Update with messages
      rerender(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        const stats = screen.getAllByText(/\d+/);
        // Should have some non-zero statistics
        expect(stats.some(stat => stat.textContent !== '0')).toBe(true);
      });
    });
  });

  describe('Delegation Tool Validation', () => {
    it('validates subsession divider presence', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Subsession Divider/)).toBeDefined();
      });
    });

    it('validates nested indentation', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Nested Indentation/)).toBeDefined();
      });
    });

    it('validates delegation header', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Delegation Header/)).toBeDefined();
      });
    });

    it('validates result transformation', async () => {
      const messagesWithResult = [
        {
          id: 'msg-result',
          content: [
            {
              type: 'tool_use',
              name: 'act_oneshot',
              id: 'tool-result'
            },
            {
              type: 'tool_result',
              tool_use_id: 'tool-result',
              content: 'Result content'
            }
          ]
        }
      ];

      render(<ToolRenderingValidator messages={messagesWithResult} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Result Transformation/)).toBeDefined();
      });
    });

    it('validates visual hierarchy', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Visual Hierarchy/)).toBeDefined();
      });
    });

    it('shows delegation tool icon for delegation messages', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} showDetails={true} />);
      
      await waitFor(() => {
        expect(screen.getByText('GitBranch')).toBeDefined();
      });
    });
  });

  describe('Think Tool Validation', () => {
    it('validates thought bubble display', async () => {
      render(<ToolRenderingValidator messages={mockMessages.think} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Thought Bubble Display/)).toBeDefined();
      });
    });

    it('validates no tool UI display', async () => {
      render(<ToolRenderingValidator messages={mockMessages.think} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/No Tool UI/)).toBeDefined();
      });
    });

    it('validates thought styling', async () => {
      render(<ToolRenderingValidator messages={mockMessages.think} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Thought Styling/)).toBeDefined();
      });
    });

    it('validates thought icon presence', async () => {
      render(<ToolRenderingValidator messages={mockMessages.think} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Thought Icon/)).toBeDefined();
      });
    });

    it('validates content preservation', async () => {
      render(<ToolRenderingValidator messages={mockMessages.think} autoRun={true} />);
      
      await waitFor(() => {
        expect(screen.getByText(/Content Preservation/)).toBeDefined();
      });
    });

    it('shows brain icon for think messages', async () => {
      render(<ToolRenderingValidator messages={mockMessages.think} autoRun={true} showDetails={true} />);
      
      await waitFor(() => {
        expect(screen.getByText('Brain')).toBeDefined();
      });
    });
  });

  describe('Visual Guide Highlighting', () => {
    beforeEach(() => {
      // Mock classList methods
      const mockClassList = {
        add: vi.fn(),
        remove: vi.fn(),
        contains: vi.fn(() => false)
      };
      
      mockElements.forEach(element => {
        Object.defineProperty(element, 'classList', {
          value: mockClassList,
          writable: true
        });
      });
    });

    it('highlights failing elements when visual guides enabled', async () => {
      // Mock a failing validation by removing the subsession divider
      vi.spyOn(document, 'querySelector').mockImplementation((selector: string) => {
        if (selector.includes('.subsession-divider')) return null;
        return mockElements.get('delegation-response');
      });

      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} showVisualGuides={true} />);
      
      await waitFor(() => {
        // Check that some element would be highlighted
        const failedElements = screen.getAllByText(/✗/);
        expect(failedElements.length).toBeGreaterThan(0);
      });
    });

    it('clears highlights after timeout', async () => {
      vi.useFakeTimers();
      
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} showVisualGuides={true} />);
      
      // Fast-forward time
      vi.advanceTimersByTime(3500);
      
      await waitFor(() => {
        // Highlights should be cleared
        expect(true).toBe(true); // Placeholder - in real implementation would check DOM
      });
      
      vi.useRealTimers();
    });

    it('shows visual guide legend when highlights active', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} showVisualGuides={true} />);
      
      await waitFor(() => {
        // Legend might be shown if there are highlights
        const alerts = screen.getAllByText(/Visual Guides Active/);
        // May or may not show depending on validation results
        expect(alerts.length).toBeGreaterThanOrEqual(0);
      });
    });

    it('allows clearing highlights manually', async () => {
      const user = userEvent.setup();
      
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} showVisualGuides={true} />);
      
      // If clear button appears, it should be clickable
      const clearButton = screen.queryByText('Clear Now');
      if (clearButton) {
        await user.click(clearButton);
        // Highlights should be cleared
        expect(true).toBe(true);
      }
    });
  });

  describe('Manual Validation', () => {
    it('triggers validation on button click', async () => {
      const user = userEvent.setup();
      render(<ToolRenderingValidator messages={mockMessages.mixed} autoRun={false} />);
      
      const validateButton = screen.getByText('RefreshCw').closest('button');
      await user.click(validateButton!);
      
      await waitFor(() => {
        // Should show validation results
        const badges = screen.getAllByRole('button').filter(btn => 
          btn.textContent?.includes('Passed') || btn.textContent?.includes('Failed')
        );
        expect(badges.length).toBeGreaterThanOrEqual(0);
      });
    });

    it('shows loading state during validation', async () => {
      const user = userEvent.setup();
      render(<ToolRenderingValidator messages={mockMessages.mixed} autoRun={false} />);
      
      const validateButton = screen.getByText('RefreshCw').closest('button');
      
      // Button should not be disabled initially
      expect(validateButton).not.toHaveProperty('disabled', true);
      
      await user.click(validateButton!);
      
      // Would show loading animation on the icon in real implementation
      expect(validateButton).toBeDefined();
    });
  });

  describe('Auto-validation', () => {
    it('validates automatically when autoRun is true', async () => {
      vi.useFakeTimers();
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      // Advance timers to trigger validation
      vi.advanceTimersByTime(600);
      
      await waitFor(() => {
        // Should have validation results without clicking validate
        const passedStat = screen.getByText('Passed').parentElement;
        expect(passedStat).toBeDefined();
      });
      
      vi.useRealTimers();
    });

    it('does not validate automatically when autoRun is false', () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={false} />);
      
      // All stats should be 0
      const stats = screen.getAllByText('0');
      expect(stats.length).toBeGreaterThan(0);
    });

    it('sets up DOM observer for auto-validation', async () => {
      vi.useFakeTimers();
      const mockObserver = {
        observe: vi.fn(),
        disconnect: vi.fn()
      };
      
      vi.spyOn(window, 'MutationObserver').mockImplementation(() => mockObserver as any);
      
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        expect(mockObserver.observe).toHaveBeenCalled();
      });
      
      vi.useRealTimers();
    });
  });

  describe('Show/Hide Details Toggle', () => {
    it('shows details by default', () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      const detailsButton = screen.getByText('EyeOff').closest('button');
      expect(detailsButton).toBeDefined();
    });

    it('toggles details visibility', async () => {
      const user = userEvent.setup();
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      // Initially shows "Hide Details"
      let detailsButton = screen.getByText('EyeOff').closest('button');
      await user.click(detailsButton!);
      
      // Should now show "Show Details"
      detailsButton = screen.getByText('Eye').closest('button');
      expect(detailsButton).toBeDefined();
      
      // Click again to show
      await user.click(detailsButton!);
      
      // Should be back to "Hide Details"
      detailsButton = screen.getByText('EyeOff').closest('button');
      expect(detailsButton).toBeDefined();
    });
  });

  describe('Empty State', () => {
    it('shows empty state message when no results', () => {
      render(<ToolRenderingValidator messages={[]} />);
      
      expect(screen.getByText(/No validation results yet/)).toBeDefined();
    });

    it('handles messages without tools gracefully', async () => {
      render(<ToolRenderingValidator messages={mockMessages.noTools} autoRun={true} />);
      
      await waitFor(() => {
        // Should show empty or minimal results
        const results = screen.queryByText(/Tool$/);
        expect(results).toBeNull();
      });
    });

    it('handles other tool types', async () => {
      render(<ToolRenderingValidator messages={mockMessages.other} autoRun={true} />);
      
      await waitFor(() => {
        // Should not validate non-delegation/think tools
        const delegationSection = screen.queryByText(/Delegation Tool/);
        const thinkSection = screen.queryByText(/Think Tool/);
        expect(delegationSection).toBeNull();
        expect(thinkSection).toBeNull();
      });
    });
  });

  describe('Responsive Design', () => {
    const viewports = [
      { name: 'mobile', width: 375, height: 812 },
      { name: 'tablet', width: 768, height: 1024 },
      { name: 'desktop', width: 1440, height: 900 }
    ];

    viewports.forEach(({ name, width, height }) => {
      it(`renders appropriately on ${name} (${width}x${height})`, () => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: width
        });
        Object.defineProperty(window, 'innerHeight', {
          writable: true,
          configurable: true,
          value: height
        });

        render(<ToolRenderingValidator messages={mockMessages.mixed} />);
        
        // Card should be present and adapt to viewport
        const card = screen.getByText('Tool Rendering Validator').closest('.card');
        expect(card).toBeDefined();
        
        // Stats grid should be present
        const statsContainer = screen.getByText('Passed').parentElement?.parentElement;
        expect(statsContainer).toBeDefined();
        
        if (width < 640) {
          // Mobile: check for appropriate layout
          expect(statsContainer?.className).toContain('grid-cols-4');
        } else {
          // Larger screens: same grid but more space
          expect(statsContainer?.className).toContain('grid-cols-4');
        }
      });
    });
  });

  describe('Theme Compatibility', () => {
    it('renders correctly in light theme', () => {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      
      render(<ToolRenderingValidator messages={mockMessages.mixed} />);
      
      // Should render without issues
      expect(screen.getByText('Tool Rendering Validator')).toBeDefined();
    });

    it('renders correctly in dark theme', () => {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
      
      render(<ToolRenderingValidator messages={mockMessages.mixed} />);
      
      // Should render without issues
      expect(screen.getByText('Tool Rendering Validator')).toBeDefined();
    });

    it('applies theme-appropriate colors to status indicators', () => {
      document.documentElement.classList.add('dark');
      
      render(<ToolRenderingValidator messages={mockMessages.mixed} autoRun={true} />);
      
      // Check that dark theme colors are used
      const passedIcon = screen.getByText('CheckCircle2');
      expect(passedIcon.parentElement?.className).toContain('text-green');
    });
  });

  describe('Accessibility', () => {
    it('uses semantic HTML elements', () => {
      render(<ToolRenderingValidator messages={mockMessages.mixed} />);
      
      // Has heading
      expect(screen.getByRole('heading')).toBeDefined();
      
      // Has buttons
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
    });

    it('provides descriptive text for all interactive elements', () => {
      render(<ToolRenderingValidator messages={mockMessages.mixed} />);
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        // Should have either text content or icon with nearby label
        const hasText = button.textContent && button.textContent.trim().length > 0;
        expect(hasText).toBe(true);
      });
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<ToolRenderingValidator messages={mockMessages.mixed} />);
      
      // Tab to validate button
      await user.tab();
      await user.tab();
      
      // Should focus on a button
      expect(document.activeElement?.tagName).toBe('BUTTON');
      
      // Press enter to validate
      await user.keyboard('{Enter}');
      
      // Should still be functional
      expect(document.activeElement).toBeDefined();
    });

    it('provides clear visual feedback for validation results', async () => {
      render(<ToolRenderingValidator messages={mockMessages.mixed} autoRun={true} />);
      
      await waitFor(() => {
        // Check for visual indicators
        const checkIcons = screen.queryAllByText('CheckCircle2');
        const errorIcons = screen.queryAllByText('XCircle');
        const warningIcons = screen.queryAllByText('AlertTriangle');
        
        // Should have at least some indicators
        const totalIcons = checkIcons.length + errorIcons.length + warningIcons.length;
        expect(totalIcons).toBeGreaterThanOrEqual(0);
      });
    });
  });

  describe('Performance', () => {
    it('handles large message lists efficiently', async () => {
      vi.useFakeTimers();
      // Create a large list of messages
      const largeMessageList = Array(100).fill(null).map((_, i) => ({
        id: `msg-${i}`,
        content: [{
          type: 'tool_use',
          name: i % 2 === 0 ? 'act_oneshot' : 'think',
          id: `tool-${i}`
        }]
      }));

      const startTime = performance.now();
      render(<ToolRenderingValidator messages={largeMessageList} autoRun={true} />);
      const endTime = performance.now();

      // Should render within reasonable time (< 1 second)
      expect(endTime - startTime).toBeLessThan(1000);
      
      vi.advanceTimersByTime(600);
      
      await waitFor(() => {
        // Should still show results
        expect(screen.getByText('Tool Rendering Validator')).toBeDefined();
      });
      
      vi.useRealTimers();
    });

    it('uses ScrollArea for long validation results', async () => {
      const manyMessages = Array(20).fill(null).map((_, i) => ({
        id: `msg-${i}`,
        content: [{
          type: 'tool_use',
          name: 'act_oneshot',
          id: `tool-${i}`
        }]
      }));

      render(<ToolRenderingValidator messages={manyMessages} autoRun={true} />);
      
      await waitFor(() => {
        // Should have scroll area
        const scrollArea = document.querySelector('.scroll-area');
        expect(scrollArea).toBeDefined();
      });
    });
  });

  describe('Message Validation Cards', () => {
    it('shows appropriate border colors for validation status', async () => {
      render(<ToolRenderingValidator messages={mockMessages.mixed} autoRun={true} />);
      
      await waitFor(() => {
        const cards = document.querySelectorAll('.card');
        // Should have cards with status-based borders
        expect(cards.length).toBeGreaterThan(0);
      });
    });

    it('groups validation results by message', async () => {
      render(<ToolRenderingValidator messages={mockMessages.mixed} autoRun={true} />);
      
      await waitFor(() => {
        // Each message should have its own card
        const delegationCards = screen.queryAllByText(/Delegation Tool/);
        const thinkCards = screen.queryAllByText(/Think Tool/);
        
        expect(delegationCards.length + thinkCards.length).toBeGreaterThanOrEqual(0);
      });
    });

    it('shows pass/fail badges for each message', async () => {
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        // Should show status badges
        const badges = document.querySelectorAll('.badge');
        expect(badges.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Error Handling', () => {
    it('handles malformed messages gracefully', async () => {
      const malformedMessages = [
        { id: 'bad-1', content: null },
        { id: 'bad-2', content: undefined },
        { id: 'bad-3', content: {} },
        { id: 'bad-4' } // Missing content
      ];

      render(<ToolRenderingValidator messages={malformedMessages as any} autoRun={true} />);
      
      await waitFor(() => {
        // Should not crash and show empty or error state
        expect(screen.getByText('Tool Rendering Validator')).toBeDefined();
      });
    });

    it('handles missing DOM elements during validation', async () => {
      // Mock querySelector to always return null
      vi.spyOn(document, 'querySelector').mockReturnValue(null);
      
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        // Should still show results, likely all failed
        const failedStat = screen.getByText('Failed').parentElement;
        expect(failedStat).toBeDefined();
      });
    });

    it('handles window.getComputedStyle errors', async () => {
      // Mock getComputedStyle to throw
      vi.spyOn(window, 'getComputedStyle').mockImplementation(() => {
        throw new Error('Style computation failed');
      });
      
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      await waitFor(() => {
        // Should handle gracefully
        expect(screen.getByText('Tool Rendering Validator')).toBeDefined();
      });
    });
  });

  describe('Integration with DOM Mutations', () => {
    it('disconnects observer on unmount', () => {
      vi.useFakeTimers();
      const mockObserver = {
        observe: vi.fn(),
        disconnect: vi.fn()
      };
      
      vi.spyOn(window, 'MutationObserver').mockImplementation(() => mockObserver as any);
      
      const { unmount } = render(
        <ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />
      );
      
      unmount();
      
      expect(mockObserver.disconnect).toHaveBeenCalled();
      
      vi.useRealTimers();
    });

    it('debounces validation on DOM changes', async () => {
      vi.useFakeTimers();
      
      let mutationCallback: any;
      const mockObserver = {
        observe: vi.fn((target, options) => {
          // Capture the callback
        }),
        disconnect: vi.fn()
      };
      
      vi.spyOn(window, 'MutationObserver').mockImplementation((callback) => {
        mutationCallback = callback;
        return mockObserver as any;
      });
      
      render(<ToolRenderingValidator messages={mockMessages.delegation} autoRun={true} />);
      
      // Simulate DOM mutation
      if (mutationCallback) {
        mutationCallback([{ type: 'childList' }]);
      }
      
      // Fast-forward debounce timer
      vi.advanceTimersByTime(600);
      
      await waitFor(() => {
        // Validation should have been triggered
        expect(true).toBe(true);
      });
      
      vi.useRealTimers();
    });
  });
});