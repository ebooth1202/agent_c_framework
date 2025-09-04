/**
 * Verification script for auth persistence
 * This ensures that full user data is properly stored and retrieved
 */

import type { LoginResponse } from './auth';

export function verifyAuthPersistence() {
  // Check if localStorage is available
  if (typeof window === 'undefined' || !window.localStorage) {
    console.error('localStorage is not available');
    return false;
  }

  // Try to get stored user data
  const storedUserData = localStorage.getItem('agentc-user-data');
  const storedLoginResponse = localStorage.getItem('agentc-login-response');

  if (!storedUserData && !storedLoginResponse) {
    console.log('No stored auth data found (user not logged in)');
    return null;
  }

  try {
    const userData = storedUserData ? JSON.parse(storedUserData) : null;
    const loginResponse = storedLoginResponse ? JSON.parse(storedLoginResponse) as LoginResponse : null;

    console.log('Stored User Data:', userData);
    console.log('Stored Login Response:', loginResponse);

    // Verify user data has all expected fields
    if (userData) {
      const expectedFields = [
        'id',
        'user_id',
        'user_name',
        'email',
        'first_name', 
        'last_name',
        'is_active',
        'roles',
        'groups',
        'created_at',
        'last_login'
      ];

      const missingFields = expectedFields.filter(field => !(field in userData));
      
      if (missingFields.length > 0) {
        console.warn('Missing user fields:', missingFields);
      } else {
        console.log('✓ All user fields present');
      }
    }

    // Verify login response has expected data
    if (loginResponse) {
      const hasAllData = !!(
        loginResponse.agent_c_token &&
        loginResponse.user &&
        loginResponse.agents &&
        loginResponse.avatars &&
        loginResponse.toolsets &&
        loginResponse.voices &&
        loginResponse.ui_session_id
      );

      if (hasAllData) {
        console.log('✓ Complete login response data present');
      } else {
        console.warn('Login response missing some expected data');
      }
    }

    return {
      userData,
      loginResponse,
      isComplete: !!(userData && loginResponse)
    };
  } catch (error) {
    console.error('Error parsing stored auth data:', error);
    return false;
  }
}

// Export for use in browser console
if (typeof window !== 'undefined') {
  (window as any).verifyAuthPersistence = verifyAuthPersistence;
}