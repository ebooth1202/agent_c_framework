import React, { useState, useCallback } from 'react';
import { Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

/**
 * A reusable button component for copying content to clipboard
 *
 * @param {Object} props
 * @param {string|Function} props.content - Content to copy or function that returns content
 * @param {string} [props.tooltipText="Copy to clipboard"] - Text to show in tooltip
 * @param {string} [props.successText="Copied!"] - Text to show after successful copy
 * @param {string} [props.className=""] - Additional CSS classes
 * @param {string} [props.position="top"] - Tooltip position
 * @param {string} [props.size="sm"] - Button size
 * @param {string} [props.variant="ghost"] - Button variant
 */
const CopyButton = ({
  content,
  tooltipText = "Copy to clipboard",
  successText = "Copied!",
  className = "",
  position = "top",
  size = "sm",
  variant = "ghost",
}) => {
  const [isCopied, setIsCopied] = useState(false);

  const copyToClipboard = useCallback(async () => {
    try {
      const textToCopy = typeof content === 'function' ? content() : content;

      await navigator.clipboard.writeText(textToCopy);

      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy content:', error);
    }
  }, [content]);

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button
            variant={variant}
            size={size}
            className={`hover:bg-gray-100 transition-colors ${className}`}
            onClick={copyToClipboard}
          >
            {isCopied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
          </Button>
        </TooltipTrigger>
        <TooltipContent side={position}>
          <p>{isCopied ? successText : tooltipText}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

export default CopyButton;