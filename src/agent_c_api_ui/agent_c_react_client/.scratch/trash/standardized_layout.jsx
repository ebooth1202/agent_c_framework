import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';

// Import shadcn/ui components
import { ThemeToggle } from './ui/theme-toggle';
import { Button } from './ui/button';
import { Sheet, SheetContent, SheetTrigger } from './ui/sheet';
import { SidebarProvider } from './ui/sidebar';

// Import our standardized AppSidebar
import AppSidebar from './AppSidebar';

/**
 * Main application layout with responsive sidebar and header
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Page content
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} Layout component
 */
const Layout = ({ children, className }) => {
  const location = useLocation();
  const [open, setOpen] = React.useState(false);
  
  // Navigation items for both sidebar and mobile nav
  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/chat', label: 'Chat' },
    { path: '/rag', label: 'RAG Admin' },
    { path: '/settings', label: 'Settings' },
    { path: '/interactions', label: 'Sessions' },
  ];

  return (
    <div className={cn('layout-container', className)}>
      {/* Mobile Navigation */}
      <Sheet open={open} onOpenChange={setOpen}>
        <header className="layout-header">
          <div className="layout-header-content">
            <div className="layout-title-container">
              <h1 className="layout-title">Agent C Conversational Interface</h1>
            </div>
            <div className="layout-controls">
              <ThemeToggle />
              
              {/* Desktop Navigation */}
              <nav className="layout-nav">
                {navItems.map((item, index) => (
                  <Link key={index} to={item.path}>
                    <Button 
                      variant={location.pathname === item.path ? "default" : "ghost"} 
                      className={cn("layout-nav-button", index > 0 && "ml-2")}
                    >
                      {item.label}
                    </Button>
                  </Link>
                ))}
              </nav>
              
              {/* Mobile Menu Trigger */}
              <SheetTrigger asChild className="layout-mobile-trigger">
                <Button variant="ghost" size="icon" aria-label="Menu">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
            </div>
          </div>
        </header>
        
        {/* Mobile Sidebar */}
        <SheetContent side="left" className="p-0 w-64">
          <AppSidebar 
            items={navItems} 
            title="Navigation"
            footer={<div className="text-center">© 2025 Agent C</div>}
          />
        </SheetContent>
      </Sheet>
      
      {/* Main Content Area */}
      <main className="layout-main">
        {children}
      </main>
    </div>
  );
};

export default Layout;