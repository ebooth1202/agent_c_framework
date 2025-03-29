import React, { useCallback } from 'react';
import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { formatChatAsHTML } from '@/components/chat_interface/utils/htmlChatFormatter';

/**
 * A button to export chat content as an HTML file
 *
 * @param {Object} props
 * @param {Array} props.messages - The chat messages to export
 * @param {string} [props.tooltipText="Export as HTML"] - Text to show in tooltip
 * @param {string} [props.filename="chat-export.html"] - Default filename for export
 * @param {string} [props.className=""] - Additional CSS classes
 * @param {string} [props.position="top"] - Tooltip position
 * @param {string} [props.size="sm"] - Button size
 * @param {string} [props.variant="ghost"] - Button variant
 */
const ExportHTMLButton = ({
  messages,
  tooltipText = "Export as HTML",
  filename = "chat-export.html",
  className = "",
  position = "top",
  size = "sm",
  variant = "ghost",
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
    document.body.appendChild(link);
    link.click();

    // Clean up
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [messages, filename]);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={variant}
            size={size}
            className={`hover:bg-gray-100 transition-colors ${className}`}
            onClick={handleExport}
          >
            <Download className="h-4 w-4" />
          </Button>
        </TooltipTrigger>
        <TooltipContent side={position}>
          <p>{tooltipText}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default ExportHTMLButton;