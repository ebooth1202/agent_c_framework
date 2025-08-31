// API endpoints are now proxied through Next.js API routes for security

/**
 * Authentication credentials for login
 */
export interface LoginCredentials {
  username?: string;
  email?: string;
  password: string;
}

/**
 * Login response from the /api/rt/login endpoint
 */
export interface LoginResponse {
  agent_c_token: string;
  heygen_token: string;
  user: {
    user_id: string;
    user_name: string;
    email: string | null;
    first_name: string | null;
    last_name: string | null;
    is_active: boolean;
    roles: string[];
    groups: string[];
    created_at: string | null;
    last_login: string | null;
  };
  agents: Array<{
    name: string;
    key: string;
    agent_description: string | null;
    category: string[];
  }>;
  avatars: Array<{
    avatar_id: string;
    created_at: number;
    default_voice: string;
    is_public: boolean;
    normal_preview: string;
    pose_name: string;
    status: string;
  }>;
  toolsets: Array<{
    name: string;
    key: string;
    description: string | null;
    category: string[];
  }>;
  voices: Array<{
    voice_id: string;
    vendor: string;
    description: string;
    output_format: string;
  }>;
  ui_session_id: string;
}

/**
 * Decoded JWT token payload
 */
export interface JWTPayload {
  sub: string;
  exp: number;
  iat: number;
  [key: string]: any;
}

/**
 * Auth service configuration
 */
const AUTH_CONFIG = {
  tokenCookieName: 'agentc-auth-token',
  tokenCookieOptions: {
    secure: true, // Always use secure cookies for JWT tokens
    sameSite: 'strict' as const,
    httpOnly: false, // Need to access from JavaScript for API calls
    path: '/',
    maxAge: 60 * 60 * 24 * 7, // 7 days
  },
  apiEndpoints: {
    login: '/api/auth/login',
    session: '/api/auth/session',
  },
};

/**
 * Session information returned from the API
 */
export interface SessionInfo {
  websocketUrl: string;
  user: {
    id: string;
    [key: string]: any;
  };
  expiresAt: number;
}

/**
 * Parse JWT token without verification (client-side only)
 * For actual verification, rely on server-side validation
 */
function parseJWT(token: string): JWTPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }
    
    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded);
  } catch (error) {
    console.error('Failed to parse JWT:', error);
    return null;
  }
}

/**
 * Set a cookie value
 */
function setCookie(name: string, value: string, options = AUTH_CONFIG.tokenCookieOptions) {
  let cookie = `${name}=${encodeURIComponent(value)}`;
  
  if (options.maxAge) {
    cookie += `; Max-Age=${options.maxAge}`;
  }
  
  if (options.path) {
    cookie += `; Path=${options.path}`;
  }
  
  if (options.secure) {
    cookie += '; Secure';
  }
  
  if (options.sameSite) {
    cookie += `; SameSite=${options.sameSite}`;
  }
  
  if (options.httpOnly) {
    // Note: httpOnly cookies cannot be set from JavaScript
    console.warn('httpOnly flag is ignored when setting cookies from JavaScript');
  }
  
  document.cookie = cookie;
}

/**
 * Get a cookie value
 */
function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  
  if (parts.length === 2) {
    const cookieValue = parts.pop()?.split(';').shift();
    return cookieValue ? decodeURIComponent(cookieValue) : null;
  }
  
  return null;
}

/**
 * Delete a cookie
 */
function deleteCookie(name: string, path = '/') {
  document.cookie = `${name}=; Path=${path}; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; SameSite=strict`;
}

/**
 * Login with credentials
 * Calls the Next.js API route that proxies to the Agent C backend
 */
export async function login(credentials: LoginCredentials): Promise<LoginResponse> {
  try {
    const response = await fetch(AUTH_CONFIG.apiEndpoints.login, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || errorData.message || `Login failed: ${response.statusText}`);
    }

    const data: LoginResponse = await response.json();
    
    if (!data.agent_c_token) {
      throw new Error('No agent_c_token received from login endpoint');
    }

    // Store agent_c_token in secure cookie
    setCookie(AUTH_CONFIG.tokenCookieName, data.agent_c_token);

    // Store HeyGen token if provided
    if (data.heygen_token) {
      setCookie('agentc-heygen-token', data.heygen_token, {
        ...AUTH_CONFIG.tokenCookieOptions,
        maxAge: 60 * 60, // 1 hour for HeyGen token
      });
    }

    return data;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
}

/**
 * Logout the current user
 * Logout is handled purely client-side by clearing tokens from cookies
 */
export function logout(): void {
  // Clear all authentication tokens from cookies
  deleteCookie(AUTH_CONFIG.tokenCookieName);
  deleteCookie('agentc-heygen-token');
}

/**
 * Get the current authentication token
 */
export function getToken(): string | null {
  if (typeof window === 'undefined') {
    return null; // Server-side rendering
  }
  
  return getCookie(AUTH_CONFIG.tokenCookieName);
}

/**
 * Get the HeyGen token if available
 */
export function getHeyGenToken(): string | null {
  if (typeof window === 'undefined') {
    return null;
  }
  
  return getCookie('agentc-heygen-token');
}

/**
 * Check if the user is authenticated
 * Validates token existence and expiration
 */
export function isAuthenticated(): boolean {
  const token = getToken();
  
  if (!token) {
    return false;
  }

  // Parse and check token expiration
  const payload = parseJWT(token);
  
  if (!payload || !payload.exp) {
    return false;
  }

  // Check if token is expired (with 30 second buffer)
  const expirationTime = payload.exp * 1000; // Convert to milliseconds
  const currentTime = Date.now();
  const buffer = 30 * 1000; // 30 second buffer
  
  return currentTime < (expirationTime - buffer);
}

/**
 * Get the current user from the JWT token
 */
export function getCurrentUser(): { id: string; [key: string]: any } | null {
  const token = getToken();
  
  if (!token) {
    return null;
  }

  const payload = parseJWT(token);
  
  if (!payload || !payload.sub) {
    return null;
  }

  return {
    id: payload.sub,
    ...payload,
  };
}

/**
 * Create an Authorization header value
 */
export function getAuthHeader(): { Authorization: string } | {} {
  const token = getToken();
  
  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
}

/**
 * Get session information including WebSocket URL
 * Requires a valid authentication token
 */
export async function getSessionInfo(): Promise<SessionInfo> {
  const token = getToken();
  
  if (!token) {
    throw new Error('No authentication token available');
  }

  try {
    const response = await fetch(AUTH_CONFIG.apiEndpoints.session, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `Failed to get session info: ${response.statusText}`);
    }

    const data: SessionInfo = await response.json();
    return data;
  } catch (error) {
    console.error('Get session info error:', error);
    throw error;
  }
}

/**
 * Refresh the token if it's close to expiration
 * Returns true if token was refreshed or is still valid
 */
export async function refreshTokenIfNeeded(): Promise<boolean> {
  const token = getToken();
  
  if (!token) {
    return false;
  }

  const payload = parseJWT(token);
  
  if (!payload || !payload.exp) {
    return false;
  }

  // Check if token expires in less than 5 minutes
  const expirationTime = payload.exp * 1000;
  const currentTime = Date.now();
  const fiveMinutes = 5 * 60 * 1000;
  
  if (currentTime > (expirationTime - fiveMinutes)) {
    // Token is expiring soon, attempt refresh
    // Note: This would require a refresh endpoint which may not exist yet
    // For now, return false to indicate refresh is needed
    console.warn('Token expiring soon, refresh required');
    return false;
  }

  return true;
}