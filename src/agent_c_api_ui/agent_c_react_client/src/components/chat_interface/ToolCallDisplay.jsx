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
    <Card 
      className={cn(
        "border border-muted overflow-hidden",
        isOpen ? "max-w-[50%]" : "w-fit",
        "my-2 ml-8 shadow-lg",
        className
      )}
    >
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <div className={cn(
            "flex items-center justify-between p-4 cursor-pointer",
            "bg-muted/50 hover:bg-muted/80 transition-colors",
            "rounded-t-xl"
          )}>
            <div className="flex items-center gap-3">
              <Wrench className="h-5 w-5 text-primary" />
              <h4 className="text-foreground font-medium">Tool Calls</h4>
              <Badge variant="outline" className="bg-muted/80 text-foreground border border-border">
                {toolCount}
              </Badge>
            </div>
            <span className="text-primary">
              {isOpen ? "▲" : "▼"}
            </span>
          </div>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className="p-4 space-y-2 bg-card">
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