import React, { useState } from 'react';
import { PocketKnife, ChevronDown } from 'lucide-react';
import CopyButton from './CopyButton';

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

const ToolCallItem = ({ tool, results }) => {
  const [isExpanded, setIsExpanded] = useState(false); // Default to collapsed

  if (!tool?.name) return null;

  const formattedArguments = tool.arguments ? formatData(tool.arguments) : "";
  const formattedResults = results ? formatData(results) : "";

  return (
    <div className="border border-blue-200 rounded-lg mb-2 bg-white shadow-sm overflow-hidden">
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer bg-blue-50 hover:bg-blue-100 transition-colors rounded-lg"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <PocketKnife className="h-5 w-5 text-blue-600" />
          <span className="font-semibold text-blue-800">
            {tool.name}
          </span>
        </div>
        <div className="flex items-center gap-2">
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
              className="text-blue-600 hover:text-blue-800 hover:bg-blue-100"
            />
          </div>
          <ChevronDown
            className={`h-5 w-5 text-blue-600 transform transition-transform duration-200 ${
              isExpanded ? "rotate-180" : ""
            }`}
          />
        </div>
      </div>

      {isExpanded && (
        <div className="border-t border-blue-200 bg-white p-4 rounded-b-lg">
          {formattedArguments && (
            <div className="mb-4 relative group">
              <div className="flex justify-between items-center mb-2">
                <h5 className="text-sm font-semibold text-blue-600">Arguments:</h5>
                <CopyButton
                  content={formattedArguments}
                  tooltipText="Copy arguments"
                  variant="ghost"
                  className="text-blue-600 hover:text-blue-800 hover:bg-blue-100"
                  size="xs"
                />
              </div>
              <pre className="text-sm font-mono bg-blue-50 p-2 rounded-md whitespace-pre-wrap overflow-x-auto max-w-full">
                {formattedArguments}
              </pre>
            </div>
          )}

          {formattedResults && (
            <div className="relative group">
              <div className="flex justify-between items-center mb-2">
                <h5 className="text-sm font-semibold text-blue-600">Results:</h5>
                <CopyButton
                  content={formattedResults}
                  tooltipText="Copy results"
                  variant="ghost"
                  className="text-blue-600 hover:text-blue-800 hover:bg-blue-100"
                  size="xs"
                />
              </div>
              <pre className="text-sm font-mono bg-blue-50 p-2 rounded-md whitespace-pre-wrap overflow-x-auto max-w-full">
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