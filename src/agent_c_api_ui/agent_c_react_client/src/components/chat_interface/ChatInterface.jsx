import React, {useState, useRef, useEffect, useCallback, useContext} from "react";
import {Card} from "@/components/ui/card";
import {Button} from "@/components/ui/button";
import {Input} from "@/components/ui/input";
import {Send, Upload, User, Mic, FileIcon, Settings} from "lucide-react";
import {ScrollArea} from "@/components/ui/scroll-area";
import ToolCallDisplay from "./ToolCallDisplay";
import MediaMessage from './MediaMessage';
import TokenUsageDisplay from './TokenUsageDisplay';
import MarkdownMessage from './MarkdownMessage';
import ThoughtDisplay from './ThoughtDisplay';
import ModelIcon from './ModelIcon';
import CopyButton from './CopyButton';
import StatusBar from './StatusBar';
import CollapsibleOptions from './CollapsibleOptions';
import {API_URL} from "@/config/config";
import {createClipboardContent} from '@/components/chat_interface/utils/htmlChatFormatter';
import ExportHTMLButton from './ExportHTMLButton';
import { SessionContext } from '@/contexts/SessionContext';

/**
 * ChatInterface component provides a complete chat interface with support for
 * message streaming, file uploads, and various message types including text,
 * media, and tool calls.
 */
