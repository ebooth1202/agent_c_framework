import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Settings, Database, PanelLeft, Menu } from 'lucide-react';
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
  useSidebar,
} from './ui/sidebar';
import { ThemeToggle } from './ui/theme-toggle';
import { Separator } from './ui/separator';
import { cn } from '../lib/utils';

/**
 * Main application sidebar using shadcn/ui Sidebar component
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Content to be displayed alongside the sidebar
 * @param {boolean} [props.defaultOpen=true] - Whether the sidebar is open by default
 * @returns {JSX.Element} AppSidebar component
 */
const AppSidebar = ({ children, defaultOpen = true }) => {
  const location = useLocation();

  // Application navigation links with icons
  const navLinks = [
    { path: '/', label: 'Home', icon: <Home className="mr-2" size={18} /> },
    { path: '/chat', label: 'Chat', icon: <PanelLeft className="mr-2" size={18} /> },
    { path: '/rag', label: 'RAG', icon: <Database className="mr-2" size={18} /> },
    { path: '/settings', label: 'Settings', icon: <Settings className="mr-2" size={18} /> },
  ];

  // Check if a path is the current active route
  const isActive = (path) => location.pathname === path;

  return (
    <SidebarProvider defaultOpen={defaultOpen}>
      <div className="sidebar-layout">
        <Sidebar>
          <SidebarHeader className="flex items-center justify-between">
            <div className="sidebar-logo">
              <h2 className="text-lg font-semibold">Agent C</h2>
              <p className="text-xs text-muted-foreground">React UI</p>
            </div>
            <SidebarTrigger />
          </SidebarHeader>
          
          <SidebarContent>
            <SidebarMenu>
              {navLinks.map((link) => (
                <SidebarMenuItem key={link.path}>
                  <Link to={link.path} className="w-full">
                    <SidebarMenuButton 
                      isActive={isActive(link.path)}
                      tooltip={link.label}
                      className={cn(
                        "w-full justify-start",
                        isActive(link.path) && "font-medium"
                      )}
                    >
                      {link.icon}
                      <span>{link.label}</span>
                    </SidebarMenuButton>
                  </Link>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>

          <SidebarFooter>
            <Separator className="my-2" />
            <div className="flex items-center justify-between px-2">
              <p className="text-xs text-muted-foreground">Agent C UI</p>
              <ThemeToggle />
            </div>
          </SidebarFooter>
        </Sidebar>

        <div className="sidebar-content">
          <FloatingToggle />
          {children}
        </div>
      </div>
    </SidebarProvider>
  );
};

// Separate component for the floating toggle to access useSidebar within SidebarProvider context
const FloatingToggle = () => {
  // Access the sidebar context for the toggle functionality
  const { toggleSidebar } = useSidebar();
  
  return (
    <button
      aria-label="Open Sidebar"
      title="Open Sidebar"
      className="sidebar-floating-toggle"
      onClick={toggleSidebar}
    >
      <Menu size={18} />
    </button>
  );
};

export default AppSidebar;