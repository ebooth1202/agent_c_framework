'use client';

import React, { createContext, useContext, useState, useCallback, useEffect, useMemo } from 'react';
import {
  login as authLogin,
  logout as authLogout,
  getToken,
  getCurrentUser,
  getStoredUser,
  isAuthenticated as checkIsAuthenticated,
  type LoginCredentials,
  type LoginResponse,
  type JWTPayload
} from '@/lib/auth';

// Import auth debug utilities (will auto-run diagnostic in dev mode)
import '@/lib/auth-debug';

// DEBUG MODE - Set to true for verbose logging
const DEBUG_AUTH = true;

// Debug logger
const authLog = {
  info: (message: string, data?: any) => {
    if (DEBUG_AUTH) {
      console.log(`[AUTH-CONTEXT] ✅ ${message}`, data || '');
    }
  },
  error: (message: string, error?: any) => {
    console.error(`[AUTH-CONTEXT] ❌ ${message}`, error || '');
  },
  warn: (message: string, data?: any) => {
    console.warn(`[AUTH-CONTEXT] ⚠️ ${message}`, data || '');
  },
  critical: (message: string, data?: any) => {
    console.error(`[AUTH-CONTEXT] 🚨 CRITICAL: ${message}`, data || '');
  },
  debug: (message: string, data?: any) => {
    if (DEBUG_AUTH) {
      console.log(`[AUTH-CONTEXT] 🔍 ${message}`, data || '');
    }
  }
};

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
    authLog.critical('useAuth called outside of AuthProvider!');
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  // Log when components access auth
  if (DEBUG_AUTH) {
    authLog.debug('useAuth accessed:', {
      isAuthenticated: context.isAuthenticated,
      isLoading: context.isLoading,
      hasUser: !!context.user,
      userId: context.user?.id,
      userEmail: context.user?.email,
      userName: context.user?.user_name,
      hasLoginResponse: !!context.loginResponse
    });
    
    // CRITICAL: Alert if user data is missing when authenticated
    if (context.isAuthenticated && !context.user) {
      authLog.critical('USER IS AUTHENTICATED BUT USER OBJECT IS NULL!');
      authLog.critical('This will cause UserDisplay to show fallback values!');
    }
    
    if (context.user && (!context.user.email || !context.user.user_name)) {
      authLog.critical('USER OBJECT EXISTS BUT IS MISSING CRITICAL FIELDS!', {
        user: context.user,
        hasEmail: !!context.user.email,
        hasUserName: !!context.user.user_name,
        hasId: !!context.user.id
      });
    }
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
  
  // Run diagnostic on mount
  useEffect(() => {
    if (DEBUG_AUTH && typeof window !== 'undefined') {
      console.log('%c=== AUTH DIAGNOSTIC ON MOUNT ===', 'color: yellow; font-size: 16px; font-weight: bold');
      console.log('%cChecking localStorage...', 'color: yellow');
      
      const diagnostics = {
        localStorage: {
          'agentc-user-data': localStorage.getItem('agentc-user-data'),
          'agentc-login-response': localStorage.getItem('agentc-login-response'),
          'agentc-auth-token': localStorage.getItem('agentc-auth-token')
        },
        cookies: document.cookie,
        hasToken: !!getToken(),
        isAuthenticatedCheck: checkIsAuthenticated()
      };
      
      console.table(diagnostics.localStorage);
      
      if (diagnostics.localStorage['agentc-user-data']) {
        try {
          const userData = JSON.parse(diagnostics.localStorage['agentc-user-data']);
          console.log('%cStored User Data:', 'color: cyan; font-weight: bold', userData);
        } catch (e) {
          console.error('Failed to parse stored user data:', e);
        }
      } else {
        console.warn('%cNo user data in localStorage', 'color: orange');
      }
      
      if (diagnostics.localStorage['agentc-login-response']) {
        try {
          const loginResp = JSON.parse(diagnostics.localStorage['agentc-login-response']);
          console.log('%cStored Login Response:', 'color: cyan; font-weight: bold', {
            hasToken: !!loginResp.agent_c_token,
            hasUser: !!loginResp.user,
            userEmail: loginResp.user?.email,
            userName: loginResp.user?.user_name
          });
        } catch (e) {
          console.error('Failed to parse stored login response:', e);
        }
      } else {
        console.warn('%cNo login response in localStorage', 'color: orange');
      }
      
      console.log('%cAuth Token Check:', 'color: cyan', {
        hasToken: diagnostics.hasToken,
        isAuthenticated: diagnostics.isAuthenticatedCheck
      });
      
      console.log('%c=== END DIAGNOSTIC ===', 'color: yellow; font-size: 16px; font-weight: bold');
    }
  }, []);

  // Helper to get stored user data
  const getStoredUserData = () => {
    authLog.debug('Getting stored user data from localStorage...');
    try {
      const stored = localStorage.getItem('agentc-user-data');
      authLog.debug('Raw localStorage value for agentc-user-data:', stored);
      
      if (!stored) {
        authLog.warn('No stored user data found in localStorage');
        return null;
      }
      
      const parsed = JSON.parse(stored);
      authLog.info('Successfully retrieved stored user data', {
        userId: parsed?.id,
        userName: parsed?.user_name,
        email: parsed?.email,
        hasRoles: !!parsed?.roles,
        hasGroups: !!parsed?.groups
      });
      return parsed;
    } catch (error) {
      authLog.error('FAILED to parse stored user data', error);
      authLog.critical('localStorage may be corrupted - clearing bad data');
      try {
        localStorage.removeItem('agentc-user-data');
      } catch (e) {
        authLog.error('Failed to clear corrupted data', e);
      }
    }
    return null;
  };

  // Helper to store user data
  const storeUserData = (userData: any) => {
    authLog.info('Storing user data to localStorage', {
      userId: userData?.id,
      userName: userData?.user_name,
      email: userData?.email,
      keys: Object.keys(userData || {})
    });
    
    if (!userData) {
      authLog.critical('Attempted to store NULL/UNDEFINED user data!');
      return;
    }
    
    try {
      const stringified = JSON.stringify(userData);
      authLog.debug('Stringified user data length:', stringified.length);
      localStorage.setItem('agentc-user-data', stringified);
      
      // Verify it was stored
      const verification = localStorage.getItem('agentc-user-data');
      if (verification === stringified) {
        authLog.info('User data successfully stored and verified in localStorage');
      } else {
        authLog.error('User data storage verification FAILED!');
        authLog.debug('Expected:', stringified);
        authLog.debug('Got:', verification);
      }
    } catch (error) {
      authLog.error('FAILED to store user data', error);
      authLog.critical('User data will not persist across refreshes!');
    }
  };

  // Helper to clear stored user data
  const clearStoredUserData = () => {
    authLog.info('Clearing all stored auth data from localStorage');
    try {
      localStorage.removeItem('agentc-user-data');
      localStorage.removeItem('agentc-login-response');
      authLog.info('Successfully cleared auth data from localStorage');
    } catch (error) {
      authLog.error('FAILED to clear stored user data', error);
    }
  };

  // Helper to get stored login response
  const getStoredLoginResponse = (): LoginResponse | null => {
    authLog.debug('Getting stored login response from localStorage...');
    try {
      const stored = localStorage.getItem('agentc-login-response');
      authLog.debug('Raw localStorage value for agentc-login-response:', stored ? `${stored.length} chars` : 'null');
      
      if (!stored) {
        authLog.warn('No stored login response found in localStorage');
        return null;
      }
      
      const parsed = JSON.parse(stored);
      authLog.info('Successfully retrieved stored login response', {
        hasToken: !!parsed?.token,
        hasUiSessionId: !!parsed?.ui_session_id,
        hasUser: !!parsed?.user,
        userEmail: parsed?.user?.email
      });
      return parsed;
    } catch (error) {
      authLog.error('FAILED to parse stored login response', error);
      authLog.critical('Login response may be corrupted - clearing bad data');
      try {
        localStorage.removeItem('agentc-login-response');
      } catch (e) {
        authLog.error('Failed to clear corrupted login response', e);
      }
    }
    return null;
  };

  // Helper to store login response
  const storeLoginResponse = (response: LoginResponse) => {
    authLog.info('Storing login response to localStorage', {
      hasToken: !!response?.agent_c_token,
      hasUiSessionId: !!response?.ui_session_id,
      userEmail: response?.user?.email,
      userName: response?.user?.user_name
    });
    
    if (!response) {
      authLog.critical('Attempted to store NULL/UNDEFINED login response!');
      return;
    }
    
    try {
      const stringified = JSON.stringify(response);
      authLog.debug('Stringified login response length:', stringified.length);
      localStorage.setItem('agentc-login-response', stringified);
      
      // Verify it was stored
      const verification = localStorage.getItem('agentc-login-response');
      if (verification === stringified) {
        authLog.info('Login response successfully stored and verified in localStorage');
      } else {
        authLog.error('Login response storage verification FAILED!');
      }
    } catch (error) {
      authLog.error('FAILED to store login response', error);
      authLog.critical('Login session will not persist across refreshes!');
    }
  };

  // Check authentication status on mount
  useEffect(() => {
    authLog.info('=== AUTH CONTEXT INITIALIZING ===');
    
    const checkAuth = () => {
      authLog.debug('Checking authentication status...');
      
      try {
        // Check if authenticated
        const authenticated = checkIsAuthenticated();
        authLog.info('Authentication check result:', { authenticated });
        
        // Get current token for debugging
        const token = getToken();
        authLog.debug('Current token status:', {
          hasToken: !!token,
          tokenLength: token?.length || 0,
          tokenPreview: token ? `${token.substring(0, 20)}...` : 'none'
        });
        
        setIsAuthenticated(authenticated);
        
        if (authenticated) {
          authLog.info('User is authenticated - retrieving user data...');
          
          // First try to get stored user data and login response
          const storedUser = getStoredUserData();
          const storedResponse = getStoredLoginResponse();
          
          authLog.debug('Retrieved from storage:', {
            hasStoredUser: !!storedUser,
            storedUserId: storedUser?.id,
            storedUserEmail: storedUser?.email,
            hasStoredResponse: !!storedResponse,
            storedResponseEmail: storedResponse?.user?.email
          });
          
          if (storedUser) {
            authLog.info('Using stored user data', {
              userId: storedUser.id,
              email: storedUser.email,
              userName: storedUser.user_name
            });
            setUser(storedUser);
            
            // CRITICAL: Verify user was actually set
            if (!storedUser.id || !storedUser.email) {
              authLog.critical('STORED USER DATA IS INCOMPLETE!', storedUser);
            }
          } else if (storedResponse && storedResponse.user) {
            // CRITICAL FIX: Use user from stored login response, NOT from JWT!
            authLog.warn('No stored user data, but login response exists - extracting user from response');
            
            const userData = {
              id: storedResponse.user.user_id,
              user_id: storedResponse.user.user_id,
              user_name: storedResponse.user.user_name,
              email: storedResponse.user.email,
              first_name: storedResponse.user.first_name,
              last_name: storedResponse.user.last_name,
              is_active: storedResponse.user.is_active,
              roles: storedResponse.user.roles,
              groups: storedResponse.user.groups,
              created_at: storedResponse.user.created_at,
              last_login: storedResponse.user.last_login
            };
            
            authLog.info('Extracted user from login response', {
              userId: userData.id,
              email: userData.email,
              userName: userData.user_name
            });
            
            setUser(userData);
            storeUserData(userData); // Store it for next time
            
            if (!userData.id || !userData.email || !userData.user_name) {
              authLog.critical('USER DATA FROM LOGIN RESPONSE IS INCOMPLETE!', userData);
            }
          } else {
            // LAST RESORT: JWT payload (should rarely happen)
            authLog.critical('NO stored user data AND NO login response - falling back to JWT (VERY LIMITED)!');
            
            const currentUser = getCurrentUser();
            authLog.debug('JWT fallback user (MINIMAL DATA):', currentUser);
            
            if (currentUser) {
              authLog.warn('Using JWT payload for user data - THIS IS NOT IDEAL!');
              authLog.warn('User will see fallback values like "User" and "user@example.com"');
              authLog.warn('User should log in again to get full profile data');
              // DO NOT use this minimal data - it lacks email, user_name, etc.
              // Just set a minimal object to prevent crashes
              setUser({
                id: currentUser.id || currentUser.sub,
                user_id: currentUser.id || currentUser.sub,
                // These will be undefined, causing fallbacks in UI
                user_name: undefined,
                email: undefined,
                first_name: undefined,
                last_name: undefined
              } as any);
            } else {
              authLog.critical('NO USER DATA AVAILABLE AT ALL - Auth is completely broken!');
              authLog.critical('UserDisplay will show fallback values');
            }
          }
          
          // Restore login response if available
          if (storedResponse) {
            authLog.info('Restoring login response from storage');
            setLoginResponse(storedResponse);
          } else {
            authLog.warn('No stored login response - user may need to re-login for full functionality');
          }
        } else {
          authLog.info('User is NOT authenticated - clearing all data');
          setUser(null);
          setLoginResponse(null);
          clearStoredUserData();
        }
      } catch (error) {
        authLog.error('CRITICAL ERROR checking authentication', error);
        authLog.critical('Auth system has failed - resetting to unauthenticated state');
        setIsAuthenticated(false);
        setUser(null);
        setLoginResponse(null);
        clearStoredUserData();
      } finally {
        authLog.info('Auth check complete, setting isLoading to false');
        setIsLoading(false);
        
        // Log final state for debugging
        authLog.debug('Final auth state after check:', {
          isAuthenticated,
          hasUser: !!user,
          userId: user?.id,
          userEmail: user?.email,
          hasLoginResponse: !!loginResponse
        });
      }
    };

    // Initial auth check
    checkAuth();

    // Expose auth state to window for debugging
    if (DEBUG_AUTH && typeof window !== 'undefined') {
      (window as any).__AUTH_STATE__ = {
        getState: () => ({
          isAuthenticated,
          isLoading,
          user,
          loginResponse,
          localStorage: {
            userData: localStorage.getItem('agentc-user-data'),
            loginResponse: localStorage.getItem('agentc-login-response'),
            token: localStorage.getItem('agentc-token')
          }
        }),
        checkAuth,
        clearAll: () => {
          localStorage.clear();
          window.location.reload();
        }
      };
      authLog.info('Debug tools exposed at window.__AUTH_STATE__');
      console.log('%c[AUTH-CONTEXT] Debug tools available:', 'color: cyan; font-weight: bold');
      console.log('%c  window.__AUTH_STATE__.getState() - View current auth state', 'color: cyan');
      console.log('%c  window.__AUTH_STATE__.checkAuth() - Manually trigger auth check', 'color: cyan');
      console.log('%c  window.__AUTH_STATE__.clearAll() - Clear all auth data and reload', 'color: cyan');
    }

    // Check auth status every 30 seconds to handle token expiration
    const interval = setInterval(() => {
      authLog.debug('Running periodic auth check...');
      checkAuth();
    }, 30000);
    
    return () => {
      authLog.debug('Cleaning up auth context interval');
      clearInterval(interval);
    };
  }, []);

  /**
   * Login function
   */
  const login = useCallback(async (credentials: LoginCredentials): Promise<LoginResponse> => {
    authLog.info('=== LOGIN ATTEMPT STARTING ===');
    authLog.debug('Login credentials:', { 
      email: credentials.email,
      hasPassword: !!credentials.password,
      passwordLength: credentials.password?.length 
    });
    
    setIsLoading(true);
    
    try {
      authLog.info('Calling authLogin with credentials...');
      const response = await authLogin(credentials);
      
      authLog.info('LOGIN RESPONSE RECEIVED!', {
        hasToken: !!response?.agent_c_token,
        tokenLength: response?.agent_c_token?.length,
        hasUiSessionId: !!response?.ui_session_id,
        uiSessionId: response?.ui_session_id,
        hasUser: !!response?.user
      });
      
      if (!response) {
        authLog.critical('LOGIN RESPONSE IS NULL/UNDEFINED!');
        throw new Error('Login response is null or undefined');
      }
      
      if (!response.user) {
        authLog.critical('LOGIN RESPONSE HAS NO USER OBJECT!');
        authLog.error('Full response:', response);
        throw new Error('Login response missing user object');
      }
      
      authLog.debug('User object from login response:', response.user);
      
      // Update state with login response data
      authLog.info('Setting login response in state...');
      setLoginResponse(response);
      
      // Store full response for persistence
      authLog.info('Storing login response to localStorage...');
      storeLoginResponse(response);
      
      // Transform user object to match expected structure with all fields
      authLog.info('Transforming user object...');
      const userData = {
        id: response.user.user_id,
        user_id: response.user.user_id,
        user_name: response.user.user_name,
        email: response.user.email,
        first_name: response.user.first_name,
        last_name: response.user.last_name,
        is_active: response.user.is_active,
        roles: response.user.roles,
        groups: response.user.groups,
        created_at: response.user.created_at,
        last_login: response.user.last_login
      };
      
      authLog.info('Transformed user data:', {
        id: userData.id,
        email: userData.email,
        user_name: userData.user_name,
        full_name: `${userData.first_name} ${userData.last_name}`,
        roles_count: userData.roles?.length,
        groups_count: userData.groups?.length
      });
      
      // CRITICAL: Check for missing required fields
      if (!userData.id || !userData.email || !userData.user_name) {
        authLog.critical('USER DATA MISSING REQUIRED FIELDS!', {
          hasId: !!userData.id,
          hasEmail: !!userData.email,
          hasUserName: !!userData.user_name,
          userData
        });
      }
      
      authLog.info('Setting user in state...');
      setUser(userData);
      
      authLog.info('Storing user data to localStorage...');
      storeUserData(userData);
      
      authLog.info('Setting isAuthenticated to true...');
      setIsAuthenticated(true);
      
      // Final verification
      authLog.info('LOGIN SUCCESSFUL!', {
        userId: userData.id,
        email: userData.email,
        userName: userData.user_name
      });
      
      // Verify localStorage was actually written
      const verifyStored = localStorage.getItem('agentc-user-data');
      if (verifyStored) {
        authLog.info('Verified user data in localStorage:', {
          storedDataLength: verifyStored.length,
          preview: verifyStored.substring(0, 100)
        });
      } else {
        authLog.critical('USER DATA NOT IN LOCALSTORAGE AFTER LOGIN!');
      }
      
      return response;
    } catch (error) {
      authLog.error('LOGIN FAILED!', error);
      authLog.critical('Login error details:', {
        message: (error as any)?.message,
        status: (error as any)?.response?.status,
        data: (error as any)?.response?.data
      });
      
      setIsAuthenticated(false);
      setUser(null);
      setLoginResponse(null);
      clearStoredUserData();
      throw error;
    } finally {
      authLog.info('Login attempt complete, setting isLoading to false');
      setIsLoading(false);
    }
  }, []);

  /**
   * Logout function
   */
  const logout = useCallback(() => {
    authLog.info('=== LOGOUT INITIATED ===');
    authLogout();
    setIsAuthenticated(false);
    setUser(null);
    setLoginResponse(null);
    clearStoredUserData();
    authLog.info('Logout complete - all auth data cleared');
  }, []);

  /**
   * Get auth token
   */
  const getAuthToken = useCallback(() => {
    const token = getToken();
    authLog.debug('getAuthToken called:', {
      hasToken: !!token,
      tokenLength: token?.length || 0
    });
    return token;
  }, []);

  /**
   * Get UI session ID from login response
   */
  const getUiSessionId = useCallback(() => {
    const sessionId = loginResponse?.ui_session_id;
    authLog.debug('getUiSessionId called:', {
      hasSessionId: !!sessionId,
      sessionId
    });
    return sessionId;
  }, [loginResponse]);

  /**
   * Context value
   */
  const value = useMemo<AuthContextValue>(() => {
    const contextValue = {
      isAuthenticated,
      isLoading,
      user,
      loginResponse,
      login,
      logout,
      getAuthToken,
      getUiSessionId
    };
    
    // Log context value updates
    if (DEBUG_AUTH) {
      authLog.debug('Auth context value updated:', {
        isAuthenticated,
        isLoading,
        hasUser: !!user,
        userId: user?.id,
        userEmail: user?.email,
        userName: user?.user_name,
        hasLoginResponse: !!loginResponse
      });
      
      // CRITICAL CHECK
      if (isAuthenticated && !isLoading && !user) {
        authLog.critical('CONTEXT VALUE: Authenticated but NO USER OBJECT!');
        authLog.critical('Components will receive null user despite being authenticated!');
      }
    }
    
    return contextValue;
  }, [
    isAuthenticated,
    isLoading,
    user,
    loginResponse,
    login,
    logout,
    getAuthToken,
    getUiSessionId
  ]);

  // Log initial render and re-renders
  useEffect(() => {
    authLog.info('AuthProvider render state:', {
      isAuthenticated,
      isLoading,
      hasUser: !!user,
      userId: user?.id,
      userEmail: user?.email,
      userName: user?.user_name
    });
  }, [isAuthenticated, isLoading, user]);

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// Export types and context for advanced use cases
export { AuthContext };
export type { AuthContextValue, AuthProviderProps };