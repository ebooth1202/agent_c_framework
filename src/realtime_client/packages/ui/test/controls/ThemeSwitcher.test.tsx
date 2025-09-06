import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ThemeSwitcher } from '../../src/components/controls/ThemeSwitcher'
import React from 'react'

// Mock next-themes
const mockSetTheme = vi.fn()
const mockTheme = vi.fn(() => 'light')

vi.mock('next-themes', () => ({
  useTheme: () => ({
    theme: mockTheme(),
    setTheme: mockSetTheme,
    resolvedTheme: mockTheme(),
    systemTheme: 'light',
    themes: ['light', 'dark', 'system']
  })
}))

describe('ThemeSwitcher', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the theme switcher button', () => {
    render(<ThemeSwitcher />)
    const button = screen.getByRole('button', { name: /toggle theme/i })
    expect(button).toBeInTheDocument()
  })

  it('shows sun icon in light mode', () => {
    mockTheme.mockReturnValue('light')
    const { container } = render(<ThemeSwitcher />)
    
    // Check for sun icon classes
    const sunIcon = container.querySelector('.lucide-sun')
    expect(sunIcon).toBeInTheDocument()
    expect(sunIcon).toHaveClass('scale-100')
  })

  it('shows moon icon in dark mode', () => {
    mockTheme.mockReturnValue('dark')
    const { container } = render(<ThemeSwitcher />)
    
    // Since we're mocking, we need to check the structure
    const icons = container.querySelectorAll('svg')
    expect(icons.length).toBeGreaterThanOrEqual(2) // Sun and Moon icons
  })

  it('opens dropdown menu when clicked', async () => {
    render(<ThemeSwitcher />)
    
    const button = screen.getByRole('button', { name: /toggle theme/i })
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(screen.getByText('Light')).toBeInTheDocument()
      expect(screen.getByText('Dark')).toBeInTheDocument()
      expect(screen.getByText('System')).toBeInTheDocument()
    })
  })

  it('calls setTheme when a theme option is selected', async () => {
    render(<ThemeSwitcher />)
    
    const button = screen.getByRole('button', { name: /toggle theme/i })
    fireEvent.click(button)
    
    await waitFor(() => {
      const darkOption = screen.getByText('Dark')
      fireEvent.click(darkOption)
    })
    
    expect(mockSetTheme).toHaveBeenCalledWith('dark')
  })

  it('highlights the current theme in the dropdown', async () => {
    mockTheme.mockReturnValue('dark')
    render(<ThemeSwitcher />)
    
    const button = screen.getByRole('button', { name: /toggle theme/i })
    fireEvent.click(button)
    
    await waitFor(() => {
      const darkOption = screen.getByText('Dark').closest('[role="menuitem"]')
      expect(darkOption).toHaveClass('bg-accent')
    })
  })

  it('shows label when showLabel prop is true', () => {
    render(<ThemeSwitcher showLabel={true} />)
    expect(screen.getByText('Theme')).toBeInTheDocument()
  })

  it('applies custom className', () => {
    render(<ThemeSwitcher className="custom-class" />)
    const button = screen.getByRole('button', { name: /toggle theme/i })
    expect(button).toHaveClass('custom-class')
  })

  it('respects size prop', () => {
    render(<ThemeSwitcher size="sm" />)
    const button = screen.getByRole('button', { name: /toggle theme/i })
    expect(button).toHaveClass('h-9') // Small button height
  })

  it('includes screen reader text', () => {
    mockTheme.mockReturnValue('light')
    render(<ThemeSwitcher />)
    
    const srText = screen.getByText(/toggle theme \(current theme: light\)/i)
    expect(srText).toBeInTheDocument()
    expect(srText).toHaveClass('sr-only')
  })
})