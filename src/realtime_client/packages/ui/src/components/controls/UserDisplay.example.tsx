/**
 * UserDisplay Component Examples
 * Demonstrating various configurations and use cases
 */

import React from 'react';
import { UserDisplay, UserAvatar } from './UserDisplay';

// Example 1: Basic compact display
export function CompactUserDisplay() {
  return (
    <UserDisplay variant="compact" />
  );
}

// Example 2: Compact display with menu and connection status
export function CompactWithMenu() {
  const handleLogout = () => {
    console.log('Logout clicked');
    // Handle logout logic
  };

  const handleSettings = () => {
    console.log('Settings clicked');
    // Navigate to settings
  };

  return (
    <UserDisplay 
      variant="compact"
      showMenu
      showConnectionStatus
      onLogout={handleLogout}
      onSettings={handleSettings}
    />
  );
}

// Example 3: Full profile card
export function FullProfileCard() {
  return (
    <UserDisplay 
      variant="full"
      className="max-w-sm"
    />
  );
}

// Example 4: Full profile with menu and custom actions
export function FullProfileWithActions() {
  const customMenuItems = [
    {
      label: 'View Profile',
      icon: <UserIcon className="h-4 w-4" />,
      onClick: () => console.log('View profile'),
    },
    {
      label: 'Switch Account',
      icon: <SwitchIcon className="h-4 w-4" />,
      onClick: () => console.log('Switch account'),
    },
    {
      label: 'Delete Account',
      icon: <TrashIcon className="h-4 w-4" />,
      onClick: () => console.log('Delete account'),
      variant: 'destructive' as const,
    },
  ];

  return (
    <UserDisplay 
      variant="full"
      showMenu
      showConnectionStatus
      customMenuItems={customMenuItems}
      onLogout={() => console.log('Logout')}
      onSettings={() => console.log('Settings')}
      className="max-w-md"
    />
  );
}

// Example 5: Custom avatar URL
export function CustomAvatar() {
  return (
    <UserDisplay 
      variant="compact"
      avatarUrl="https://example.com/user-avatar.jpg"
      avatarSize="lg"
    />
  );
}

// Example 6: Standalone avatar component
export function StandaloneAvatar() {
  return (
    <div className="flex items-center gap-4">
      <UserAvatar size="sm" />
      <UserAvatar size="md" />
      <UserAvatar size="lg" />
      <UserAvatar 
        size="lg" 
        avatarUrl="https://example.com/custom-avatar.jpg" 
      />
    </div>
  );
}

// Example 7: Header integration
export function HeaderUserDisplay() {
  return (
    <header className="flex items-center justify-between px-4 py-2 border-b">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold">My App</h1>
      </div>
      
      <UserDisplay 
        variant="compact"
        showMenu
        showConnectionStatus
        onLogout={() => window.location.href = '/logout'}
        onSettings={() => window.location.href = '/settings'}
      />
    </header>
  );
}

// Example 8: Loading state demo
export function LoadingStateDemo() {
  // This will show loading state until user data is received
  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-medium mb-2">Compact Loading</h3>
        <UserDisplay variant="compact" />
      </div>
      
      <div>
        <h3 className="text-sm font-medium mb-2">Full Loading</h3>
        <UserDisplay variant="full" className="max-w-sm" />
      </div>
    </div>
  );
}

// Helper icons for examples (would normally import from lucide-react)
const UserIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
  </svg>
);

const SwitchIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
  </svg>
);

const TrashIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
);