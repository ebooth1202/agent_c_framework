/**
 * Auth Debug Utilities
 * 
 * This file provides debugging tools for the authentication system.
 * Import and call runAuthDiagnostic() to get a comprehensive report.
 */

import { getToken, getCurrentUser, getStoredUser, isAuthenticated } from './auth';

export interface AuthDiagnosticReport {
  timestamp: string;
  localStorage: {
    userData: any;
    loginResponse: any;
    authToken: string | null;
  };
  cookies: {
    hasAuthToken: boolean;
    authTokenLength: number;
    hasHeyGenToken: boolean;
  };
  authState: {
    isAuthenticated: boolean;
    currentUser: any;
    token: string | null;
  };
  issues: string[];
  recommendations: string[];
}

/**
 * Run a comprehensive auth diagnostic
 */
export function runAuthDiagnostic(): AuthDiagnosticReport {
  console.log('%c=== AUTH DIAGNOSTIC TOOL ===', 'color: cyan; font-size: 16px; font-weight: bold');
  
  const report: AuthDiagnosticReport = {
    timestamp: new Date().toISOString(),
    localStorage: {
      userData: null,
      loginResponse: null,
      authToken: null
    },
    cookies: {
      hasAuthToken: false,
      authTokenLength: 0,
      hasHeyGenToken: false
    },
    authState: {
      isAuthenticated: false,
      currentUser: null,
      token: null
    },
    issues: [],
    recommendations: []
  };

  // Check localStorage
  console.log('%cChecking localStorage...', 'color: yellow');
  
  try {
    const userData = localStorage.getItem('agentc-user-data');
    if (userData) {
      report.localStorage.userData = JSON.parse(userData);
      console.log('✅ User data found in localStorage:', report.localStorage.userData);
    } else {
      report.issues.push('No user data in localStorage');
      console.warn('❌ No user data in localStorage');
    }
  } catch (e) {
    report.issues.push('Failed to parse user data from localStorage');
    console.error('❌ Failed to parse user data:', e);
  }

  try {
    const loginResponse = localStorage.getItem('agentc-login-response');
    if (loginResponse) {
      report.localStorage.loginResponse = JSON.parse(loginResponse);
      console.log('✅ Login response found in localStorage');
    } else {
      report.issues.push('No login response in localStorage');
      console.warn('❌ No login response in localStorage');
    }
  } catch (e) {
    report.issues.push('Failed to parse login response from localStorage');
    console.error('❌ Failed to parse login response:', e);
  }

  // Check auth token in localStorage (backup check)
  const storedToken = localStorage.getItem('agentc-auth-token');
  if (storedToken) {
    report.localStorage.authToken = storedToken;
    console.log('✅ Auth token found in localStorage (backup)');
  }

  // Check cookies
  console.log('%cChecking cookies...', 'color: yellow');
  
  const cookieToken = document.cookie.match(/agentc-auth-token=([^;]+)/)?.[1];
  if (cookieToken) {
    report.cookies.hasAuthToken = true;
    report.cookies.authTokenLength = decodeURIComponent(cookieToken).length;
    console.log('✅ Auth token found in cookies');
  } else {
    report.issues.push('No auth token in cookies');
    console.warn('❌ No auth token in cookies');
  }

  const heygenToken = document.cookie.match(/agentc-heygen-token=([^;]+)/)?.[1];
  if (heygenToken) {
    report.cookies.hasHeyGenToken = true;
    console.log('✅ HeyGen token found in cookies');
  }

  // Check auth state
  console.log('%cChecking auth state...', 'color: yellow');
  
  report.authState.isAuthenticated = isAuthenticated();
  report.authState.currentUser = getCurrentUser();
  report.authState.token = getToken();

  if (report.authState.isAuthenticated) {
    console.log('✅ User is authenticated');
  } else {
    report.issues.push('User is not authenticated');
    console.warn('❌ User is not authenticated');
  }

  if (report.authState.currentUser) {
    console.log('⚠️ Current user from JWT (MINIMAL DATA):', report.authState.currentUser);
    console.warn('%c⚠️ JWT only contains: id, sub, permissions, exp, iat', 'color: orange; font-weight: bold');
    console.warn('%c⚠️ JWT DOES NOT contain: email, user_name, first_name, last_name, roles', 'color: orange; font-weight: bold');
  } else {
    report.issues.push('Cannot get current user from JWT');
    console.warn('❌ Cannot get current user from JWT');
  }
  
  // CRITICAL: Check stored user vs JWT user
  console.log('%c🔍 Comparing JWT user vs Stored user...', 'color: magenta; font-weight: bold');
  const storedUser = getStoredUser();
  
  if (storedUser) {
    console.log('✅ Full user data from storage:', storedUser);
    console.log('%c✅ This is the CORRECT data to use for user profiles!', 'color: green; font-weight: bold');
    
    // Compare with JWT
    if (report.authState.currentUser) {
      console.log('%c📊 Comparison:', 'color: cyan; font-weight: bold');
      console.table({
        'User ID': {
          'JWT': report.authState.currentUser.id || report.authState.currentUser.sub,
          'Stored': storedUser.user_id,
          'Match': (report.authState.currentUser.id || report.authState.currentUser.sub) === storedUser.user_id
        },
        'Email': {
          'JWT': report.authState.currentUser.email || 'NOT IN JWT',
          'Stored': storedUser.email,
          'Match': report.authState.currentUser.email === storedUser.email
        },
        'Username': {
          'JWT': report.authState.currentUser.user_name || 'NOT IN JWT',
          'Stored': storedUser.user_name,
          'Match': report.authState.currentUser.user_name === storedUser.user_name
        },
        'First Name': {
          'JWT': report.authState.currentUser.first_name || 'NOT IN JWT',
          'Stored': storedUser.first_name,
          'Match': report.authState.currentUser.first_name === storedUser.first_name
        },
        'Last Name': {
          'JWT': report.authState.currentUser.last_name || 'NOT IN JWT',
          'Stored': storedUser.last_name,
          'Match': report.authState.currentUser.last_name === storedUser.last_name
        },
        'Roles': {
          'JWT': report.authState.currentUser.permissions?.join(', ') || 'NOT IN JWT',
          'Stored': storedUser.roles?.join(', ') || 'None',
          'Match': false
        }
      });
      
      if (!storedUser.email || !storedUser.user_name) {
        report.issues.push('CRITICAL: Stored user is missing email or username!');
        console.error('%c❌ CRITICAL: Using JWT data would result in fallback UI values!', 'color: red; font-size: 14px; font-weight: bold');
      }
    }
  } else {
    console.error('%c❌ No stored user data found!', 'color: red; font-weight: bold');
    report.issues.push('CRITICAL: No stored user data - app will use JWT minimal data');
    report.recommendations.push('User must log in again to get full profile data');
  }

  // Analysis and recommendations
  console.log('%cAnalyzing issues...', 'color: yellow');

  // Check for data consistency
  if (report.authState.isAuthenticated && !report.localStorage.userData) {
    report.issues.push('CRITICAL: Authenticated but no user data in localStorage');
    report.recommendations.push('User needs to log in again to restore full user data');
  }

  if (report.localStorage.userData && !report.authState.isAuthenticated) {
    report.issues.push('User data exists but not authenticated');
    report.recommendations.push('Token may have expired - user needs to log in again');
  }

  if (report.localStorage.userData && report.localStorage.loginResponse) {
    // Check data consistency
    const userData = report.localStorage.userData;
    const loginUser = report.localStorage.loginResponse.user;
    
    if (loginUser && userData.email !== loginUser.email) {
      report.issues.push('User data email mismatch between stored data and login response');
    }
  }

  // Check for required fields
  if (report.localStorage.userData) {
    const userData = report.localStorage.userData;
    const requiredFields = ['id', 'email', 'user_name'];
    const missingFields = requiredFields.filter(field => !userData[field]);
    
    if (missingFields.length > 0) {
      report.issues.push(`User data missing required fields: ${missingFields.join(', ')}`);
      report.recommendations.push('User needs to log in again to get complete data');
    }
  }

  // Final report
  console.log('%c=== DIAGNOSTIC REPORT ===', 'color: cyan; font-size: 14px; font-weight: bold');
  
  if (report.issues.length === 0) {
    console.log('%c✅ No issues found!', 'color: green; font-size: 14px; font-weight: bold');
  } else {
    console.error('%c❌ Issues found:', 'color: red; font-weight: bold');
    report.issues.forEach(issue => console.error(`  - ${issue}`));
  }

  if (report.recommendations.length > 0) {
    console.log('%c💡 Recommendations:', 'color: yellow; font-weight: bold');
    report.recommendations.forEach(rec => console.log(`  - ${rec}`));
  }

  console.log('%cFull report object:', 'color: gray');
  console.log(report);

  // Expose to window for manual debugging
  if (typeof window !== 'undefined') {
    (window as any).__AUTH_DIAGNOSTIC__ = report;
    console.log('%cReport saved to window.__AUTH_DIAGNOSTIC__', 'color: gray');
  }

  return report;
}

