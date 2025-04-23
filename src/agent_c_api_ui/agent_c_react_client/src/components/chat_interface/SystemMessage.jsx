import React from 'react';
import CopyButton from './CopyButton';

/**
 * SystemMessage component displays system messages and errors in the chat interface
 * with consistent styling and copy functionality.
 * 
 * @param {Object} props - Component props
 * @param {string} props.content - The message content
 * @param {boolean} [props.isError=false] - Whether this is an error message
 * @param {boolean} [props.isCritical=false] - Whether this is a critical error
 */
const SystemMessage = ({ content, isError = false, isCritical = false }) => {
  return (
    <div className="flex justify-start group">
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2 shadow-sm ${
          isError
            ? "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border border-red-300 dark:border-red-800"
            : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600"
        }`}
      >
        <div className="flex justify-between items-start gap-4">
          <div className="prose dark:prose-invert flex-1">
            {isError ? "⛔ Error: " : ""}{content}
            {isCritical && (
              <div className="mt-1 text-xs text-red-500 dark:text-red-400 font-medium">
                This is a critical error that may require restarting the session.
              </div>
            )}
          </div>
          {/* Copy button that appears on hover */}
          <CopyButton
            content={content}
            tooltipText="Copy message"
            position="left"
            variant="ghost"
            size="xs"
            className="mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-gray-500 hover:bg-gray-200"
          />
        </div>
      </div>
    </div>
  );
};

export default SystemMessage;