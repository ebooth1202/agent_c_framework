import React, { useState } from "react";
import ToolCallItem from "./ToolCallItem";
import { Wrench } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const ToolCallDisplay = ({ toolCalls }) => {
  const [isExpanded, setIsExpanded] = useState(false); // Default to collapsed

  // Ensure toolCalls is an array and filter out any null values
  const validTools = Array.isArray(toolCalls) ? toolCalls.filter(tool => tool) : [];
  const toolCount = validTools.length;

  if (toolCount === 0) return null;

  return (
    <div className="border rounded-2xl my-2 bg-card shadow-lg overflow-hidden max-w-[80%] ml-8">
      <div
        className="flex items-center justify-between p-4 cursor-pointer bg-blue-100/80 dark:bg-blue-950/30 hover:bg-blue-200/90 dark:hover:bg-blue-900/40 transition-colors rounded-t-2xl"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <Wrench className="h-5 w-5 text-blue-500 dark:text-blue-400" />
          <h4 className="text-blue-700 dark:text-blue-300 font-medium">Tool Calls</h4>
          <Badge variant="secondary" className="bg-blue-200 dark:bg-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300">
            {toolCount}
          </Badge>
        </div>
        <span className="text-blue-500 dark:text-blue-400">{isExpanded ? "▲" : "▼"}</span>
      </div>

      {isExpanded && (
        <div className="p-4 space-y-2 rounded-b-2xl bg-card">
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
        </div>
      )}
    </div>
  );
};

export default ToolCallDisplay;