/**
 * Clear all auth data (nuclear option)
 */
export function clearAllAuthData() {
  console.warn('%c⚠️ CLEARING ALL AUTH DATA...', 'color: red; font-size: 16px; font-weight: bold');
  
  // Clear localStorage
  localStorage.removeItem('agentc-user-data');
  localStorage.removeItem('agentc-login-response');
  localStorage.removeItem('agentc-auth-token');
  
  // Clear cookies
  document.cookie = 'agentc-auth-token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; SameSite=strict';
  document.cookie = 'agentc-heygen-token=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT; Secure; SameSite=strict';
  
  console.log('✅ All auth data cleared');
  console.log('Reload the page to reset the app');
}

// Auto-run diagnostic in development
if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
  // Wait a bit for app to initialize
  setTimeout(() => {
    console.log('%c[Auth Debug] Auto-diagnostic will run in 2 seconds...', 'color: gray');
    setTimeout(() => {
      runAuthDiagnostic();
    }, 2000);
  }, 1000);

  // Expose utility functions
  (window as any).__AUTH_DEBUG__ = {
    runDiagnostic: runAuthDiagnostic,
    clearAll: clearAllAuthData,
    getReport: () => (window as any).__AUTH_DIAGNOSTIC__
  };
  
  console.log('%c[Auth Debug] Debug tools available:', 'color: cyan');
  console.log('  window.__AUTH_DEBUG__.runDiagnostic() - Run diagnostic');
  console.log('  window.__AUTH_DEBUG__.clearAll() - Clear all auth data');
  console.log('  window.__AUTH_DEBUG__.getReport() - Get last diagnostic report');
}