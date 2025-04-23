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
    <div className="flex flex-col">
      <div className="flex justify-start items-start gap-2 group">
        <ModelIcon vendor={vendor} />
        <div
          className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-purple-50 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 mr-12 rounded-bl-sm border border-purple-200 dark:border-purple-700"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          <div className="flex justify-between items-start gap-4">
            <div className="prose dark:prose-invert flex-1">
              <MarkdownMessage content={content} />
              
              {/* Footer with token usage and tool call info */}
              <div className="flex flex-wrap items-center gap-2 mt-2 pt-1 border-t border-purple-100 dark:border-purple-700/50">
                {tokenUsage && <TokenUsageDisplay usage={tokenUsage} />}
                
                {/* Tool call toggle button - only show if there are tool calls */}
                {hasToolCalls && (
                  <div 
                    className="flex items-center gap-1 text-xs py-1 px-2 rounded-full bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 cursor-pointer hover:bg-blue-200 dark:hover:bg-blue-800/50 transition-colors"
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
                <div className="mt-3 pt-2 border-t border-purple-100 dark:border-purple-700/50">
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
              className="mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssistantMessage;