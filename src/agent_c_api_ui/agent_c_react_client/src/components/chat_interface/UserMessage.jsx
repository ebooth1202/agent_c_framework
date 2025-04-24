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
    <div className={cn("user-message-row group", className)}>
      <Card className="user-message-bubble">
        <CardContent className="user-message-content p-0">
          <div className="user-message-body prose dark:prose-invert">
            {isVoiceMessage ? (
              <div className="user-message-voice">
                <Mic className="h-4 w-4 text-white" />
                <span>Voice message</span>
              </div>
            ) : (
              <div className="markdown-user-message">
                <MarkdownMessage content={content} />
              </div>
            )}
            
            {/* Display file attachments if any */}
            {files && files.length > 0 && (
              <div className="user-message-files">
                <div className="user-message-files-text">
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
            className="user-message-copy-button"
          />
        </CardContent>
      </Card>
      <Avatar className="user-message-icon">
        <AvatarFallback>
          <User className="h-4 w-4" />
        </AvatarFallback>
      </Avatar>
    </div>
  );
};

export default UserMessage;