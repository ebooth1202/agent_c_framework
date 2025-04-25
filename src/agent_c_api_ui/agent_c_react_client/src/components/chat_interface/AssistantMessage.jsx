import React from 'react';
import PropTypes from 'prop-types';
import { Wrench } from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
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
    <div className={cn("assistant-message-wrapper", className)}>
      <div className="assistant-message-container">
        <ModelIcon vendor={vendor} className="assistant-message-avatar" />
        
        <Card className="assistant-message-card">
          <CardContent className="assistant-message-content">
            <div className="assistant-message-body">
              <MarkdownMessage content={content} />
              
              {/* Footer with token usage and tool call info */}
              <div className="assistant-message-footer">
                {tokenUsage && <TokenUsageDisplay usage={tokenUsage} />}
                
                {/* Tool call toggle button - only show if there are tool calls */}
                {hasToolCalls && (
                  <Collapsible
                    open={isToolCallsExpanded}
                    onOpenChange={onToggleToolCalls}
                    className="assistant-message-tool-calls-collapsible"
                  >
                    <CollapsibleTrigger asChild>
                      <Button
                        variant="outline"
                        size="sm"
                        className="assistant-message-tool-calls-button"
                        aria-label={`${isToolCallsExpanded ? 'Hide' : 'Show'} ${toolCallCount} tool call${toolCallCount !== 1 ? 's' : ''}`}
                      >
                        <Wrench className="h-3 w-3" />
                        <span>Tool Calls {toolCallCount}</span>
                        <span className="assistant-message-tool-calls-arrow">
                          {isToolCallsExpanded ? "▲" : "▼"}
                        </span>
                      </Button>
                    </CollapsibleTrigger>
                    
                    <CollapsibleContent className="assistant-message-tool-calls-content">
                      <Separator className="my-2" />
                      <div className="assistant-message-tool-calls-list">
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
                    </CollapsibleContent>
                  </Collapsible>
                )}
              </div>
            </div>
            
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className="assistant-message-actions">
                    <CopyButton
                      content={content}
                      variant="secondary"
                      size="xs"
                      aria-label="Copy message content"
                    />
                  </div>
                </TooltipTrigger>
                <TooltipContent side="left">
                  <p>Copy message</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// PropTypes validation for runtime type checking
AssistantMessage.propTypes = {
  content: PropTypes.string.isRequired,
  vendor: PropTypes.string,
  tokenUsage: PropTypes.object,
  toolCalls: PropTypes.array,
  isToolCallsExpanded: PropTypes.bool,
  onToggleToolCalls: PropTypes.func.isRequired,
  className: PropTypes.string
};

export default AssistantMessage;