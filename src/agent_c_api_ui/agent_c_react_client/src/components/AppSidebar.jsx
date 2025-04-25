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
const AppSidebar = ({ children, defaultOpen = true, collapsible = "icon" }) => {
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
        <Sidebar collapsible={collapsible}>
          <SidebarHeader className="flex items-center justify-start">
            <div className="sidebar-logo flex items-center gap-2">
              <SidebarTrigger />
              <h2 className="text-lg font-semibold sidebar-title">Agent C</h2>
            </div>
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
                      <span className="sidebar-menu-label">{link.label}</span>
                    </SidebarMenuButton>
                  </Link>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>

          <SidebarFooter>
            <Separator className="my-2" />
            <div className="flex items-center justify-between px-2">
              <p className="text-xs text-muted-foreground sidebar-title">Agent C UI</p>
              <div className="theme-toggle-container">
                <ThemeToggle />
              </div>
            </div>
          </SidebarFooter>
        </Sidebar>

        <div className="sidebar-content">
          <MobileFloatingToggle />
          {children}
        </div>
      </div>
    </SidebarProvider>
  );
};

// Mobile-only floating toggle that appears on small screens
const MobileFloatingToggle = () => {
  const { toggleSidebar, isMobile } = useSidebar();
  
  // Only render on mobile devices
  if (!isMobile) return null;
  
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