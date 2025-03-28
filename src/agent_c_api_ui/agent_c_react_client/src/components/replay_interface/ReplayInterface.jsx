import React, { useState, useEffect, useRef } from 'react';
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TabsContent, Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Clock, Code, MessageSquare, List } from "lucide-react";
import EnhancedChatEventReplay from './EnhancedChatEventReplay';
import EventDisplay from './EventDisplay';
import ModelCardDisplay from './ModelCardDisplay';
import SystemPromptDisplay from './SystemPromptDisplay';
import { API_URL } from "@/config/config";

/**
 * ReplayInterface is the main component for replaying chat sessions
 * It provides tabs to switch between chat view, raw events view, and settings
 *
 * @component
 * @param {Object} props
 * @param {string} props.sessionId - The session ID to replay
 */
const ReplayInterface = ({ sessionId }) => {
  const [sessionInfo, setSessionInfo] = useState(null);
  const [events, setEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [playbackSettings, setPlaybackSettings] = useState({
    speed: 1,
    autoPlay: false
  });
  const [currentEventIndex, setCurrentEventIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const eventSourceRef = useRef(null);

  // Fetch session info when sessionId changes
  useEffect(() => {
    const fetchSessionInfo = async () => {
      if (!sessionId) return;

      try {
        setIsLoading(true);

        // Fetch session info
        const sessionResponse = await fetch(`${API_URL}/interactions/${sessionId}`);
        if (!sessionResponse.ok) {
          throw new Error(`HTTP error! status: ${sessionResponse.status}`);
        }
        const sessionData = await sessionResponse.json();
        setSessionInfo(sessionData);

        // Fetch initial events (non-streaming) for UI setup
        await fetchInitialEvents();

        setIsLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError(`Error: ${error.message}`);
        setIsLoading(false);
      }
    };

    fetchSessionInfo();

    // Cleanup function to close eventSource if component unmounts
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [sessionId]);

  // Effect for handling streaming based on playback state
  useEffect(() => {
    if (isPlaying) {
      startEventStream();
    } else {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    }
    
    // Log the current state of events
    console.log(`Playback state changed - isPlaying: ${isPlaying}, events: ${events.length}, currentIndex: ${currentEventIndex}`);

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [isPlaying, playbackSettings.speed, sessionId]);

  const fetchInitialEvents = async () => {
    try {
      // Fetch initial events (limited to improve load time)
      const eventsResponse = await fetch(`${API_URL}/events/${sessionId}?limit=1000`);
      if (!eventsResponse.ok) {
        throw new Error(`HTTP error! status: ${eventsResponse.status}`);
      }

      const eventData = await eventsResponse.json();
      // Make sure we're always dealing with an array of events
      const parsedEvents = Array.isArray(eventData) ? eventData : [eventData];
      
      // Log the actual number of events fetched
      console.log(`Loaded ${parsedEvents.length} events from the API`);
      
      setEvents(parsedEvents);
      // If events exist, set the currentEventIndex properly
      if (parsedEvents.length > 0) {
        // Start at the beginning by default
        setCurrentEventIndex(0);
      }
      
      return parsedEvents;
    } catch (error) {
      console.error("Error fetching initial events:", error);
      throw error;
    }
  };

  const startEventStream = () => {
    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      // Connect to the streaming endpoint with proper parameters
      const streamUrl = `${API_URL}/events/${sessionId}/stream?real_time=true&speed_factor=${playbackSettings.speed}`;
      console.log('Connecting to stream:', streamUrl);
      const eventSource = new EventSource(streamUrl);

      eventSource.onopen = () => {
        console.log('EventSource connection opened');
      };

      eventSource.onmessage = (e) => {
        console.log('Received event data:', e.data);
        try {
          // Handle possible data format issues
          if (!e.data || e.data.trim() === '') {
            console.warn('Empty event data received');
            return;
          }

          // For SSE, the data field might contain "data: {json}" format
          // If it has this prefix, extract just the JSON part
          let dataStr = e.data;
          if (dataStr.startsWith('data: ')) {
            dataStr = dataStr.substring(6);
          }

          const eventData = JSON.parse(dataStr);
          
          // Generate a unique ID for this event to detect duplicates more reliably
          const eventType = eventData.event?.type || eventData.type || 'unknown';
          const timestamp = eventData.timestamp || new Date().toISOString();
          const eventId = `${timestamp}-${eventType}-${JSON.stringify(eventData).slice(0, 50)}`; // Include part of content for uniqueness

          // Check if this event already exists in our array to avoid duplicates
          const isDuplicate = events.some(existingEvent => {
            const existingType = existingEvent.event?.type || existingEvent.type || 'unknown';
            const existingTimestamp = existingEvent.timestamp || '';
            const existingContent = JSON.stringify(existingEvent).slice(0, 50);
            return existingTimestamp === timestamp && 
                  existingType === eventType && 
                  existingContent === JSON.stringify(eventData).slice(0, 50);
          });

          if (!isDuplicate) {
            console.log('Adding new event:', eventType, 'at time:', timestamp);
            
            // Update events state with appropriate handling for arrays
            setEvents(prevEvents => {
              let newEvents;
              
              // Handle array events properly
              if (Array.isArray(eventData)) {
                console.log('Received array of events:', eventData.length);
                newEvents = [...prevEvents, ...eventData];
              } else {
                newEvents = [...prevEvents, eventData];
              }
              
              // Keep events sorted by timestamp
              const sortedEvents = newEvents.sort((a, b) => {
                const timeA = a.timestamp || '';
                const timeB = b.timestamp || '';
                return new Date(timeA) - new Date(timeB);
              });
              
              // If we're playing, update the currentEventIndex properly
              if (isPlaying) {
                // Use setTimeout to ensure this happens after the state update
                setTimeout(() => {
                  // Find the index of the newly added event in the sorted array
                  const newIndex = sortedEvents.findIndex(e => {
                    const eType = e.event?.type || e.type || 'unknown';
                    const eTimestamp = e.timestamp || '';
                    const eContent = JSON.stringify(e).slice(0, 50);
                    return eTimestamp === timestamp && 
                           eType === eventType && 
                           eContent === JSON.stringify(eventData).slice(0, 50);
                  });
                  
                  // Only update if we found the event and it's beyond our current position
                  if (newIndex !== -1 && newIndex > currentEventIndex) {
                    setCurrentEventIndex(newIndex);
                    console.log(`Updated current event index to ${newIndex}`);
                  }
                }, 10);
              }
              
              return sortedEvents;
            });
          } else {
            console.log('Skipped duplicate event:', eventType, 'at time:', timestamp);
          }
        } catch (err) {
          console.error('Error processing event data:', err);
        }
      };

      eventSource.onerror = (err) => {
        console.error('EventSource error:', err);

        // Check if connection was closed due to error
        if (eventSource.readyState === EventSource.CLOSED) {
          console.error('EventSource connection was closed due to error');
        }

        // Close the connection and clean up
        eventSource.close();
        setIsPlaying(false);

        // Fallback to polling method if streaming fails
        console.log('Falling back to polling mode...');
        fetchInitialEvents();
      };

      eventSourceRef.current = eventSource;

    } catch (err) {
      console.error('Failed to establish event stream:', err);
      setError('Failed to establish event stream connection');
      setIsPlaying(false);
    }
  };

  // Handle playback control
  const handlePlayPauseToggle = async () => {
    const newPlayingState = !isPlaying;
    setIsPlaying(newPlayingState);

    // Send control request to the API
    try {
      const response = await fetch(`${API_URL}/events/${sessionId}/replay/control`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: newPlayingState ? 'play' : 'pause',
          position: null
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Failed to control replay:', errorText);
      }
    } catch (err) {
      console.error('Error controlling replay:', err);
    }
  };

  // Update playback settings
  const handleSpeedChange = (speed) => {
    setPlaybackSettings(prev => ({ ...prev, speed }));

    // If we're currently playing, restart the stream with the new speed
    if (isPlaying) {
      // Briefly pause to reset the stream
      setIsPlaying(false);
      // Small delay to ensure the state updates before we start again
      setTimeout(() => {
        setIsPlaying(true);
      }, 100);
    }
  };

  const handleAutoPlayToggle = () => {
    const newAutoPlay = !playbackSettings.autoPlay;
    setPlaybackSettings(prev => ({ ...prev, autoPlay: newAutoPlay }));

    // If turning on autoPlay, also start playing
    if (newAutoPlay && !isPlaying) {
      setIsPlaying(true);
    }
  };

  // Helper to extract system prompt from events
  const getSystemPrompt = () => {
    const systemPromptEvent = events.find(event => {
      if (event.type === 'system_prompt') return true;
      if (event.event?.type === 'system_prompt') return true;
      if (event.raw?.event?.type === 'system_prompt') return true;
      return false;
    });

    if (systemPromptEvent) {
      return systemPromptEvent.content ||
             systemPromptEvent.event?.content ||
             systemPromptEvent.raw?.event?.content ||
             '';
    }

    return '';
  };

  // Helper to get model info from events
  const getModelInfo = () => {
    // Look for completion_options event with active flag
    const completionOptionsEvent = events.find(event => {
      const eventData = event.raw?.event || event.event || event;
      return eventData.type === 'completion_options' && eventData.active === true;
    });

    if (completionOptionsEvent) {
      const options = completionOptionsEvent.raw?.event?.completion_options ||
                     completionOptionsEvent.event?.completion_options ||
                     completionOptionsEvent.completion_options || {};
      return {
        modelName: options.model || 'unknown',
        parameters: {
          temperature: options.temperature,
          reasoning_effort: options.reasoning_effort
        }
      };
    }

    // Fallback: look for completion event with model info
    const completionEvent = events.find(event => {
      const eventData = event.raw?.event || event.event || event;
      return eventData.type === 'completion' &&
             (eventData.completion_options?.model || eventData.model);
    });

    if (completionEvent) {
      const options = completionEvent.raw?.event?.completion_options ||
                      completionEvent.event?.completion_options ||
                      completionEvent.completion_options || {};
      return {
        modelName: options.model || 'unknown',
        parameters: {
          temperature: options.temperature,
          reasoning_effort: options.reasoning_effort
        }
      };
    }

    return {
      modelName: 'unknown',
      parameters: {}
    };
  };

  if (isLoading) {
    return (
      <Card className="p-8 flex justify-center items-center">
        <div className="text-gray-500">Loading session data...</div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-8 flex justify-center items-center">
        <div className="text-red-500">{error}</div>
      </Card>
    );
  }

  const modelInfo = getModelInfo();
  const systemPrompt = getSystemPrompt();

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Session Replay: {sessionId}</h1>

      <div className="mb-6 space-y-4">
        <ModelCardDisplay
          modelName={modelInfo.modelName}
          modelParameters={modelInfo.parameters}
        />

        <SystemPromptDisplay content={systemPrompt} />
      </div>

      <Tabs defaultValue="chat" className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Chat View
          </TabsTrigger>
          <TabsTrigger value="events" className="flex items-center gap-2">
            <Code className="h-4 w-4" />
            Raw Events
          </TabsTrigger>
          <TabsTrigger value="timeline" className="flex items-center gap-2">
            <Clock className="h-4 w-4" />
            Timeline
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex items-center gap-2">
            <List className="h-4 w-4" />
            Settings
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <Card className="p-4 mb-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-medium">Chat Replay</h2>
              <div className="flex items-center gap-2">
                <Button
                  onClick={handlePlayPauseToggle}
                  variant={isPlaying ? "default" : "outline"}
                  size="sm">
                  {isPlaying ? "Pause" : "Play"}
                </Button>
                <span className="text-sm">
                  Event: {currentEventIndex + 1} of {events.length}
                </span>
              </div>
            </div>
          </Card>
          <EnhancedChatEventReplay
            events={events.flatMap(event => {
              // If the event is an array or has a special type 'event_array', expand it
              if (Array.isArray(event)) {
                return event;
              } else if (event.type === 'event_array' && Array.isArray(event.events)) {
                return event.events;
              }
              return event;
            })}
            currentEventIndex={currentEventIndex}
            isPlaying={isPlaying}
            playbackSpeed={playbackSettings.speed}
            onEventIndexChange={setCurrentEventIndex}
          />
        </TabsContent>

        <TabsContent value="events" className="space-y-4">
          <Card className="p-4">
            <h2 className="text-lg font-medium mb-4">Raw Events</h2>
            <div className="space-y-4">
              {events.slice(0, currentEventIndex + 1).map((event, index) => (
                <EventDisplay key={`${event.timestamp}-${index}`} event={event} />
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="timeline" className="space-y-4">
          <Card className="p-4">
            <h2 className="text-lg font-medium mb-4">Event Timeline</h2>
            <div className="relative">
              <div className="border-l-2 border-gray-200 ml-4">
                {events.map((event, index) => {
                  const normalizedEvent = event.event || event;
                  const eventType = normalizedEvent.type || 'unknown';
                  const timestamp = event.timestamp || normalizedEvent.timestamp;
                  const formattedTime = timestamp
                    ? new Date(timestamp).toLocaleTimeString()
                    : 'unknown time';

                  return (
                    <div
                      key={`${timestamp}-${index}`}
                      className={`ml-6 mb-4 relative ${index <= currentEventIndex ? 'opacity-100' : 'opacity-50'}`}
                      onClick={() => setCurrentEventIndex(index)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className={`absolute -left-8 mt-1 w-4 h-4 rounded-full ${index <= currentEventIndex ? 'bg-blue-500' : 'bg-gray-300'}`}></div>
                      <div className="text-xs text-gray-500">{formattedTime}</div>
                      <div className="text-sm font-medium">{eventType}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>
        </TabsContent>
        
        <TabsContent value="settings" className="space-y-4">
          <Card className="p-4">
            <h2 className="text-lg font-medium mb-4">Playback Settings</h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium mb-2">Playback Speed</h3>
                <div className="flex space-x-2">
                  <Button 
                    onClick={() => handleSpeedChange(0.5)} 
                    variant={playbackSettings.speed === 0.5 ? "default" : "outline"} 
                    size="sm">
                    0.5x
                  </Button>
                  <Button 
                    onClick={() => handleSpeedChange(1)} 
                    variant={playbackSettings.speed === 1 ? "default" : "outline"} 
                    size="sm">
                    1x
                  </Button>
                  <Button 
                    onClick={() => handleSpeedChange(2)} 
                    variant={playbackSettings.speed === 2 ? "default" : "outline"} 
                    size="sm">
                    2x
                  </Button>
                  <Button 
                    onClick={() => handleSpeedChange(4)} 
                    variant={playbackSettings.speed === 4 ? "default" : "outline"} 
                    size="sm">
                    4x
                  </Button>
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium mb-2">Auto-Play</h3>
                <Button 
                  onClick={handleAutoPlayToggle} 
                  variant={playbackSettings.autoPlay ? "default" : "outline"} 
                  size="sm">
                  {playbackSettings.autoPlay ? "Enabled" : "Disabled"}
                </Button>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReplayInterface;