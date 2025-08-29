/**
 * useAudio - React hook for audio control and status monitoring
 * Provides a simple interface to the RealtimeClient's audio functionality
 */

import { useEffect, useState, useCallback, useRef } from 'react';
import { RealtimeClient } from '@agentc/realtime-core';
import type { AudioStatus } from '@agentc/realtime-core';

/**
 * Options for the useAudio hook
 */
export interface UseAudioOptions {
  /** Automatically start recording when component mounts */
  autoStart?: boolean;
  
  /** Whether to respect turn state when streaming audio */
  respectTurnState?: boolean;
  
  /** RealtimeClient instance (temporary until we have context provider) */
  client?: RealtimeClient | null;
}

/**
 * Return type for the useAudio hook
 */
export interface UseAudioReturn {
  // Status
  /** Current audio system status */
  status: AudioStatus;
  
  /** Whether microphone is currently recording */
  isRecording: boolean;
  
  /** Whether audio is streaming to server */
  isStreaming: boolean;
  
  /** Whether user can send audio input (based on turn state) */
  canSendInput: boolean;
  
  /** Current audio input level (0.0 to 1.0) */
  audioLevel: number;
  
  // Control methods
  /** Start recording from microphone */
  startRecording: () => Promise<void>;
  
  /** Stop recording from microphone */
  stopRecording: () => void;
  
  /** Start streaming audio to server */
  startStreaming: () => Promise<void>;
  
  /** Stop streaming audio to server */
  stopStreaming: () => void;
  
  /** Request microphone permission */
  requestPermission: () => Promise<boolean>;
  
  /** Set audio output volume (0.0 to 1.0) */
  setVolume: (volume: number) => void;
  
  // Derived states
  /** Whether recording can be started (connected and not recording) */
  canStartRecording: boolean;
  
  /** Whether microphone permission is needed */
  needsPermission: boolean;
  
  /** Whether there's an audio error */
  hasError: boolean;
  
  /** Error message if there's an error */
  errorMessage?: string;
}

/**
 * Default audio status when client is not available
 */
const DEFAULT_AUDIO_STATUS: AudioStatus = {
  // Input status
  isRecording: false,
  isStreaming: false,
  isProcessing: false,
  hasPermission: false,
  currentLevel: 0,
  averageLevel: 0,
  
  // Output status
  isPlaying: false,
  bufferSize: 0,
  volume: 1,
  
  // System status
  isAudioEnabled: false,
  isInputEnabled: false,
  isOutputEnabled: false
};

/**
 * React hook for audio control and status monitoring
 * Provides a clean interface to the RealtimeClient's audio functionality
 */
