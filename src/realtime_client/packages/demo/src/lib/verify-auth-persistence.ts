/**
 * Verification script for auth persistence
 * Updated for the new simplified authentication flow
 */

import type { LoginResponse } from './auth';

export function verifyAuthPersistence() {
  // Check if localStorage is available
  if (typeof window === 'undefined' || !window.localStorage) {
    console.error('localStorage is not available');
    return false;
  }

  console.log('=== AUTH PERSISTENCE VERIFICATION ===');
  console.log('Note: User data now comes from WebSocket, not from login response');

  // Check for JWT token
  const token = localStorage.getItem('agentc-token');
  const uiSessionId = localStorage.getItem('agentc-ui-session-id');
  
  // These should NO LONGER exist in the new flow
  const oldUserData = localStorage.getItem('agentc-user-data');
  const oldLoginResponse = localStorage.getItem('agentc-login-response');

  const results: any = {
    hasToken: !!token,
    hasUiSessionId: !!uiSessionId,
    // These should be false in the new flow
    hasOldUserData: !!oldUserData,
    hasOldLoginResponse: !!oldLoginResponse
  };

  // Report findings
  console.log('\n📋 Current State:');
  console.log('✅ JWT Token:', results.hasToken ? 'Present' : '❌ Missing');
  console.log('✅ UI Session ID:', results.hasUiSessionId ? 'Present' : '❌ Missing');

  if (results.hasOldUserData || results.hasOldLoginResponse) {
    console.warn('\n⚠️ WARNING: Old auth data found!');
    console.warn('The following keys should be removed:');
    if (results.hasOldUserData) {
      console.warn('  - agentc-user-data (no longer used)');
    }
    if (results.hasOldLoginResponse) {
      console.warn('  - agentc-login-response (no longer used)');
    }
    console.warn('\nTo clean up, run: localStorage.removeItem("agentc-user-data"); localStorage.removeItem("agentc-login-response");');
  }

  // Parse and display token payload (without exposing sensitive data)
  if (token) {
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        console.log('\n🔐 Token Payload (non-sensitive):');
        console.log('  Subject:', payload.sub || 'N/A');
        console.log('  Expires:', payload.exp ? new Date(payload.exp * 1000).toLocaleString() : 'N/A');
        
        const now = Math.floor(Date.now() / 1000);
        const timeLeft = payload.exp ? payload.exp - now : 0;
        if (timeLeft > 0) {
          console.log('  Time until expiry:', Math.floor(timeLeft / 60), 'minutes');
        } else {
          console.warn('  ⚠️ Token has expired!');
        }
      }
    } catch (error) {
      console.error('Failed to parse token:', error);
    }
  }

  if (uiSessionId) {
    console.log('\n🔗 UI Session ID:', uiSessionId);
    console.log('  This is used for WebSocket reconnection');
  }

  console.log('\n📌 Important Notes:');
  console.log('1. User profile data now comes from the WebSocket chat_user_data event');
  console.log('2. The auth context only manages tokens and authentication state');
  console.log('3. Use the useUserData() hook to access user profile information');
  console.log('4. Login response only contains: agent_c_token, heygen_token, ui_session_id');

  console.log('\n=== END VERIFICATION ===');

  return {
    isAuthenticated: results.hasToken,
    hasUiSessionId: results.hasUiSessionId,
    needsCleanup: results.hasOldUserData || results.hasOldLoginResponse
  };
}

// Export for use in browser console
if (typeof window !== 'undefined') {
  (window as any).verifyAuthPersistence = verifyAuthPersistence;
}