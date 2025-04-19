// src/components/replay_interface/ReplayPage.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { API_URL } from '@/config/config';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import {
  PlayCircle,
  PauseCircle,
  SkipForward,
  SkipBack,
  RefreshCw,
  ChevronLeft,
  FastForward,
  Trash2
} from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import EnhancedChatEventReplay from './EnhancedChatEventReplay';

const ReplayPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [currentEventIndex, setCurrentEventIndex] = useState(0);
  const [sessionInfo, setSessionInfo] = useState(null);
  const [showingAll, setShowingAll] = useState(false);
  const [isLoadingAll, setIsLoadingAll] = useState(false);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    fetchSessionInfo();
    return () => {
      // Clean up EventSource when component unmounts
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [sessionId]);

  // Helper function to reset event state
  const resetEvents = () => {
    setEvents([]);
    setCurrentEventIndex(0);
    setShowingAll(false);
  };

  // Effect for handling streaming
  useEffect(() => {
    // Add debugging for the events array
    console.log(`Current events array: ${events.length} events`);
    if (events.length > 0) {
      // Log a sample event to see its structure
      console.log('Sample event structure:', JSON.stringify(events[0]).substring(0, 200));
    }

    if (isPlaying && !showingAll) {
      // If we're about to start playing, clear events first to avoid duplicate issues
      if (events.length > 0) {
        resetEvents();
        // Use setTimeout to ensure state updates before starting the stream
        setTimeout(() => {
          startEventStream();
        }, 50);
      } else {
        startEventStream();
      }
    } else {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    }

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [isPlaying, playbackSpeed, sessionId, showingAll]);

  const fetchSessionInfo = async () => {
    try {
      const response = await fetch(`${API_URL}/interactions/${sessionId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSessionInfo(data);

      // Initial fetch of events to populate the timeline
      // This will load the events without streaming for initial display
      fetchInitialEvents();
    } catch (err) {
      console.error('Error fetching session info:', err);
      setError('Failed to load session information');
    }
  };

  const fetchInitialEvents = async () => {
    try {
      setLoading(true);
      // Fetch just enough events to show the timeline without streaming
      const response = await fetch(`${API_URL}/events/${sessionId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const text = await response.text();
      
      let parsedEvents = [];
      
      try {
        // First try as a single JSON object or array
        const jsonData = JSON.parse(text);
        
        if (Array.isArray(jsonData)) {
          parsedEvents = jsonData;
        } else if (jsonData.events && Array.isArray(jsonData.events)) {
          parsedEvents = jsonData.events;
        } else if (jsonData.data && Array.isArray(jsonData.data)) {
          parsedEvents = jsonData.data;
        } else {
          parsedEvents = [jsonData];
        }
      } catch (jsonError) {
        // Fall back to NDJSON format
        try {
          const eventLines = text.trim().split('\n');
          parsedEvents = eventLines
            .filter(line => line.trim())
            .map(line => JSON.parse(line));
        } catch (lineError) {
          console.error("Failed to parse events as NDJSON", lineError);
          throw new Error("Could not parse event data in any known format");
        }
      }
      
      // Handle complex event structures
      const expandedEvents = parsedEvents.flatMap(event => {
        if (event.type === 'event_array' && Array.isArray(event.events)) {
          return event.events;
        }
        if (event.events && Array.isArray(event.events)) {
          return event.events;
        }
        return event;
      });

      // Sort by timestamp
      const sortedEvents = expandedEvents.sort((a, b) => {
        const getTimestamp = (event) => {
          if (event.timestamp) return event.timestamp;
          if (event.raw && event.raw.timestamp) return event.raw.timestamp;
          if (event.event && event.event.timestamp) return event.event.timestamp;
          return '';
        };
        
        const timeA = getTimestamp(a);
        const timeB = getTimestamp(b);
        return new Date(timeA) - new Date(timeB);
      });

      setEvents(sortedEvents);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching initial events:', err);
      setError('Failed to load session events: ' + err.message);
      setLoading(false);
    }
  };

  const startEventStream = () => {
    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }

    try {
      // Connect to the streaming endpoint
      const streamUrl = `${API_URL}/events/${sessionId}/stream?real_time=true&speed_factor=${playbackSpeed}`;
      console.log('Connecting to stream:', streamUrl);
      
      // Create a new EventSource with the stream URL
      const eventSource = new EventSource(streamUrl);

      // Add an event handler for when the connection opens
      eventSource.onopen = () => {
        console.log('EventSource connection opened successfully');
      };

      eventSource.onmessage = (e) => {
        try {
          console.log('Received event data:', e.data.substring(0, 100) + '...');
          
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
          
          // Check if this is a stream_complete message
          if (eventData.type === 'stream_complete') {
            console.log('Stream complete message received:', eventData.message);
            // Close the connection gracefully
            eventSource.close();
            setIsPlaying(false);
            return;
          }

          // Check if this event already exists in our array to avoid duplicates
          // Get the type from the event data - it could be at different levels depending on the format
          const eventType = eventData.type || eventData.event?.type || null;
          const eventTimestamp = eventData.timestamp || '';
          
          // Look for any existing event with the same timestamp and type
          const isDuplicate = events.some(existingEvent => {
            // Handle different event structures
            const existingType = existingEvent.type || existingEvent.event?.type || null;
            const existingTimestamp = existingEvent.timestamp || '';
            
            const typeMatch = existingType === eventType;
            const timestampMatch = existingTimestamp === eventTimestamp;
            
            // Only consider it a duplicate if both timestamp and type match
            return typeMatch && timestampMatch && existingTimestamp !== '';
          });

          if (!isDuplicate) {
            // Handle array events
            if (Array.isArray(eventData)) {
              console.log(`Received array of ${eventData.length} events`);
              // Update events state with the array
              setEvents(prevEvents => {
                const combined = [...prevEvents, ...eventData];
                // Keep events sorted by timestamp
                return combined.sort((a, b) =>
                  new Date(a.timestamp || 0) - new Date(b.timestamp || 0)
                );
              });
              
              // Advance current event index to the end of the array
              setCurrentEventIndex(prevIndex => {
                return prevIndex + eventData.length;
              });
            } 
            // Handle event array container
            else if (eventData.events && Array.isArray(eventData.events)) {
              console.log(`Received event container with ${eventData.events.length} events`);
              // Update events state with the events array
              setEvents(prevEvents => {
                const combined = [...prevEvents, ...eventData.events];
                // Keep events sorted by timestamp
                return combined.sort((a, b) =>
                  new Date(a.timestamp || 0) - new Date(b.timestamp || 0)
                );
              });
              
              // Advance current event index to the end of the array
              setCurrentEventIndex(prevIndex => {
                return prevIndex + eventData.events.length;
              });
            }
            // Handle single event
            else {
              setEvents(prevEvents => {
                const newEvents = [...prevEvents, eventData];
                // Keep events sorted by timestamp
                return newEvents.sort((a, b) =>
                  new Date(a.timestamp || 0) - new Date(b.timestamp || 0)
                );
              });

              // Advance current event index to show the latest event if we're playing
              setCurrentEventIndex(prevIndex => {
                return prevIndex + 1;
              });
            }
          } else {
            console.log('Skipped duplicate event');
          }
        } catch (err) {
          console.error('Error processing event data:', err, e.data);
        }
      };

      eventSource.onerror = (err) => {
        console.error('EventSource error:', err);
        
        // Check if the connection was closed due to error
        if (eventSource.readyState === EventSource.CLOSED) {
          console.log('EventSource connection was closed due to error');
        }
        
        // Handle the error and implement a fallback strategy
        console.log('Stream connection failed, falling back to manual events loading');
        
        // Close the existing connection to clean up
        eventSource.close();
        eventSourceRef.current = null;
        
        // Pause the playback since streaming failed
        setIsPlaying(false);
        
        // Show an error message but don't set the error state (to avoid full page error)
        console.error('Streaming error: Using cached events instead');
        
        // We keep the current events and allow manual navigation
      };

      // Store the event source in the ref so we can close it later
      eventSourceRef.current = eventSource;

    } catch (err) {
      console.error('Failed to establish event stream:', err);
      setError('Failed to establish event stream connection. Try using "Show All" instead.');
      setIsPlaying(false);
    }
  };

  // Function to extract events from various container formats
  const extractEvents = (data) => {
    if (Array.isArray(data)) {
      // It's already an array of events
      return data;
    }
    
    // Check for an events array property
    if (data.events && Array.isArray(data.events)) {
      return data.events;
    }
    
    // Check for a data array property
    if (data.data && Array.isArray(data.data)) {
      return data.data;
    }
    
    // Check for a raw array property
    if (data.raw && Array.isArray(data.raw)) {
      return data.raw;
    }
    
    // If it's a single event object with no array property
    return [data];
  };
  
  // Fetch all events at once for "Show All" mode
  const fetchAllEvents = async () => {
    setIsLoadingAll(true);
    setError(null); // Clear any previous errors
    
    try {
      // Close any existing event stream
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      
      // Pause playback when fetching all events
      setIsPlaying(false);
      
      console.log("Fetching all events for session:", sessionId);
      // Set a high limit to get all events
      const url = `${API_URL}/events/${sessionId}?limit=100000`;
      console.log("Request URL:", url);
      
      const eventsResponse = await fetch(url);
      if (!eventsResponse.ok) {
        throw new Error(`HTTP error! status: ${eventsResponse.status}`);
      }

      // Get the response content type to determine parsing strategy
      const contentType = eventsResponse.headers.get('content-type') || '';
      console.log("Response content type:", contentType);
      
      // Get the response as text first
      const text = await eventsResponse.text();
      console.log("Fetched response length:", text.length);
      
      if (text.length === 0) {
        console.warn("Empty response when fetching events");
        setError('No events found. The server returned an empty response.');
        setIsLoadingAll(false);
        return;
      }
      
      let parsedEvents = [];
      
      // Try different parsing strategies
      try {
        // First try as a single JSON object or array
        const jsonData = JSON.parse(text);
        console.log("Successfully parsed JSON, type:", Array.isArray(jsonData) ? "array" : typeof jsonData);
        
        // Extract events based on the structure
        parsedEvents = extractEvents(jsonData);
      } catch (jsonError) {
        console.log("Failed to parse as single JSON, trying line-by-line", jsonError);
        
        // Fall back to NDJSON format (one JSON object per line)
        try {
          const eventLines = text.trim().split('\n');
          console.log("Found", eventLines.length, "lines in NDJSON format");
          
          // Parse each line as JSON and filter out any errors
          const lineEvents = [];
          eventLines.forEach((line, i) => {
            try {
              if (line.trim()) {
                const eventData = JSON.parse(line);
                lineEvents.push(eventData);
              }
            } catch (lineErr) {
              console.error(`Error parsing line ${i}:`, lineErr, line.substring(0, 100));
            }
          });
          
          parsedEvents = lineEvents;
        } catch (lineError) {
          console.error("Failed to parse events as NDJSON", lineError);
          throw new Error("Could not parse event data in any known format");
        }
      }
      
      console.log(`Initially parsed ${parsedEvents.length} events`);
      
      // Handle complicated nested structures with multiple levels of events
      let expandedEvents = [];
      const processEvent = (event) => {
        // Check if this is an event array container
        if (event.type === 'event_array' && Array.isArray(event.events)) {
          console.log(`Found event_array with ${event.events.length} events`);
          event.events.forEach(processEvent);
        }
        // Check if this has a raw.events array
        else if (event.raw && Array.isArray(event.raw)) {
          console.log(`Found event with raw array of ${event.raw.length} events`);
          event.raw.forEach(processEvent);
        }
        // Check if this has an events array property
        else if (event.events && Array.isArray(event.events)) {
          console.log(`Found events array with ${event.events.length} events`);
          event.events.forEach(processEvent);
        }
        // It's a regular event, add it to our collection
        else {
          expandedEvents.push(event);
        }
      };
      
      // Process each event to expand nested arrays
      parsedEvents.forEach(processEvent);
      
      if (expandedEvents.length > parsedEvents.length) {
        console.log(`Expanded from ${parsedEvents.length} to ${expandedEvents.length} total events`);
        parsedEvents = expandedEvents;
      }
      
      if (parsedEvents.length === 0) {
        console.warn("No events were found after parsing");
        setError('No events were found. Try regular playback instead.');
        setIsLoadingAll(false);
        return;
      }
      
      console.log(`Final count: ${parsedEvents.length} events ready for display`);
      
      // Sort events by timestamp, handling various timestamp locations
      const sortedEvents = parsedEvents.sort((a, b) => {
        // Extract timestamp from either direct property or nested event structure
        const getTimestamp = (event) => {
          if (event.timestamp) return event.timestamp;
          if (event.raw && event.raw.timestamp) return event.raw.timestamp;
          if (event.event && event.event.timestamp) return event.event.timestamp;
          return '';
        };
        
        const timeA = getTimestamp(a);
        const timeB = getTimestamp(b);
        return new Date(timeA || 0) - new Date(timeB || 0);
      });
      
      // Update the events array
      console.log("Setting events array with", sortedEvents.length, "events");
      setEvents(sortedEvents);
      
      // Use a timeout to ensure state updates have propagated
      setTimeout(() => {
        // Set to show the last event
        setCurrentEventIndex(sortedEvents.length - 1);
        setShowingAll(true);
        setIsLoadingAll(false);
        console.log("Show All completed. Current index set to", sortedEvents.length - 1);
      }, 200);
      
    } catch (error) {
      console.error("Error fetching all events:", error);
      setError('Failed to load all events: ' + error.message);
      setIsLoadingAll(false);
    }
  };

  // Reset from "Show All" mode back to streaming mode
  const handleResetToStreaming = async () => {
    setShowingAll(false);
    setIsPlaying(false);
    
    // Reload initial events to reset the state
    await fetchInitialEvents();
    
    // Reset to the first event
    setCurrentEventIndex(0);
  };

  const handlePlayPause = async () => {
    // If showing all events, just toggle the play state locally
    if (showingAll) {
      setIsPlaying(!isPlaying);
      return;
    }
    
    // If we're starting playback, reset events to avoid any issues with duplicates
    if (!isPlaying) {
      resetEvents();
    }
    
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
        }),
      });

      if (!response.ok) {
        console.error('Failed to control replay:', await response.text());
      }
    } catch (err) {
      console.error('Error controlling replay:', err);
    }
  };

  const handleSpeedChange = async (value) => {
    const newSpeed = value[0] || value;
    setPlaybackSpeed(newSpeed);

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

  const handleSkipForward = async () => {
    if (currentEventIndex < events.length - 1) {
      const newIndex = currentEventIndex + 1;
      setCurrentEventIndex(newIndex);

      // If we're streaming, we need to tell the server to seek
      if (eventSourceRef.current) {
        try {
          await fetch(`${API_URL}/events/${sessionId}/replay/control`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              action: 'seek',
              position: events[newIndex].timestamp,
            }),
          });
        } catch (err) {
          console.error('Error seeking in replay:', err);
        }
      }
    }
  };

  const handleSkipBack = async () => {
    if (currentEventIndex > 0) {
      const newIndex = currentEventIndex - 1;
      setCurrentEventIndex(newIndex);

      // If we're streaming, we need to tell the server to seek
      if (eventSourceRef.current) {
        try {
          await fetch(`${API_URL}/events/${sessionId}/replay/control`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              action: 'seek',
              position: events[newIndex].timestamp,
            }),
          });
        } catch (err) {
          console.error('Error seeking in replay:', err);
        }
      }
    }
  };

  const handleRestart = async () => {
    setCurrentEventIndex(0);

    // If we're playing, we need to restart the stream
    if (isPlaying) {
      setIsPlaying(false);

      // Send control request to seek to the beginning
      try {
        if (events.length > 0) {
          await fetch(`${API_URL}/events/${sessionId}/replay/control`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              action: 'seek',
              position: events[0].timestamp,
            }),
          });
        }
      } catch (err) {
        console.error('Error restarting replay:', err);
      }

      // Small delay to ensure the state updates before we start again
      setTimeout(() => {
        setIsPlaying(true);
      }, 100);
    } else {
      // Just move to the first event
      setCurrentEventIndex(0);
    }
  };

  const handleBack = () => {
    // Clean up before navigating away
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    navigate('/interactions');
  };

  const handleDeleteSessions = async () => {
    try {
      const response = await fetch(`${API_URL}/sessions`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete sessions');
      }

      const data = await response.json();
      // Navigate back to the interactions page after deletion
      navigate('/interactions');
    } catch (error) {
      console.error('Error deleting sessions:', error);
      setError('Failed to delete sessions: ' + error.message);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
    </div>
  );

  if (error) return (
    <div className="container mx-auto p-4">
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        <p>{error}</p>
        <Button variant="outline" onClick={handleBack} className="mt-2">
          Back to Sessions
        </Button>
      </div>
    </div>
  );

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center mb-4">
        <Button
          variant="ghost"
          onClick={handleBack}
          className="mr-2"
          aria-label="Back to sessions"
        >
          <ChevronLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Session Replay: {sessionId}</h1>
      </div>

      {sessionInfo && (
        <Card className="p-4 mb-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h3 className="font-medium">Session Start</h3>
              <p className="text-sm text-gray-600">
                {new Date(sessionInfo.start_time).toLocaleString()}
              </p>
            </div>
            <div>
              <h3 className="font-medium">Duration</h3>
              <p className="text-sm text-gray-600">
                {sessionInfo.duration_seconds ? `${Math.round(sessionInfo.duration_seconds)}s` : 'N/A'}
              </p>
            </div>
            <div>
              <h3 className="font-medium">Events</h3>
              <p className="text-sm text-gray-600">{events.length} events</p>
            </div>
          </div>
        </Card>
      )}
      {/* Dedicated Show All Section */}
      <Card className="p-4 mb-4 border-2 border-blue-200 bg-blue-50">
        <div className="flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Advanced Replay Options</h3>
              <p className="text-sm text-gray-600 mt-1">
                {showingAll 
                  ? "All events have been loaded. You can navigate through the entire session." 
                  : "Want to see the entire conversation at once? Use the Show All button to load all events instantly."}
              </p>
            </div>
            
            {showingAll ? (
              <Button
                variant="outline"
                onClick={handleResetToStreaming}
                aria-label="Reset to streaming mode"
                className="whitespace-nowrap"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Reset to Stream Mode
              </Button>
            ) : (
              <Button
                variant="default"
                onClick={fetchAllEvents}
                disabled={isLoadingAll}
                aria-label="Show all events"
                className="bg-blue-500 hover:bg-blue-600 text-white whitespace-nowrap"
              >
                {isLoadingAll ? (
                  <span className="flex items-center gap-2">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></div>
                    Loading All Events...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <FastForward className="h-4 w-4" />
                    Show All Events
                  </span>
                )}
              </Button>
            )}
          </div>
          
          <div className="flex justify-end border-t pt-3">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  variant="destructive"
                  size="sm"
                  className="flex items-center space-x-1 bg-red-500/90 hover:bg-red-600"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  <span>Delete All Sessions</span>
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-background">
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This action will delete all active chat sessions and cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="border border-input rounded-md">Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleDeleteSessions}
                    className="bg-red-500 hover:bg-red-600 text-white rounded-md"
                  >
                    Delete All Sessions
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </Card>

      <Card className="p-4 mb-4">
        <h3 className="text-lg font-semibold mb-3">Playback Controls</h3>
        <div className="flex flex-wrap items-center gap-2 border-t pt-3">
          {showingAll ? (
            <Button
              variant="ghost"
              onClick={handleResetToStreaming}
              aria-label="Reset to streaming mode"
            >
              <RefreshCw className="h-5 w-5" />
              <span className="ml-1">Reset</span>
            </Button>
          ) : (
            <Button
              variant="ghost"
              onClick={handlePlayPause}
              aria-label={isPlaying ? "Pause playback" : "Play playback"}
            >
              {isPlaying ? (
                <PauseCircle className="h-6 w-6" />
              ) : (
                <PlayCircle className="h-6 w-6" />
              )}
            </Button>
          )}

          <Button
            variant="ghost"
            onClick={handleSkipBack}
            disabled={currentEventIndex <= 0}
            aria-label="Skip backward"
          >
            <SkipBack className="h-5 w-5" />
          </Button>

          <Button
            variant="ghost"
            onClick={handleSkipForward}
            disabled={currentEventIndex >= events.length - 1}
            aria-label="Skip forward"
          >
            <SkipForward className="h-5 w-5" />
          </Button>

          {!showingAll && (
            <Button
              variant="ghost"
              onClick={handleRestart}
              aria-label="Restart playback"
            >
              <RefreshCw className="h-5 w-5" />
            </Button>
          )}



          <div className="flex items-center gap-2 ml-4">
            <span className="text-sm">Speed: {playbackSpeed}x</span>
            <Slider
              value={[playbackSpeed]}
              min={0.5}
              max={10}
              step={0.5}
              onValueChange={handleSpeedChange}
              className="w-32"
              aria-label="Playback speed"
            />
          </div>

          <div className="flex items-center gap-2 ml-auto">
            <span className="text-sm">
              Event: {currentEventIndex + 1} of {events.length}
              {showingAll && " (All Loaded)"}
            </span>
          </div>
        </div>
      </Card>

      {/* Only render chat events if we're playing, have clicked "Show All", 
          or have manually moved through events (currentEventIndex > 0) */}
      {(isPlaying || showingAll || currentEventIndex > 0) && events.length > 0 && (
        <EnhancedChatEventReplay
          events={events}
          currentEventIndex={Math.min(currentEventIndex, events.length - 1)}
          isPlaying={isPlaying}
          playbackSpeed={playbackSpeed}
          onEventIndexChange={setCurrentEventIndex}
        />
      )}
      
      {/* Show a message when no events are loaded but we're trying to display them */}
      {((isPlaying || showingAll || currentEventIndex > 0) && events.length === 0) && (
        <Card className="p-8 text-center">
          <p className="text-gray-500 mb-4">No events found for this session. Try reloading the page.</p>
        </Card>
      )}
      
      {/* Show a prompt when no events are being displayed by choice */}
      {!isPlaying && !showingAll && currentEventIndex === 0 && (
        <Card className="p-8 text-center">
          <p className="text-gray-500 mb-4">Click Play to start the replay or Show All to view the entire session</p>
        </Card>
      )}
    </div>
  );
};

export default ReplayPage;