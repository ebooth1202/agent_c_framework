import React, { useState } from 'react';
import { PocketKnife, ChevronDown } from 'lucide-react';
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import CopyButton from './CopyButton';
import '../../styles/components/tool-call-item-integrated.css';

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

  const containerClass = integrated ? "integrated-tool-call-item" : "tool-call-item";
  const headerClass = integrated ? "integrated-tool-call-item-header" : "tool-call-item-header";
  const contentClass = integrated ? "integrated-tool-call-item-content" : "tool-call-item-content";
  const iconClass = integrated ? "integrated-tool-call-item-icon" : "tool-call-item-icon";
  const sectionTitleClass = integrated ? "integrated-tool-call-item-section-title" : "tool-call-item-section-title";
  const codeClass = integrated ? "integrated-tool-call-item-code" : "tool-call-item-code";

  return (
    <Card className={cn(containerClass, className)}>
      <Collapsible open={isOpen} onOpenChange={setIsOpen}>
        <CollapsibleTrigger asChild>
          <div className={headerClass}>
            <div className="tool-call-item-name-container">
              <PocketKnife className={iconClass} />
              <span className="tool-call-item-name">
                {tool.name}
              </span>
            </div>
            <div className="tool-call-item-buttons">
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
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-800/50"
                />
              </div>
              <ChevronDown
                className={`tool-call-item-chevron ${
                  isOpen ? "tool-call-item-chevron-rotated" : ""
                }`}
              />
            </div>
          </div>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <CardContent className={cn(contentClass, "p-0")}>
            {formattedArguments && (
              <div className="tool-call-item-section">
                <div className="tool-call-item-section-header">
                  <h5 className={sectionTitleClass}>Arguments:</h5>
                  <CopyButton
                    content={formattedArguments}
                    tooltipText="Copy arguments"
                    variant="ghost"
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-800/50"
                    size="xs"
                  />
                </div>
                <pre className={codeClass}>
                  {formattedArguments}
                </pre>
              </div>
            )}

            {formattedResults && (
              <div className="tool-call-item-section">
                <div className="tool-call-item-section-header">
                  <h5 className={sectionTitleClass}>Results:</h5>
                  <CopyButton
                    content={formattedResults}
                    tooltipText="Copy results"
                    variant="ghost"
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-800/50"
                    size="xs"
                  />
                </div>
                <pre className={codeClass}>
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