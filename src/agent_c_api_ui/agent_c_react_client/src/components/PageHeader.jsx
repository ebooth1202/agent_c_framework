import React from 'react';
import { Card, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Separator } from './ui/separator';
import { cn } from "@/lib/utils";

/**
 * Reusable page header component
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Page title
 * @param {string} [props.description] - Optional page description
 * @param {React.ReactNode} [props.actions] - Optional action buttons/elements
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} Page header component
 */
const PageHeader = ({
  title,
  description,
  actions,
  className = ''
}) => {
  return (
    <div className={cn("page-header", className)}>
      <Card className="bg-transparent border-0 shadow-none">
        <CardHeader className="p-0 space-y-0">
          <div className="page-header-content">
            <div className="page-header-text">
              <CardTitle className="page-header-title">{title}</CardTitle>
              {description && (
                <CardDescription className="page-header-description">{description}</CardDescription>
              )}
            </div>
            {actions && (
              <div className="page-header-actions">
                {actions}
              </div>
            )}
          </div>
        </CardHeader>
      </Card>
      <Separator className="mt-4" />
    </div>
  );
};

export default PageHeader;