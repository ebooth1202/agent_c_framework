/**
 * User Profile Client Component
 * Client-side component for displaying user profile information
 */

'use client';

import { useEffect } from 'react';
import { UserInfoDisplay } from '@/components/user-info-display';
import { verifyAuthPersistence } from '@/lib/verify-auth-persistence';
import { AuthProvider } from '@/contexts/auth-context';
import { Logger } from '@/utils/logger';

function UserProfileContent() {
  // Make verification function available in browser console
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).verifyAuthPersistence = verifyAuthPersistence;
      Logger.debug('Auth persistence verification available. Run verifyAuthPersistence() in console.');
    }
  }, []);

  return (
    <div className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold">User Profile</h1>
          <p className="text-muted-foreground mt-2">
            This page demonstrates that full user data is properly persisted and accessible.
          </p>
        </div>
        
        <UserInfoDisplay />
        
        <div className="text-sm text-muted-foreground p-4 bg-muted/50 rounded-lg">
          <p className="font-semibold mb-2">How to verify persistence:</p>
          <ol className="list-decimal list-inside space-y-1">
            <li>Log in to see your full user information displayed above</li>
            <li>Refresh the page - all data should persist</li>
            <li>Open browser DevTools console and run: <code className="bg-background px-1">verifyAuthPersistence()</code></li>
            <li>Check localStorage for &apos;agentc-user-data&apos; and &apos;agentc-login-response&apos; keys</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

export default function UserProfileClient() {
  return (
    <AuthProvider>
      <UserProfileContent />
    </AuthProvider>
  );
}