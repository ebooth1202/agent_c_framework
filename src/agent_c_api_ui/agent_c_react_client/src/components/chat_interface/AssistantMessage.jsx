import React from 'react';
import { Wrench } from 'lucide-react';
import MarkdownMessage from './MarkdownMessage';
import TokenUsageDisplay from './TokenUsageDisplay';
import ModelIcon from './ModelIcon';
import CopyButton from './CopyButton';
import ToolCallItem from './ToolCallItem';

/**
 * AssistantMessage component displays messages from the AI assistant with
 * formatting, token usage, and expandable tool calls.
 * 
 * @param {Object} props - Component props
 * @param {string} props.content - The message content
 * @param {string} [props.vendor] - The AI model vendor
 * @param {Object} [props.tokenUsage] - Token usage information
 * @param {Array} [props.toolCalls] - Tool calls associated with this message
 * @param {boolean} [props.isToolCallsExpanded=false] - Whether tool calls are expanded
 * @param {function} props.onToggleToolCalls - Function to toggle tool call expansion
 */
const AssistantMessage = ({
  content,
  vendor,
  tokenUsage,
  toolCalls,
  isToolCallsExpanded = false,
  onToggleToolCalls
}) => {
  const hasToolCalls = toolCalls && toolCalls.length > 0;
  const toolCallCount = hasToolCalls ? toolCalls.length : 0;
  
  return (
    <div className="assistant-message-container">
      <div className="assistant-message-row group">
        <ModelIcon vendor={vendor} />
        <div className="assistant-message-bubble">
          <div className="assistant-message-content">
            <div className="assistant-message-body prose dark:prose-invert">
              <MarkdownMessage content={content} />
              
              {/* Footer with token usage and tool call info */}
              <div className="assistant-message-footer">
                {tokenUsage && <TokenUsageDisplay usage={tokenUsage} />}
                
                {/* Tool call toggle button - only show if there are tool calls */}
                {hasToolCalls && (
                  <div 
                    className="assistant-message-tool-toggle"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleToolCalls();
                    }}
                  >
                    <Wrench className="h-3 w-3" />
                    <span>Tool Calls {toolCallCount}</span>
                    <span>{isToolCallsExpanded ? "▲" : "▼"}</span>
                  </div>
                )}
              </div>
              
              {/* Expanded tool calls - only show if expanded */}
              {hasToolCalls && isToolCallsExpanded && (
                <div className="assistant-message-tool-calls">
                  <div className="tool-call-content space-y-2">
                    {toolCalls.map((toolCall, toolIdx) => (
                      <ToolCallItem
                        key={toolCall.id || toolIdx}
                        tool={{
                          name: toolCall.name || toolCall.function?.name,
                          arguments: toolCall.arguments || toolCall.function?.arguments,
                          id: toolCall.id || toolCall.tool_call_id
                        }}
                        results={toolCall.results}
                        integrated={true}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
            <CopyButton
              content={content}
              tooltipText="Copy message"
              position="left"
              variant="secondary"
              size="xs"
              className="assistant-message-copy-button"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssistantMessage;