/**
 * Tests for AuthManager
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { AuthManager } from '../AuthManager';
import { AuthConfig, MemoryTokenStorage, TokenPair } from '../AuthConfig';
import { LoginResponse, RefreshTokenResponse } from '../../events/types/CommonTypes';
import { createMockJWT, sleep } from './utils/test-helpers';

describe('AuthManager', () => {
  let authManager: AuthManager;
  let mockFetch: ReturnType<typeof vi.fn>;
  let mockStorage: MemoryTokenStorage;
  let config: AuthConfig;

  // Mock data
  const mockUser = {
    id: 'user-123',
    username: 'testuser',
    email: 'test@example.com',
    roles: ['user']
  };

  const mockAgent = {
    id: 'agent-1',
    name: 'Test Agent',
    description: 'A test agent',
    capabilities: ['chat']
  };

  const mockAvatar = {
    id: 'avatar-1',
    name: 'Default Avatar',
    type: 'heygen',
    avatar_id: 'avatar_123'
  };

  const mockVoice = {
    id: 'voice-1',
    name: 'Default Voice',
    provider: 'openai',
    voice_id: 'alloy',
    sample_rate: 24000,
    language: 'en-US'
  };

  const mockToolset = {
    id: 'toolset-1',
    name: 'Default Tools',
    tools: []
  };

  const mockLoginResponse: LoginResponse = {
    agent_c_token: createMockJWT({ sub: 'user-123' }, 3600),
    heygen_token: 'heygen-test-token',
    ui_session_id: 'session-123'
  };

  const mockRefreshResponse: RefreshTokenResponse = {
    agent_c_token: createMockJWT({ sub: 'user-123' }, 3600),
    heygen_token: 'heygen-refreshed-token'
  };

  beforeEach(() => {
    // Create mock fetch
    mockFetch = vi.fn();
    
    // Create mock storage
    mockStorage = new MemoryTokenStorage();
    
    // Create config
    config = {
      apiUrl: 'https://api.example.com',
      storage: mockStorage,
      fetch: mockFetch,
      autoRefresh: false, // Disable by default for predictable tests
      refreshBufferMs: 60000
    };
    
    // Create AuthManager instance
    authManager = new AuthManager(config);
  });

  afterEach(() => {
    authManager.destroy();
    vi.clearAllMocks();
  });

  describe('Initialization', () => {
    it('should initialize with default state', () => {
      const state = authManager.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.tokens).toBeNull();
      expect(state.user).toBeNull();
      expect(state.uiSessionId).toBeNull();
      expect(state.wsUrl).toBeNull();
      expect(state.isAuthenticating).toBe(false);
      expect(state.isRefreshing).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should load stored tokens on initialization', async () => {
      const storedTokens: TokenPair = {
        agentCToken: createMockJWT({ sub: 'user-123' }, 3600),
        heygenToken: 'stored-heygen-token',
        expiresAt: Date.now() + 3600000
      };
      
      // Set tokens in storage before creating AuthManager
      await mockStorage.setTokens(storedTokens);
      
      // Create new AuthManager instance
      const newAuthManager = new AuthManager(config);
      
      // Wait for async initialization
      await sleep(10);
      
      const state = newAuthManager.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.tokens).toEqual(storedTokens);
      
      newAuthManager.destroy();
    });

    it('should clear expired tokens on initialization', async () => {
      const expiredTokens: TokenPair = {
        agentCToken: createMockJWT({ sub: 'user-123' }, -100), // Expired
        heygenToken: 'expired-heygen-token',
        expiresAt: Date.now() - 100000 // Expired
      };
      
      // Set expired tokens in storage
      await mockStorage.setTokens(expiredTokens);
      
      // Create new AuthManager instance
      const newAuthManager = new AuthManager(config);
      
      // Wait for async initialization
      await sleep(10);
      
      const state = newAuthManager.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.tokens).toBeNull();
      
      // Verify tokens were cleared from storage
      const storedTokens = await mockStorage.getTokens();
      expect(storedTokens).toBeNull();
      
      newAuthManager.destroy();
    });
  });

  describe('Login', () => {
    it('should successfully login with valid credentials', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLoginResponse
      });
      
      const loginHandler = vi.fn();
      const stateHandler = vi.fn();
      authManager.on('auth:login', loginHandler);
      authManager.on('auth:state-changed', stateHandler);
      
      const result = await authManager.login({
        username: 'testuser',
        password: 'password123'
      });
      
      expect(result).toEqual(mockLoginResponse);
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/rt/login',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: 'testuser',
            password: 'password123'
          })
        }
      );
      
      // Check state was updated
      const state = authManager.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.tokens?.agentCToken).toBe(mockLoginResponse.agent_c_token);
      expect(state.tokens?.heygenToken).toBe(mockLoginResponse.heygen_token);
      expect(state.user).toBeNull(); // User data will come from WebSocket events
      expect(state.uiSessionId).toBe('session-123');
      
      // Check events were emitted
      expect(loginHandler).toHaveBeenCalledWith(mockLoginResponse);
      expect(stateHandler).toHaveBeenCalled();
      
      // Check tokens were stored
      const storedTokens = await mockStorage.getTokens();
      expect(storedTokens?.agentCToken).toBe(mockLoginResponse.agent_c_token);
      expect(storedTokens?.heygenToken).toBe(mockLoginResponse.heygen_token);
    });

    it('should handle login failure', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        text: async () => 'Invalid credentials'
      });
      
      const errorHandler = vi.fn();
      authManager.on('auth:error', errorHandler);
      
      await expect(authManager.login({
        username: 'testuser',
        password: 'wrongpassword'
      })).rejects.toThrow('Authentication failed: 401 - Invalid credentials');
      
      // Check state
      const state = authManager.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.tokens).toBeNull();
      expect(state.error).toBeInstanceOf(Error);
      
      // Check error event was emitted
      expect(errorHandler).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should prevent concurrent login attempts', async () => {
      mockFetch.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => mockLoginResponse
        }), 100))
      );
      
      const firstLogin = authManager.login({
        username: 'testuser',
        password: 'password123'
      });
      
      // Try to login again while first is in progress
      await expect(authManager.login({
        username: 'testuser',
        password: 'password123'
      })).rejects.toThrow('Authentication already in progress');
      
      // Wait for first login to complete
      await firstLogin;
    });
  });

  describe('Token Refresh', () => {
    beforeEach(async () => {
      // Setup authenticated state
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLoginResponse
      });
      
      await authManager.login({
        username: 'testuser',
        password: 'password123'
      });
      
      mockFetch.mockClear();
    });

    it('should successfully refresh tokens', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRefreshResponse
      });
      
      const refreshHandler = vi.fn();
      authManager.on('auth:tokens-refreshed', refreshHandler);
      
      const newTokens = await authManager.refreshTokens();
      
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/rt/refresh_token',
        {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${mockLoginResponse.agent_c_token}`
          }
        }
      );
      
      expect(newTokens.agentCToken).toBe(mockRefreshResponse.agent_c_token);
      expect(newTokens.heygenToken).toBe(mockRefreshResponse.heygen_token);
      
      // Check state was updated
      const state = authManager.getState();
      expect(state.tokens?.agentCToken).toBe(mockRefreshResponse.agent_c_token);
      expect(state.tokens?.heygenToken).toBe(mockRefreshResponse.heygen_token);
      
      // Check event was emitted
      expect(refreshHandler).toHaveBeenCalledWith(expect.objectContaining({
        agentCToken: mockRefreshResponse.agent_c_token,
        heygenToken: mockRefreshResponse.heygen_token
      }));
      
      // Check tokens were stored
      const storedTokens = await mockStorage.getTokens();
      expect(storedTokens?.agentCToken).toBe(mockRefreshResponse.agent_c_token);
    });

    it('should handle refresh failure and logout on 401', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        text: async () => 'Token expired'
      });
      
      const logoutHandler = vi.fn();
      const errorHandler = vi.fn();
      authManager.on('auth:logout', logoutHandler);
      authManager.on('auth:error', errorHandler);
      
      await expect(authManager.refreshTokens()).rejects.toThrow('Token refresh failed: 401 - Token expired');
      
      // Should have logged out
      const state = authManager.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.tokens).toBeNull();
      
      // Check events
      expect(logoutHandler).toHaveBeenCalled();
      expect(errorHandler).toHaveBeenCalledWith(expect.any(Error));
    });

    it('should prevent concurrent refresh attempts', async () => {
      mockFetch.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => mockRefreshResponse
        }), 100))
      );
      
      const firstRefresh = authManager.refreshTokens();
      
      // Try to refresh again while first is in progress
      await expect(authManager.refreshTokens()).rejects.toThrow('Token refresh already in progress');
      
      // Wait for first refresh to complete
      await firstRefresh;
    });

    it('should throw error when refreshing without tokens', async () => {
      // Logout first
      await authManager.logout();
      
      await expect(authManager.refreshTokens()).rejects.toThrow('No tokens to refresh');
    });
  });

  describe('Auto Refresh', () => {
    it('should schedule automatic refresh when enabled', async () => {
      vi.useFakeTimers();
      
      // Create AuthManager with auto refresh
      const autoRefreshManager = new AuthManager({
        ...config,
        autoRefresh: true,
        refreshBufferMs: 60000 // 1 minute buffer
      });
      
      // Mock token that expires in 2 minutes
      const shortLivedResponse = {
        ...mockLoginResponse,
        agent_c_token: createMockJWT({ sub: 'user-123' }, 120) // 2 minutes
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => shortLivedResponse
      });
      
      await autoRefreshManager.login({
        username: 'testuser',
        password: 'password123'
      });
      
      // Mock refresh response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRefreshResponse
      });
      
      // Advance time to just before refresh (1 minute before expiry)
      vi.advanceTimersByTime(60000);
      
      // Wait for async refresh
      await vi.runAllTimersAsync();
      
      // Check that refresh was called
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/rt/refresh_token',
        expect.any(Object)
      );
      
      autoRefreshManager.destroy();
      vi.useRealTimers();
    });
  });

  describe('Logout', () => {
    beforeEach(async () => {
      // Setup authenticated state
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLoginResponse
      });
      
      await authManager.login({
        username: 'testuser',
        password: 'password123'
      });
    });

    it('should clear all authentication state on logout', async () => {
      const logoutHandler = vi.fn();
      authManager.on('auth:logout', logoutHandler);
      
      await authManager.logout();
      
      // Check state was cleared
      const state = authManager.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.tokens).toBeNull();
      expect(state.user).toBeNull();
      expect(state.uiSessionId).toBeNull();
      expect(state.error).toBeNull();
      
      // Check event was emitted
      expect(logoutHandler).toHaveBeenCalled();
      
      // Check tokens were cleared from storage
      const storedTokens = await mockStorage.getTokens();
      expect(storedTokens).toBeNull();
    });
  });

  describe('Getters', () => {
    beforeEach(async () => {
      // Setup authenticated state
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLoginResponse
      });
      
      await authManager.login({
        username: 'testuser',
        password: 'password123'
      });
    });

    it('should return correct token values', () => {
      expect(authManager.getAgentCToken()).toBe(mockLoginResponse.agent_c_token);
      expect(authManager.getHeygenToken()).toBe(mockLoginResponse.heygen_token);
      expect(authManager.isAuthenticated()).toBe(true);
    });

    it('should return user information', () => {
      expect(authManager.getUser()).toBeNull(); // User data will come from WebSocket events
      expect(authManager.getUiSessionId()).toBe('session-123');
    });

    it('should construct WebSocket URL from API URL', () => {
      const wsUrl = authManager.getWebSocketUrl();
      expect(wsUrl).toBe('wss://api.example.com/rt/ws');
    });

    it('should handle HTTP to WS conversion', () => {
      const httpManager = new AuthManager({
        ...config,
        apiUrl: 'http://localhost:8000'
      });
      
      const wsUrl = httpManager.getWebSocketUrl();
      expect(wsUrl).toBe('ws://localhost:8000/rt/ws');
      
      httpManager.destroy();
    });
  });

  describe('Initialize from Payload', () => {
    it('should initialize from complete login payload', async () => {
      const loginHandler = vi.fn();
      authManager.on('auth:login', loginHandler);
      
      await authManager.initializeFromPayload(mockLoginResponse, 'wss://custom.example.com/ws');
      
      // Check state was set correctly
      const state = authManager.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.tokens?.agentCToken).toBe(mockLoginResponse.agent_c_token);
      expect(state.tokens?.heygenToken).toBe(mockLoginResponse.heygen_token);
      expect(state.user).toBeNull(); // User data will come from WebSocket events
      expect(state.uiSessionId).toBe('session-123');
      expect(state.wsUrl).toBe('wss://custom.example.com/ws');
      
      // Check login event was emitted
      expect(loginHandler).toHaveBeenCalledWith(mockLoginResponse);
    });
  });

  describe('Set Tokens', () => {
    it('should set tokens directly', async () => {
      const tokens: TokenPair = {
        agentCToken: createMockJWT({ sub: 'user-456' }, 7200),
        heygenToken: 'direct-heygen-token',
        expiresAt: Date.now() + 7200000
      };
      
      await authManager.setTokens(tokens);
      
      // Check state was updated
      const state = authManager.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.tokens).toEqual(tokens);
      
      // Check tokens were stored
      const storedTokens = await mockStorage.getTokens();
      expect(storedTokens).toEqual(tokens);
    });

    it('should parse JWT expiry if not provided', async () => {
      const tokens: TokenPair = {
        agentCToken: createMockJWT({ sub: 'user-456' }, 7200),
        heygenToken: 'direct-heygen-token'
        // No expiresAt provided
      };
      
      await authManager.setTokens(tokens);
      
      const state = authManager.getState();
      expect(state.tokens?.expiresAt).toBeDefined();
      expect(state.tokens?.expiresAt).toBeGreaterThan(Date.now());
    });
  });

  describe('Error Handling', () => {
    it('should handle fetch errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      
      const errorHandler = vi.fn();
      authManager.on('auth:error', errorHandler);
      
      await expect(authManager.login({
        username: 'testuser',
        password: 'password123'
      })).rejects.toThrow('Network error');
      
      expect(errorHandler).toHaveBeenCalledWith(expect.objectContaining({
        message: 'Network error'
      }));
    });

    it('should handle malformed JWT tokens', async () => {
      const invalidResponse = {
        ...mockLoginResponse,
        agent_c_token: 'invalid-jwt-token'
      };
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => invalidResponse
      });
      
      // Should not throw, but won't have expiry
      await authManager.login({
        username: 'testuser',
        password: 'password123'
      });
      
      const state = authManager.getState();
      expect(state.tokens?.expiresAt).toBeUndefined();
    });

    it('should call onAuthError callback', async () => {
      const onAuthError = vi.fn();
      const errorManager = new AuthManager({
        ...config,
        onAuthError
      });
      
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        text: async () => 'Unauthorized'
      });
      
      await expect(errorManager.login({
        username: 'testuser',
        password: 'wrongpassword'
      })).rejects.toThrow();
      
      expect(onAuthError).toHaveBeenCalledWith(expect.any(Error));
      
      errorManager.destroy();
    });
  });

  describe('Cleanup', () => {
    it('should clean up resources on destroy', () => {
      const removeListenersSpy = vi.spyOn(authManager, 'removeAllListeners');
      
      authManager.destroy();
      
      expect(removeListenersSpy).toHaveBeenCalled();
    });

    it('should cancel refresh timer on destroy', async () => {
      vi.useFakeTimers();
      
      // Create AuthManager with auto refresh
      const autoRefreshManager = new AuthManager({
        ...config,
        autoRefresh: true,
        refreshBufferMs: 60000
      });
      
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLoginResponse
      });
      
      await autoRefreshManager.login({
        username: 'testuser',
        password: 'password123'
      });
      
      // Destroy should cancel the timer
      autoRefreshManager.destroy();
      
      // Mock refresh that should not be called
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRefreshResponse
      });
      
      // Advance time
      vi.advanceTimersByTime(120000);
      
      // Refresh should not have been called
      expect(mockFetch).toHaveBeenCalledTimes(1); // Only the login call
      
      vi.useRealTimers();
    });
  });
});