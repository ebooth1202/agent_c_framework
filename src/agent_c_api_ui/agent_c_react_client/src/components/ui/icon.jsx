import React from 'react';
import { cn } from "@/lib/utils";

/**
 * Icon component for Font Awesome icons with hover state support
 * 
 * @param {string} icon - Font Awesome icon class (e.g., "fa-regular fa-copy")
 * @param {string} hoverIcon - Optional Font Awesome icon for hover state (e.g., "fa-solid fa-copy")
 * @param {string} size - Icon size (xs, sm, lg, xl, 2x, 3x, etc.)
 * @param {boolean} fixedWidth - Whether the icon should have a fixed width
 * @param {boolean} spin - Whether the icon should have a spinning animation
 * @param {boolean} pulse - Whether the icon should have a pulse animation
 * @param {string} className - Additional CSS classes
 */
export function Icon({
  icon,
  hoverIcon,
  size,
  fixedWidth = false,
  spin = false,
  pulse = false,
  className,
  ...props
}) {
  // Common classes for both base and hover icons
  const commonClasses = cn(
    size && `fa-${size}`,
    fixedWidth && "fa-fw",
    spin && "fa-spin",
    pulse && "fa-pulse"
  );

  // Base icon classes
  const baseIconClass = cn(
    icon,
    commonClasses,
    "icon-base",
    hoverIcon && "has-hover-icon",
    className
  );

  // Hover icon classes if provided
  const hoverIconClass = hoverIcon ? cn(hoverIcon, commonClasses, "icon-hover") : "";

  // Calculate wrapper size class based on icon size
  const wrapperSizeClass = size ? `icon-size-${size}` : "";

  return (
    <span 
      className={cn("icon-wrapper", wrapperSizeClass)} 
      style={{ fontSize: size ? (typeof size === 'number' ? `${size}px` : 'inherit') : 'inherit' }}
      {...props}
    >
      <i className={baseIconClass}></i>
      {hoverIcon && <i className={hoverIconClass}></i>}
    </span>
  );
}