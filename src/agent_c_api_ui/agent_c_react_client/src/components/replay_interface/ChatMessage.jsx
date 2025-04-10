import React from 'react';
import { User } from 'lucide-react';
import ModelIcon from '../chat_interface/ModelIcon';
import MarkdownMessage from '../chat_interface/MarkdownMessage';

/**
 * ChatMessage component for displaying different types of chat messages in the replay interface
 * Now supports dynamic vendor selection for assistant messages and token usage display
 */
const ChatMessage = ({
  role,
  content,
  timestamp,
  streaming,
  className = '',
  isThought = false,
  isSystem = false,
  vendor = 'unknown',
  tokenUsage = null
}) => {
  const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString() : '';

  if (role === 'user') {
    return (
      <div className={`flex justify-end items-start gap-2 group ${className}`}>
        <div className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-blue-500 text-white ml-12 rounded-br-sm relative">
          <div className="markdown-user-message">
            <MarkdownMessage content={content} />
          </div>
          {timestamp && <div className="text-xs opacity-70 mt-1">{formattedTime}</div>}
        </div>
        <User className="h-6 w-6 text-blue-500" />
      </div>
    );
  }

  if (role === 'assistant') {
    // Added support for dynamic vendor and token usage
    return (
      <div className={`flex flex-col ${className}`}>
        <div className="flex justify-start items-start gap-2 group">
          <ModelIcon vendor={vendor} />
          <div className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-purple-50 text-purple-800 mr-12 rounded-bl-sm">
            <MarkdownMessage content={content} />

            {/* Footer with metadata */}
            <div className="flex flex-wrap items-center justify-between mt-2 pt-1 border-t border-purple-100 text-xs text-gray-500">
              <div className="flex items-center">
                {timestamp && <span>{formattedTime}</span>}
                {streaming && <span className="ml-2 text-purple-400 animate-pulse">Streaming...</span>}
              </div>

              {/* Token usage display */}
              {tokenUsage && !streaming && (
                <div className="flex items-center text-xs font-medium mt-1">
                  <div className="flex gap-2">
                    <span className="text-purple-500">
                      🔤 {tokenUsage.prompt_tokens + tokenUsage.completion_tokens} tokens
                    </span>
                    <span className="text-gray-400 text-[10px]">
                      ({tokenUsage.prompt_tokens} prompt / {tokenUsage.completion_tokens} completion)
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  if (role === 'assistant (thought)' || isThought) {
    return (
      <div className={`flex justify-start group ${className}`}>
        <div className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-gray-50 text-gray-800 border border-gray-200">
          <div className="text-xs font-medium text-gray-500 mb-1">Assistant Thinking:</div>
          <div className="whitespace-pre-wrap">{content}</div>
          {timestamp && <div className="text-xs text-gray-500 mt-1">{formattedTime}</div>}
        </div>
      </div>
    );
  }
  
  if (role === 'system' || isSystem) {
    return (
      <div className={`flex justify-center group ${className}`}>
        <div className="max-w-[80%] rounded-xl px-4 py-2 shadow-sm bg-gray-100 text-gray-600 border border-gray-200 text-center">
          <div className="whitespace-pre-wrap">{content}</div>
          {timestamp && <div className="text-xs text-gray-500 mt-1">{formattedTime}</div>}
        </div>
      </div>
    );
  }
  
  // Default case for any other role
  return (
    <div className={`flex justify-start group ${className}`}>
      <div className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-gray-50 border border-gray-200">
        <div className="text-xs font-medium text-gray-500 mb-1">{role}:</div>
        <div className="whitespace-pre-wrap">{content}</div>
        {timestamp && <div className="text-xs text-gray-500 mt-1">{formattedTime}</div>}
      </div>
    </div>
  );
};

export default ChatMessage;