const ChatInterface = ({
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
    // Access SessionContext for StatusBar props and options panel state
    const { 
        isReady, 
        activeTools, 
        settingsVersion,
        isOptionsOpen,
        setIsOptionsOpen
    } = useContext(SessionContext);
    
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState("");
    const [isStreaming, setIsStreaming] = useState(false);
    const [activeToolCalls, setActiveToolCalls] = useState(new Map()); // Track active tool calls
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const [selectedFileForUpload, setSelectedFileForUpload] = useState(null); // Track selected file
    
    // State for drag & drop functionality
    const [isDraggingOver, setIsDraggingOver] = useState(false);
    const dragCounterRef = useRef(0);

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

    // Use the enhanced formatter function
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

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({behavior: "smooth"});
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // console.log('Streaming state:', isStreaming);
        if (onProcessingStatus) {
            onProcessingStatus(isStreaming);
        }
    }, [isStreaming, onProcessingStatus]);

    /**
     * Handles file selection change
     * @param {Event} e - Change event from the file input
     */
    const handleFileSelection = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            const file = e.target.files[0];
            setSelectedFileForUpload(file);
            
            // Automatically upload the file when selected
            setTimeout(() => {
                handleUploadFile(file);
            }, 0);
        } else {
            setSelectedFileForUpload(null);
        }
    };

    /**
     * Opens the file picker dialog
     */
    const openFilePicker = () => {
        fileInputRef.current?.click();
    };

    /**
     * Handles drag enter events
     */
    const handleDragEnter = (e) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounterRef.current++;
        
        if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
            setIsDraggingOver(true);
        }
    };

    /**
     * Handles drag leave events
     */
    const handleDragLeave = (e) => {
        e.preventDefault();
        e.stopPropagation();
        dragCounterRef.current--;
        
        if (dragCounterRef.current === 0) {
            setIsDraggingOver(false);
        }
    };

    /**
     * Handles drag over events
     */
    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    /**
     * Handles drop events
     */
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDraggingOver(false);
        dragCounterRef.current = 0;
        
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setSelectedFileForUpload(e.dataTransfer.files[0]);
            // Automatically upload the file when dropped
            setTimeout(() => {
                handleUploadFile(e.dataTransfer.files[0]);
            }, 0);
        }
    };

    /**
     * Handles file upload to the server and tracks processing status
     * @param {File} fileToUpload - Optional file to upload, if not provided uses selectedFileForUpload
     * @returns {Promise<void>}
     * @throws {Error} If the file upload fails
     */
    const handleUploadFile = async (fileToUpload = null) => {
        // Use provided file or the selected file from state
        const fileToProcess = fileToUpload || selectedFileForUpload;
        if (!fileToProcess) return;

        setIsUploading(true);

        const formData = new FormData();
        formData.append("ui_session_id", sessionId);
        formData.append("file", fileToProcess);

        try {
            // Upload the file
            const response = await fetch(`${API_URL}/upload_file`, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Add file to state with initial "pending" status
            const newFile = {
                id: data.id,
                name: data.filename,
                type: data.mime_type,
                size: data.size,
                selected: true,
                processing_status: "pending", // Initial status
                processing_error: null
            };

            setUploadedFiles(prev => [...prev, newFile]);
            setSelectedFiles(prev => [...prev, newFile]);

            setMessages((prev) => [
                ...prev,
                {
                    role: "system",
                    type: "content",
                    content: `File uploaded: ${fileToProcess.name}`,
                },
            ]);

            // Reset file input and state
            if (fileInputRef.current) {
                fileInputRef.current.value = null;
            }
            setSelectedFileForUpload(null);

            // Check processing status after upload
            checkFileProcessingStatus(data.id);

        } catch (error) {
            console.error("Error uploading file:", error);
            setMessages((prev) => [
                ...prev,
                {
                    role: "system",
                    type: "content",
                    content: `Error uploading file: ${error.message}`,
                },
            ]);
        } finally {
            setIsUploading(false);
        }
    };

    /**
     * Checks the processing status of a file
     * @param {string} fileId - The ID of the file to check
     */
    const checkFileProcessingStatus = async (fileId) => {
        // Poll the server every 2 seconds to check processing status
        const checkStatus = async () => {
            try {
                const response = await fetch(`${API_URL}/files/${sessionId}`);
                if (!response.ok) {
                    console.error(`Error fetching file status: ${response.status}`);
                    return true; // Stop polling on error
                }

                const data = await response.json();

                // Find the file in the response
                const fileData = data.files.find(f => f.id === fileId);
                if (!fileData) return false;

                // Update state with current processing status
                setUploadedFiles(prev => prev.map(file => {
                    if (file.id === fileId) {
                        return {
                            ...file,
                            processing_status: fileData.processing_status,
                            processing_error: fileData.processing_error
                        };
                    }
                    return file;
                }));

                // If processing is complete or failed, stop polling
                return fileData.processing_status !== "pending";
            } catch (error) {
                console.error("Error checking file status:", error);
                return true; // Stop polling on error
            }
        };

        // Poll until processing completes or fails (max 30 seconds)
        let attempts = 0;
        const maxAttempts = 15; // 15 attempts * 2 seconds = 30 seconds max

        const pollTimer = setInterval(async () => {
            attempts++;
            const shouldStop = await checkStatus();

            if (shouldStop || attempts >= maxAttempts) {
                clearInterval(pollTimer);

                // If we hit max attempts and status is still pending, mark as failed
                if (attempts >= maxAttempts) {
                    setUploadedFiles(prev => prev.map(file => {
                        if (file.id === fileId && file.processing_status === "pending") {
                            return {
                                ...file,
                                processing_status: "failed",
                                processing_error: "Processing timed out"
                            };
                        }
                        return file;
                    }));
                }
            }
        }, 2000);
    };

    const toggleFileSelection = (fileId) => {
        setUploadedFiles(prev => prev.map(file => {
            if (file.id === fileId) {
                const newSelected = !file.selected;

                // Update selectedFiles state
                if (newSelected) {
                    setSelectedFiles(prev => [...prev, file]);
                } else {
                    setSelectedFiles(prev => prev.filter(f => f.id !== fileId));
                }

                return {...file, selected: newSelected};
            }
            return file;
        }));
    };

    const [toolSelectionState, setToolSelectionState] = useState({
        inProgress: false,
        toolName: null,
        timestamp: null
    });
    /**
     * Handles the start of a tool call operation
     * @param {Array<Object>} toolDetails - Array of tool call details
     * @param {string} toolDetails[].id - Unique identifier for the tool call
     * @param {string} toolDetails[].name - Name of the tool being called
     * @param {Object} toolDetails[].arguments - Arguments for the tool call
     */
    const handleToolStart = (toolDetails) => {
        console.log("=== handleToolStart called ===");
        console.log("Received tool details:", toolDetails);

        // Process each tool call in the array
        const newToolCalls = toolDetails.map((tool) => ({
            id: tool.id || tool.tool_call_id,
            name: tool.name || tool.function?.name,  // Handle function name if in nested structure
            arguments: tool.arguments || tool.function?.arguments,  // Handle nested arguments
            results: null
        }));

        // Update state with the new tool calls
        setActiveToolCalls((prev) => {
            const newMap = new Map(prev);
            newToolCalls.forEach((call) => newMap.set(call.id, call));
            return newMap;
        });

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
    };

    /**
     * Handles the completion of a tool call operation and updates relevant state
     * @param {Object} toolResults - Results from the completed tool operation
     * @param {string} toolResults.tool_call_id - Unique identifier of the completed tool call
     * @param {string|Object} toolResults.content - Results/output from the tool operation
     * @throws {Warning} If required fields are missing from tool results
     */
    const handleToolEnd = (toolResults) => {
        console.log("=== handleToolEnd called ===");
        console.log("Received tool results:", toolResults);

        if (!toolResults) {
            console.warn("Invalid tool results:", toolResults);
            return;
        }

        const toolCallId = toolResults.tool_call_id;
        const content = toolResults.content;

        if (!toolCallId || !content) {
            console.warn("Missing required tool result fields:", toolResults);
            return;
        }

        setActiveToolCalls((prev) => {
            const updated = new Map(prev);
            if (updated.has(toolCallId)) {
                const call = updated.get(toolCallId);
                updated.set(toolCallId, {...call, results: content});
            }
            return updated;
        });

        setMessages((prev) => {
            return prev.map((message) => {
                if (message.type === "tool_calls") {
                    const updatedToolCalls = message.toolCalls.map((call) => {
                        if (call.id === toolCallId) {
                            return {...call, results: content};
                        }
                        return call;
                    });
                    return {...message, toolCalls: updatedToolCalls};
                }
                return message;
            });
        });
    };

    /**
     * Sends a message to the chat backend and processes the response stream
     * @returns {Promise<void>}
     * @throws {Error} If the message send fails or stream processing encounters an error
     */
    const handleSendMessage = async () => {
        if ((!inputText.trim() && selectedFiles.length === 0) || isStreaming) return;

        try {
            setIsStreaming(true);
            setActiveToolCalls(new Map());

            // Add user message
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

            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = "";

            try {
                while (true) {
                    const {value, done} = await reader.read();

                    if (done) {
                        // Handle any remaining buffer content
                        if (buffer.trim()) {
                            await processLine(buffer.trim());
                        }
                        break;
                    }

                    buffer += decoder.decode(value, {stream: true});

                    // Process complete lines
                    let newlineIndex;
                    while ((newlineIndex = buffer.indexOf("\n")) !== -1) {
                        const line = buffer.slice(0, newlineIndex).trim();
                        buffer = buffer.slice(newlineIndex + 1);

                        if (line) {
                            await processLine(line);
                        }
                    }
                }
            } finally {
                reader.releaseLock();
            }
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
        } finally {
            setIsStreaming(false);
            setSelectedFiles([]);
            setUploadedFiles(prev => prev.map(file => ({...file, selected: false})));
        }
    };

// Helper function to process each line of the stream
    /**
     * Processes a single line from the message stream
     * @param {string} line - Raw line from the message stream
     * @returns {Promise<void>}
     * @throws {Error} If the line cannot be parsed or processed
     */
    const processLine = async (line) => {
        // Check if the line is the termination marker.
        if (line === "null") {
            console.log("Termination marker received. Ending stream processing.");
            return;
        }
        try {
            const parsed = JSON.parse(line);
            // If parsed is null (in case JSON.parse("null") returns null), exit early.
            if (parsed === null) {
                console.log("Termination marker received after parsing.");
                return;
            }
            // console.log("=== Received message ===");
            console.log("Full parsed data:", parsed);

            switch (parsed.type) {
                case "message":
                    // Handle message type (typically used for errors from the model)
                    console.log("Message received:", parsed);

                    // Add as a system message (error)
                    setMessages((prev) => [
                        ...prev,
                        {
                            role: "system",
                            type: "error",
                            content: `Error: ${parsed.data}`,
                            critical: parsed.critical || false
                        },
                    ]);

                    // End streaming if we receive a message (especially errors)
                    setIsStreaming(false);
                    break;

                case "tool_select_delta":
                    try {
                        const toolData = JSON.parse(parsed.data)[0];
                        setToolSelectionState({
                            inProgress: true,
                            toolName: toolData?.name || "unknown tool",
                            timestamp: Date.now()
                        });
                    } catch (err) {
                        console.error("Error parsing tool selection data:", err);
                        setToolSelectionState({
                            inProgress: false,
                            toolName: "unknown tool",
                            timestamp: Date.now()
                        });
                    }
                    break;

                case "tool_calls":
                    if (parsed.tool_calls) {
                        handleToolStart(parsed.tool_calls);
                        setToolSelectionState({
                            inProgress: true,
                            toolName: parsed.tool_calls[0]?.name || "unknown tool",
                            timestamp: Date.now()
                        });
                    }
                    break;

                case "content":
                    setMessages((prev) => {
                        const last = prev[prev.length - 1];
                        if (last?.role === "assistant" && last?.type === "content") {
                            return prev.map((msg, i) =>
                                i === prev.length - 1
                                    ? {
                                        ...msg,
                                        content: msg.content + parsed.data,
                                        vendor: parsed.vendor || msg.vendor
                                    }
                                    : msg
                            );
                        }
                        return [...prev, {
                            role: "assistant",
                            type: "content",
                            content: parsed.data,
                            vendor: parsed.vendor || 'unknown'
                        }];
                    });
                    break;

                case "tool_results":
                    if (parsed.tool_results) {
                        parsed.tool_results.forEach((result) => handleToolEnd(result));
                    }
                    // Clear tool selection state when actual call happens
                    setToolSelectionState({
                        inProgress: false,
                        toolName: null,
                        timestamp: null
                    });
                    break;

                case "render_media":
                    setMessages((prev) => [
                        ...prev,
                        {
                            role: "assistant",
                            type: "media",
                            content: parsed.content,
                            contentType: parsed.content_type,
                            metadata: parsed.metadata
                        },
                    ]);
                    break;

                case "completion_status":
                    if (!parsed.data.running) {
                        if (parsed.data.input_tokens || parsed.data.output_tokens) {
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
                                                prompt_tokens: parsed.data.input_tokens,
                                                completion_tokens: parsed.data.output_tokens,
                                                total_tokens: parsed.data.input_tokens + parsed.data.output_tokens,
                                            },
                                        };
                                    }
                                    return msg;
                                });
                            });
                        }
                    }
                    break;
                case "thought_delta":
                    setMessages((prev) => {
                        const last = prev[prev.length - 1];
                        if (last?.role === "assistant" && last?.type === "thinking") {
                            return prev.map((msg, i) =>
                                i === prev.length - 1
                                    ? {
                                        ...msg,
                                        content: msg.content + parsed.data,
                                        vendor: parsed.vendor || msg.vendor
                                    }
                                    : msg
                            );
                        }
                        return [...prev, {
                            role: "assistant",
                            type: "thinking",
                            content: parsed.data,
                            vendor: parsed.vendor || 'unknown'
                        }];
                    });
                    break;

                // These cases don't require any specific handling
                case "interaction_start":
                case "interaction_end":
                case "history":
                    break;
                default:
                    console.warn("Unknown message type:", parsed.type);
            }
        } catch (err) {
            console.error("Error processing message:", err);
            throw err;
        }
    };


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
        <Card 
            className="flex flex-col h-full min-h-0 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border dark:border-gray-700 shadow-lg rounded-xl relative z-0 group"
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
        >
            {/* Drag & Drop overlay */}
            {isDraggingOver && (
                <div className="absolute inset-0 bg-blue-500/10 dark:bg-blue-800/20 backdrop-blur-sm z-50 rounded-xl flex items-center justify-center border-2 border-blue-500 dark:border-blue-400 border-dashed">
                    <div className="text-center p-6 bg-white/80 dark:bg-gray-800/80 rounded-xl shadow-lg">
                        <Upload className="h-10 w-10 text-blue-500 dark:text-blue-400 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-blue-700 dark:text-blue-300">Drop your file here</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Files will be uploaded and processed automatically</p>
                    </div>
                </div>
            )}
            
            {/* Buttons moved to status bar */}
            <ScrollArea className="flex-1 px-4 py-3" type="auto">

                <div className="space-y-4 w-full overflow-x-hidden">
                    {messages.map((msg, idx) => {
                        // === USER MESSAGES ===
                        if (msg.role === "user") {
                            return (
                                <div key={idx} className="flex justify-end items-start gap-2 group">
                                    <div
                                        className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-blue-500 text-white ml-12 rounded-br-sm relative border border-blue-600">
                                        {msg.isVoiceMessage ? (
                                            <div className="flex items-center space-x-2">
                                                <Mic className="h-4 w-4 text-white"/>
                                                <span className="text-white">Voice message</span>
                                            </div>
                                        ) : (
                                            <div className="markdown-user-message">
                                                <MarkdownMessage content={msg.content}/>
                                            </div>
                                        )}

                                        {/* Copy button that appears on hover */}
                                        <div
                                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity transform -translate-x-full">
                                            <CopyButton
                                                content={msg.content}
                                                tooltipText="Copy message"
                                                position="left"
                                                variant="secondary"
                                                size="xs"
                                                className="bg-blue-600 hover:bg-blue-700 text-white"
                                            />
                                        </div>
                                    </div>
                                    <User className="h-6 w-6 text-blue-500"/>
                                </div>
                            );
                        }

                        // === ASSISTANT TEXT ===
                        if (msg.role === "assistant" && msg.type === "content") {
                            return (
                                <div key={idx} className="flex flex-col">
                                    <div className="flex justify-start items-start gap-2 group">
                                        <ModelIcon vendor={msg.vendor}/>
                                        <div
                                            className="max-w-[80%] rounded-2xl px-4 py-2 shadow-sm bg-purple-50 dark:bg-purple-900/30 text-purple-800 dark:text-purple-200 mr-12 rounded-bl-sm border border-purple-200 dark:border-purple-700">
                                            <MarkdownMessage content={msg.content}/>
                                            {msg.tokenUsage && <TokenUsageDisplay usage={msg.tokenUsage}/>}
                                        </div>
                                    </div>
                                </div>
                            );
                        }

                        // === TOOL CALLS (single container for all tool calls) ===
                        if (msg.type === "tool_calls") {
                            return (
                                <div key={idx}>
                                    <ToolCallDisplay toolCalls={msg.toolCalls}/>
                                </div>
                            );
                        }

                        // === THINKING MESSAGES ===
                        if (msg.role === "assistant" && msg.type === "thinking") {
                            return (
                                <div key={idx}>
                                    <ThoughtDisplay content={msg.content} vendor={msg.vendor}/>
                                </div>
                            );
                        }

                        // === MEDIA ===
                        if (msg.type === "media") {
                            return (
                                <div key={idx}>
                                    <MediaMessage message={msg}/>
                                </div>
                            );
                        }

                        // === SYSTEM MESSAGES ===
                        if (msg.role === "system") {
                            const isError = msg.type === "error";
                            return (
                                <div key={idx} className="flex justify-start group">
                                    <div
                                        className={`max-w-[80%] rounded-2xl px-4 py-2 shadow-sm relative ${
                                            isError
                                                ? "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300 border border-red-300 dark:border-red-800"
                                                : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300"
                                        }`}
                                    >
                                        {isError ? "ud83dudeab Error: " : ""}{msg.content}

                                        {/* Copy button that appears on hover */}
                                        <div
                                            className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <CopyButton
                                                content={msg.content}
                                                tooltipText="Copy message"
                                                position="left"
                                                variant="ghost"
                                                size="xs"
                                                className="text-gray-500 hover:bg-gray-200"
                                            />
                                        </div>
                                    </div>
                                </div>
                            );
                        }

                        return null;
                    })}
                    {
                        toolSelectionState.inProgress && (
                            <div className="flex items-center gap-2 text-sm text-gray-500 italic my-1 ml-8">
                                <div className="animate-pulse h-2 w-2 bg-purple-400 rounded-full"></div>
                                <span>Preparing to use: {toolSelectionState.toolName.replace(/-/g, ' ')}</span>
                            </div>
                        )
                    }
                    <div ref={messagesEndRef}/>
                </div>
            </ScrollArea>

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
            <div className="border-t dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm p-4 space-y-3 rounded-b-xl">
                {/* Add the file list here - before the message input */}
                {uploadedFiles.length > 0 && (
                    <div
                        className="my-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg max-h-32 overflow-y-auto border border-gray-300 dark:border-gray-600 shadow-sm">
                        <div className="text-xs font-medium text-gray-500 mb-2">Uploaded Files</div>
                        {uploadedFiles.map((file) => (
                            <div key={file.id}
                                 className={`file-item flex items-center justify-between mb-1 p-2 rounded border ${
                                     file.processing_status === 'failed' ? 'bg-red-50 dark:bg-red-900/50 border-red-200 dark:border-red-800' :
                                         file.processing_status === 'complete' ? 'bg-green-50 dark:bg-green-900/50 border-green-200 dark:border-green-800' : 'bg-gray-100 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
                                 }`}>
                                <span className="text-sm truncate max-w-[70%]">{file.name}</span>
                                <div className="flex items-center space-x-2">
                                    {file.processing_status === 'pending' &&
                                        <span
                                            className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/70 text-blue-700 dark:text-blue-300 rounded-full">Processing...</span>
                                    }
                                    {file.processing_status === 'failed' && (
                                        <span className="text-xs px-2 py-0.5 bg-red-100 dark:bg-red-900/70 text-red-700 dark:text-red-300 rounded-full"
                                              title={file.processing_error || "Error processing file"}>
                            Error
                        </span>
                                    )}
                                    {file.processing_status === 'complete' &&
                                        <span
                                            className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/70 text-green-700 dark:text-green-300 rounded-full">Ready</span>
                                    }
                                    <input
                                        type="checkbox"
                                        checked={file.selected}
                                        onChange={() => toggleFileSelection(file.id)}
                                        className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                <div className="flex gap-2">
                    {/* Hidden file input */}
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileSelection}
                        className="hidden"
                    />
                    
                    {/* Text input with action buttons */}
                    <div className="relative flex-1">
                        <textarea
                            placeholder="Type your message..."
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={handleKeyPress}
                            disabled={isStreaming}
                            rows="2"
                            className="w-full rounded-xl border border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm transition-colors
                            hover:bg-white/80 dark:hover:bg-gray-700/80 focus:border-blue-300 dark:focus:border-blue-600 focus:ring focus:ring-blue-200 dark:focus:ring-blue-800 focus:ring-opacity-50
                            placeholder-gray-400 dark:placeholder-gray-500 text-gray-900 dark:text-gray-100 py-2 pl-3 pr-12 resize-none"
                        />
                        
                        {/* Settings gear icon button - added above the file upload button */}
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
                            onClick={openFilePicker}
                            variant="ghost"
                            size="icon"
                            disabled={isStreaming || isUploading}
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
                        isProcessing={isStreaming || isUploading}
                        getChatCopyContent={getChatCopyContent}
                        getChatCopyHTML={getChatCopyHTML}
                        messages={messages}
                    />
                </div>
            </div>
        </Card>
    );
};

export default ChatInterface;