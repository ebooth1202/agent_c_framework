import React from 'react';
import { cn } from '@/lib/utils';

/**
 * Reusable page header component
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Page title
 * @param {React.ReactNode} [props.children] - Optional action elements
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} Page header component
 */
const PageHeader = ({
  title,
  children,
  className,
}) => {
  return (
    <div className={cn("page-header", className)}>
      <div className="flex items-center justify-between w-full h-full px-4">
        <h1 className="text-xl font-semibold">{title}</h1>
        {children && (
          <div className="flex items-center gap-2">
            {children}
          </div>
        )}
      </div>
    </div>
  );
};

export default PageHeader;