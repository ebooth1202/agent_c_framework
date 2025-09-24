/**
 * Test for TestControls component
 */

import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TestControls, FloatingTestButton } from '../test-controls';

// Mock the useTestSession hook
const mockUseTestSession = vi.fn();

vi.mock('@/hooks/use-test-session', () => ({
  useTestSession: () => mockUseTestSession()
}));

// Mock UI components
vi.mock('@agentc/realtime-ui', () => ({
  Button: ({ children, onClick, disabled, ...props }: any) => (
    <button onClick={onClick} disabled={disabled} {...props}>{children}</button>
  ),
  Select: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  SelectTrigger: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  SelectContent: ({ children }: any) => <div>{children}</div>,
  SelectItem: ({ children, value }: any) => <div data-value={value}>{children}</div>,
  SelectValue: ({ placeholder }: any) => <span>{placeholder}</span>,
  Card: ({ children, className }: any) => <div className={className}>{children}</div>,
  CardHeader: ({ children }: any) => <div>{children}</div>,
  CardTitle: ({ children }: any) => <h3>{children}</h3>,
  CardDescription: ({ children }: any) => <p>{children}</p>,
  CardContent: ({ children }: any) => <div>{children}</div>,
  Label: ({ children, ...props }: any) => <label {...props}>{children}</label>,
  Alert: ({ children, variant }: any) => <div data-variant={variant}>{children}</div>,
  AlertDescription: ({ children }: any) => <p>{children}</p>,
  Separator: () => <hr />,
  Badge: ({ children, variant }: any) => <span data-variant={variant}>{children}</span>,
  ScrollArea: ({ children }: any) => <div>{children}</div>,
  Skeleton: ({ className }: any) => <div className={className}>Loading...</div>
}));

// Mock Lucide React icons
vi.mock('lucide-react', () => ({
  FlaskConical: () => <span>FlaskConical</span>,
  Play: () => <span>Play</span>,
  RotateCcw: () => <span>RotateCcw</span>,
  X: () => <span>X</span>,
  ChevronDown: () => <span>ChevronDown</span>,
  ChevronUp: () => <span>ChevronUp</span>,
  FileJson: () => <span>FileJson</span>,
  AlertCircle: () => <span>AlertCircle</span>,
  CheckCircle: () => <span>CheckCircle</span>
}));

