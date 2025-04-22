/**
 * Theme handling utilities for the Agent C React client.
 * This file provides functions for managing themes, applying CSS variables, and checking theme state.
 */

// List of available themes
export type ThemeType = 'light' | 'dark' | 'system';

/**
 * Apply the specified theme to the document.
 * @param theme The theme to apply ('light', 'dark', or 'system')
 */
export function applyTheme(theme: ThemeType): void {
  const root = window.document.documentElement;
  
  // Remove both theme classes first
  root.classList.remove('light', 'dark');
  
  // Handle system theme
  if (theme === 'system') {
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    root.classList.add(systemTheme);
    return;
  }
  
  // Apply the specified theme
  root.classList.add(theme);
}

/**
 * Check if the current theme is dark mode.
 * @returns boolean indicating if dark mode is active
 */
export function isDarkMode(): boolean {
  return document.documentElement.classList.contains('dark');
}

/**
 * Get the current theme from local storage or use system default.
 * @returns The current theme setting
 */
export function getStoredTheme(): ThemeType {
  return (localStorage.getItem('theme') as ThemeType) || 'system';
}

/**
 * Store the selected theme in local storage.
 * @param theme The theme to store
 */
export function storeTheme(theme: ThemeType): void {
  localStorage.setItem('theme', theme);
}

/**
 * Set up theme detection for the system theme preference.
 * This will update the theme automatically when the system preference changes.
 */
export function setupThemeDetection(): void {
  // Monitor for system theme changes
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handleChange = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme === 'system') {
      applyTheme('system');
    }
  };
  
  mediaQuery.addEventListener('change', handleChange);
  
  // Apply the initial theme
  applyTheme(getStoredTheme());
  
  return () => {
    mediaQuery.removeEventListener('change', handleChange);
  };
}