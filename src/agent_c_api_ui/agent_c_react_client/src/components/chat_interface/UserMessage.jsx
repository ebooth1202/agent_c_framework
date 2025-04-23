import React from 'react';
import { User, Mic, FileIcon } from 'lucide-react';
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
 */
const UserMessage = ({ content, files, isVoiceMessage }) => {
  return (
    <div className="user-message-row group">
      <div className="user-message-bubble">
        <div className="user-message-content">
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
        </div>
      </div>
      <User className="user-message-icon" />
    </div>
  );
};

export default UserMessage;