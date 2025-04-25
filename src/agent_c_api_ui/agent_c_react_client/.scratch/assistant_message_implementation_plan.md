# AssistantMessage Component Standardization Plan

## Component Analysis

### Current Implementation

- The AssistantMessage component already uses several shadcn/ui components:
  - Card, CardContent for message container
  - Button for tool call toggle
- Uses Tailwind CSS classes extensively
- Has proper JSDoc documentation
- Contains integrated ToolCallItem for displaying tool calls
- Overall structure is good, but could use some enhancements

### Opportunities for Improvement

1. **Accessibility**:
   - Add ARIA labels to buttons and interactive elements
   - Improve keyboard navigation

2. **Additional shadcn/ui Components**:
   - Use Tooltip from shadcn/ui instead of custom tooltip
   - Add Separator for visual divisions
   - Use Collapsible for tool calls section

3. **Style Enhancements**:
   - Move some Tailwind classes to CSS variables for consistency
   - Improve hover and focus states
   - Enhance dark mode support

4. **PropTypes Validation**:
   - Add PropTypes validation for runtime type checking

## Implementation Plan

### 1. Component Updates

```jsx
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
```

### 2. CSS Updates

```css
/* ===== COMPONENT: AssistantMessage ===== */
/* Description: Displays messages from the AI assistant with formatting, token usage, and expandable tool calls */

/* AssistantMessage: Wrapper and container */
.assistant-message-wrapper {
  display: flex;
  flex-direction: column;
}

.assistant-message-container {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  position: relative;
}

.assistant-message-container:hover .assistant-message-actions {
  opacity: 1;
}

/* AssistantMessage: Avatar */
.assistant-message-avatar {
  flex-shrink: 0;
}

/* AssistantMessage: Message card */
.assistant-message-card {
  max-width: 80%;
  border-radius: 0.75rem;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  border: 1px solid var(--border);
  background-color: var(--card);
  color: var(--card-foreground);
}

/* AssistantMessage: Content area */
.assistant-message-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
}

.assistant-message-body {
  flex: 1;
  min-width: 0; /* Prevent overflow */
  overflow-wrap: break-word;
}

/* AssistantMessage: Footer section */
.assistant-message-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  padding-top: 0.25rem;
  border-top: 1px solid var(--border);
}

/* AssistantMessage: Tool calls section */
.assistant-message-tool-calls-button {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}

.assistant-message-tool-calls-arrow {
  font-size: 0.625rem;
  margin-left: 0.25rem;
}

.assistant-message-tool-calls-content {
  margin-top: 0.75rem;
}

.assistant-message-tool-calls-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* AssistantMessage: Actions */
.assistant-message-actions {
  margin-top: 0.25rem;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.2s ease;
}

/* Markdown code styling */
.prose .markdown-inline-code {
  background-color: hsl(var(--muted) / 0.5);
  color: var(--foreground);
  font-weight: 600;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
}

@media (max-width: 640px) {
  .assistant-message-card {
    max-width: 90%;
  }
}
```

## Testing Plan

1. **Visual Testing**:
   - Verify appearance in both light and dark modes
   - Test responsiveness on different screen sizes
   - Check hover and focus states for interactive elements

2. **Functional Testing**:
   - Verify tool call expansion/collapse functionality
   - Test copy button functionality
   - Check markdown rendering works correctly

3. **Accessibility Testing**:
   - Verify screen reader compatibility
   - Test keyboard navigation
   - Check color contrast

## Benefits

- **Enhanced User Experience**: Improved visual consistency and interaction patterns
- **Better Accessibility**: Proper ARIA attributes and keyboard navigation
- **Type Safety**: Runtime type checking with PropTypes
- **Maintainability**: Clean code structure and standardized CSS