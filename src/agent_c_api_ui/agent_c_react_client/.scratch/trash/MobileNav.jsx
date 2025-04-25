import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X } from 'lucide-react';
import { Button } from './ui/button';
// CSS already imported through main.css

/**
 * Mobile navigation component with dropdown menu
 * 
 * @param {Object} props - Component props
 * @param {Array<{path: string, label: string}>} props.links - Navigation links
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} Mobile navigation component
 */
const MobileNav = ({ 
  links,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const toggle = () => setIsOpen(!isOpen);
  const close = () => setIsOpen(false);

  const isActive = (path) => {
    return location.pathname === path ? 'mobile-nav-link-active' : 'mobile-nav-link';
  };

  return (
    <div className={`mobile-nav ${className}`}>
      <Button 
        variant="ghost" 
        size="icon" 
        onClick={toggle}
        className="mobile-nav-toggle"
        aria-label="Toggle menu"
        aria-expanded={isOpen}
      >
        {isOpen ? <X size={20} /> : <Menu size={20} />}
      </Button>
      
      {isOpen && (
        <div className="mobile-nav-dropdown">
          <nav className="mobile-nav-menu">
            {links.map((link, index) => (
              <Link 
                key={index} 
                to={link.path} 
                className={isActive(link.path)}
                onClick={close}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </div>
  );
};

export default MobileNav;