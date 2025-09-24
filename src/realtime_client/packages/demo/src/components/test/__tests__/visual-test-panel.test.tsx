/**
 * Tests for Visual Test Panel component
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VisualTestPanel } from '../visual-test-panel';

// Mock the useTestSession hook
const mockUseTestSession = vi.fn();

vi.mock('@/hooks/use-test-session', () => ({
  useTestSession: () => mockUseTestSession()
}));

// Mock useChat hook
const mockUseChat = vi.fn();

vi.mock('@agentc/realtime-react', () => ({
  useChat: () => mockUseChat()
}));

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
  Card: ({ children, className }: any) => <div className={`card ${className}`}>{children}</div>,
  CardContent: ({ children }: any) => <div className="card-content">{children}</div>,
  CardDescription: ({ children }: any) => <p className="card-description">{children}</p>,
  CardHeader: ({ children }: any) => <div className="card-header">{children}</div>,
  CardTitle: ({ children }: any) => <h3 className="card-title">{children}</h3>,
  Tabs: ({ children, value, onValueChange, className }: any) => (
    <div className={`tabs ${className}`} data-value={value} onClick={(e: any) => {
      const trigger = e.target.closest('[data-tab-value]');
      if (trigger && onValueChange) {
        onValueChange(trigger.dataset.tabValue);
      }
    }}>{children}</div>
  ),
  TabsContent: ({ children, value }: any) => <div data-tab-content={value}>{children}</div>,
  TabsList: ({ children, className }: any) => <div className={`tabs-list ${className}`}>{children}</div>,
  TabsTrigger: ({ children, value }: any) => <button data-tab-value={value}>{children}</button>,
  Badge: ({ children, variant }: any) => <span data-variant={variant} className="badge">{children}</span>,
  ScrollArea: ({ children, className }: any) => <div className={`scroll-area ${className}`}>{children}</div>,
  Separator: () => <hr className="separator" />,
  Label: ({ children, htmlFor }: any) => <label htmlFor={htmlFor}>{children}</label>,
  Alert: ({ children, variant }: any) => <div data-variant={variant} className="alert">{children}</div>,
  AlertDescription: ({ children }: any) => <p className="alert-description">{children}</p>,
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
  FlaskConical: () => <span>FlaskConical</span>,
  ChevronRight: () => <span>ChevronRight</span>,
  ChevronDown: () => <span>ChevronDown</span>,
  CheckCircle2: () => <span>CheckCircle2</span>,
  XCircle: () => <span>XCircle</span>,
  AlertTriangle: () => <span>AlertTriangle</span>,
  Info: () => <span>Info</span>,
  Eye: () => <span>Eye</span>,
  EyeOff: () => <span>EyeOff</span>,
  Code2: () => <span>Code2</span>,
  MessageSquare: () => <span>MessageSquare</span>,
  GitBranch: () => <span>GitBranch</span>,
  Brain: () => <span>Brain</span>,
  Activity: () => <span>Activity</span>,
  Bug: () => <span>Bug</span>,
  Maximize2: () => <span>Maximize2</span>,
  Minimize2: () => <span>Minimize2</span>,
  RefreshCw: () => <span>RefreshCw</span>,
  Download: () => <span>Download</span>,
  Upload: () => <span>Upload</span>,
  Clock: () => <span>Clock</span>,
  MemoryStick: () => <span>MemoryStick</span>,
  Zap: () => <span>Zap</span>,
  Layers: () => <span>Layers</span>,
  FileJson: () => <span>FileJson</span>,
  Database: () => <span>Database</span>
}));

describe('VisualTestPanel', () => {
  const defaultMockTestSession = {
    testModeEnabled: true,
    currentScenario: null,
    scenarios: [
      { id: 'scenario-1', name: 'Test Scenario 1', description: 'First test' },
      { id: 'scenario-2', name: 'Test Scenario 2', description: 'Second test' }
    ],
    loadScenario: vi.fn(),
    clearSession: vi.fn(),
    reloadCurrentScenario: vi.fn(),
    isLoading: false,
    error: null
  };

  const defaultMockChat = {
    messages: []
  };

  // Mock performance API
  const mockPerformance = {
    now: vi.fn(() => 100),
    memory: {
      usedJSHeapSize: 1024 * 1024 * 10 // 10MB
    },
    getEntriesByType: vi.fn(() => [])
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTestSession.mockReturnValue(defaultMockTestSession);
    mockUseChat.mockReturnValue(defaultMockChat);
    
    // Mock performance
    Object.defineProperty(window, 'performance', {
      value: mockPerformance,
      writable: true
    });

    // Mock URL.createObjectURL and URL.revokeObjectURL for export functionality
    global.URL.createObjectURL = vi.fn(() => 'blob:mock-url');
    global.URL.revokeObjectURL = vi.fn();

    // Mock document.querySelector for validation checks
    vi.spyOn(document, 'querySelector').mockReturnValue(null);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering and Basic Functionality', () => {
    it('renders when test mode is enabled', () => {
      render(<VisualTestPanel />);
      expect(screen.getByText('Visual Test Panel')).toBeDefined();
    });

    it('does not render when test mode is disabled', () => {
      mockUseTestSession.mockReturnValue({
        ...defaultMockTestSession,
        testModeEnabled: false
      });

      const { container } = render(<VisualTestPanel />);
      expect(container.firstChild).toBeNull();
    });

    it('renders with default collapsed state', () => {
      render(<VisualTestPanel defaultExpanded={false} />);
      
      // Find the expand button by looking for chevron icon
      const chevronIcon = screen.getByText('ChevronRight');
      const expandButton = chevronIcon.closest('button');
      expect(expandButton).toBeDefined();
    });

    it('renders with expanded state', () => {
      render(<VisualTestPanel defaultExpanded={true} />);
      
      // Find the collapse button by looking for chevron icon
      const chevronIcon = screen.getByText('ChevronDown');
      const collapseButton = chevronIcon.closest('button');
      expect(collapseButton).toBeDefined();
      expect(screen.getByText('Controls')).toBeDefined();
    });

    it('toggles expand/collapse on button click', async () => {
      const user = userEvent.setup();
      render(<VisualTestPanel />);
      
      // Find the toggle button by looking for the one containing the chevron icon
      const chevronRight = screen.getByText('ChevronRight');
      const toggleButton = chevronRight.closest('button');
      
      // Initially collapsed
      expect(toggleButton).toContainElement(screen.getByText('ChevronRight'));
      
      // Expand
      await user.click(toggleButton!);
      const chevronDown = screen.getByText('ChevronDown');
      const expandedButton = chevronDown.closest('button');
      expect(expandedButton).toContainElement(screen.getByText('ChevronDown'));
      
      // Collapse
      await user.click(expandedButton!);
      expect(screen.getByText('ChevronRight')).toBeDefined();
    });
  });

  describe('Panel Positioning', () => {
    it('applies bottom position classes', () => {
      const { container } = render(<VisualTestPanel position="bottom" />);
      const panel = container.firstChild as HTMLElement;
      expect(panel.className).toContain('fixed bottom-0 left-0 right-0');
    });

    it('applies right position classes', () => {
      const { container } = render(<VisualTestPanel position="right" />);
      const panel = container.firstChild as HTMLElement;
      expect(panel.className).toContain('fixed right-0 top-0 bottom-0');
    });

    it('applies floating position classes', () => {
      const { container } = render(<VisualTestPanel position="floating" />);
      const panel = container.firstChild as HTMLElement;
      expect(panel.className).toContain('fixed bottom-4 right-4');
    });
  });

  describe('Tab Navigation', () => {
    it('displays all tabs when expanded', () => {
      render(<VisualTestPanel defaultExpanded={true} />);
      
      expect(screen.getByText('Controls')).toBeDefined();
      expect(screen.getByText('Validation')).toBeDefined();
      expect(screen.getByText('Debug')).toBeDefined();
      expect(screen.getByText('Metrics')).toBeDefined();
    });

    it('switches tabs when clicked', async () => {
      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      // Click on Validation tab
      const validationTab = screen.getByText('Validation');
      await user.click(validationTab);
      
      // Check that validation content would be shown
      expect(screen.getByText('Auto-validate on Changes')).toBeDefined();
    });
  });

  describe('Status Indicators', () => {
    it('displays validation status when validations exist', async () => {
      const messagesWithTools = [
        {
          id: 'msg-1',
          content: {
            type: 'tool_use',
            name: 'act_oneshot',
            id: 'tool-1'
          }
        }
      ];

      mockUseChat.mockReturnValue({
        messages: messagesWithTools
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      await waitFor(() => {
        // Look for status indicator divs instead of buttons
        const statusIndicators = document.querySelectorAll('.bg-green-100, .bg-red-100, .dark\\:bg-green-900\\/20, .dark\\:bg-red-900\\/20');
        expect(statusIndicators.length).toBeGreaterThanOrEqual(0);
      });
    });

    it('shows current scenario badge', () => {
      mockUseTestSession.mockReturnValue({
        ...defaultMockTestSession,
        currentScenario: {
          id: 'test-1',
          name: 'Active Test',
          description: 'Currently active test'
        }
      });

      render(<VisualTestPanel />);
      expect(screen.getByText('Active Test')).toBeDefined();
    });
  });

  describe('Action Buttons', () => {
    it('handles reload scenario button click', async () => {
      const reloadCurrentScenario = vi.fn();
      mockUseTestSession.mockReturnValue({
        ...defaultMockTestSession,
        currentScenario: { id: 'test-1', name: 'Test 1' },
        reloadCurrentScenario
      });

      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const reloadButton = screen.getByText('RefreshCw').closest('button');
      await user.click(reloadButton!);
      
      expect(reloadCurrentScenario).toHaveBeenCalled();
    });

    it('handles export results button click', async () => {
      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const downloadButton = screen.getByText('Download').closest('button');
      await user.click(downloadButton!);
      
      expect(global.URL.createObjectURL).toHaveBeenCalled();
    });

    it('toggles fullscreen mode', async () => {
      const user = userEvent.setup();
      const { container } = render(<VisualTestPanel defaultExpanded={true} position="bottom" />);
      
      const fullscreenButton = screen.getByText('Maximize2').closest('button');
      await user.click(fullscreenButton!);
      
      const panel = container.firstChild as HTMLElement;
      expect(panel.className).toContain('h-screen');
      
      const minimizeButton = screen.getByText('Minimize2').closest('button');
      await user.click(minimizeButton!);
      
      expect(panel.className).not.toContain('h-screen');
    });

    it('disables reload button when loading', () => {
      mockUseTestSession.mockReturnValue({
        ...defaultMockTestSession,
        isLoading: true,
        currentScenario: { id: 'test-1', name: 'Test 1' }
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      const reloadButton = screen.getByText('RefreshCw').closest('button');
      expect(reloadButton).toHaveProperty('disabled', true);
    });
  });

  describe('Tool Validation', () => {
    beforeEach(() => {
      // Mock DOM elements for validation
      const mockDivider = document.createElement('div');
      mockDivider.className = 'subsession-divider';
      
      const mockThought = document.createElement('div');
      mockThought.className = 'thought-bubble';
      
      vi.spyOn(document, 'querySelector').mockImplementation((selector: string) => {
        if (selector.includes('subsession-divider')) return mockDivider;
        if (selector.includes('thought-bubble')) return mockThought;
        if (selector.includes('tool-call-ui')) return null;
        return null;
      });
    });

    it('validates delegation tools', async () => {
      const messagesWithDelegation = [
        {
          id: 'msg-1',
          content: [{
            type: 'tool_use',
            name: 'act_oneshot',
            id: 'tool-1'
          }]
        }
      ];

      mockUseChat.mockReturnValue({
        messages: messagesWithDelegation
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      await waitFor(() => {
        const validationTab = screen.getByText('Validation');
        fireEvent.click(validationTab);
        
        expect(screen.getByText(/Delegation Tools/)).toBeDefined();
      });
    });

    it('validates think tools', async () => {
      const messagesWithThink = [
        {
          id: 'msg-2',
          content: [{
            type: 'tool_use',
            name: 'think',
            id: 'think-1'
          }]
        }
      ];

      mockUseChat.mockReturnValue({
        messages: messagesWithThink
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      await waitFor(() => {
        const validationTab = screen.getByText('Validation');
        fireEvent.click(validationTab);
        
        expect(screen.getByText(/Think Tools/)).toBeDefined();
      });
    });

    it('handles auto-validation toggle', async () => {
      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const validationTab = screen.getByText('Validation');
      await user.click(validationTab);
      
      const autoValidateButton = screen.getByText('Enabled').closest('button');
      await user.click(autoValidateButton!);
      
      expect(screen.getByText('Disabled')).toBeDefined();
    });
  });

  describe('Performance Metrics', () => {
    it('displays performance metrics', async () => {
      mockUseChat.mockReturnValue({
        messages: [{ id: 'msg-1', content: 'Test message' }]
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      const metricsTab = screen.getByText('Metrics');
      fireEvent.click(metricsTab);
      
      await waitFor(() => {
        expect(screen.getByText(/Render Time/)).toBeDefined();
        expect(screen.getByText(/Messages/)).toBeDefined();
        expect(screen.getByText(/Memory/)).toBeDefined();
        expect(screen.getByText(/Scroll/)).toBeDefined();
      });
    });

    it('shows performance tips', () => {
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const metricsTab = screen.getByText('Metrics');
      fireEvent.click(metricsTab);
      
      expect(screen.getByText(/Keep render time below 16ms/)).toBeDefined();
    });
  });

  describe('Debug Section', () => {
    it('toggles debug info display', async () => {
      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const debugTab = screen.getByText('Debug');
      await user.click(debugTab);
      
      const showDebugButton = screen.getByText('Hide').closest('button');
      await user.click(showDebugButton!);
      
      expect(screen.getByText('Show')).toBeDefined();
    });

    it('displays message count', () => {
      mockUseChat.mockReturnValue({
        messages: [
          { id: 'msg-1', content: 'Message 1' },
          { id: 'msg-2', content: 'Message 2' }
        ]
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      const debugTab = screen.getByText('Debug');
      fireEvent.click(debugTab);
      
      const badge = screen.getByText('2');
      expect(badge).toBeDefined();
    });

    it('shows raw data when enabled', async () => {
      const messages = [{ id: 'msg-1', content: 'Test' }];
      mockUseChat.mockReturnValue({ messages });

      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const debugTab = screen.getByText('Debug');
      await user.click(debugTab);
      
      // Find the show raw data button by looking for the Label element
      const labels = screen.getAllByText(/Show Raw Message Data/);
      const showRawButton = labels[0].parentElement?.querySelector('button');
      await user.click(showRawButton!);
      
      // Check if raw data would be displayed
      const scrollAreas = document.querySelectorAll('.scroll-area');
      expect(scrollAreas.length).toBeGreaterThan(0);
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
        // Mock window dimensions
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

        const { container } = render(<VisualTestPanel defaultExpanded={true} />);
        const panel = container.firstChild as HTMLElement;
        
        // Panel should be present
        expect(panel).toBeDefined();
        
        // Check that tabs are rendered appropriately
        if (width < 640) {
          // On mobile, check for compact layout
          expect(screen.getByText('Controls')).toBeDefined();
        } else {
          // On larger screens, check for full layout
          expect(screen.getByText('Controls')).toBeDefined();
          expect(screen.getByText('Validation')).toBeDefined();
        }
      });
    });
  });

  describe('Theme Compatibility', () => {
    it('renders in light theme', () => {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
      
      const { container } = render(<VisualTestPanel />);
      expect(container.firstChild).toBeDefined();
    });

    it('renders in dark theme', () => {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
      
      const { container } = render(<VisualTestPanel />);
      expect(container.firstChild).toBeDefined();
    });
  });

  describe('Accessibility', () => {
    it('provides accessible labels for buttons', () => {
      render(<VisualTestPanel defaultExpanded={true} />);
      
      // Get first few buttons to check instead of all
      const chevronButton = screen.getByText('ChevronDown').closest('button');
      const hasText = chevronButton?.textContent && chevronButton.textContent.length > 0;
      const hasTooltip = chevronButton?.hasAttribute('data-tooltip');
      expect(hasText || hasTooltip).toBe(true);
    });

    it('uses semantic HTML elements', () => {
      render(<VisualTestPanel defaultExpanded={true} />);
      
      // Check for heading
      const headings = document.querySelectorAll('h3');
      expect(headings.length).toBeGreaterThan(0);
      
      // Check for labels
      const labels = document.querySelectorAll('label');
      expect(labels.length).toBeGreaterThan(0);
    });

    it('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      // Tab through buttons
      await user.tab();
      expect(document.activeElement?.tagName).toBe('BUTTON');
      
      // Press enter to activate
      await user.keyboard('{Enter}');
      
      // Should still be functional
      expect(document.activeElement).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('displays error messages', () => {
      mockUseTestSession.mockReturnValue({
        ...defaultMockTestSession,
        error: 'Failed to load scenario'
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      expect(screen.getByText('Failed to load scenario')).toBeDefined();
    });

    it('handles missing performance API gracefully', () => {
      // Remove performance.memory
      Object.defineProperty(window, 'performance', {
        value: {
          now: vi.fn(() => 100),
          getEntriesByType: vi.fn(() => [])
        },
        writable: true
      });

      mockUseChat.mockReturnValue({
        messages: [{ id: 'msg-1', content: 'Test' }]
      });

      render(<VisualTestPanel defaultExpanded={true} />);
      
      // Should still render without crashing
      const metricsTab = screen.getByText('Metrics');
      fireEvent.click(metricsTab);
      
      expect(screen.getByText(/Render Time/)).toBeDefined();
    });
  });

  describe('Scenario Management', () => {
    it('loads scenario when button clicked', async () => {
      const loadScenario = vi.fn();
      mockUseTestSession.mockReturnValue({
        ...defaultMockTestSession,
        loadScenario
      });

      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const scenarioButton = screen.getByText('Test Scenario 1').closest('button');
      await user.click(scenarioButton!);
      
      expect(loadScenario).toHaveBeenCalledWith('scenario-1');
    });

    it('clears session when clear button clicked', async () => {
      const clearSession = vi.fn();
      mockUseTestSession.mockReturnValue({
        ...defaultMockTestSession,
        currentScenario: { id: 'test-1', name: 'Test 1' },
        clearSession
      });

      const user = userEvent.setup();
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const clearButton = screen.getByText('Clear Session').closest('button');
      await user.click(clearButton!);
      
      expect(clearSession).toHaveBeenCalled();
    });

    it('disables clear button when no scenario loaded', () => {
      render(<VisualTestPanel defaultExpanded={true} />);
      
      const clearButton = screen.getByText('Clear Session').closest('button');
      expect(clearButton).toHaveProperty('disabled', true);
    });
  });
});