import React, { useState } from 'react';
import { PocketKnife, ChevronDown } from 'lucide-react';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import CopyButton from './CopyButton';

/**
 * Format data (arguments or results) as pretty JSON or string
 * @param {any} data - The data to format
 * @returns {string} - Formatted string representation
 */
function formatData(data) {
  if (!data) return "";

  try {
    if (typeof data === "string") {
      const parsed = JSON.parse(data);
      return JSON.stringify(parsed, null, 2);
    }
    return JSON.stringify(data, null, 2);
  } catch (e) {
    return String(data);
  }
}

/**
 * ToolCallItem component displays individual tool calls with their arguments and results.
 * 
 * @param {Object} props - Component props
 * @param {Object} props.tool - The tool object with name, arguments, and id
 * @param {any} props.results - The results of the tool call
 * @param {boolean} [props.integrated=false] - Whether this is integrated in an assistant message
 * @param {string} [props.className] - Optional additional class names
 */
const ToolCallItem = ({ tool, results, integrated = false, className }) => {
  const [isOpen, setIsOpen] = useState(false); // Default to collapsed

  if (!tool?.name) return null;

  const formattedArguments = tool.arguments ? formatData(tool.arguments) : "";
  const formattedResults = results ? formatData(results) : "";

  // Determine styling based on integrated mode
  const cardStyles = integrated 
    ? "bg-transparent mb-2 overflow-hidden" 
    : "border border-primary/20 rounded-lg mb-2 overflow-hidden shadow-sm";
    
  const headerStyles = integrated
    ? "bg-muted/40 hover:bg-muted/60 border border-border rounded-md"
    : "bg-primary/5 hover:bg-primary/10 rounded-lg";
    
  const contentStyles = integrated
    ? "bg-muted/20 rounded-b-md border border-t-0 border-border p-3"
    : "border-t border-primary/20 bg-card p-4 rounded-b-lg";
    
  const codeStyles = integrated
    ? "bg-card border border-border text-card-foreground p-2 rounded-md text-sm font-mono whitespace-pre-wrap overflow-x-auto max-w-full tool-call-code"
    : "bg-primary/5 p-2 rounded-md text-sm font-mono whitespace-pre-wrap overflow-x-auto max-w-full tool-call-code";
    
  const sectionTitleStyles = "text-sm font-semibold text-primary";
  const iconStyles = "h-5 w-5 text-primary";

  return (
    <Card className={cn(cardStyles, className)}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <div className={cn(
            "flex items-center justify-between p-3 cursor-pointer transition-colors",
            headerStyles
          )}>
            <div className="flex items-center gap-2">
              <PocketKnife className={iconStyles} />
              <span className="font-medium text-foreground">
                {tool.name}
              </span>
            </div>
            <div className="flex items-center gap-1">
              {/* Copy entire tool call including arguments and results */}
              <div onClick={(e) => e.stopPropagation()}>
                <CopyButton
                  content={() => {
                    const toolData = {
                      name: tool.name,
                      arguments: tool.arguments ? JSON.parse(typeof tool.arguments === 'string' ? tool.arguments : JSON.stringify(tool.arguments)) : {},
                      results: results
                    };
                    return JSON.stringify(toolData, null, 2);
                  }}
                  tooltipText="Copy tool call"
                  variant="ghost"
                  size="sm"
                  className="text-primary hover:text-primary/80 hover:bg-primary/10"
                />
              </div>
              <ChevronDown
                className={cn(
                  "h-4 w-4 text-primary transition-transform",
                  isOpen && "rotate-180"
                )}
              />
            </div>
          </div>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className={cn(contentStyles, "p-0")}>
            {formattedArguments && (
              <div className="mt-2">
                <div className="flex justify-between items-center mb-1">
                  <h5 className={sectionTitleStyles}>Arguments:</h5>
                  <CopyButton
                    content={formattedArguments}
                    tooltipText="Copy arguments"
                    variant="ghost"
                    size="xs"
                    className="text-primary hover:text-primary/80 hover:bg-primary/10"
                  />
                </div>
                <pre className={codeStyles}>
                  {formattedArguments}
                </pre>
              </div>
            )}

            {formattedResults && (
              <div className="mt-2">
                <div className="flex justify-between items-center mb-1">
                  <h5 className={sectionTitleStyles}>Results:</h5>
                  <CopyButton
                    content={formattedResults}
                    tooltipText="Copy results"
                    variant="ghost"
                    size="xs"
                    className="text-primary hover:text-primary/80 hover:bg-primary/10"
                  />
                </div>
                <pre className={codeStyles}>
                  {formattedResults}
                </pre>
              </div>
            )}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};

export default ToolCallItem;