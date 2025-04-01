import React, {useState, useEffect, useRef} from 'react';
import ChatMessage from '@/components/replay_interface/ChatMessage';
import ToolCallDisplay from '@/components/chat_interface/ToolCallDisplay';
import ThoughtDisplay from '@/components/chat_interface/ThoughtDisplay';
import SystemPromptDisplay from "@/components/replay_interface/SystemPromptDisplay";
import ModelCardDisplay from '@/components/replay_interface/ModelCardDisplay';
import TokenUsageDisplay from '@/components/chat_interface/TokenUsageDisplay';
import MediaMessage from "@/components/chat_interface/MediaMessage";

const getVendor = (name) => {
    if (!name) return 'anthropic'; // Default to anthropic
    name = name.toLowerCase();
    if (name.includes('gpt') || name.includes('o1') || name.includes('o3')) {
        return 'openai';
    } else if (name.includes('claude')) {
        return 'anthropic';
    }
    return 'unknown';
};

/**
 * Normalizes event data from different possible structures
 * @param {Object} event - The event object to normalize
 * @returns {Object} - Normalized event data
 */
const normalizeEvent = (event) => {
    if (!event) return null;

    // If we get an array of events, log it but return a special marker
    // This allows the parent component to handle arrays properly
    if (Array.isArray(event)) {
        // console.log("Number of events in array is:", event.length);
        // Return a special flag to indicate this is an array of events
        // The parent component should handle this differently
        return {
            type: 'event_array',
            events: event,
            timestamp: new Date().toISOString()
        };
    }

    // Initialize variables at this scope so they're available for the return statement
    let type = 'unknown';
    let timestamp = '';
    let content = '';
    let toolCalls = [];
    let toolResults = [];
    let running = null;
    let active = null;
    let modelInfo = null;
    let toolNames = [];
    let tokenUsage = null;
    let vendor = 'unknown';
    let sessionId = null;
    let mediaContent = null;
    let mediaContentType = null;
    let mediaMetadata = null;

    // Grab the raw event data
    if (event.raw && event.raw.timestamp && (event.raw.event || event.raw.type)) {
        const rawData = event.raw;
        timestamp = rawData.timestamp;

        // Handle nested or flat structure in raw
        const eventData = rawData.event || rawData;
        type = eventData.type || 'unknown';

        // Extract vendor and session ID if available
        vendor = eventData.vendor || vendor;
        sessionId = eventData.session_id || sessionId;

        // Handle different event types and content extraction
        if (type === 'user_request' && eventData.data && eventData.data.message) {
            // User request with message in data.message
            content = eventData.data.message;
        } else if (type === 'completion') {
            // Special handling for completion events
            // console.log("Processing completion event data:", eventData);
            if (eventData.running === false) {
                // Only gather token data when running is false
                tokenUsage = {
                    prompt_tokens: eventData.input_tokens || 0,
                    completion_tokens: eventData.output_tokens || 0,
                    total_tokens: (eventData.input_tokens || 0) + (eventData.output_tokens || 0)
                };
            } else if (eventData.running === true) {
                // only get model/completion_opts when running is true
                const options = eventData.completion_options;

                if (options) {
                    // Extract model info (excluding system prompt)
                    modelInfo = {
                        model: options.model || 'Unknown Model',
                        temperature: options.temperature,
                        max_tokens: options.max_tokens
                    };

                    // If thinking is enabled, add the reasoning effort
                    if (options.thinking && options.thinking.type === 'enabled') {
                        // Claude style - uses thinking object
                        modelInfo.extended_thinking = true;

                        // budget_tokens is a value, not a function
                        if (options.thinking.budget_tokens !== undefined) {
                            modelInfo.budget_tokens = options.thinking.budget_tokens;
                        }
                    }

                    // OpenAI reasoning models
                    if (options.reasoning_effort !== undefined) {
                        modelInfo.reasoning_effort = options.reasoning_effort;
                    }

                    // Extract tool names
                    if (options.tools && Array.isArray(options.tools)) {
                        // First get the full tool names
                        const fullToolNames = options.tools.map(tool => {
                            // Handle OpenAI-style tools with nested function object
                            if (tool.type === 'function' && tool.function && tool.function.name) {
                                return tool.function.name;
                            }
                            // Handle Claude-style tools with direct name property
                            else if (tool.name) {
                                return tool.name;
                            }
                            // Fallback for unknown format
                            return 'unknown-tool';
                        });

                        // Then extract unique base tool names (before the first hyphen)
                        const baseToolSet = new Set();
                        fullToolNames.forEach(fullName => {
                            // Special case for tools without hyphens
                            if (!fullName.includes('-')) {
                                baseToolSet.add(fullName);
                            } else {
                                // Extract the part before the first hyphen
                                const baseName = fullName.split('-')[0];
                                baseToolSet.add(baseName);
                            }
                        });

                        // Convert Set to Array
                        toolNames = Array.from(baseToolSet);
                        // console.log('Found base tool categories:', toolNames);
                    }
                } else {
                    console.log('No completion options found in event data');
                }
            }

        } else if (type === 'system_prompt') {
            content = eventData.content || '';
        } else if (type === 'render_media') {
            // Extract media content and content type from render_media events
            console.log("Media Detals: ", eventData.data)
            if (eventData.data) {
                // Handle the specific format of the render_media event
                const mediaData = eventData.data;

                // Map the fields to match what MediaMessage expects
                mediaContent = mediaData.content || '';
                mediaContentType = mediaData.content_type || 'text/html';

                // Create metadata object with sent_by information if available
                mediaMetadata = {
                    sent_by_class: mediaData.sent_by_class || null,
                    sent_by_function: mediaData.sent_by_function || null
                };

                console.log('Extracted media data:', {
                    mediaContent,
                    mediaContentType,
                    mediaMetadata,
                    originalData: mediaData
                });
            }
        } else {
            // Default case for other event types
            content = eventData.content || '';
        }

        // Normalize tool calls and results
        toolCalls = eventData.tool_calls || [];
        toolResults = eventData.tool_results || [];
        running = eventData.running !== undefined ? eventData.running : null;
        active = eventData.active !== undefined ? eventData.active : null;
    }

    return {
        type,
        timestamp,
        content,
        toolCalls,
        toolResults,
        running,
        active,
        modelInfo,
        toolNames,
        tokenUsage,
        vendor,
        sessionId,
        mediaContent,
        mediaContentType,
        mediaMetadata,
        raw: event
    };
};

/**
 * EnhancedChatEventReplay component for replaying chat events
 */
const EnhancedChatEventReplay = ({
                                     events = [],
                                     currentEventIndex = 0,
                                     isPlaying = false,
                                     playbackSpeed = 1,
                                     onEventIndexChange = () => {
                                     }
                                 }) => {
    // State for processed messages
    const [messages, setMessages] = useState([]);

    // References for accumulating text - MODIFIED to track multiple assistant messages
    const assistantMessagesRef = useRef([]);
    const currentAssistantMessageRef = useRef(null);
    const thoughtMessagesRef = useRef([]);
    const currentThoughtMessageRef = useRef(null);

    // Keep track of previous event type for detecting changes
    const previousEventTypeRef = useRef(null);

    // Keep track of interactions
    const [currentInteraction, setCurrentInteraction] = useState(null);

    // State for active tool calls - changed to track tool call groups
    const toolCallGroupsRef = useRef([]);
    const currentToolCallGroupRef = useRef(null);

    // Model information from completion_options
    const [modelInfo, setModelInfo] = useState(null);

    // Keep track of processed event timestamps to prevent duplicate processing
    const processedEventIds = useRef(new Set());
    const [currentVendor, setCurrentVendor] = useState('unknown');

    // Process visible events into messages
    useEffect(() => {
        if (!events || events.length === 0) {
            console.log('No events available to process');
            thoughtMessagesRef.current = [];
            currentThoughtMessageRef.current = null;
            return;
        }

        console.log(`EnhancedChatEventReplay: Processing events up to index ${currentEventIndex} (total events: ${events.length})`);

        // Only process events up to the current index
        // Make sure we don't try to access beyond the array bounds
        const safeIndex = Math.min(currentEventIndex, events.length - 1);
        const visibleEvents = events.slice(0, safeIndex + 1);

        // Filter out events we've already processed to avoid duplicates
        // This is critical for preventing duplicate model cards and repeated processing
        const newUnprocessedEvents = visibleEvents.filter(event => {
            // Create a unique ID for each event based on timestamp and type
            const eventData = event.raw?.event || event.event || event;
            const eventType = eventData.type || 'unknown';
            const timestamp = event.timestamp || eventData.timestamp || Date.now();
            const eventId = `${timestamp}-${eventType}`;

            // If we've already processed this event, skip it
            if (processedEventIds.current.has(eventId)) {
                return false;
            }

            // Otherwise, mark it as processed and include it
            processedEventIds.current.add(eventId);
            return true;
        });

        // Only process new events if there are any
        if (newUnprocessedEvents.length > 0) {
            console.log(`Processing ${newUnprocessedEvents.length} new events`);
            processEvents(visibleEvents); // Still pass all visible events for context
        }
    }, [events, currentEventIndex]);

    /**
     * Process events into renderable messages
     */
    const processEvents = (visibleEvents) => {
        if (!visibleEvents || visibleEvents.length === 0) return;

        // Log the number of visible events being processed
        console.log(`Processing ${visibleEvents.length} visible events (out of ${events.length} total events)`);

        // Create a map to deduplicate messages by type+content hash
        // This ensures we don't create duplicate model cards or other elements
        const messageDeduplicationMap = new Map();
        const newMessages = [];

        // Reset our text accumulation references
        assistantMessagesRef.current = [];
        currentAssistantMessageRef.current = null;
        thoughtMessagesRef.current = [];
        currentThoughtMessageRef.current = null;
        previousEventTypeRef.current = null;
        toolCallGroupsRef.current = [];
        currentToolCallGroupRef.current = null;

        // Track which model cards we've already added
        const modelCardTracker = new Set();

        // Process each visible event
        visibleEvents.forEach((rawEvent) => {
            const event = normalizeEvent(rawEvent);
            if (!event) return;

            try {
                // Check if there's a change in event type
                const eventTypeChanged = previousEventTypeRef.current !== event.type;

                // If the event type changed from text_delta to something else, finalize the current assistant message
                if (previousEventTypeRef.current === 'text_delta' && event.type !== 'text_delta' && currentAssistantMessageRef.current) {
                    // console.log('Event type changed from text_delta to', event.type, '. Finalizing assistant message.');
                    currentAssistantMessageRef.current.isComplete = true;
                    currentAssistantMessageRef.current = null;
                }

                // If the event type changed from thought_delta to something else, finalize the current thought message
                if (previousEventTypeRef.current === 'thought_delta' && event.type !== 'thought_delta' && currentThoughtMessageRef.current) {
                    // console.log('Event type changed from thought_delta to', event.type, '. Finalizing thought message.');
                    currentThoughtMessageRef.current.isComplete = true;
                    currentThoughtMessageRef.current = null;
                }

                // Update the previous event type
                previousEventTypeRef.current = event.type;

                // Process the event based on its type
                switch (event.type) {
                    case 'system_prompt':
                        // console.log('Processing system prompt event:', event.type);
                        newMessages.push({
                            type: 'system',
                            content: event.content,
                            timestamp: event.timestamp
                        });
                        break;

                    case 'user_message':
                    case 'user_request':
                        // console.log('Processing user_request event:', event.type);
                        // Finalize any ongoing assistant message when a new user message arrives
                        if (currentAssistantMessageRef.current) {
                            currentAssistantMessageRef.current.isComplete = true;
                            currentAssistantMessageRef.current = null;
                        }
                        if (currentThoughtMessageRef.current) {
                            currentThoughtMessageRef.current.isComplete = true;
                            currentThoughtMessageRef.current = null;
                        }

                        // Reset the current tool call group
                        currentToolCallGroupRef.current = null;

                        // Add user message
                        newMessages.push({
                            type: 'user',
                            content: event.content,
                            timestamp: event.timestamp
                        });
                        break;

                    case 'text_delta':
                        // console.log('Processing text_delta event:', event.type);
                        // Create a new assistant message if there isn't an active one or if event type changed
                        if (!currentAssistantMessageRef.current || eventTypeChanged) {
                            // If there was a previous incomplete message, mark it as complete
                            if (currentAssistantMessageRef.current) {
                                currentAssistantMessageRef.current.isComplete = true;
                            }

                            // Create a new message
                            currentAssistantMessageRef.current = {
                                id: `assistant-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
                                text: '',
                                isComplete: false,
                                timestamp: event.timestamp
                            };
                            assistantMessagesRef.current.push(currentAssistantMessageRef.current);
                        }

                        // Accumulate assistant message text
                        currentAssistantMessageRef.current.text += event.content || '';
                        break;

                    case 'thought_delta':
                        // console.log('Processing thought_delta event:', event.type);
                        // Create a new thought message if there isn't an active one or if event type changed
                        if (!currentThoughtMessageRef.current || eventTypeChanged) {
                            // If there was a previous incomplete message, mark it as complete
                            if (currentThoughtMessageRef.current) {
                                currentThoughtMessageRef.current.isComplete = true;
                            }

                            // Create a new message
                            currentThoughtMessageRef.current = {
                                id: `thought-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
                                text: '',
                                isComplete: false,
                                timestamp: event.timestamp,
                                vendor: event.vendor || currentVendor
                            };
                            thoughtMessagesRef.current.push(currentThoughtMessageRef.current);
                        }

                        // Accumulate thought text
                        currentThoughtMessageRef.current.text += event.content || '';
                        break;

                    case 'tool_call':
                        // console.log('Processing tool_call event:', event.type);

                        // Finalize current assistant message when a tool call occurs
                        if (currentAssistantMessageRef.current && currentAssistantMessageRef.current.text) {
                            currentAssistantMessageRef.current.isComplete = true;
                            currentAssistantMessageRef.current = null;
                        }

                        // Process the tool call
                        if (event.toolCalls && event.toolCalls.length > 0) {
                            // Generate a unique group ID for these tool calls
                            const toolCallGroupId = `tool-group-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

                            // Check if we need to create a new tool call group
                            const isNewToolCallGroup =
                                !currentToolCallGroupRef.current ||  // No current group
                                checkIsDifferentToolCallSet(event.toolCalls, currentToolCallGroupRef.current.toolCalls); // Different set of calls

                            if (isNewToolCallGroup) {
                                // Create a new tool call group
                                // console.log('Creating new tool call group');
                                currentToolCallGroupRef.current = {
                                    id: toolCallGroupId,
                                    toolCalls: [],
                                    timestamp: event.timestamp,
                                    vendor: event.vendor
                                };
                                toolCallGroupsRef.current.push(currentToolCallGroupRef.current);
                            }

                            // Process and normalize the tool calls
                            const normalizedToolCalls = event.toolCalls.map(toolCall => {
                                // Extract the tool call ID based on vendor
                                const toolId = toolCall.id ||
                                    (toolCall.function ? toolCall.function.name + Date.now() : null) ||
                                    `tool-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

                                // Normalize arguments based on vendor format
                                const args = toolCall.input || toolCall.arguments || toolCall.parameters || {};

                                // Create a normalized tool call object
                                return {
                                    id: toolId,
                                    name: toolCall.name || (toolCall.function ? toolCall.function.name : 'unknown-tool'),
                                    arguments: typeof args === 'string' ? args : JSON.stringify(args),
                                    type: toolCall.type || 'function',
                                    timestamp: event.timestamp,
                                    results: null // Will be filled in when results arrive
                                };
                            });

                            // Update or add these tool calls to the current group
                            normalizedToolCalls.forEach(normalizedToolCall => {
                                // Check if this tool call already exists in the group
                                const existingIndex = currentToolCallGroupRef.current.toolCalls.findIndex(
                                    tc => tc.id === normalizedToolCall.id
                                );

                                if (existingIndex >= 0) {
                                    // Update the existing tool call
                                    currentToolCallGroupRef.current.toolCalls[existingIndex] = {
                                        ...currentToolCallGroupRef.current.toolCalls[existingIndex],
                                        ...normalizedToolCall
                                    };
                                } else {
                                    // Add the new tool call to the group
                                    currentToolCallGroupRef.current.toolCalls.push(normalizedToolCall);
                                }
                            });

                            // Process any tool results included with this event
                            if (event.toolResults && event.toolResults.length > 0) {
                                event.toolResults.forEach(result => {
                                    // Get the tool ID based on vendor format
                                    const toolId = result.tool_call_id || result.tool_use_id;

                                    if (toolId) {
                                        // Find the matching tool call
                                        const matchingToolCall = currentToolCallGroupRef.current.toolCalls.find(
                                            tc => tc.id === toolId
                                        );

                                        if (matchingToolCall) {
                                            // Add the results to the tool call
                                            matchingToolCall.results = result.content;
                                        }
                                    }
                                });
                            }
                        }
                        break;

                    case 'tool_results':
                        // console.log('Processing tool_results event:', event.type);
                        // Process standalone tool results (when not included with the tool call)
                        if (event.toolResults && event.toolResults.length > 0 && currentToolCallGroupRef.current) {
                            event.toolResults.forEach(result => {
                                // Get the tool ID based on vendor format
                                const toolId = result.tool_call_id || result.tool_use_id;

                                if (toolId) {
                                    // Find the matching tool call
                                    const matchingToolCall = currentToolCallGroupRef.current.toolCalls.find(
                                        tc => tc.id === toolId
                                    );

                                    if (matchingToolCall) {
                                        // Add the results to the tool call
                                        matchingToolCall.results = result.content;
                                    }
                                }
                            });
                        }
                        break;

                    case 'completion_options':
                        // Only process active completion options (for model information)
                        if (event.active && event.completionOptions) {
                            setModelInfo(event.completionOptions);
                        }
                        break;

                    case 'completion':
                    case 'completion_status':
                        // Start of a new completion - create a new assistant message
                        if (event.running === true) {
                            if (event.modelInfo) {
                                // console.log('Setting model info:', event.modelInfo);
                                setModelInfo(event.modelInfo);
                                const vendor = getVendor(event.modelInfo.model);
                                setCurrentVendor(vendor);

                                // Check if we need to start a new thought message
                                if (currentThoughtMessageRef.current && currentThoughtMessageRef.current.isComplete) {
                                    currentThoughtMessageRef.current = null;
                                }

                                // Check if we already have a model card with this model name
                                const existingModelCard = newMessages.find(msg =>
                                    msg.type === 'model_card' &&
                                    msg.modelName === event.modelInfo.model
                                );

                                // Only add a model card if we don't already have one for this model
                                if (!existingModelCard) {
                                    // console.log('Adding new model card for:', event.modelInfo.model);
                                    newMessages.push({
                                        type: 'model_card',
                                        modelName: event.modelInfo.model,
                                        modelParameters: event.modelInfo,
                                        toolNames: event.toolNames,
                                        timestamp: event.timestamp
                                    });
                                } else {
                                    // console.log('Model card already exists for:', event.modelInfo.model);
                                }
                            }

                            // Start a new assistant message for this completion if needed
                            if (currentAssistantMessageRef.current && currentAssistantMessageRef.current.isComplete) {
                                currentAssistantMessageRef.current = null;
                            }
                        }

                        // Mark the current assistant message as complete when completion finishes
                        if (event.running === false) {
                            if (currentAssistantMessageRef.current) {
                                currentAssistantMessageRef.current.isComplete = true;
                                if (event.tokenUsage) {
                                    // console.log('Adding token usage to assistant message:', event.tokenUsage);
                                    currentAssistantMessageRef.current.tokenUsage = event.tokenUsage;
                                }
                                currentAssistantMessageRef.current = null;
                            }

                            // Separately handle thought message completion
                            if (currentThoughtMessageRef.current) {
                                currentThoughtMessageRef.current.isComplete = true;
                                currentThoughtMessageRef.current = null;
                            }

                            // Mark the current tool call group as complete
                            currentToolCallGroupRef.current = null;
                        }
                        break;

                    case 'interaction_start':
                        setCurrentInteraction(event.content || 'Interaction');
                        break;

                    case 'interaction_end':
                        // Mark the current assistant message as complete when interaction ends
                        if (currentAssistantMessageRef.current) {
                            currentAssistantMessageRef.current.isComplete = true;
                            currentAssistantMessageRef.current = null;
                        }
                        if (currentThoughtMessageRef.current) {
                            currentThoughtMessageRef.current.isComplete = true;
                            currentThoughtMessageRef.current = null;
                        }

                        // Mark the current tool call group as complete
                        currentToolCallGroupRef.current = null;
                        break;
                    case "render_media":
                        // Add a new media message
                        const mediaMessageObject = {
                            content: event.mediaContent,
                            contentType: event.mediaContentType,
                            metadata: event.mediaMetadata
                        };
                        newMessages.push({
                            type: 'media',
                            message: mediaMessageObject,
                            timestamp: event.timestamp
                        });
                        break;

                    case 'interaction':
                        // Handle the interaction type which groups multiple events
                        // We don't need to do specific processing since we handle the individual events
                        break;
                    case 'history':
                        // Handle the history type contains all data for an interaction. Not used yet.
                        break;

                    case 'event_array':
                        // Process array of events
                        if (event.events && Array.isArray(event.events)) {
                            console.log(`Processing array of ${event.events.length} events`);
                            // The events will be processed separately by the parent component
                            // We don't need special handling here as ReplayInterface already flattens these arrays
                        }
                        break;
                    
                    default:
                        console.log(`Unhandled event type: ${event.type}`, event);
                }
            } catch (error) {
                console.error('Error processing event:', error, event);
            }
        });

        // Add all accumulated assistant messages
        assistantMessagesRef.current.forEach(assistantMessage => {
            if (assistantMessage.text && assistantMessage.text.trim() !== '') {
                newMessages.push({
                    type: 'assistant',
                    content: assistantMessage.text,
                    timestamp: assistantMessage.timestamp || new Date().toISOString(),
                    streaming: !assistantMessage.isComplete,
                    id: assistantMessage.id,  // Include the ID for proper keying
                    vendor: assistantMessage.vendor || currentVendor,
                    tokenUsage: assistantMessage.tokenUsage || null
                });
            }
        });

        // Add any accumulated thought text
        thoughtMessagesRef.current.forEach(thoughtMessage => {
            if (thoughtMessage.text && thoughtMessage.text.trim() !== '') {
                newMessages.push({
                    type: 'thought',
                    content: thoughtMessage.text,
                    timestamp: thoughtMessage.timestamp || new Date().toISOString(),
                    streaming: !thoughtMessage.isComplete,
                    id: thoughtMessage.id, // Include the ID for proper keying
                    vendor: thoughtMessage.vendor || currentVendor
                });
            }
        });

        // Add each tool call group as a separate message
        toolCallGroupsRef.current.forEach(toolCallGroup => {
            if (toolCallGroup.toolCalls && toolCallGroup.toolCalls.length > 0) {
                newMessages.push({
                    type: 'tool',
                    toolCalls: toolCallGroup.toolCalls,
                    timestamp: toolCallGroup.timestamp || new Date().toISOString(),
                    id: toolCallGroup.id
                });
            }
        });

        // Sort messages by timestamp
        newMessages.sort((a, b) => {
            return new Date(a.timestamp) - new Date(b.timestamp);
        });

        // Do a quick check to see if the message array has actually changed
        // This avoids unnecessary re-renders
        const messagesChanged = messages.length !== newMessages.length ||
            JSON.stringify(messages) !== JSON.stringify(newMessages);

        if (messagesChanged) {
            console.log('Message array has changed, updating state');
            setMessages(newMessages);
        } else {
            console.log('No changes to message array, skipping update');
        }
    };

    /**
     * Checks if a set of tool calls is different from those in a current group
     * Used to determine when to create a new group of tool calls
     */
    const checkIsDifferentToolCallSet = (newToolCalls, existingToolCalls) => {
        // Early check - if lengths are different, it's a different set
        if (!newToolCalls || !existingToolCalls || newToolCalls.length !== existingToolCalls.length) {
            return true;
        }

        // Check if all tool call IDs in the new set exist in current group
        const newIds = new Set(newToolCalls.map(tc => tc.id));
        const existingIds = new Set(existingToolCalls.map(tc => tc.id));

        // If a new ID is not in the existing set, it's a different group
        for (const id of newIds) {
            if (!existingIds.has(id)) {
                return true;
            }
        }

        // If we get here, it's the same set of tool calls
        return false;
    };

    // Playback controls
    const handlePlay = () => onEventIndexChange(currentEventIndex);
    const handlePause = () => onEventIndexChange(currentEventIndex);
    const handleReset = () => {
        assistantMessagesRef.current = [];
        currentAssistantMessageRef.current = null;
        thoughtMessagesRef.current = [];
        currentThoughtMessageRef.current = null;
        previousEventTypeRef.current = null;
        toolCallGroupsRef.current = [];
        currentToolCallGroupRef.current = null;
        onEventIndexChange(0);
    };

    return (
        <div className="enhanced-chat-replay flex flex-col space-y-4">
            <div className="mb-4 flex items-center space-x-4">
                <button
                    onClick={isPlaying ? handlePause : handlePlay}
                    className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                    {isPlaying ? 'Pause' : 'Play'}
                </button>
                <button
                    onClick={handleReset}
                    className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
                >
                    Reset
                </button>
                <div className="text-sm text-gray-500">
                    Event {currentEventIndex + 1} of {events && events.length > 0 ? events.length : '?'}
                    {events && events.length > 0 &&
                        <span className="ml-2">({Math.round((currentEventIndex + 1) / events.length * 100)}%)</span>}
                </div>
            </div>

            <div className="chat-messages space-y-4">
                {messages.map((message, i) => {
                    // Render different content based on message type
                    if (message.type === 'user') {
                        return (
                            <ChatMessage
                                key={`user-${i}-${message.timestamp}`}
                                role="user"
                                content={message.content}
                                timestamp={message.timestamp}
                            />
                        );
                    } else if (message.type === 'assistant') {
                        return (
                            <ChatMessage
                                key={`assistant-${message.id || i}-${message.timestamp}`}
                                role="assistant"
                                content={message.content}
                                timestamp={message.timestamp}
                                streaming={message.streaming}
                                vendor={message.vendor}
                                tokenUsage={message.tokenUsage}
                            />
                        );
                    } else if (message.type === 'thought') {
                        return (
                            <ThoughtDisplay
                                key={`thought-${message.id || i}-${message.timestamp}`}
                                content={message.content}
                                vendor={message.vendor}
                            />
                        );
                    } else if (message.type === 'system') {
                        return (
                            <SystemPromptDisplay
                                key={`system-${i}-${message.timestamp}`}
                                content={message.content}
                            />
                        );
                    } else if (message.type === 'tool') {
                        return (
                            <ToolCallDisplay
                                key={`tool-${message.id || i}-${message.timestamp}`}
                                toolCalls={message.toolCalls}
                            />
                        );
                    } else if (message.type === 'media') {
                        return (
                            <MediaMessage
                                key={`media-${i}-${message.timestamp}`}
                                message={message.message}
                            />
                        );
                    } else if (message.type === 'model_card') {
                        return (
                            <div key={`model-card-${i}-${message.timestamp}`} className="mx-auto w-full max-w-3xl">
                                <ModelCardDisplay
                                    modelName={message.modelName}
                                    modelParameters={message.modelParameters}
                                    toolNames={message.toolNames}
                                />
                            </div>
                        );
                    } else if (message.type === 'token_usage') {
                        return (
                            <div key={`token-usage-${i}-${message.timestamp}`} className="mx-auto w-full max-w-3xl">
                                <TokenUsageDisplay usage={message.usage}/>
                            </div>
                        );
                    }
                    return null;
                })}
            </div>
        </div>
    );
};

export default EnhancedChatEventReplay;