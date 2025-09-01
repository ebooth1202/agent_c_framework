'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthProvider, useAuth } from '@/contexts/auth-context';
import { ClientProvider } from '@/components/providers/client-provider';
import { ChatInterface } from '@/components/chat/chat-interface';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, MessageSquare, Mic, Video } from 'lucide-react';

/**
 * AuthGuard component - Ensures user is authenticated before rendering children
 */
function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoading, user } = useAuth();

  useEffect(() => {
    // Redirect to login if not authenticated after loading
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen space-y-4">
        <div className="space-y-2 text-center">
          <Skeleton className="h-8 w-48 mx-auto" />
          <Skeleton className="h-4 w-36 mx-auto" />
        </div>
        <p className="text-sm text-muted-foreground">
          Verifying authentication...
        </p>
      </div>
    );
  }

  // Don't render children if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Authentication Required</CardTitle>
            <CardDescription>
              Please log in to access the chat interface.
            </CardDescription>
          </CardHeader>
          <div className="p-6 pt-0">
            <Button 
              onClick={() => router.push('/login')}
              className="w-full"
            >
              Go to Login
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // Render children when authenticated
  return <>{children}</>;
}

/**
 * Chat content component - The main chat interface
 */
function ChatContent() {
  const router = useRouter();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleBackToDashboard = () => {
    router.push('/dashboard');
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="icon"
                onClick={handleBackToDashboard}
                title="Back to Dashboard"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-lg font-semibold">Agent C Realtime Chat</h1>
                <p className="text-sm text-muted-foreground">
                  Connected as {user?.name || user?.id || 'User'}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="hidden sm:flex items-center space-x-1 mr-4">
                <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                  <MessageSquare className="h-3 w-3" />
                  <span>Text</span>
                </div>
                <span className="text-muted-foreground mx-2">•</span>
                <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                  <Mic className="h-3 w-3" />
                  <span>Voice</span>
                </div>
                <span className="text-muted-foreground mx-2">•</span>
                <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                  <Video className="h-3 w-3" />
                  <span>Avatar</span>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleLogout}
              >
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main chat area */}
      <main className="flex-1 overflow-hidden">
        <div className="container mx-auto h-full px-4 py-6">
          <ChatInterface 
            className="h-full"
            showViewManager={true}
            showConnectionAlerts={true}
            maxHeight="calc(100vh - 200px)"
            emptyStateComponent={
              <div className="flex flex-col items-center justify-center h-64 text-center space-y-4">
                <div className="p-4 rounded-full bg-primary/10">
                  <MessageSquare className="h-8 w-8 text-primary" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">Start a Conversation</h3>
                  <p className="text-sm text-muted-foreground max-w-sm">
                    Choose your preferred mode below and start chatting with Agent C.
                    You can switch between text, voice, and avatar modes at any time.
                  </p>
                </div>
              </div>
            }
          />
        </div>
      </main>
    </div>
  );
}

/**
 * Main chat page component
 * Integrates authentication, client initialization, and chat interface
 */
export default function ChatPage() {
  return (
    <AuthProvider>
      <AuthGuard>
        <ClientProvider
          apiUrl={process.env.NEXT_PUBLIC_AGENTC_API_URL}
          enableAudio={true}
          enableTurnManagement={true}
          respectTurnState={true}
        >
          <ChatContent />
        </ClientProvider>
      </AuthGuard>
    </AuthProvider>
  );
}