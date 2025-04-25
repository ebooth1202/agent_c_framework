import React from 'react';
import { Wrench } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
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
 * @param {string} [props.className] - Optional additional class names
 */
const AssistantMessage = ({
  content,
  vendor,
  tokenUsage,
  toolCalls,
  isToolCallsExpanded = false,
  onToggleToolCalls,
  className
}) => {
  const hasToolCalls = toolCalls && toolCalls.length > 0;
  const toolCallCount = hasToolCalls ? toolCalls.length : 0;
  
  return (
    <div className={cn("flex flex-col", className)}>
      <div className="flex items-start gap-2 group">
        <ModelIcon vendor={vendor} />
        
        <Card className="max-w-[80%] rounded-xl shadow-md overflow-hidden border border-border bg-card text-card-foreground">
          <CardContent className="flex justify-between items-start gap-4 p-4">
            <div className="flex-1 prose dark:prose-invert">
              <MarkdownMessage content={content} />
              
              {/* Footer with token usage and tool call info */}
              <div className="flex flex-wrap items-center gap-2 mt-2 pt-1 border-t border-border">
                {tokenUsage && <TokenUsageDisplay usage={tokenUsage} />}
                
                {/* Tool call toggle button - only show if there are tool calls */}
                {hasToolCalls && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-1 text-xs py-1 px-2 rounded-full"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleToolCalls();
                    }}
                  >
                    <Wrench className="h-3 w-3" />
                    <span>Tool Calls {toolCallCount}</span>
                    <span>{isToolCallsExpanded ? "▲" : "▼"}</span>
                  </Button>
                )}
              </div>
              
              {/* Expanded tool calls - only show if expanded */}
              {hasToolCalls && isToolCallsExpanded && (
                <div className="mt-3 pt-2 border-t border-border bg-muted -mx-6 px-6 pb-3 rounded-b-lg">
                  <div className="space-y-2">
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
              className="mt-1 flex-shrink-0 opacity-0 transition-opacity group-hover:opacity-100"
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AssistantMessage;