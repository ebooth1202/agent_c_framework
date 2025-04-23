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
    <div className="flex justify-end items-start gap-2 group">
      <div className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-blue-500 text-white ml-12 rounded-br-sm border border-blue-600" style={{ fontFamily: 'Georgia, serif' }}>
        <div className="flex justify-between items-start gap-4">
          <div className="prose dark:prose-invert flex-1">
            {isVoiceMessage ? (
              <div className="flex items-center space-x-2">
                <Mic className="h-4 w-4 text-white" />
                <span className="text-white">Voice message</span>
              </div>
            ) : (
              <div className="markdown-user-message">
                <MarkdownMessage content={content} />
              </div>
            )}
            
            {/* Display file attachments if any */}
            {files && files.length > 0 && (
              <div className="mt-2 pt-1 border-t border-blue-400">
                <div className="text-xs text-blue-100 flex items-center gap-1">
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
            className="mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity bg-blue-600 hover:bg-blue-700 text-white"
          />
        </div>
      </div>
      <User className="h-6 w-6 text-blue-500" />
    </div>
  );
};

export default UserMessage;