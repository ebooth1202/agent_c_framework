/**
 * Set of utility functions to format chat messages as HTML for copying
 */

import ReactDOMServer from 'react-dom/server';
import ReactMarkdown from 'react-markdown';

/**
 * Format a chat message as HTML for clipboard
 * @param {Object} msg - Message object
 * @returns {string} HTML representation of the message
 */
export const formatMessageAsHTML = (msg) => {
  // Base styles for all messages
  const baseStyles = `
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    margin-bottom: 16px;
    max-width: 100%;
    line-height: 1.5;
  `;

  // Common message container
  const messageWrapperStart = (bg, border) => `<div style="${baseStyles} padding: 12px 16px; border-radius: 8px; background-color: ${bg}; border: 1px solid ${border};">`;
  const messageWrapperEnd = `</div>`;

  // User message
  if (msg.role === 'user') {
    return `
      <div style="display: flex; justify-content: flex-end; margin-bottom: 16px;">
        <div style="${baseStyles} background-color: #EBF5FF; border: 1px solid #CCE5FF; padding: 12px 16px; border-radius: 12px; color: #0066CC; max-width: 80%;">
          <strong style="display: block; margin-bottom: 4px; color: #0055AA;">User:</strong>
          ${msg.content}
        </div>
      </div>
    `;
  }

  // Assistant content (markdown)
  if (msg.role === 'assistant' && msg.type === 'content') {
    // Convert markdown to HTML
    const htmlContent = ReactDOMServer.renderToStaticMarkup(
      <ReactMarkdown>{msg.content}</ReactMarkdown>
    );

    return `
      <div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">
        <div style="${baseStyles} background-color: #F9F5FF; border: 1px solid #E9D5FF; padding: 12px 16px; border-radius: 12px; color: #5B21B6; max-width: 80%;">
          <strong style="display: block; margin-bottom: 4px; color: #7E22CE;">Assistant:</strong>
          <div style="font-size: 14px;">${htmlContent}</div>
          ${msg.tokenUsage ? formatTokenUsageHTML(msg.tokenUsage) : ''}
        </div>
      </div>
    `;
  }

  // Tool calls
  if (msg.type === 'tool_calls') {
    return `
      <div style="margin: 16px 0;">
        <div style="border: 1px solid #BFDBFE; border-radius: 8px; overflow: hidden; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
          <div style="background-color: #EFF6FF; padding: 10px 16px; border-bottom: 1px solid #BFDBFE;">
            <strong style="color: #1E40AF;">Tool Calls (${msg.toolCalls.length})</strong>
          </div>
          <div style="padding: 12px 16px;">
            ${msg.toolCalls.map(toolCall => formatToolCallHTML(toolCall)).join('')}
          </div>
        </div>
      </div>
    `;
  }

  // Thinking messages
  if (msg.role === 'assistant' && msg.type === 'thinking') {
    return `
      <div style="margin: 16px 0;">
        <div style="border: 1px solid #FEF3C7; border-radius: 8px; overflow: hidden; background-color: #FFFBEB; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
          <div style="background-color: #FEF3C7; padding: 10px 16px; border-bottom: 1px solid #FEF3C7;">
            <strong style="color: #92400E;">Thinking Process</strong>
          </div>
          <div style="padding: 12px 16px;">
            <pre style="font-family: monospace; white-space: pre-wrap; color: #92400E; margin: 0; font-size: 13px;">${msg.content}</pre>
          </div>
        </div>
      </div>
    `;
  }

  // Media
  if (msg.type === 'media') {
    let mediaContent = '';

    if (msg.contentType === 'image/svg+xml') {
      mediaContent = msg.content;
    } else if (msg.contentType?.startsWith('image/')) {
      mediaContent = `<img src="data:${msg.contentType};base64,${msg.content}" style="max-width: 100%; border-radius: 4px; margin: 8px 0;" />`;
    } else if (msg.contentType === 'text/html') {
      mediaContent = `<div style="border: 1px solid #E5E7EB; padding: 8px; border-radius: 4px; margin: 8px 0;">${msg.content}</div>`;
    }

    return `
      <div style="margin: 16px 0;">
        <div style="border: 1px solid #FEF3C7; border-radius: 8px; overflow: hidden; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
          <div style="background-color: #FFFBEB; padding: 10px 16px; border-bottom: 1px solid #FEF3C7;">
            <strong style="color: #92400E;">Media (${msg.contentType.split('/')[1].toUpperCase()})</strong>
          </div>
          <div style="padding: 12px 16px;">
            ${mediaContent}
          </div>
        </div>
      </div>
    `;
  }

  // System messages
  if (msg.role === 'system') {
    const isError = msg.type === 'error';
    const bgColor = isError ? '#FEE2E2' : '#F3F4F6';
    const borderColor = isError ? '#FECACA' : '#E5E7EB';
    const textColor = isError ? '#B91C1C' : '#4B5563';

    return `
      <div style="margin: 8px 0;">
        <div style="${baseStyles} background-color: ${bgColor}; border: 1px solid ${borderColor}; padding: 8px 12px; border-radius: 6px; color: ${textColor}; font-size: 13px;">
          <strong>${isError ? '🚫 Error: ' : 'System: '}</strong>${msg.content}
        </div>
      </div>
    `;
  }

  return '';
};

