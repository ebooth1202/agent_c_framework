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
    <div className={cn("flex justify-start gap-2 group", className)}>
      <MessageComponent
        className={cn(
          "max-w-[80%] rounded-2xl shadow-sm",
          isError 
            ? "border-destructive/50 bg-destructive/10 text-destructive dark:bg-destructive/20" 
            : "bg-background text-foreground border-border"
        )}
        variant={isError ? "destructive" : "default"}
      >
        <ContentComponent className="flex justify-between items-start gap-4 p-4">
          <div className="flex-1 prose dark:prose-invert">
            {isError ? "⛔ Error: " : ""}{content}
            {isCritical && (
              <div className="mt-1 text-xs font-medium text-destructive">
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
            className="mt-1 flex-shrink-0 opacity-0 transition-opacity group-hover:opacity-100"
          />
        </ContentComponent>
      </MessageComponent>
    </div>
  );
};

export default SystemMessage;