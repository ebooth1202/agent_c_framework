/**
 * Demo Application Testing Utilities
 * Helper functions for testing the demo application
 */

import React, { ReactElement } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { userEvent, UserEvent } from '@testing-library/user-event';
import { vi } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import type { RealtimeClient } from '@agentc/realtime-core';

/**
 * Mock application configuration
 */
export const mockAppConfig = {
  apiUrl: 'ws://localhost:8080/test',
  authToken: 'test-token',
  enableAnalytics: false,
  enableDebugMode: true,
  maxReconnectAttempts: 3,
  sessionTimeout: 30000
};

/**
 * Create mock client with demo-specific features
 */
export function createDemoMockClient(): Partial<RealtimeClient> {
  return {
    isConnected: vi.fn(() => false),
    connect: vi.fn().mockResolvedValue(undefined),
    disconnect: vi.fn(),
    destroy: vi.fn(),
    sendText: vi.fn(),
    sendBinaryFrame: vi.fn(),
    sendEvent: vi.fn(),
    updateSession: vi.fn(),
    setAudioEnabled: vi.fn(),
    getStatistics: vi.fn(() => ({
      connection: {
        state: 'disconnected',
        latency: 0,
        packetsLost: 0,
        reconnectAttempts: 0
      },
      audio: {
        inputLevel: 0,
        outputLevel: 0,
        isRecording: false,
        isMuted: false
      },
      session: {
        duration: 0,
        messageCount: 0,
        turnCount: 0
      }
    })),
    on: vi.fn(),
    off: vi.fn(),
    once: vi.fn(),
    emit: vi.fn(),
    removeAllListeners: vi.fn()
  };
}

/**
 * Demo app wrapper with routing
 */
interface DemoWrapperProps {
  children: ReactNode;
  initialRoute?: string;
  client?: Partial<RealtimeClient>;
}

export function DemoWrapper({ 
  children, 
  initialRoute = '/',
  client = createDemoMockClient()
}: DemoWrapperProps) {
  return (
    <MemoryRouter initialEntries={[initialRoute]}>
      {children}
    </MemoryRouter>
  );
}

/**
 * Render with demo context and routing
 */
export function renderDemo(
  ui: ReactElement,
  options?: {
    route?: string;
    client?: Partial<RealtimeClient>;
  } & RenderOptions
): RenderResult & { user: UserEvent; client: Partial<RealtimeClient> } {
  const { 
    route = '/', 
    client = createDemoMockClient(),
    ...renderOptions 
  } = options || {};
  
  const user = userEvent.setup();
  
  const result = render(
    <DemoWrapper initialRoute={route} client={client}>
      {ui}
    </DemoWrapper>,
    renderOptions
  );

  return {
    ...result,
    user,
    client
  };
}

/**
 * Page object models for demo app sections
 */
export const pages = {
  /**
   * Chat page selectors and actions
   */
  chat: {
    selectors: {
      container: '[data-testid="chat-container"]',
      input: '[data-testid="chat-input"]',
      sendButton: '[data-testid="send-button"]',
      messageList: '[data-testid="message-list"]',
      message: '[data-testid="chat-message"]',
      typingIndicator: '[data-testid="typing-indicator"]'
    },
    
    actions: {
      sendMessage: async (user: UserEvent, message: string) => {
        const input = document.querySelector(pages.chat.selectors.input) as HTMLElement;
        const sendButton = document.querySelector(pages.chat.selectors.sendButton) as HTMLElement;
        
        await user.type(input, message);
        await user.click(sendButton);
      },
      
      clearChat: async (user: UserEvent) => {
        const clearButton = document.querySelector('[data-testid="clear-chat"]') as HTMLElement;
        if (clearButton) {
          await user.click(clearButton);
        }
      }
    }
  },

  /**
   * Settings page selectors and actions
   */
  settings: {
    selectors: {
      container: '[data-testid="settings-container"]',
      audioToggle: '[data-testid="audio-toggle"]',
      themeToggle: '[data-testid="theme-toggle"]',
      saveButton: '[data-testid="save-settings"]'
    },
    
    actions: {
      toggleAudio: async (user: UserEvent) => {
        const toggle = document.querySelector(pages.settings.selectors.audioToggle) as HTMLElement;
        await user.click(toggle);
      },
      
      toggleTheme: async (user: UserEvent) => {
        const toggle = document.querySelector(pages.settings.selectors.themeToggle) as HTMLElement;
        await user.click(toggle);
      },
      
      saveSettings: async (user: UserEvent) => {
        const button = document.querySelector(pages.settings.selectors.saveButton) as HTMLElement;
        await user.click(button);
      }
    }
  },

  /**
   * Connection panel selectors and actions
   */
  connection: {
    selectors: {
      panel: '[data-testid="connection-panel"]',
      connectButton: '[data-testid="connect-button"]',
      disconnectButton: '[data-testid="disconnect-button"]',
      status: '[data-testid="connection-status"]',
      indicator: '[data-testid="connection-indicator"]'
    },
    
    actions: {
      connect: async (user: UserEvent) => {
        const button = document.querySelector(pages.connection.selectors.connectButton) as HTMLElement;
        await user.click(button);
      },
      
      disconnect: async (user: UserEvent) => {
        const button = document.querySelector(pages.connection.selectors.disconnectButton) as HTMLElement;
        await user.click(button);
      }
    }
  }
};

/**
 * Demo app state management mocks
 */
export const mockState = {
  /**
   * Create initial app state
   */
  createInitialState: () => ({
    connection: {
      isConnected: false,
      status: 'disconnected',
      error: null
    },
    chat: {
      messages: [],
      isTyping: false
    },
    audio: {
      isEnabled: false,
      isMuted: false,
      level: 0
    },
    settings: {
      theme: 'light',
      audioEnabled: true,
      notifications: true
    },
    session: {
      id: null,
      startTime: null,
      duration: 0
    }
  }),

  /**
   * Create connected state
   */
  createConnectedState: () => ({
    ...mockState.createInitialState(),
    connection: {
      isConnected: true,
      status: 'connected',
      error: null
    },
    session: {
      id: 'test-session-123',
      startTime: new Date().toISOString(),
      duration: 0
    }
  }),

  /**
   * Create state with messages
   */
  createWithMessages: (messageCount: number = 5) => {
    const state = mockState.createConnectedState();
    state.chat.messages = Array.from({ length: messageCount }, (_, i) => ({
      id: `msg-${i}`,
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Test message ${i}`,
      timestamp: new Date(Date.now() - (messageCount - i) * 1000).toISOString()
    }));
    return state;
  }
};

/**
 * Local storage utilities for demo app
 */
export const storage = {
  /**
   * Set up local storage with test data
   */
  setup: (data: Record<string, any> = {}) => {
    Object.entries(data).forEach(([key, value]) => {
      localStorage.setItem(key, JSON.stringify(value));
    });
  },

  /**
   * Get item from local storage
   */
  get: (key: string): any => {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  },

  /**
   * Clear all local storage
   */
  clear: () => {
    localStorage.clear();
  }
};

/**
 * Analytics mocking for demo app
 */
export const mockAnalytics = {
  track: vi.fn(),
  page: vi.fn(),
  identify: vi.fn(),
  reset: () => {
    mockAnalytics.track.mockClear();
    mockAnalytics.page.mockClear();
    mockAnalytics.identify.mockClear();
  }
};

/**
 * Network mocking utilities
 */
export const network = {
  /**
   * Mock successful API response
   */
  mockSuccess: (data: any) => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => data,
      status: 200,
      statusText: 'OK'
    });
  },

  /**
   * Mock API error
   */
  mockError: (status: number = 500, message: string = 'Internal Server Error') => {
    global.fetch = vi.fn().mockRejectedValue({
      ok: false,
      status,
      statusText: message,
      json: async () => ({ error: message })
    });
  },

  /**
   * Mock WebSocket connection
   */
  mockWebSocket: () => {
    const ws = {
      readyState: WebSocket.OPEN,
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn()
    };
    
    global.WebSocket = vi.fn(() => ws) as any;
    return ws;
  }
};

/**
 * Performance testing utilities
 */
export const performance = {
  /**
   * Measure render time
   */
  measureRender: async (component: ReactElement): Promise<number> => {
    const start = window.performance.now();
    render(component);
    const end = window.performance.now();
    return end - start;
  },

  /**
   * Measure interaction time
   */
  measureInteraction: async (
    action: () => Promise<void>
  ): Promise<number> => {
    const start = window.performance.now();
    await action();
    const end = window.performance.now();
    return end - start;
  }
};

/**
 * Test data generators
 */
export const generate = {
  /**
   * Generate chat messages
   */
  messages: (count: number = 10) => {
    return Array.from({ length: count }, (_, i) => ({
      id: `msg-${Date.now()}-${i}`,
      role: i % 2 === 0 ? 'user' : 'assistant',
      content: `Generated message ${i}`,
      timestamp: new Date(Date.now() - (count - i) * 1000).toISOString()
    }));
  },

  /**
   * Generate audio data
   */
  audioData: (duration: number = 1000) => {
    const sampleRate = 44100;
    const samples = Math.floor((duration / 1000) * sampleRate);
    const buffer = new ArrayBuffer(samples * 2);
    const view = new Int16Array(buffer);
    
    for (let i = 0; i < samples; i++) {
      view[i] = Math.sin(2 * Math.PI * 440 * i / sampleRate) * 32767;
    }
    
    return buffer;
  }
};

/**
 * Common test scenarios for demo app
 */
export const scenarios = {
  /**
   * Test complete chat flow
   */
  testChatFlow: async (user: UserEvent) => {
    // Connect
    await pages.connection.actions.connect(user);
    
    // Send message
    await pages.chat.actions.sendMessage(user, 'Hello, assistant!');
    
    // Wait for response
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Check messages
    const messages = document.querySelectorAll(pages.chat.selectors.message);
    expect(messages.length).toBeGreaterThan(0);
  },

  /**
   * Test settings persistence
   */
  testSettingsPersistence: async (user: UserEvent) => {
    // Change settings
    await pages.settings.actions.toggleTheme(user);
    await pages.settings.actions.toggleAudio(user);
    await pages.settings.actions.saveSettings(user);
    
    // Check localStorage
    const settings = storage.get('app-settings');
    expect(settings).toBeDefined();
  }
};