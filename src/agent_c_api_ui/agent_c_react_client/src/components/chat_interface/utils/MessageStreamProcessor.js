/**
 * MessageStreamProcessor - A utility for processing streaming message events
 * from the chat API in a structured way.
 */

/**
 * Process a single line from the message stream and call appropriate handlers
 * @param {string} line - Raw line from the message stream
 * @param {Object} handlers - Object containing handler functions for different event types
 * @param {Function} [handlers.onMessage] - Handles system/error messages
 * @param {Function} [handlers.onToolSelect] - Handles tool selection events
 * @param {Function} [handlers.onToolCalls] - Handles tool call events
 * @param {Function} [handlers.onContent] - Handles assistant content
 * @param {Function} [handlers.onToolResults] - Handles tool results
 * @param {Function} [handlers.onRenderMedia] - Handles media rendering events
 * @param {Function} [handlers.onCompletionStatus] - Handles completion status updates
 * @param {Function} [handlers.onThoughtDelta] - Handles thinking/reasoning process updates
 * @param {Function} [handlers.onUnknownType] - Handles unknown event types
 * @returns {boolean} - Returns true if processing should continue, false if stream should end
 * @throws {Error} If the line cannot be parsed
 */
export const processStreamLine = (line, handlers) => {
  // Check if the line is the termination marker
  if (line === "null") {
    console.log("Termination marker received. Ending stream processing.");
    return false;
  }
  
  try {
    const parsed = JSON.parse(line);
    
    // If parsed is null, exit early
    if (parsed === null) {
      console.log("Termination marker received after parsing.");
      return false;
    }
    
    console.log("Full parsed data:", parsed);
    
    switch (parsed.type) {
      case "message":
        // Handle message type (typically used for errors from the model)
        if (handlers.onMessage) {
          handlers.onMessage({
            content: parsed.data,
            critical: parsed.critical || false
          });
        }
        return true;
        
      case "tool_select_delta":
        if (handlers.onToolSelect) {
          try {
            const toolData = JSON.parse(parsed.data)[0];
            handlers.onToolSelect({
              inProgress: true,
              toolName: toolData?.name || "unknown tool",
              timestamp: Date.now()
            });
          } catch (err) {
            console.error("Error parsing tool selection data:", err);
            handlers.onToolSelect({
              inProgress: false,
              toolName: "unknown tool",
              timestamp: Date.now()
            });
          }
        }
        return true;
        
      case "tool_calls":
        if (handlers.onToolCalls && parsed.tool_calls) {
          handlers.onToolCalls(parsed.tool_calls);
        }
        return true;
        
      case "content":
        if (handlers.onContent) {
          handlers.onContent({
            content: parsed.data,
            vendor: parsed.vendor || 'unknown'
          });
        }
        return true;
        
      case "tool_results":
        if (handlers.onToolResults && parsed.tool_results) {
          handlers.onToolResults(parsed.tool_results);
        }
        return true;
        
      case "render_media":
        if (handlers.onRenderMedia) {
          handlers.onRenderMedia({
            content: parsed.content,
            contentType: parsed.content_type,
            metadata: parsed.metadata
          });
        }
        return true;
        
      case "completion_status":
        if (handlers.onCompletionStatus) {
          handlers.onCompletionStatus({
            running: parsed.data.running,
            inputTokens: parsed.data.input_tokens,
            outputTokens: parsed.data.output_tokens,
            totalTokens: parsed.data.input_tokens + parsed.data.output_tokens
          });
        }
        return true;
        
      case "thought_delta":
        if (handlers.onThoughtDelta) {
          handlers.onThoughtDelta({
            content: parsed.data,
            vendor: parsed.vendor || 'unknown'
          });
        }
        return true;
        
      // These cases don't require any specific handling
      case "interaction_start":
      case "interaction_end":
      case "history":
        return true;
        
      default:
        if (handlers.onUnknownType) {
          handlers.onUnknownType(parsed);
        } else {
          console.warn("Unknown message type:", parsed.type);
        }
        return true;
    }
  } catch (err) {
    console.error("Error processing message:", err);
    throw err;
  }
};

/**
 * Read and process a stream from the chat API
 * @param {ReadableStream} stream - Stream from fetch response
 * @param {Object} handlers - Event handlers for different message types
 * @returns {Promise<void>}
 */
export const processMessageStream = async (stream, handlers) => {
  const reader = stream.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";
  
  try {
    while (true) {
      const { value, done } = await reader.read();
      
      if (done) {
        // Handle any remaining buffer content
        if (buffer.trim()) {
          processStreamLine(buffer.trim(), handlers);
        }
        break;
      }
      
      buffer += decoder.decode(value, { stream: true });
      
      // Process complete lines
      let newlineIndex;
      while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, newlineIndex).trim();
        buffer = buffer.slice(newlineIndex + 1);
        
        if (line) {
          const shouldContinue = processStreamLine(line, handlers);
          if (!shouldContinue) {
            return; // Stop processing if a termination signal is received
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
};

export default {
  processStreamLine,
  processMessageStream
};