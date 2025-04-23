import React, { useState, useRef, useEffect, useCallback, useContext } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Send, Upload, Settings } from "lucide-react";
import { SessionContext } from '@/contexts/SessionContext';
import { API_URL } from "@/config/config";
import { createClipboardContent } from '@/components/chat_interface/utils/htmlChatFormatter';
import { processMessageStream } from './utils/MessageStreamProcessor';

// Import our refactored components
import MessagesList from './MessagesList';
import StatusBar from './StatusBar';
import CollapsibleOptions from './CollapsibleOptions';
import FileUploadManager from './FileUploadManager';
import DragDropArea from './DragDropArea';
import { ToolCallProvider, useToolCalls } from './ToolCallContext';
import ExportHTMLButton from './ExportHTMLButton';

/**
 * Main chat interface inner component that uses the tool calls context
 */
const ChatInterfaceInner = ({
  sessionId, 
  customPrompt, 
  modelName, 
  modelParameters, 
  onProcessingStatus,
  // Added props for options panel
  persona,
  personas,
  availableTools,
  onEquipTools,
  modelConfigs,
  selectedModel,
  onUpdateSettings,
  isInitialized
}) => {
  // Access tool call context
  const { 
    handleToolStart, 
    handleToolEnd, 
    updateToolSelectionState,
    toolSelectionState
  } = useToolCalls();
  
  // Access SessionContext for StatusBar props and options panel state
  const { 
    isReady, 
    activeTools, 
    settingsVersion,
    isOptionsOpen,
    setIsOptionsOpen
  } = useContext(SessionContext);
  
  // State for messages and UI
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [expandedToolCallMessages, setExpandedToolCallMessages] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  
  // Refs
  const fileInputRef = useRef(null);
  
  // Effect to notify parent of processing status
  useEffect(() => {
    if (onProcessingStatus) {
      onProcessingStatus(isStreaming);
    }
  }, [isStreaming, onProcessingStatus]);
  
  // Toggle the expanded state of tool calls for a specific message
  const toggleToolCallExpansion = (messageIdx) => {
    setExpandedToolCallMessages(prev => {
      if (prev.includes(messageIdx)) {
        return prev.filter(idx => idx !== messageIdx);
      } else {
        return [...prev, messageIdx];
      }
    });
  };
  
  // Helper function to format a message for copying
  const formatMessageForCopy = useCallback((msg) => {
    if (msg.role === 'user') {
      return `User: ${msg.content}\n`;
    } else if (msg.role === 'assistant' && msg.type === 'content') {
      return `Assistant: ${msg.content}\n`;
    } else if (msg.role === 'assistant' && msg.type === 'thinking') {
      return `Assistant (thinking): ${msg.content}\n`;
    } else if (msg.type === 'tool_calls') {
      // Format tool calls
      let result = `Assistant (tool): Using ${msg.toolCalls.map(t => t.name || t.function?.name).join(', ')}\n`;
      msg.toolCalls.forEach(tool => {
        const toolName = tool.name || tool.function?.name;
        const toolArgs = tool.arguments || tool.function?.arguments;
        if (toolArgs) {
          result += `  ${toolName} Arguments: ${typeof toolArgs === 'string' ? toolArgs : JSON.stringify(toolArgs)}\n`;
        }
        if (tool.results) {
          result += `  ${toolName} Results: ${typeof tool.results === 'string' ? tool.results : JSON.stringify(tool.results)}\n`;
        }
      });
      return result;
    } else if (msg.type === 'media') {
      return `Assistant (media): Shared ${msg.contentType} content\n`;
    } else if (msg.role === 'system') {
      return `System: ${msg.content}\n`;
    }
    return '';
  }, []);
  
  // Format the entire chat for copying
  const formatChatForCopy = useCallback(() => {
    return messages.map(formatMessageForCopy).join('\n');
  }, [messages, formatMessageForCopy]);
  
  // Get both text and HTML versions for the entire chat
  const getChatCopyContent = useCallback(() => {
    const clipboardContent = createClipboardContent(messages);
    return clipboardContent.text;
  }, [messages]);
  
  // Get HTML version for rich copying
  const getChatCopyHTML = useCallback(() => {
    const clipboardContent = createClipboardContent(messages);
    return clipboardContent.html;
  }, [messages]);
  
  /**
   * Handles file drop from drag and drop
   * @param {File} file - The dropped file
   */
  const handleFileDrop = (file) => {
    if (file && fileInputRef.current) {
      // Trigger the FileUploadManager to handle the file
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInputRef.current.files = dataTransfer.files;
      
      // Trigger the change event
      const event = new Event('change', { bubbles: true });
      fileInputRef.current.dispatchEvent(event);
    }
  };
  
  /**
   * Handles file upload notification
   * @param {Object} file - The file that was uploaded
   */
  const handleFileUploaded = (file) => {
    setMessages((prev) => [
      ...prev,
      {
        role: "system",
        type: "content",
        content: `File uploaded: ${file.name}`,
      },
    ]);
  };
  
  /**
   * Handles file upload error
   * @param {string} errorMessage - The error message
   */
  const handleFileError = (errorMessage) => {
    setMessages((prev) => [
      ...prev,
      {
        role: "system",
        type: "error",
        content: `Error uploading file: ${errorMessage}`,
      },
    ]);
  };
  
  /**
   * Handles changes to selected files
   * @param {Array} files - The currently selected files
   */
  const handleSelectedFilesChange = (files) => {
    setSelectedFiles(files);
  };
  
  /**
   * Sends a message to the chat backend and processes the response stream
   * @returns {Promise<void>}
   */
  const handleSendMessage = async () => {
    // Don't send if empty or already streaming
    if ((!inputText.trim() && selectedFiles.length === 0) || isStreaming) return;
    
    try {
      setIsStreaming(true);
      
      // Add user message to the UI
      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          type: "content",
          content: inputText,
          files: selectedFiles.length > 0 ? selectedFiles.map(f => f.name) : undefined
        },
      ]);
      
      const userText = inputText;
      setInputText("");
      
      // Prepare form data for API request
      const formData = new FormData();
      formData.append("ui_session_id", sessionId);
      formData.append("message", userText);
      formData.append("custom_prompt", customPrompt || "");
      
      if (selectedFiles.length > 0) {
        formData.append("file_ids", JSON.stringify(selectedFiles.map(f => f.id)));
      }
      
      // Add the correct parameter based on model type
      if (modelParameters.temperature !== undefined) {
        formData.append("temperature", modelParameters.temperature);
      }
      if (modelParameters.reasoning_effort !== undefined) {
        formData.append("reasoning_effort", modelParameters.reasoning_effort);
      }
      
      formData.append("llm_model", modelName);
      
      // Make the API request
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      if (!response.body) {
        throw new Error("No response body");
      }
      
      // Process the message stream with our utility
      processMessageStream(response.body, {
        onMessage: ({ content, critical }) => {
          setMessages((prev) => [
            ...prev,
            {
              role: "system",
              type: "error",
              content: `Error: ${content}`,
              critical: critical || false
            },
          ]);
          setIsStreaming(false);
        },
        
        onToolSelect: (selectionState) => {
          updateToolSelectionState(selectionState);
        },
        
        onToolCalls: (toolCalls) => {
          const newToolCalls = handleToolStart(toolCalls);
          
          setMessages((prev) => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage?.type === "tool_calls") {
              // Update existing tool calls message
              return prev.map((msg, i) =>
                i === prev.length - 1
                  ? {...msg, toolCalls: [...(msg.toolCalls || []), ...newToolCalls]}
                  : msg
              );
            }
            // Create new tool calls message
            return [...prev, {
              role: "assistant",
              type: "tool_calls",
              toolCalls: newToolCalls
            }];
          });
        },
        
        onContent: ({ content, vendor }) => {
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last?.role === "assistant" && last?.type === "content") {
              return prev.map((msg, i) =>
                i === prev.length - 1
                  ? {
                    ...msg,
                    content: msg.content + content,
                    vendor: vendor || msg.vendor
                  }
                  : msg
              );
            }
            return [...prev, {
              role: "assistant",
              type: "content",
              content: content,
              vendor: vendor || 'unknown'
            }];
          });
        },
        
        onToolResults: (toolResults) => {
          if (toolResults) {
            toolResults.forEach((result) => {
              const updatedCall = handleToolEnd(result);
              
              if (updatedCall) {
                setMessages((prev) => {
                  return prev.map((message) => {
                    if (message.type === "tool_calls") {
                      const updatedToolCalls = message.toolCalls.map((call) => {
                        if (call.id === updatedCall.id) {
                          return { ...call, results: updatedCall.results };
                        }
                        return call;
                      });
                      return { ...message, toolCalls: updatedToolCalls };
                    }
                    return message;
                  });
                });
              }
            });
          }
        },
        
        onRenderMedia: ({ content, contentType, metadata }) => {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              type: "media",
              content: content,
              contentType: contentType,
              metadata: metadata
            },
          ]);
        },
        
        onCompletionStatus: ({ running, inputTokens, outputTokens, totalTokens }) => {
          if (!running && (inputTokens || outputTokens)) {
            setMessages((prev) => {
              const lastAssistantMessage = [...prev].reverse().find(
                (msg) => msg.role === "assistant" && msg.type === "content"
              );
              if (!lastAssistantMessage) return prev;
              return prev.map((msg) => {
                if (msg === lastAssistantMessage) {
                  return {
                    ...msg,
                    tokenUsage: {
                      prompt_tokens: inputTokens,
                      completion_tokens: outputTokens,
                      total_tokens: inputTokens + outputTokens,
                    },
                  };
                }
                return msg;
              });
            });
          }
        },
        
        onThoughtDelta: ({ content, vendor }) => {
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last?.role === "assistant" && last?.type === "thinking") {
              return prev.map((msg, i) =>
                i === prev.length - 1
                  ? {
                    ...msg,
                    content: msg.content + content,
                    vendor: vendor || msg.vendor
                  }
                  : msg
              );
            }
            return [...prev, {
              role: "assistant",
              type: "thinking",
              content: content,
              vendor: vendor || 'unknown'
            }];
          });
        },
        
        onUnknownType: (data) => {
          console.warn("Unknown message type:", data.type);
        }
      }).catch(error => {
        console.error("Error processing stream:", error);
        setMessages((prev) => [
          ...prev,
          {
            role: "system",
            type: "error",
            content: `Error: ${error.message}`,
          },
        ]);
      }).finally(() => {
        setIsStreaming(false);
        setSelectedFiles([]);
      });
      
    } catch (error) {
      console.error("Error in chat:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          type: "content",
          content: `Error: ${error.message}`,
        },
      ]);
      setIsStreaming(false);
      setSelectedFiles([]);
    }
  };
  
  /**
   * Handles keyboard shortcuts for sending messages
   * @param {KeyboardEvent} e - Keyboard event
   */
  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  // Toggle options panel visibility
  const toggleOptionsPanel = () => {
    setIsOptionsOpen(!isOptionsOpen);
  };
  
  return (
    <DragDropArea 
      onFileDrop={handleFileDrop}
      disabled={isStreaming}
      className="flex flex-col h-full min-h-0 relative z-0 group"
    >
      <Card className="flex flex-col h-full min-h-0 bg-card/90 dark:bg-gray-800/50 backdrop-blur-sm border border-gray-300 dark:border-gray-700 shadow-xl rounded-xl">
        {/* Messages list */}
        <MessagesList 
          messages={messages}
          expandedToolCallMessages={expandedToolCallMessages}
          toggleToolCallExpansion={toggleToolCallExpansion}
          toolSelectionInProgress={toolSelectionState.inProgress}
          toolSelectionName={toolSelectionState.toolName}
        />
        
        {/* Options Panel - conditionally rendered between messages and input */}
        {isOptionsOpen && (
          <div className="mx-4 mb-2">
            <CollapsibleOptions
              isOpen={isOptionsOpen}
              setIsOpen={setIsOptionsOpen}
              persona={persona}
              personas={personas}
              availableTools={availableTools}
              customPrompt={customPrompt}
              temperature={modelParameters.temperature}
              modelName={modelName}
              modelConfigs={modelConfigs}
              sessionId={sessionId}
              isReady={isReady}
              onEquipTools={onEquipTools}
              activeTools={activeTools}
              modelParameters={modelParameters}
              selectedModel={selectedModel}
              onUpdateSettings={onUpdateSettings}
              isInitialized={isInitialized}
            />
          </div>
        )}
        
        {/* Footer with file upload and message input */}
        <div className="border-t border-gray-300 dark:border-gray-700 bg-card/90 dark:bg-gray-800/50 backdrop-blur-sm p-4 space-y-3 rounded-b-xl">
          {/* File management component */}
          <FileUploadManager
            sessionId={sessionId}
            onFileUploadComplete={handleFileUploaded}
            onFileError={handleFileError}
            onSelectedFilesChange={handleSelectedFilesChange}
            fileInputRef={fileInputRef}
          />
          
          <div className="flex gap-2">
            {/* Text input with action buttons */}
            <div className="relative flex-1">
              <textarea
                placeholder="Type your message..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyPress}
                disabled={isStreaming}
                rows="2"
                className="w-full rounded-xl border border-gray-300 dark:border-gray-700 bg-white/80 dark:bg-gray-800/50 backdrop-blur-sm transition-colors
                hover:bg-white dark:hover:bg-gray-700/80 focus:border-blue-400 dark:focus:border-blue-600 focus:ring focus:ring-blue-200 dark:focus:ring-blue-800 focus:ring-opacity-50
                placeholder-gray-500 dark:placeholder-gray-500 text-gray-900 dark:text-gray-100 py-2 pl-3 pr-12 resize-none"
              />
              
              {/* Settings gear icon button */}
              <Button
                onClick={toggleOptionsPanel}
                variant="ghost"
                size="icon"
                className="absolute right-20 bottom-2 h-8 w-8 text-gray-500 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-full transition-colors"
              >
                <Settings className="h-4 w-4" />
              </Button>
              
              {/* File upload button positioned inside the input area */}
              <Button
                onClick={() => FileUploadManager.openFilePicker(fileInputRef)}
                variant="ghost"
                size="icon"
                disabled={isStreaming}
                className="absolute right-12 bottom-2 h-8 w-8 text-gray-500 hover:text-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-full transition-colors"
              >
                <Upload className="h-4 w-4" />
              </Button>
              
              {/* Send button */}
              <Button
                onClick={handleSendMessage}
                disabled={isStreaming}
                size="icon"
                className="absolute right-2 bottom-2 h-8 w-8 rounded-full bg-blue-500 hover:bg-blue-600 transition-colors"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
          
          {/* StatusBar positioned just below the input */}
          <div className="-mt-1 flex justify-center w-full transform translate-y-1">
            <StatusBar
              isReady={isReady}
              activeTools={activeTools}
              sessionId={sessionId}
              settingsVersion={settingsVersion}
              isProcessing={isStreaming}
              getChatCopyContent={getChatCopyContent}
              getChatCopyHTML={getChatCopyHTML}
              messages={messages}
            />
          </div>
        </div>
      </Card>
    </DragDropArea>
  );
};

/**
 * ChatInterface component provides a complete chat interface with support for
 * message streaming, file uploads, and various message types including text,
 * media, and tool calls.
 */
const ChatInterface = (props) => {
  return (
    <ToolCallProvider>
      <ChatInterfaceInner {...props} />
    </ToolCallProvider>
  );
};

export default ChatInterface;