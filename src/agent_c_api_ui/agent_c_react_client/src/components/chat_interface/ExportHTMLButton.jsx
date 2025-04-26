import React, { useCallback } from 'react';
import PropTypes from 'prop-types';
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { formatChatAsHTML } from '@/components/chat_interface/utils/htmlChatFormatter';

/**
 * A button component that exports chat conversations as HTML files
 *
 * @param {Object} props
 * @param {Array} props.messages - The chat messages to export
 * @param {string} [props.tooltipText="Export as HTML"] - Text to show in tooltip
 * @param {string} [props.filename="chat-export.html"] - Default filename for export
 * @param {string} [props.className=""] - Additional CSS classes
 * @param {string} [props.position="top"] - Tooltip position (top, bottom, left, right)
 * @param {string} [props.size="sm"] - Button size (sm, md, lg)
 * @param {string} [props.variant="ghost"] - Button variant (primary, secondary, ghost, etc.)
 * @param {boolean} [props.iconOnly=false] - Whether to show only the icon without text
 * @param {React.ReactNode} [props.icon] - Custom icon to use instead of default Download icon
 * @param {boolean} [props.disabled=false] - Whether the button is disabled
 */
const ExportHTMLButton = ({
  messages,
  tooltipText = "Export as HTML",
  filename = "chat-export.html",
  className = "",
  position = "top",
  size = "sm",
  variant = "ghost",
  iconOnly = false,
  icon = null,
  disabled = false,
}) => {
  const handleExport = useCallback(() => {
    if (!messages || messages.length === 0) return;

    // Generate HTML content
    const htmlContent = formatChatAsHTML(messages);

    // Create a blob from the HTML content
    const blob = new Blob([htmlContent], { type: 'text/html' });

    // Create a URL for the blob
    const url = URL.createObjectURL(blob);

    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.setAttribute('aria-hidden', 'true');
    document.body.appendChild(link);
    link.click();

    // Clean up
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [messages, filename]);

  // Determine if export is possible
  const isExportPossible = messages && messages.length > 0;
  const exportDisabled = disabled || !isExportPossible;
  
  // Create a more descriptive aria-label based on button state
  const ariaLabel = exportDisabled 
    ? "Export chat as HTML (disabled - no messages to export)" 
    : "Export chat as HTML";
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={variant}
            size={size}
            className={`export-html-btn ${className}`}
            onClick={handleExport}
            disabled={exportDisabled}
            aria-label={ariaLabel}
          >
            <span className="export-html-btn-icon">
              {icon || <Download aria-hidden="true" className="h-4 w-4" />}
            </span>
          </Button>
        </TooltipTrigger>
        <TooltipContent side={position}>
          <p>{tooltipText}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

ExportHTMLButton.propTypes = {
  messages: PropTypes.array.isRequired,
  tooltipText: PropTypes.string,
  filename: PropTypes.string,
  className: PropTypes.string,
  position: PropTypes.oneOf(['top', 'bottom', 'left', 'right']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  variant: PropTypes.string,
  iconOnly: PropTypes.bool,
  icon: PropTypes.node,
  disabled: PropTypes.bool
};

export default ExportHTMLButton;