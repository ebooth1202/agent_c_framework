import React, { useState } from "react";
import PropTypes from "prop-types";
import ToolCallItem from "./ToolCallItem";
import { Wrench } from "lucide-react";
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/**
 * ToolCallDisplay component displays tool calls made by the AI, with a collapsible
 * interface to show multiple ToolCallItem components.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.toolCalls - Array of tool call objects to display
 * @param {string} [props.className] - Optional additional class names
 */
const ToolCallDisplay = ({ toolCalls, className }) => {
  const [isOpen, setIsOpen] = useState(false); // Default to collapsed

  // Ensure toolCalls is an array, filter out any null values and 'think' tool calls
  const validTools = Array.isArray(toolCalls) 
    ? toolCalls.filter(tool => 
        tool && 
        tool.name !== 'think' && 
        tool.function?.name !== 'think'
      ) 
    : [];
  const toolCount = validTools.length;

  if (toolCount === 0) return null;

  return (
    <Card 
      className={cn(
        "tool-call-display",
        "border border-muted overflow-hidden",
        isOpen ? "max-w-[50%]" : "w-fit",
        "my-2 ml-8 shadow-lg",
        className
      )}
      role="region"
      aria-label="Tool calls"
    >
      <Collapsible 
        open={isOpen} 
        onOpenChange={setIsOpen}
      >
        <CollapsibleTrigger asChild>
          <div 
            className={cn(
              "tool-call-header",
              "flex items-center justify-between p-4 cursor-pointer",
              "bg-muted/50 hover:bg-muted/80 transition-colors",
              "rounded-t-xl"
            )}
            aria-expanded={isOpen}
            aria-controls="tool-call-content"
          >
            <div className="flex items-center gap-3">
              <Wrench className="h-5 w-5 text-primary" aria-hidden="true" />
              <h4 className="text-foreground font-medium">Tool Calls</h4>
              <Badge variant="outline" className="bg-muted/80 text-foreground border border-border">
                {toolCount}
              </Badge>
            </div>
            <span className="text-primary" aria-hidden="true">
              {isOpen ? "▲" : "▼"}
            </span>
          </div>
        </CollapsibleTrigger>

        <CollapsibleContent id="tool-call-content">
          <CardContent className="tool-call-content p-4 space-y-2 bg-card">
            {validTools.map((toolCall, idx) => (
              <ToolCallItem
                key={toolCall.id || idx}
                tool={{
                  name: toolCall.name || toolCall.function?.name,
                  arguments: toolCall.arguments || toolCall.function?.arguments,
                  id: toolCall.id || toolCall.tool_call_id
                }}
                results={toolCall.results}
              />
            ))}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};

ToolCallDisplay.propTypes = {
  toolCalls: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      tool_call_id: PropTypes.string,
      name: PropTypes.string,
      function: PropTypes.shape({
        name: PropTypes.string,
        arguments: PropTypes.oneOfType([PropTypes.string, PropTypes.object])
      }),
      arguments: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
      results: PropTypes.any
    })
  ),
  className: PropTypes.string
};

export default ToolCallDisplay;