describe('TestControls', () => {
  const defaultMockReturn = {
    testModeEnabled: true,
    testConfig: {
      enabled: true,
      scenarios: [],
      showTestControls: true
    },
    scenarios: [
      { id: 'test-1', name: 'Test Scenario 1', description: 'First test' },
      { id: 'test-2', name: 'Test Scenario 2', description: 'Second test' }
    ],
    currentScenario: null,
    enableTestMode: vi.fn(),
    loadScenario: vi.fn(),
    clearSession: vi.fn(),
    reloadCurrentScenario: vi.fn(),
    showTestControls: true,
    setShowTestControls: vi.fn(),
    isLoading: false,
    error: null
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTestSession.mockReturnValue(defaultMockReturn);
  });

  it('renders test controls when test mode is enabled', () => {
    render(<TestControls />);
    
    expect(screen.getByText('Test Session Manager')).toBeDefined();
    expect(screen.getByText('Load and test chat sessions for validation')).toBeDefined();
  });

  it('does not render when test mode is disabled and showTestControls is false', () => {
    mockUseTestSession.mockReturnValue({
      ...defaultMockReturn,
      testModeEnabled: false,
      showTestControls: false
    });

    const { container } = render(<TestControls />);
    expect(container.firstChild).toBeNull();
  });

  it('shows test mode toggle and handles click', async () => {
    const enableTestMode = vi.fn();
    mockUseTestSession.mockReturnValue({
      ...defaultMockReturn,
      enableTestMode
    });

    render(<TestControls />);
    
    const toggleButton = screen.getByText('Enabled');
    fireEvent.click(toggleButton);
    
    expect(enableTestMode).toHaveBeenCalledWith(false);
  });

  it('displays current scenario when loaded', () => {
    mockUseTestSession.mockReturnValue({
      ...defaultMockReturn,
      currentScenario: {
        id: 'test-1',
        name: 'Test Scenario 1',
        description: 'First test scenario',
        filePath: '/test-data/test1.json',
        tags: ['test', 'demo']
      }
    });

    render(<TestControls />);
    
    expect(screen.getByText('Current Session')).toBeDefined();
    expect(screen.getAllByText('Test Scenario 1').length).toBeGreaterThan(0);
    expect(screen.getByText('First test scenario')).toBeDefined();
    expect(screen.getByText('test')).toBeDefined();
    expect(screen.getByText('demo')).toBeDefined();
  });

  it('displays error message when error occurs', () => {
    mockUseTestSession.mockReturnValue({
      ...defaultMockReturn,
      error: 'Failed to load scenario'
    });

    render(<TestControls />);
    
    expect(screen.getByText('Failed to load scenario')).toBeDefined();
  });

  it('shows loading state', () => {
    mockUseTestSession.mockReturnValue({
      ...defaultMockReturn,
      isLoading: true
    });

    render(<TestControls />);
    
    expect(screen.getByText('Loading scenario...')).toBeDefined();
  });

  it('handles compact mode toggle', () => {
    render(<TestControls compact={true} />);
    
    // Should start collapsed in compact mode
    const expandButton = screen.getByText('Test Mode');
    expect(expandButton).toBeDefined();
    
    // Click to expand
    fireEvent.click(expandButton);
    
    // Should now show full controls
    expect(screen.getByText('Test Session Manager')).toBeDefined();
  });

  it('calls clearSession when clear button is clicked', () => {
    const clearSession = vi.fn();
    mockUseTestSession.mockReturnValue({
      ...defaultMockReturn,
      currentScenario: { id: 'test-1', name: 'Test 1', filePath: '/test.json' },
      clearSession
    });

    render(<TestControls />);
    
    const clearButton = screen.getByText('Clear');
    fireEvent.click(clearButton);
    
    expect(clearSession).toHaveBeenCalled();
  });

  it('calls reloadCurrentScenario when reload button is clicked', () => {
    const reloadCurrentScenario = vi.fn();
    mockUseTestSession.mockReturnValue({
      ...defaultMockReturn,
      currentScenario: { id: 'test-1', name: 'Test 1', filePath: '/test.json' },
      reloadCurrentScenario
    });

    render(<TestControls />);
    
    const reloadButton = screen.getByText('Reload');
    fireEvent.click(reloadButton);
    
    expect(reloadCurrentScenario).toHaveBeenCalled();
  });
});

describe('FloatingTestButton', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseTestSession.mockReturnValue({
      testModeEnabled: true,
      testConfig: { enabled: true, scenarios: [], showTestControls: true },
      scenarios: [],
      currentScenario: null,
      enableTestMode: vi.fn(),
      loadScenario: vi.fn(),
      clearSession: vi.fn(),
      reloadCurrentScenario: vi.fn(),
      showTestControls: true,
      setShowTestControls: vi.fn(),
      isLoading: false,
      error: null
    });
  });

  it('renders floating button when test mode is enabled', () => {
    render(<FloatingTestButton />);
    
    const button = screen.getByTitle('Open test controls');
    expect(button).toBeDefined();
  });

  it('does not render when test mode is disabled', () => {
    mockUseTestSession.mockReturnValue({
      testModeEnabled: false,
      testConfig: { enabled: false, scenarios: [], showTestControls: false },
      scenarios: [],
      currentScenario: null,
      enableTestMode: vi.fn(),
      loadScenario: vi.fn(),
      clearSession: vi.fn(),
      reloadCurrentScenario: vi.fn(),
      showTestControls: false,
      setShowTestControls: vi.fn(),
      isLoading: false,
      error: null
    });

    const { container } = render(<FloatingTestButton />);
    expect(container.firstChild).toBeNull();
  });
});