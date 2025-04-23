import React, { useState, useCallback } from 'react';

/**
 * ToolCallManager component manages tool call state and processing.
 * It doesn't render any UI itself but exposes methods via a render prop pattern.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {Function} props.children - Render prop function that receives tool call state and methods
 */
const ToolCallManager = ({ children }) => {
  const [activeToolCalls, setActiveToolCalls] = useState(new Map());
  const [toolSelectionState, setToolSelectionState] = useState({
    inProgress: false,
    toolName: null,
    timestamp: null
  });

  /**
   * Handles the start of a tool call operation
   * @param {Array<Object>} toolDetails - Array of tool call details
   */
  const handleToolStart = useCallback((toolDetails) => {
    console.log("=== handleToolStart called ===");
    console.log("Received tool details:", toolDetails);

    // Process each tool call in the array
    const newToolCalls = toolDetails.map((tool) => ({
      id: tool.id || tool.tool_call_id,
      name: tool.name || tool.function?.name,
      arguments: tool.arguments || tool.function?.arguments,
      results: null
    }));

    // Update state with the new tool calls
    setActiveToolCalls((prev) => {
      const newMap = new Map(prev);
      newToolCalls.forEach((call) => newMap.set(call.id, call));
      return newMap;
    });

    // Update tool selection state
    setToolSelectionState({
      inProgress: true,
      toolName: newToolCalls[0]?.name || "unknown tool",
      timestamp: Date.now()
    });

    return newToolCalls;
  }, []);

  /**
   * Handles the completion of a tool call operation
   * @param {Object} toolResults - Results from the completed tool operation
   */
  const handleToolEnd = useCallback((toolResults) => {
    console.log("=== handleToolEnd called ===");
    console.log("Received tool results:", toolResults);

    if (!toolResults) {
      console.warn("Invalid tool results:", toolResults);
      return null;
    }

    const toolCallId = toolResults.tool_call_id;
    const content = toolResults.content;

    if (!toolCallId || !content) {
      console.warn("Missing required tool result fields:", toolResults);
      return null;
    }

    let updatedCall = null;

    setActiveToolCalls((prev) => {
      const updated = new Map(prev);
      if (updated.has(toolCallId)) {
        const call = updated.get(toolCallId);
        updatedCall = {...call, results: content};
        updated.set(toolCallId, updatedCall);
      }
      return updated;
    });

    // Clear tool selection state when actual call completes
    setToolSelectionState({
      inProgress: false,
      toolName: null,
      timestamp: null
    });

    return updatedCall;
  }, []);

  /**
   * Updates tool selection state without creating an actual tool call
   * @param {Object} selectionState - The tool selection state
   */
  const updateToolSelectionState = useCallback((selectionState) => {
    setToolSelectionState(selectionState);
  }, []);

  /**
   * Clears all active tool calls
   */
  const clearToolCalls = useCallback(() => {
    setActiveToolCalls(new Map());
    setToolSelectionState({
      inProgress: false,
      toolName: null,
      timestamp: null
    });
  }, []);

  // Return render prop with state and methods
  return children({
    activeToolCalls,
    toolSelectionState,
    handleToolStart,
    handleToolEnd,
    updateToolSelectionState,
    clearToolCalls
  });
};

export default ToolCallManager;