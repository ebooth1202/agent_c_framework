'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';
import {
  login as authLogin,
  logout as authLogout,
  getToken,
  getCurrentUser,
  isAuthenticated as checkIsAuthenticated,
  type LoginCredentials,
  type LoginResponse,
  type JWTPayload
} from '@/lib/auth';

/**
 * Authentication context value
 */
interface AuthContextValue {
  // State
  isAuthenticated: boolean;
  isLoading: boolean;
  user: { id: string; [key: string]: any } | null;
  loginResponse: LoginResponse | null;
  
  // Auth functions
  login: (credentials: LoginCredentials) => Promise<LoginResponse>;
  logout: () => void;
  
  // Helper functions
  getAuthToken: () => string | null;
  getUiSessionId: () => string | undefined;
}

/**
 * Auth context
 */
const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Hook to use auth context
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

/**
 * Auth provider props
 */
interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * Auth provider component
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<{ id: string; [key: string]: any } | null>(null);
  const [loginResponse, setLoginResponse] = useState<LoginResponse | null>(null);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = () => {
      try {
        const authenticated = checkIsAuthenticated();
        setIsAuthenticated(authenticated);
        
        if (authenticated) {
          const currentUser = getCurrentUser();
          setUser(currentUser);
        } else {
          setUser(null);
          setLoginResponse(null);
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        setIsAuthenticated(false);
        setUser(null);
        setLoginResponse(null);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();

    // Check auth status every 30 seconds to handle token expiration
    const interval = setInterval(checkAuth, 30000);
    
    return () => clearInterval(interval);
  }, []);

  /**
   * Login function
   */
  const login = useCallback(async (credentials: LoginCredentials): Promise<LoginResponse> => {
    setIsLoading(true);
    try {
      const response = await authLogin(credentials);
      
      // Update state with login response data
      setLoginResponse(response);
      // Transform user object to match expected structure
      setUser({
        id: response.user.user_id,
        ...response.user
      });
      setIsAuthenticated(true);
      
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      setIsAuthenticated(false);
      setUser(null);
      setLoginResponse(null);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Logout function
   */
  const logout = useCallback(() => {
    authLogout();
    setIsAuthenticated(false);
    setUser(null);
    setLoginResponse(null);
  }, []);

  /**
   * Get auth token
   */
  const getAuthToken = useCallback(() => {
    return getToken();
  }, []);

  /**
   * Get UI session ID from login response
   */
  const getUiSessionId = useCallback(() => {
    return loginResponse?.ui_session_id;
  }, [loginResponse]);

  /**
   * Context value
   */
  const value = useMemo<AuthContextValue>(() => ({
    isAuthenticated,
    isLoading,
    user,
    loginResponse,
    login,
    logout,
    getAuthToken,
    getUiSessionId
  }), [
    isAuthenticated,
    isLoading,
    user,
    loginResponse,
    login,
    logout,
    getAuthToken,
    getUiSessionId
  ]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Export types and context for advanced use cases
export { AuthContext };
export type { AuthContextValue, AuthProviderProps };