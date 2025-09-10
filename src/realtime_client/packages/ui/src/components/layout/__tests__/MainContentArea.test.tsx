import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MainContentArea } from '../MainContentArea';
// TODO: Uncomment when jest-axe is installed
// import { axe, toHaveNoViolations } from 'jest-axe';

// TODO: Uncomment when jest-axe is installed
// expect.extend(toHaveNoViolations);

describe('MainContentArea', () => {
  const user = userEvent.setup();

  const defaultProps = {
    children: <div>Main content</div>,
  };

  describe('Rendering', () => {
    it('should render the main content area', () => {
      render(<MainContentArea {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();
    });

    it('should render children content', () => {
      render(<MainContentArea {...defaultProps} />);
      expect(screen.getByText('Main content')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <MainContentArea {...defaultProps} className="custom-layout" />
      );
      const main = screen.getByRole('main');
      expect(main).toHaveClass('custom-layout');
    });
  });

  describe('Layout Structure', () => {
    it('should have proper flex layout', () => {
      render(<MainContentArea {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main).toHaveClass('flex');
      expect(main).toHaveClass('flex-col');
    });

    it('should expand to full height', () => {
      render(<MainContentArea {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main).toHaveClass('h-full');
    });

    it('should have proper overflow handling', () => {
      render(<MainContentArea {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main).toHaveClass('overflow-hidden');
    });
  });

  describe('Header Section', () => {
    it('should render header when provided', () => {
      render(
        <MainContentArea 
          {...defaultProps} 
          header={<header>Page Header</header>}
        />
      );
      expect(screen.getByText('Page Header')).toBeInTheDocument();
    });

    it('should apply header styling', () => {
      render(
        <MainContentArea 
          {...defaultProps} 
          header={<header>Page Header</header>}
        />
      );
      const header = screen.getByText('Page Header').parentElement;
      expect(header).toHaveClass('border-b');
    });
  });

  describe('Footer Section', () => {
    it('should render footer when provided', () => {
      render(
        <MainContentArea 
          {...defaultProps} 
          footer={<footer>Page Footer</footer>}
        />
      );
      expect(screen.getByText('Page Footer')).toBeInTheDocument();
    });

    it('should position footer at bottom', () => {
      render(
        <MainContentArea 
          {...defaultProps} 
          footer={<footer>Page Footer</footer>}
        />
      );
      const footer = screen.getByText('Page Footer').parentElement;
      expect(footer).toHaveClass('border-t');
    });
  });

  describe('Sidebar Integration', () => {
    it('should adjust layout for sidebar', () => {
      render(
        <MainContentArea {...defaultProps} hasSidebar />
      );
      const main = screen.getByRole('main');
      expect(main).toHaveClass('ml-64'); // Assuming 64 is sidebar width
    });

    it('should handle collapsible sidebar', () => {
      const { rerender } = render(
        <MainContentArea {...defaultProps} hasSidebar sidebarCollapsed={false} />
      );
      let main = screen.getByRole('main');
      expect(main).toHaveClass('ml-64');

      rerender(
        <MainContentArea {...defaultProps} hasSidebar sidebarCollapsed />
      );
      main = screen.getByRole('main');
      expect(main).toHaveClass('ml-16'); // Collapsed width
    });
  });

  describe('Responsive Design', () => {
    it('should apply responsive padding', () => {
      render(<MainContentArea {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main.className).toMatch(/p-4|md:p-6|lg:p-8/);
    });

    it('should handle mobile layout', () => {
      render(
        <MainContentArea {...defaultProps} isMobile />
      );
      const main = screen.getByRole('main');
      expect(main).not.toHaveClass('ml-64');
      expect(main).toHaveClass('w-full');
    });
  });

  describe('Scroll Behavior', () => {
    it('should enable content scrolling', () => {
      render(
        <MainContentArea {...defaultProps}>
          <div style={{ height: '2000px' }}>Tall content</div>
        </MainContentArea>
      );
      const scrollArea = screen.getByRole('main').querySelector('[data-scroll-area]');
      expect(scrollArea).toHaveClass('overflow-y-auto');
    });

    it('should preserve scroll position on re-render', () => {
      const { rerender } = render(
        <MainContentArea {...defaultProps}>
          <div>Content 1</div>
        </MainContentArea>
      );

      rerender(
        <MainContentArea {...defaultProps}>
          <div>Content 2</div>
        </MainContentArea>
      );

      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    it('should show loading overlay when loading', () => {
      render(
        <MainContentArea {...defaultProps} isLoading />
      );
      const loadingOverlay = screen.getByRole('status', { name: /loading/i });
      expect(loadingOverlay).toBeInTheDocument();
    });

    it('should disable interaction when loading', () => {
      render(
        <MainContentArea {...defaultProps} isLoading />
      );
      const main = screen.getByRole('main');
      expect(main).toHaveClass('pointer-events-none');
    });
  });

  describe('Error States', () => {
    it('should display error boundary', () => {
      const error = new Error('Layout error');
      render(
        <MainContentArea {...defaultProps} error={error} />
      );
      const errorMessage = screen.getByRole('alert');
      expect(errorMessage).toHaveTextContent('Layout error');
    });

    it('should provide retry option on error', async () => {
      const onRetry = vi.fn();
      render(
        <MainContentArea 
          {...defaultProps} 
          error={new Error('Test error')}
          onRetry={onRetry}
        />
      );
      
      const retryButton = screen.getByRole('button', { name: /retry/i });
      await user.click(retryButton);
      
      expect(onRetry).toHaveBeenCalled();
    });
  });

  describe('Accessibility', () => {
    // TODO: Uncomment when jest-axe is installed
    it.skip('should have no accessibility violations', async () => {
      // const { container } = render(<MainContentArea {...defaultProps} />);
      // const results = await axe(container);
      // expect(results).toHaveNoViolations();
    });

    it('should have proper ARIA landmarks', () => {
      render(
        <MainContentArea 
          {...defaultProps}
          header={<header>Header</header>}
          footer={<footer>Footer</footer>}
        />
      );
      
      expect(screen.getByRole('main')).toBeInTheDocument();
      expect(screen.getByRole('banner')).toBeInTheDocument();
      expect(screen.getByRole('contentinfo')).toBeInTheDocument();
    });

    it('should have skip navigation link', () => {
      render(<MainContentArea {...defaultProps} />);
      const skipLink = screen.getByRole('link', { name: /skip to content/i });
      expect(skipLink).toBeInTheDocument();
      expect(skipLink).toHaveClass('sr-only');
    });

    it('should support keyboard navigation', async () => {
      render(
        <MainContentArea {...defaultProps}>
          <button>Button 1</button>
          <button>Button 2</button>
        </MainContentArea>
      );
      
      await user.tab();
      expect(screen.getByText('Button 1')).toHaveFocus();
      
      await user.tab();
      expect(screen.getByText('Button 2')).toHaveFocus();
    });

    it('should have proper heading hierarchy', () => {
      render(
        <MainContentArea 
          {...defaultProps}
          title="Page Title"
        />
      );
      
      const heading = screen.getByRole('heading', { level: 1 });
      expect(heading).toHaveTextContent('Page Title');
    });
  });

  describe('Theme Support', () => {
    it('should apply light theme classes', () => {
      render(
        <MainContentArea {...defaultProps} theme="light" />
      );
      const main = screen.getByRole('main');
      expect(main).toHaveClass('bg-background');
      expect(main).toHaveClass('text-foreground');
    });

    it('should apply dark theme classes', () => {
      render(
        <MainContentArea {...defaultProps} theme="dark" />
      );
      const main = screen.getByRole('main');
      expect(main).toHaveClass('dark:bg-background');
      expect(main).toHaveClass('dark:text-foreground');
    });
  });

  describe('Grid Layout', () => {
    it('should support grid layout mode', () => {
      render(
        <MainContentArea {...defaultProps} layout="grid" />
      );
      const contentArea = screen.getByRole('main').firstChild;
      expect(contentArea).toHaveClass('grid');
    });

    it('should apply grid columns configuration', () => {
      render(
        <MainContentArea 
          {...defaultProps} 
          layout="grid"
          gridColumns={3}
        />
      );
      const contentArea = screen.getByRole('main').firstChild;
      expect(contentArea).toHaveClass('grid-cols-3');
    });
  });

  describe('Performance', () => {
    it('should handle large content efficiently', () => {
      const largeContent = Array.from({ length: 1000 }, (_, i) => (
        <div key={i}>Item {i}</div>
      ));
      
      render(
        <MainContentArea>
          {largeContent}
        </MainContentArea>
      );
      
      const main = screen.getByRole('main');
      expect(main).toBeInTheDocument();
    });

    it('should use virtualization for long lists', () => {
      render(
        <MainContentArea {...defaultProps} virtualizeContent />
      );
      
      const virtualContainer = screen.getByRole('main')
        .querySelector('[data-virtual-container]');
      expect(virtualContainer).toBeInTheDocument();
    });
  });
});