export function useAudio(options: UseAudioOptions = {}): UseAudioReturn {
  const { autoStart = false, respectTurnState = true, client } = options;
  
  // State for audio status
  const [status, setStatus] = useState<AudioStatus>(DEFAULT_AUDIO_STATUS);
  const [canSendInput, setCanSendInput] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | undefined>(undefined);
  
  // Refs for cleanup
  const intervalRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined);
  const isMountedRef = useRef(true);
  
  // Update status from client
  const updateStatus = useCallback(() => {
    if (!client || !isMountedRef.current) return;
    
    try {
      const audioStatus = client.getAudioStatus();
      setStatus(audioStatus);
      setErrorMessage(undefined);
    } catch (error) {
      console.error('Failed to get audio status:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Unknown error');
    }
  }, [client]);
  
  // Control methods
  const startRecording = useCallback(async () => {
    if (!client) {
      throw new Error('Client not available');
    }
    
    try {
      await client.startAudioRecording();
      updateStatus();
    } catch (error) {
      console.error('Failed to start recording:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to start recording');
      throw error;
    }
  }, [client, updateStatus]);
  
  const stopRecording = useCallback(() => {
    if (!client) {
      console.warn('Client not available');
      return;
    }
    
    try {
      client.stopAudioRecording();
      updateStatus();
    } catch (error) {
      console.error('Failed to stop recording:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to stop recording');
    }
  }, [client, updateStatus]);
  
  const startStreaming = useCallback(async () => {
    if (!client) {
      throw new Error('Client not available');
    }
    
    if (!client.isConnected()) {
      throw new Error('Not connected to server');
    }
    
    // Check turn state if respect is enabled
    if (respectTurnState && !canSendInput) {
      throw new Error('Cannot start streaming - user does not have turn');
    }
    
    try {
      // If not recording, start recording first
      if (!status.isRecording) {
        await client.startAudioRecording();
      }
      
      client.startAudioStreaming();
      updateStatus();
    } catch (error) {
      console.error('Failed to start streaming:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to start streaming');
      throw error;
    }
  }, [client, canSendInput, respectTurnState, status.isRecording, updateStatus]);
  
  const stopStreaming = useCallback(() => {
    if (!client) {
      console.warn('Client not available');
      return;
    }
    
    try {
      client.stopAudioStreaming();
      updateStatus();
    } catch (error) {
      console.error('Failed to stop streaming:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to stop streaming');
    }
  }, [client, updateStatus]);
  
  const requestPermission = useCallback(async (): Promise<boolean> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Stop the stream immediately - we just needed to get permission
      stream.getTracks().forEach(track => track.stop());
      updateStatus();
      return true;
    } catch (error) {
      console.error('Failed to get microphone permission:', error);
      setErrorMessage('Microphone permission denied');
      return false;
    }
  }, [updateStatus]);
  
  const setVolume = useCallback((volume: number) => {
    if (!client) {
      console.warn('Client not available');
      return;
    }
    
    if (volume < 0 || volume > 1) {
      console.error('Volume must be between 0 and 1');
      return;
    }
    
    try {
      client.setAudioVolume(volume);
      updateStatus();
    } catch (error) {
      console.error('Failed to set volume:', error);
      setErrorMessage(error instanceof Error ? error.message : 'Failed to set volume');
    }
  }, [client, updateStatus]);
  
  // Subscribe to turn state changes
  useEffect(() => {
    if (!client) return;
    
    const turnManager = client.getTurnManager();
    if (!turnManager) {
      // If no turn manager, assume we can always send input
      setCanSendInput(true);
      return;
    }
    
    // Set initial turn state
    setCanSendInput(turnManager.canSendInput);
    
    // Subscribe to turn state changes
    const handleTurnStateChange = ({ canSendInput: newCanSendInput }: { canSendInput: boolean }) => {
      setCanSendInput(newCanSendInput);
      
      // If respect turn state is enabled and user lost turn, stop streaming
      if (respectTurnState && !newCanSendInput && status.isStreaming) {
        stopStreaming();
      }
    };
    
    turnManager.on('turn-state-changed', handleTurnStateChange);
    
    return () => {
      turnManager.off('turn-state-changed', handleTurnStateChange);
    };
  }, [client, respectTurnState, status.isStreaming, stopStreaming]);
  
  // Poll for status updates
  useEffect(() => {
    if (!client) return;
    
    // Initial update
    updateStatus();
    
    // Poll for status updates
    intervalRef.current = setInterval(updateStatus, 100);
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [client, updateStatus]);
  
  // Auto-start recording if requested
  useEffect(() => {
    if (autoStart && client && client.isConnected() && !status.isRecording) {
      startRecording().catch((error: unknown) => {
        console.error('Auto-start recording failed:', error);
      });
    }
  }, [autoStart, client, status.isRecording, startRecording]);
  
  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;
    
    return () => {
      isMountedRef.current = false;
      
      // Stop recording and streaming on unmount
      if (client) {
        if (status.isStreaming) {
          client.stopAudioStreaming();
        }
        if (status.isRecording) {
          client.stopAudioRecording();
        }
      }
    };
  }, []);
  
  // Derived states
  const canStartRecording = Boolean(
    client && 
    client.isConnected() && 
    !status.isRecording &&
    status.isAudioEnabled &&
    status.isInputEnabled
  );
  
  const needsPermission = !status.hasPermission && status.isInputEnabled;
  const hasError = Boolean(errorMessage);
  
  return {
    // Status
    status,
    isRecording: status.isRecording,
    isStreaming: status.isStreaming,
    canSendInput,
    audioLevel: status.currentLevel,
    
    // Control methods
    startRecording,
    stopRecording,
    startStreaming,
    stopStreaming,
    requestPermission,
    setVolume,
    
    // Derived states
    canStartRecording,
    needsPermission,
    hasError,
    errorMessage
  };
}