/**
 * Tests for useUserData hook
 * Tests user data management and preferences
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useUserData } from '../useUserData';
import { TestWrapper, createMockClient } from '../../test/utils/react-test-utils';
import React from 'react';

describe('useUserData', () => {
  let mockClient: any;
  let eventHandlers: Map<string, Set<Function>>;

  beforeEach(() => {
    vi.clearAllMocks();
    eventHandlers = new Map();
    
    mockClient = {
      ...createMockClient(),
      getUserData: vi.fn(() => ({
        id: 'user-123',
        name: 'Test User',
        email: 'test@example.com',
        preferences: {
          theme: 'dark',
          language: 'en',
          audioEnabled: true
        },
        metadata: {}
      })),
      updateUserData: vi.fn().mockResolvedValue(undefined),
      updateUserPreferences: vi.fn().mockResolvedValue(undefined),
      on: vi.fn((event: string, handler: Function) => {
        if (!eventHandlers.has(event)) {
          eventHandlers.set(event, new Set());
        }
        eventHandlers.get(event)!.add(handler);
      }),
      off: vi.fn((event: string, handler: Function) => {
        eventHandlers.get(event)?.delete(handler);
      })
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('returns user data', () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.user).toEqual({
        id: 'user-123',
        name: 'Test User',
        email: 'test@example.com',
        preferences: {
          theme: 'dark',
          language: 'en',
          audioEnabled: true
        },
        metadata: {}
      });
      expect(result.current.isLoading).toBe(false);
      expect(result.current.error).toBeNull();
    });

    it('returns null when no user data', () => {
      mockClient.getUserData.mockReturnValue(null);

      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.user).toBeNull();
      expect(result.current.preferences).toEqual({});
    });

    it('provides user preferences separately', () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.preferences).toEqual({
        theme: 'dark',
        language: 'en',
        audioEnabled: true
      });
    });
  });

  describe('User Data Updates', () => {
    it('updates user data', async () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const updates = {
        name: 'Updated Name',
        email: 'updated@example.com'
      };

      await act(async () => {
        await result.current.updateUser(updates);
      });

      expect(mockClient.updateUserData).toHaveBeenCalledWith(updates);
    });

    it('updates user preferences', async () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const preferences = {
        theme: 'light',
        audioEnabled: false
      };

      await act(async () => {
        await result.current.updatePreferences(preferences);
      });

      expect(mockClient.updateUserPreferences).toHaveBeenCalledWith(preferences);
    });

    it('updates single preference', async () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.setPreference('theme', 'light');
      });

      expect(mockClient.updateUserPreferences).toHaveBeenCalledWith({
        theme: 'light'
      });
    });
  });

  describe('Event Handling', () => {
    it('handles user data updated event', async () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const updatedUser = {
        id: 'user-123',
        name: 'New Name',
        email: 'new@example.com',
        preferences: {
          theme: 'light',
          language: 'es',
          audioEnabled: false
        },
        metadata: { updated: true }
      };

      mockClient.getUserData.mockReturnValue(updatedUser);

      act(() => {
        eventHandlers.get('user_data_updated')?.forEach(handler => 
          handler({ user: updatedUser })
        );
      });

      await waitFor(() => {
        expect(result.current.user).toEqual(updatedUser);
        expect(result.current.preferences).toEqual(updatedUser.preferences);
      });
    });

    it('handles preferences updated event', async () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const newPreferences = {
        theme: 'auto',
        language: 'fr',
        audioEnabled: true,
        notifications: true
      };

      mockClient.getUserData.mockReturnValue({
        ...mockClient.getUserData(),
        preferences: newPreferences
      });

      act(() => {
        eventHandlers.get('preferences_updated')?.forEach(handler => 
          handler({ preferences: newPreferences })
        );
      });

      await waitFor(() => {
        expect(result.current.preferences).toEqual(newPreferences);
      });
    });
  });

  describe('Loading States', () => {
    it('shows loading state during update', async () => {
      let resolveUpdate: any;
      mockClient.updateUserData.mockImplementation(() => 
        new Promise(resolve => { resolveUpdate = resolve; })
      );

      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      const updatePromise = act(async () => {
        await result.current.updateUser({ name: 'Loading Test' });
      });

      expect(result.current.isLoading).toBe(true);

      resolveUpdate();
      await updatePromise;

      expect(result.current.isLoading).toBe(false);
    });
  });

  describe('Error Handling', () => {
    it('handles update error', async () => {
      const error = new Error('Update failed');
      mockClient.updateUserData.mockRejectedValue(error);

      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await expect(result.current.updateUser({ name: 'Error Test' }))
          .rejects.toThrow('Update failed');
      });

      expect(result.current.error).toEqual(error);
    });

    it('clears error on successful update', async () => {
      // First cause an error
      mockClient.updateUserData.mockRejectedValueOnce(new Error('First error'));

      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        try {
          await result.current.updateUser({ name: 'Error' });
        } catch (e) {
          // Expected
        }
      });

      expect(result.current.error).toBeDefined();

      // Then successful update
      mockClient.updateUserData.mockResolvedValueOnce(undefined);

      await act(async () => {
        await result.current.updateUser({ name: 'Success' });
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('Preference Helpers', () => {
    it('gets specific preference value', () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.getPreference('theme')).toBe('dark');
      expect(result.current.getPreference('language')).toBe('en');
      expect(result.current.getPreference('nonexistent')).toBeUndefined();
    });

    it('checks if preference exists', () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.hasPreference('theme')).toBe(true);
      expect(result.current.hasPreference('audioEnabled')).toBe(true);
      expect(result.current.hasPreference('nonexistent')).toBe(false);
    });

    it('resets preferences to defaults', async () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await result.current.resetPreferences();
      });

      expect(mockClient.updateUserPreferences).toHaveBeenCalledWith({
        theme: 'system',
        language: 'en',
        audioEnabled: true
      });
    });
  });

  describe('Cleanup', () => {
    it('removes event listeners on unmount', () => {
      const { unmount } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      unmount();

      expect(mockClient.off).toHaveBeenCalledWith('user_data_updated', expect.any(Function));
      expect(mockClient.off).toHaveBeenCalledWith('preferences_updated', expect.any(Function));
    });
  });

  describe('StrictMode Compatibility', () => {
    it('handles double mounting in StrictMode', async () => {
      const StrictModeWrapper = ({ children }: { children: React.ReactNode }) => (
        <React.StrictMode>
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        </React.StrictMode>
      );

      const { result } = renderHook(() => useUserData(), {
        wrapper: StrictModeWrapper
      });

      await act(async () => {
        await result.current.updateUser({ name: 'StrictMode Test' });
      });

      // Should only call once despite double mounting
      expect(mockClient.updateUserData).toHaveBeenCalledTimes(1);
    });
  });

  describe('Edge Cases', () => {
    it('handles missing client', () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={null}>{children}</TestWrapper>
        )
      });

      expect(result.current.user).toBeNull();
      expect(result.current.preferences).toEqual({});
    });

    it('handles empty preferences', () => {
      mockClient.getUserData.mockReturnValue({
        id: 'user-456',
        name: 'No Prefs User',
        email: 'noprefs@example.com',
        preferences: {},
        metadata: {}
      });

      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.preferences).toEqual({});
      expect(result.current.getPreference('theme')).toBeUndefined();
    });

    it('handles rapid updates', async () => {
      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      await act(async () => {
        await Promise.all([
          result.current.updateUser({ name: 'Update 1' }),
          result.current.updateUser({ name: 'Update 2' }),
          result.current.updateUser({ name: 'Update 3' })
        ]);
      });

      expect(mockClient.updateUserData).toHaveBeenCalledTimes(3);
    });

    it('handles partial user data', () => {
      mockClient.getUserData.mockReturnValue({
        id: 'user-partial',
        name: 'Partial User'
        // Missing email, preferences, metadata
      });

      const { result } = renderHook(() => useUserData(), {
        wrapper: ({ children }) => (
          <TestWrapper client={mockClient}>{children}</TestWrapper>
        )
      });

      expect(result.current.user?.id).toBe('user-partial');
      expect(result.current.user?.email).toBeUndefined();
      expect(result.current.preferences).toEqual({});
    });
  });
});