/**
 * Format token usage info as HTML
 * @param {Object} usage - Token usage object
 * @returns {string} HTML representation of token usage
 */
const formatTokenUsageHTML = (usage) => {
  return `
    <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #E9D5FF; font-size: 12px; color: #7E22CE;">
      <span style="margin-right: 12px;">Prompt: ${usage.prompt_tokens}</span>
      <span style="margin-right: 12px;">Completion: ${usage.completion_tokens}</span>
      <span>Total: ${usage.total_tokens}</span>
    </div>
  `;
};

/**
 * Format a tool call as HTML
 * @param {Object} toolCall - Tool call object
 * @returns {string} HTML representation of the tool call
 */
const formatToolCallHTML = (toolCall) => {
  const formatArgOrResults = (data) => {
    if (!data) return '';

    try {
      const formatted = typeof data === 'string'
        ? JSON.stringify(JSON.parse(data), null, 2)
        : JSON.stringify(data, null, 2);

      return `<pre style="background-color: #F3F4F6; padding: 8px; border-radius: 4px; overflow-x: auto; font-family: monospace; font-size: 13px; margin: 8px 0;">${formatted}</pre>`;
    } catch (e) {
      return `<pre style="background-color: #F3F4F6; padding: 8px; border-radius: 4px; overflow-x: auto; font-family: monospace; font-size: 13px; margin: 8px 0;">${String(data)}</pre>`;
    }
  };

  return `
    <div style="border: 1px solid #DBEAFE; border-radius: 6px; margin-bottom: 8px; background-color: #F9FAFB; overflow: hidden;">
      <div style="background-color: #EFF6FF; padding: 8px 12px; border-bottom: 1px solid #DBEAFE;">
        <strong style="color: #1E40AF;">${toolCall.name || toolCall.function?.name}</strong>
      </div>
      <div style="padding: 8px 12px;">
        ${toolCall.arguments || toolCall.function?.arguments ? `
          <div style="margin-bottom: 12px;">
            <div style="font-weight: 600; color: #2563EB; margin-bottom: 4px; font-size: 13px;">Arguments:</div>
            ${formatArgOrResults(toolCall.arguments || toolCall.function?.arguments)}
          </div>
        ` : ''}
        
        ${toolCall.results ? `
          <div>
            <div style="font-weight: 600; color: #2563EB; margin-bottom: 4px; font-size: 13px;">Results:</div>
            ${formatArgOrResults(toolCall.results)}
          </div>
        ` : ''}
      </div>
    </div>
  `;
};

/**
 * Format the entire chat as HTML
 * @param {Array<Object>} messages - Array of message objects
 * @returns {string} Complete HTML representation of the chat
 */
export const formatChatAsHTML = (messages) => {
  const chatHTML = messages.map(formatMessageAsHTML).join('');

  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Chat Export</title>
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
          line-height: 1.5;
          color: #374151;
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
        }
        code {
          font-family: Menlo, Monaco, Consolas, 'Courier New', monospace;
          background-color: #F3F4F6;
          padding: 0.2em 0.4em;
          border-radius: 3px;
          font-size: 0.9em;
        }
        pre {
          background-color: #F3F4F6;
          padding: 1em;
          border-radius: 6px;
          overflow-x: auto;
          font-size: 0.9em;
        }
      </style>
    </head>
    <body>
      ${chatHTML}
    </body>
    </html>
  `;
};

/**
 * Create clipboard content for the entire chat
 * @param {Array<Object>} messages - Array of message objects
 * @returns {Object} Object with text and html properties
 */
export const createClipboardContent = (messages) => {
  // Plain text version for fallback
  const textContent = messages.map(msg => {
    if (msg.role === 'user') {
      return `User: ${msg.content}\n`;
    } else if (msg.role === 'assistant' && msg.type === 'content') {
      return `Assistant: ${msg.content}\n`;
    } else if (msg.role === 'assistant' && msg.type === 'thinking') {
      return `Assistant (thinking): ${msg.content}\n`;
    } else if (msg.type === 'tool_calls') {
      let result = `Assistant (tool): Using ${msg.toolCalls.map(t => t.name || t.function?.name).join(', ')}\n`;
      msg.toolCalls.forEach(tool => {
        const toolName = tool.name || tool.function?.name;
        const toolArgs = tool.arguments || tool.function?.arguments;
        if (toolArgs) {
          result += `  ${toolName} Arguments: ${typeof toolArgs === 'string' ? toolArgs : JSON.stringify(toolArgs)}\n`;
        }
        if (tool.results) {
          result += `  ${toolName} Results: ${typeof tool.results === 'string' ? tool.results : JSON.stringify(tool.results)}\n`;
        }
      });
      return result;
    } else if (msg.type === 'media') {
      return `Assistant (media): Shared ${msg.contentType} content\n`;
    } else if (msg.role === 'system') {
      return `System: ${msg.content}\n`;
    }
    return '';
  }).join('\n');

  // HTML version for rich copying
  const htmlContent = formatChatAsHTML(messages);

  return {
    text: textContent,
    html: htmlContent
  };
};