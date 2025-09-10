/**
 * Verification script for auth persistence
 * Updated for the new simplified authentication flow
 */

import type { LoginResponse } from './auth';
import { Logger } from '@/utils/logger';

export function verifyAuthPersistence() {
  // Check if localStorage is available
  if (typeof window === 'undefined' || !window.localStorage) {
    Logger.error('localStorage is not available');
    return false;
  }

  Logger.info('=== AUTH PERSISTENCE VERIFICATION ===');
  Logger.info('Note: User data now comes from WebSocket, not from login response');

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
  Logger.info('\n📋 Current State:');
  Logger.info('✅ JWT Token:', results.hasToken ? 'Present' : '❌ Missing');
  Logger.info('✅ UI Session ID:', results.hasUiSessionId ? 'Present' : '❌ Missing');

  if (results.hasOldUserData || results.hasOldLoginResponse) {
    Logger.warn('\n⚠️ WARNING: Old auth data found!');
    Logger.warn('The following keys should be removed:');
    if (results.hasOldUserData) {
      Logger.warn('  - agentc-user-data (no longer used)');
    }
    if (results.hasOldLoginResponse) {
      Logger.warn('  - agentc-login-response (no longer used)');
    }
    Logger.warn('\nTo clean up, run: localStorage.removeItem("agentc-user-data"); localStorage.removeItem("agentc-login-response");');
  }

  // Parse and display token payload (without exposing sensitive data)
  if (token) {
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        Logger.info('\n🔐 Token Payload (non-sensitive):');
        Logger.info('  Subject:', payload.sub || 'N/A');
        Logger.info('  Expires:', payload.exp ? new Date(payload.exp * 1000).toLocaleString() : 'N/A');
        
        const now = Math.floor(Date.now() / 1000);
        const timeLeft = payload.exp ? payload.exp - now : 0;
        if (timeLeft > 0) {
          Logger.info('  Time until expiry:', Math.floor(timeLeft / 60), 'minutes');
        } else {
          Logger.warn('  ⚠️ Token has expired!');
        }
      }
    } catch (error) {
      Logger.error('Failed to parse token:', error);
    }
  }

  if (uiSessionId) {
    Logger.info('\n🔗 UI Session ID:', uiSessionId);
    Logger.info('  This is used for WebSocket reconnection');
  }

  Logger.info('\n📌 Important Notes:');
  Logger.info('1. User profile data now comes from the WebSocket chat_user_data event');
  Logger.info('2. The auth context only manages tokens and authentication state');
  Logger.info('3. Use the useUserData() hook to access user profile information');
  Logger.info('4. Login response only contains: agent_c_token, heygen_token, ui_session_id');

  Logger.info('\n=== END VERIFICATION ===');

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