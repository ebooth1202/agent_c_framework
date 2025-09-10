/**
 * Integration Tests for Authentication Flow
 * Tests login, logout, session management, and token refresh
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { AuthProvider, useAuth } from '@/contexts/auth-context';
import { server, clearDemoAuth } from '@/test/mocks/server';
import { storage } from '@/test/utils/demo-test-utils';
import { http, HttpResponse, delay } from 'msw';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

// Test component to access auth context
function AuthTestComponent() {
  const auth = useAuth();
  
  return (
    <div>
      <div data-testid="auth-status">
        {auth.isAuthenticated ? 'Authenticated' : 'Not Authenticated'}
      </div>
      <div data-testid="loading-status">
        {auth.isLoading ? 'Loading' : 'Ready'}
      </div>
      <div data-testid="session-id">
        {auth.getUiSessionId() || 'No Session'}
      </div>
      <button onClick={() => auth.logout()} data-testid="logout-button">
        Logout
      </button>
    </div>
  );
}

// Login form component for testing
function LoginForm() {
  const auth = useAuth();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await auth.login({ email, password });
      console.log('Login successful:', response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} data-testid="login-form">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        data-testid="email-input"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        data-testid="password-input"
        required
      />
      <button type="submit" disabled={isSubmitting} data-testid="login-button">
        {isSubmitting ? 'Logging in...' : 'Login'}
      </button>
      {error && <div data-testid="login-error">{error}</div>}
    </form>
  );
}

// Protected route component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const auth = useAuth();
  
  if (auth.isLoading) {
    return <div data-testid="loading">Loading...</div>;
  }
  
  if (!auth.isAuthenticated) {
    return <div data-testid="unauthorized">Please login to continue</div>;
  }
  
  return <>{children}</>;
}

describe('Authentication Flow Integration', () => {
  beforeEach(() => {
    clearDemoAuth();
    storage.clear();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Login Flow', () => {
    it('handles successful login with token storage', async () => {
      const user = userEvent.setup();
      
      // Mock successful login response
      server.use(
        http.post('/api/auth/login', async () => {
          await delay(100);
          return HttpResponse.json({
            agent_c_token: 'jwt-token-123',
            heygen_token: 'heygen-token-456',
            ui_session_id: 'session-789'
          });
        })
      );

      const { container } = render(
        <AuthProvider>
          <LoginForm />
          <AuthTestComponent />
        </AuthProvider>
      );

      // Initial state
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      expect(screen.getByTestId('session-id')).toHaveTextContent('No Session');

      // Fill in login form
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      // Wait for login to complete
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Verify session ID is stored
      expect(screen.getByTestId('session-id')).toHaveTextContent('session-789');

      // Verify tokens are stored in localStorage
      expect(localStorage.getItem('agentc-auth-token')).toBe('jwt-token-123');
      expect(localStorage.getItem('heygen-token')).toBe('heygen-token-456');
      expect(localStorage.getItem('agentc-ui-session-id')).toBe('session-789');
    });

    it('handles login failure with error display', async () => {
      const user = userEvent.setup();
      
      // Mock failed login response
      server.use(
        http.post('/api/auth/login', async () => {
          await delay(100);
          return HttpResponse.json(
            {
              error: {
                code: 'INVALID_CREDENTIALS',
                message: 'Invalid email or password'
              }
            },
            { status: 401 }
          );
        })
      );

      const { container } = render(
        <AuthProvider>
          <LoginForm />
          <AuthTestComponent />
        </AuthProvider>
      );

      // Fill in login form
      await user.type(screen.getByTestId('email-input'), 'wrong@example.com');
      await user.type(screen.getByTestId('password-input'), 'wrongpassword');
      await user.click(screen.getByTestId('login-button'));

      // Wait for error to appear
      await waitFor(() => {
        expect(screen.getByTestId('login-error')).toBeInTheDocument();
      });

      // Verify error message
      expect(screen.getByTestId('login-error')).toHaveTextContent('Invalid email or password');

      // Verify still not authenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      expect(screen.getByTestId('session-id')).toHaveTextContent('No Session');

      // Verify no tokens stored
      expect(localStorage.getItem('agentc-auth-token')).toBeNull();
    });

    it('handles network error during login', async () => {
      const user = userEvent.setup();
      
      // Mock network error
      server.use(
        http.post('/api/auth/login', async () => {
          throw new Error('Network error');
        })
      );

      const { container } = render(
        <AuthProvider>
          <LoginForm />
        </AuthProvider>
      );

      // Try to login
      await user.type(screen.getByTestId('email-input'), 'test@example.com');
      await user.type(screen.getByTestId('password-input'), 'password123');
      await user.click(screen.getByTestId('login-button'));

      // Wait for error
      await waitFor(() => {
        expect(screen.getByTestId('login-error')).toBeInTheDocument();
      });

      // Verify network error message
      expect(screen.getByTestId('login-error')).toHaveTextContent(/network|connection/i);
    });
  });

  describe('Logout Flow', () => {
    it('handles logout and clears session data', async () => {
      const user = userEvent.setup();
      
      // Setup authenticated state
      localStorage.setItem('agentc-auth-token', 'existing-token');
      localStorage.setItem('agentc-ui-session-id', 'existing-session');
      localStorage.setItem('heygen-token', 'existing-heygen');

      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Wait for auth check
      await waitFor(() => {
        expect(screen.getByTestId('loading-status')).toHaveTextContent('Ready');
      });

      // Should be authenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('session-id')).toHaveTextContent('existing-session');

      // Click logout
      await user.click(screen.getByTestId('logout-button'));

      // Verify logged out
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      });

      expect(screen.getByTestId('session-id')).toHaveTextContent('No Session');

      // Verify tokens cleared
      expect(localStorage.getItem('agentc-auth-token')).toBeNull();
      expect(localStorage.getItem('agentc-ui-session-id')).toBeNull();
      expect(localStorage.getItem('heygen-token')).toBeNull();
    });

    it('handles logout with active connections', async () => {
      const user = userEvent.setup();
      const mockDisconnect = vi.fn();

      // Mock WebSocket connection
      const mockWebSocket = {
        close: mockDisconnect,
        readyState: WebSocket.OPEN
      };

      // Setup authenticated state with active connection
      localStorage.setItem('agentc-auth-token', 'active-token');
      localStorage.setItem('agentc-ui-session-id', 'active-session');

      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Simulate active WebSocket
      (global as any).activeWebSocket = mockWebSocket;

      // Logout
      await user.click(screen.getByTestId('logout-button'));

      // Verify connection closed
      await waitFor(() => {
        expect(mockDisconnect).toHaveBeenCalled();
      });

      // Verify logged out
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
    });
  });

  describe('Session Management', () => {
    it('restores session on mount if valid token exists', async () => {
      // Setup existing valid session
      localStorage.setItem('agentc-auth-token', 'valid-token');
      localStorage.setItem('agentc-ui-session-id', 'restored-session');

      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Initially loading
      expect(screen.getByTestId('loading-status')).toHaveTextContent('Loading');

      // Wait for auth check to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading-status')).toHaveTextContent('Ready');
      });

      // Should be authenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('session-id')).toHaveTextContent('restored-session');
    });

    it('handles expired token on mount', async () => {
      // Setup expired token
      const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.expired';
      localStorage.setItem('agentc-auth-token', expiredToken);
      localStorage.setItem('agentc-ui-session-id', 'expired-session');

      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Wait for auth check
      await waitFor(() => {
        expect(screen.getByTestId('loading-status')).toHaveTextContent('Ready');
      });

      // Should not be authenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      expect(screen.getByTestId('session-id')).toHaveTextContent('No Session');

      // Verify expired tokens cleared
      expect(localStorage.getItem('agentc-auth-token')).toBeNull();
      expect(localStorage.getItem('agentc-ui-session-id')).toBeNull();
    });

    it('handles token refresh flow', async () => {
      const user = userEvent.setup();
      
      // Setup token that will expire soon
      localStorage.setItem('agentc-auth-token', 'expiring-token');
      localStorage.setItem('agentc-ui-session-id', 'current-session');

      // Mock refresh endpoint
      server.use(
        http.post('/api/auth/refresh', async () => {
          return HttpResponse.json({
            agent_c_token: 'refreshed-token',
            ui_session_id: 'current-session' // Same session ID
          });
        })
      );

      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByTestId('loading-status')).toHaveTextContent('Ready');
      });

      // Simulate token expiration check (happens every 30 seconds)
      vi.advanceTimersByTime(30000);

      // Wait for refresh to complete
      await waitFor(() => {
        expect(localStorage.getItem('agentc-auth-token')).toBe('refreshed-token');
      });

      // Should remain authenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('session-id')).toHaveTextContent('current-session');
    });
  });

  describe('Protected Routes', () => {
    it('redirects unauthenticated users to login', async () => {
      const { container } = render(
        <MemoryRouter initialEntries={['/protected']}>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<LoginForm />} />
              <Route 
                path="/protected" 
                element={
                  <ProtectedRoute>
                    <div data-testid="protected-content">Protected Content</div>
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      // Wait for auth check
      await waitFor(() => {
        expect(screen.getByTestId('unauthorized')).toBeInTheDocument();
      });

      // Should show unauthorized message
      expect(screen.getByTestId('unauthorized')).toHaveTextContent('Please login to continue');
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });

    it('allows authenticated users to access protected routes', async () => {
      // Setup authenticated state
      localStorage.setItem('agentc-auth-token', 'valid-token');
      localStorage.setItem('agentc-ui-session-id', 'valid-session');

      const { container } = render(
        <MemoryRouter initialEntries={['/protected']}>
          <AuthProvider>
            <Routes>
              <Route 
                path="/protected" 
                element={
                  <ProtectedRoute>
                    <div data-testid="protected-content">Protected Content</div>
                  </ProtectedRoute>
                } 
              />
            </Routes>
          </AuthProvider>
        </MemoryRouter>
      );

      // Wait for auth check
      await waitFor(() => {
        expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      });

      // Should show protected content
      expect(screen.getByTestId('protected-content')).toHaveTextContent('Protected Content');
      expect(screen.queryByTestId('unauthorized')).not.toBeInTheDocument();
    });
  });

  describe('Multi-tab Session Sync', () => {
    it('syncs logout across browser tabs', async () => {
      // Setup authenticated state
      localStorage.setItem('agentc-auth-token', 'shared-token');
      localStorage.setItem('agentc-ui-session-id', 'shared-session');

      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Wait for auth
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Simulate storage event from another tab (logout)
      const storageEvent = new StorageEvent('storage', {
        key: 'agentc-auth-token',
        oldValue: 'shared-token',
        newValue: null,
        storageArea: localStorage
      });

      window.dispatchEvent(storageEvent);

      // Should detect logout and update state
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');
      });

      expect(screen.getByTestId('session-id')).toHaveTextContent('No Session');
    });

    it('syncs login across browser tabs', async () => {
      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Initially not authenticated
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not Authenticated');

      // Simulate storage event from another tab (login)
      localStorage.setItem('agentc-auth-token', 'new-token');
      localStorage.setItem('agentc-ui-session-id', 'new-session');

      const storageEvent = new StorageEvent('storage', {
        key: 'agentc-auth-token',
        oldValue: null,
        newValue: 'new-token',
        storageArea: localStorage
      });

      window.dispatchEvent(storageEvent);

      // Should detect login and update state
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      expect(screen.getByTestId('session-id')).toHaveTextContent('new-session');
    });
  });

  describe('Error Recovery', () => {
    it('retries authentication check on network recovery', async () => {
      let attemptCount = 0;
      
      // Mock intermittent network failure
      server.use(
        http.get('/api/auth/verify', async () => {
          attemptCount++;
          if (attemptCount < 3) {
            throw new Error('Network error');
          }
          return HttpResponse.json({ valid: true });
        })
      );

      // Setup token but verification will fail initially
      localStorage.setItem('agentc-auth-token', 'retry-token');

      const { container } = render(
        <AuthProvider>
          <AuthTestComponent />
        </AuthProvider>
      );

      // Wait for retries
      await waitFor(() => {
        expect(attemptCount).toBeGreaterThanOrEqual(3);
      }, { timeout: 5000 });

      // Eventually should authenticate
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });
    });

    it('handles concurrent login attempts', async () => {
      const user = userEvent.setup();
      
      // Mock login with delay
      server.use(
        http.post('/api/auth/login', async () => {
          await delay(500);
          return HttpResponse.json({
            agent_c_token: 'concurrent-token',
            ui_session_id: 'concurrent-session'
          });
        })
      );

      const { container } = render(
        <AuthProvider>
          <LoginForm />
          <AuthTestComponent />
        </AuthProvider>
      );

      // Start multiple login attempts
      await user.type(screen.getByTestId('email-input'), 'test@example.com');
      await user.type(screen.getByTestId('password-input'), 'password');
      
      // Click login multiple times quickly
      const loginButton = screen.getByTestId('login-button');
      await user.click(loginButton);
      await user.click(loginButton);
      await user.click(loginButton);

      // Should handle gracefully and only process one login
      await waitFor(() => {
        expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      });

      // Verify only one session established
      expect(screen.getByTestId('session-id')).toHaveTextContent('concurrent-session');
    });
  });
});