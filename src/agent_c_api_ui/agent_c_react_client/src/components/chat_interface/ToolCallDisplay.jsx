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
    <div className={`tool-call-container ${isExpanded ? 'tool-call-container-expanded' : 'tool-call-container-collapsed'}`}>
      <div
        className="tool-call-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <Wrench className="tool-call-icon" />
          <h4 className="tool-call-title">Tool Calls</h4>
          <Badge variant="secondary" className="tool-call-badge">
            {toolCount}
          </Badge>
        </div>
        <span className="tool-call-expand-icon">{isExpanded ? "▲" : "▼"}</span>
      </div>

      {isExpanded && (
        <div className="tool-call-content space-y-2">
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