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
  ChevronLeft
} from 'lucide-react';
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

  // Effect for handling the EventSource based on play/pause state
  useEffect(() => {
    if (isPlaying) {
      startEventStream();
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
  }, [isPlaying, playbackSpeed, sessionId]);

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
      const eventLines = text.trim().split('\n');
      const parsedEvents = eventLines
        .filter(line => line.trim())
        .map(line => JSON.parse(line));

      setEvents(parsedEvents);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching initial events:', err);
      setError('Failed to load session events');
      setLoading(false);
    }
  };

  const startEventStream = () => {
    // Close any existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    try {
      // Connect to the streaming endpoint
      const streamUrl = `${API_URL}/events/${sessionId}/stream?real_time=true&speed_factor=${playbackSpeed}`;
      const eventSource = new EventSource(streamUrl);

      eventSource.onmessage = (e) => {
        try {
          const eventData = JSON.parse(e.data);

          // Check if this event already exists in our array to avoid duplicates
          const isDuplicate = events.some(
            existingEvent =>
              existingEvent.timestamp === eventData.timestamp &&
              existingEvent.event?.type === eventData.event?.type
          );

          if (!isDuplicate) {
            setEvents(prevEvents => {
              const newEvents = [...prevEvents, eventData];
              // Keep events sorted by timestamp
              return newEvents.sort((a, b) =>
                new Date(a.timestamp) - new Date(b.timestamp)
              );
            });

            // Advance current event index to show the latest event if we're playing
            setCurrentEventIndex(prevIndex => {
              return prevIndex + 1;
            });
          }
        } catch (err) {
          console.error('Error processing event data:', err);
        }
      };

      eventSource.onerror = (err) => {
        console.error('EventSource error:', err);
        eventSource.close();
        setIsPlaying(false);
      };

      eventSourceRef.current = eventSource;

    } catch (err) {
      console.error('Failed to establish event stream:', err);
      setError('Failed to establish event stream connection');
      setIsPlaying(false);
    }
  };

  const handlePlayPause = async () => {
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

      <Card className="p-4 mb-4">
        <div className="flex flex-wrap items-center gap-2">
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

          <Button
            variant="ghost"
            onClick={handleRestart}
            aria-label="Restart playback"
          >
            <RefreshCw className="h-5 w-5" />
          </Button>

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
            </span>
          </div>
        </div>
      </Card>

      <EnhancedChatEventReplay
        events={events}
        currentEventIndex={currentEventIndex}
        isPlaying={isPlaying}
        playbackSpeed={playbackSpeed}
        onEventIndexChange={setCurrentEventIndex}
      />
    </div>
  );
};

export default ReplayPage;