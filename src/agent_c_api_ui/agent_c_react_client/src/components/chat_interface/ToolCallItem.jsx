import React, { useState } from 'react';
import { PocketKnife, ChevronDown } from 'lucide-react';
import CopyButton from './CopyButton';
import '../../styles/components/tool-call-item-integrated.css';

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

const ToolCallItem = ({ tool, results, integrated = false }) => {
  const [isExpanded, setIsExpanded] = useState(false); // Default to collapsed

  if (!tool?.name) return null;

  const formattedArguments = tool.arguments ? formatData(tool.arguments) : "";
  const formattedResults = results ? formatData(results) : "";

  return (
    <div className={integrated ? "integrated-tool-call-item" : "tool-call-item"}>
      <div
        className={integrated ? "integrated-tool-call-item-header" : "tool-call-item-header"}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="tool-call-item-name-container">
          <PocketKnife className={integrated ? "integrated-tool-call-item-icon" : "tool-call-item-icon"} />
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
              isExpanded ? "tool-call-item-chevron-rotated" : ""
            }`}
          />
        </div>
      </div>

      {isExpanded && (
        <div className={integrated ? "integrated-tool-call-item-content" : "tool-call-item-content"}>
          {formattedArguments && (
            <div className="tool-call-item-section">
              <div className="tool-call-item-section-header">
                <h5 className={integrated ? "integrated-tool-call-item-section-title" : "tool-call-item-section-title"}>Arguments:</h5>
                <CopyButton
                  content={formattedArguments}
                  tooltipText="Copy arguments"
                  variant="ghost"
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-800/50"
                  size="xs"
                />
              </div>
              <pre className={integrated ? "integrated-tool-call-item-code" : "tool-call-item-code"}>
                {formattedArguments}
              </pre>
            </div>
          )}

          {formattedResults && (
            <div className="tool-call-item-section">
              <div className="tool-call-item-section-header">
                <h5 className={integrated ? "integrated-tool-call-item-section-title" : "tool-call-item-section-title"}>Results:</h5>
                <CopyButton
                  content={formattedResults}
                  tooltipText="Copy results"
                  variant="ghost"
                  className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-800/50"
                  size="xs"
                />
              </div>
              <pre className={integrated ? "integrated-tool-call-item-code" : "tool-call-item-code"}>
                {formattedResults}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ToolCallItem;