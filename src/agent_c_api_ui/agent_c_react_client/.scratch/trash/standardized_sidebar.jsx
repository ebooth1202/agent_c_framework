import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';

// Import necessary shadcn/ui components
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
} from '@/components/ui/sidebar';

/**
 * Application sidebar navigation using shadcn/ui components
 * 
 * @param {Object} props - Component props
 * @param {Array<Object>} props.items - Navigation items with path, label, icon, and optional disabled flag
 * @param {string} [props.title] - Optional sidebar title
 * @param {React.ReactNode} [props.footer] - Optional footer content
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} Sidebar component
 */
const AppSidebar = ({
  items,
  title,
  footer,
  className,
}) => {
  const location = useLocation();

  return (
    <Sidebar className={cn('app-sidebar', className)}>
      {title && (
        <SidebarGroup>
          <SidebarGroupLabel className="sidebar-title">
            {title}
          </SidebarGroupLabel>
        </SidebarGroup>
      )}
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item, index) => (
                <SidebarMenuItem key={index}>
                  {item.disabled ? (
                    <div className="sidebar-item-disabled">
                      {item.icon && <span className="sidebar-item-icon">{item.icon}</span>}
                      <span>{item.label}</span>
                    </div>
                  ) : (
                    <SidebarMenuButton 
                      asChild
                      active={location.pathname === item.path}
                    >
                      <Link to={item.path} className="sidebar-item-link">
                        {item.icon && <span className="sidebar-item-icon">{item.icon}</span>}
                        <span>{item.label}</span>
                      </Link>
                    </SidebarMenuButton>
                  )}
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      {footer && (
        <SidebarGroup className="sidebar-footer-container">
          <SidebarGroupContent className="sidebar-footer">
            {footer}
          </SidebarGroupContent>
        </SidebarGroup>
      )}
    </Sidebar>
  );
};

export default AppSidebar;