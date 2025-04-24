import React, { useState } from "react";
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

  // Ensure toolCalls is an array and filter out any null values
  const validTools = Array.isArray(toolCalls) ? toolCalls.filter(tool => tool) : [];
  const toolCount = validTools.length;

  if (toolCount === 0) return null;

  return (
    <Card className={cn("tool-call-container", 
      isOpen ? "tool-call-container-expanded" : "tool-call-container-collapsed",
      className
    )}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <div className="tool-call-header">
            <div className="flex items-center gap-3">
              <Wrench className="tool-call-icon" />
              <h4 className="tool-call-title">Tool Calls</h4>
              <Badge variant="secondary" className="tool-call-badge">
                {toolCount}
              </Badge>
            </div>
            <span className="tool-call-expand-icon">{isOpen ? "▲" : "▼"}</span>
          </div>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="tool-call-content space-y-2 p-4">
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

export default ToolCallDisplay;