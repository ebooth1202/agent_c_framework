import React from 'react';

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
    <div className={`page-header ${className}`}>
      <div className="page-header-content">
        <div className="page-header-text">
          <h1 className="page-header-title">{title}</h1>
          {description && (
            <p className="page-header-description">{description}</p>
          )}
        </div>
        {actions && (
          <div className="page-header-actions">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};

export default PageHeader;