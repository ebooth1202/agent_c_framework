import React from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * Sidebar navigation item
 * 
 * @typedef {Object} SidebarItem
 * @property {string} path - The URL path
 * @property {string} label - Display label
 * @property {React.ReactNode} [icon] - Optional icon
 * @property {boolean} [disabled] - Whether the item is disabled
 */

/**
 * Sidebar navigation component
 * 
 * @param {Object} props - Component props
 * @param {Array<SidebarItem>} props.items - Navigation items
 * @param {string} [props.title] - Optional sidebar title
 * @param {React.ReactNode} [props.footer] - Optional footer content
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} Sidebar component
 */
const Sidebar = ({
  items,
  title,
  footer,
  className = ''
}) => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path ? 'sidebar-link-active' : 'sidebar-link';
  };

  return (
    <aside className={`sidebar ${className}`}>
      {title && <div className="sidebar-title">{title}</div>}
      
      <nav className="sidebar-nav">
        <ul className="sidebar-nav-list">
          {items.map((item, index) => (
            <li key={index} className="sidebar-nav-item">
              {item.disabled ? (
                <span className="sidebar-link-disabled">
                  {item.icon && <span className="sidebar-link-icon">{item.icon}</span>}
                  {item.label}
                </span>
              ) : (
                <Link to={item.path} className={isActive(item.path)}>
                  {item.icon && <span className="sidebar-link-icon">{item.icon}</span>}
                  {item.label}
                </Link>
              )}
            </li>
          ))}
        </ul>
      </nav>
      
      {footer && <div className="sidebar-footer">{footer}</div>}
    </aside>
  );
};

export default Sidebar;