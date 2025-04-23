import React, { createContext, useState, useContext, useCallback } from 'react';

/**
 * Context for managing tool call state throughout the application
 */
const ToolCallContext = createContext(null);

/**
 * Hook to use the tool call context
 * @returns {Object} Tool call state and methods
 */
export const useToolCalls = () => {
  const context = useContext(ToolCallContext);
  if (!context) {
    throw new Error('useToolCalls must be used within a ToolCallProvider');
  }
  return context;
};

/**
 * Provider component for tool call management
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 */
export const ToolCallProvider = ({ children }) => {
  const [activeToolCalls, setActiveToolCalls] = useState(new Map());
  const [toolSelectionState, setToolSelectionState] = useState({
    inProgress: false,
    toolName: null,
    timestamp: null
  });

  /**
   * Handles the start of a tool call operation
   * @param {Array<Object>} toolDetails - Array of tool call details
   * @returns {Array<Object>} Processed tool call details
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
   * @returns {Object|null} Updated tool call or null
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

  // Value to provide through the context
  const value = {
    activeToolCalls,
    toolSelectionState,
    handleToolStart,
    handleToolEnd,
    updateToolSelectionState,
    clearToolCalls
  };

  return (
    <ToolCallContext.Provider value={value}>
      {children}
    </ToolCallContext.Provider>
  );
};