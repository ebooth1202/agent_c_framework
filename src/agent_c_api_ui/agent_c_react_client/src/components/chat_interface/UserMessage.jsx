import React from 'react';
import { User, Mic, FileIcon } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import CopyButton from './CopyButton';
import MarkdownMessage from './MarkdownMessage';

/**
 * UserMessage component displays messages sent by the user in the chat interface
 * with consistent styling and copy functionality.
 * 
 * @param {Object} props - Component props
 * @param {string} props.content - The message content
 * @param {Array} [props.files] - Optional array of file names attached to the message
 * @param {boolean} [props.isVoiceMessage] - Whether this is a voice message
 * @param {string} [props.className] - Optional additional class names
 */
const UserMessage = ({ content, files, isVoiceMessage, className }) => {
  return (
    <div className={cn(
      "flex justify-end items-start gap-2 group", 
      className
    )}>
      <Card className={cn(
        "max-w-[80%] rounded-2xl rounded-br-[0.25rem] p-4",
        "bg-primary text-primary-foreground border border-primary/20",
        "shadow-sm"
      )}>
        <CardContent className="p-0 flex justify-between items-start gap-4">
          <div className="flex-1 prose dark:prose-invert">
            {isVoiceMessage ? (
              <div className="flex items-center gap-2">
                <Mic className="h-4 w-4" />
                <span>Voice message</span>
              </div>
            ) : (
              <div className="markdown-user-message">
                <MarkdownMessage content={content} />
              </div>
            )}
            
            {/* Display file attachments if any */}
            {files && files.length > 0 && (
              <div className="mt-2 pt-1 border-t border-primary/20">
                <div className="text-xs flex items-center gap-1">
                  <FileIcon className="h-3 w-3" />
                  <span>Files: {files.join(', ')}</span>
                </div>
              </div>
            )}
          </div>
          
          {/* Copy button that appears on hover */}
          <CopyButton
            content={content}
            tooltipText="Copy message"
            position="left"
            variant="secondary"
            size="xs"
            className="mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
          />
        </CardContent>
      </Card>
      <Avatar className="h-6 w-6 bg-transparent">
        <AvatarFallback className="bg-transparent">
          <User className="h-4 w-4 text-primary" />
        </AvatarFallback>
      </Avatar>
    </div>
  );
};

export default UserMessage;