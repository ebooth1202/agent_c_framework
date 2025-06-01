import React from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { cn } from "@/lib/utils";
import { InfoIcon, AlertTriangleIcon } from "lucide-react";
import CopyButton from './CopyButton';

/**
 * SystemMessage component displays system messages and errors in the chat interface
 * with consistent styling and copy functionality.
 * 
 * @param {Object} props - Component props
 * @param {string} props.content - The message content
 * @param {boolean} [props.isError=false] - Whether this is an error message (legacy)
 * @param {boolean} [props.isCritical=false] - Whether this is a critical error
 * @param {string} [props.severity] - Message severity: 'info', 'warning', or 'error'
 * @param {string} [props.className] - Optional additional class names
 */
const SystemMessage = ({ content, isError = false, isCritical = false, severity, className = '' }) => {
  // Determine message type based on severity or legacy isError prop
  const effectiveSeverity = severity || (isError ? 'error' : 'info');
  const isErrorMessage = effectiveSeverity === 'error';
  const isWarningMessage = effectiveSeverity === 'warning';
  
  // Use Alert for error/warning messages, Card for info messages
  const MessageComponent = (isErrorMessage || isWarningMessage) ? Alert : Card;
  const ContentComponent = (isErrorMessage || isWarningMessage) ? AlertDescription : CardContent;
  const IconComponent = isErrorMessage ? AlertTriangleIcon : InfoIcon;
  
  return (
    <div 
      className={cn("flex justify-start gap-2 group system-message-container system-message-animation", className)}
      role="log"
      aria-label={isErrorMessage ? "Error message" : isWarningMessage ? "Warning message" : "System message"}
    >
      <MessageComponent
        className={cn(
          isErrorMessage 
            ? "max-w-[80%] rounded-2xl shadow-sm border-destructive/50 bg-destructive/10 text-destructive dark:bg-destructive/20" 
            : isWarningMessage
            ? "max-w-[80%] rounded-2xl shadow-sm border-yellow-500/50 bg-yellow-50 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-200"
            : "system-message-normal"
        )}
        variant={isErrorMessage ? "destructive" : "default"}
      >
        <ContentComponent className="flex justify-between items-start gap-4 p-4">
          <div className="flex items-start gap-2">
            <IconComponent 
              className={cn(
                "h-4 w-4 mt-1 flex-shrink-0", 
                isErrorMessage ? "text-destructive" : isWarningMessage ? "text-yellow-600 dark:text-yellow-400" : "text-muted-foreground"
              )}
              aria-hidden="true"
            />
            <div 
              className="flex-1 prose dark:prose-invert"
              role="textbox"
              aria-readonly="true"
            >
              {isErrorMessage ? "Error: " : isWarningMessage ? "Warning: " : ""}{content}
              {isCritical && (
                <div 
                  className="mt-1 text-xs font-medium text-destructive"
                  role="alert"
                >
                  This is a critical error that may require restarting the session.
                </div>
              )}
            </div>
          </div>
          <CopyButton
            content={content}
            tooltipText="Copy message"
            position="left"
            variant={isErrorMessage ? "destructive" : "secondary"}
            size="xs"
            className="mt-1 flex-shrink-0 opacity-0 transition-opacity group-hover:opacity-100"
            aria-label="Copy message to clipboard"
          />
        </ContentComponent>
      </MessageComponent>
    </div>
  );
};

SystemMessage.propTypes = {
  content: PropTypes.string.isRequired,
  isError: PropTypes.bool,
  isCritical: PropTypes.bool,
  severity: PropTypes.oneOf(['info', 'warning', 'error']),
  className: PropTypes.string
};

// Default props are now handled via parameter destructuring with default values

export default SystemMessage;