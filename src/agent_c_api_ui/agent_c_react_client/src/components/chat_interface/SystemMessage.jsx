import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { cn } from "@/lib/utils";
import CopyButton from './CopyButton';

/**
 * SystemMessage component displays system messages and errors in the chat interface
 * with consistent styling and copy functionality.
 * 
 * @param {Object} props - Component props
 * @param {string} props.content - The message content
 * @param {boolean} [props.isError=false] - Whether this is an error message
 * @param {boolean} [props.isCritical=false] - Whether this is a critical error
 * @param {string} [props.className] - Optional additional class names
 */
const SystemMessage = ({ content, isError = false, isCritical = false, className }) => {
  // Use Alert for error messages, Card for regular messages
  const MessageComponent = isError ? Alert : Card;
  const ContentComponent = isError ? AlertDescription : CardContent;
  
  return (
    <div className={cn("system-message-row group", className)}>
      <MessageComponent
        className={`system-message-bubble ${
          isError
            ? "system-message-bubble-error"
            : "system-message-bubble-default"
        }`}
        variant={isError ? "destructive" : "transparent"}
      >
        <ContentComponent className="system-message-content p-0">
          <div className="system-message-body prose dark:prose-invert">
            {isError ? "⛔ Error: " : ""}{content}
            {isCritical && (
              <div className="system-message-critical">
                This is a critical error that may require restarting the session.
              </div>
            )}
          </div>
          <CopyButton
            content={content}
            tooltipText="Copy message"
            position="left"
            variant={isError ? "destructive" : "secondary"}
            size="xs"
            className="system-message-copy-button"
          />
        </ContentComponent>
      </MessageComponent>
    </div>
  );
};

export default SystemMessage;