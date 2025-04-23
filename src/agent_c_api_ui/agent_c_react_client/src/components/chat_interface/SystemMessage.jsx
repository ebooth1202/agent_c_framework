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
    <div className="system-message-row group">
      <div
        className={`system-message-bubble ${
          isError
            ? "system-message-bubble-error"
            : "system-message-bubble-default"
        }`}
      >
        <div className="system-message-content">
          <div className="system-message-body prose dark:prose-invert">
            {isError ? "⛔ Error: " : ""}{content}
            {isCritical && (
              <div className="system-message-critical">
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
            className="system-message-copy-button"
          />
        </div>
      </div>
    </div>
  );
};

export default SystemMessage;