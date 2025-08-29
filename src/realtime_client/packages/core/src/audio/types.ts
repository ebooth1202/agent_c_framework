/**
 * Core audio types and interfaces for the Agent C Realtime Client SDK
 */

/**
 * Audio chunk data structure for transmission
 */
export interface AudioChunkData {
  /** PCM16 audio data as ArrayBuffer */
  content: ArrayBuffer;
  
  /** MIME type of the audio data */
  content_type: string;
  
  /** RMS audio level (0.0 to 1.0) for visualization */
  audio_level: number;
  
  /** Sequential frame counter */
  frame_count: number;
  
  /** Timestamp when audio was captured (milliseconds) */
  timestamp: number;
  
  /** Sample rate in Hz (typically 16000) */
  sample_rate: number;
  
  /** Number of samples in this chunk */
  sample_count: number;
}

/**
 * Configuration for the audio processor
 */
export interface AudioProcessorConfig {
  /** Target sample rate in Hz (default: 16000) */
  sampleRate?: number;
  
  /** Number of audio channels (default: 1 for mono) */
  channelCount?: number;
  
  /** Buffer size in samples before sending chunk (default: 2048) */
  bufferSize?: number;
  
  /** Path to the audio worklet file */
  workletPath?: string;
  
  /** Enable debug logging */
  debug?: boolean;
}

/**
 * Status of the audio processor
 */
export interface AudioProcessorStatus {
  /** Current state of the processor */
  state: 'idle' | 'loading' | 'ready' | 'processing' | 'error';
  
  /** Whether the processor is actively processing audio */
  isProcessing: boolean;
  
  /** Whether the audio worklet is loaded and ready */
  isReady: boolean;
  
  /** Current audio level (0.0 to 1.0) */
  audioLevel: number;
  
  /** Total number of chunks processed */
  chunksProcessed: number;
  
  /** Error message if in error state */
  error?: string;
  
  /** Audio context sample rate */
  contextSampleRate?: number;
  
  /** Configured output sample rate */
  outputSampleRate: number;
}

/**
 * Audio worklet message types
 */
export interface WorkletMessage {
  type: string;
  [key: string]: any;
}

/**
 * Audio chunk message from worklet
 */
export interface AudioChunkMessage extends WorkletMessage {
  type: 'audio_chunk';
  audioBuffer: ArrayBuffer;
  audioLevel: number;
  sampleCount: number;
  timestamp: number;
  sampleRate: number;
}

/**
 * Status message from worklet
 */
export interface WorkletStatusMessage extends WorkletMessage {
  type: 'ready' | 'started' | 'stopped' | 'error';
  message?: string;
}

/**
 * Control message to worklet
 */
export interface WorkletControlMessage extends WorkletMessage {
  type: 'start' | 'stop' | 'configure';
  bufferSize?: number;
}

/**
 * Audio processor event types
 */
export interface AudioProcessorEvents {
  /** Emitted when a new audio chunk is ready */
  audioChunk: (chunk: AudioChunkData) => void;
  
  /** Emitted when the processor status changes */
  statusChange: (status: AudioProcessorStatus) => void;
  
  /** Emitted when an error occurs */
  error: (error: Error) => void;
  
  /** Emitted when audio level changes */
  levelChange: (level: number) => void;
}

/**
 * Audio processor error types
 */
export enum AudioProcessorErrorCode {
  /** Failed to create or access AudioContext */
  AUDIO_CONTEXT_ERROR = 'AUDIO_CONTEXT_ERROR',
  
  /** Failed to load audio worklet */
  WORKLET_LOAD_ERROR = 'WORKLET_LOAD_ERROR',
  
  /** Failed to access microphone */
  MICROPHONE_ACCESS_ERROR = 'MICROPHONE_ACCESS_ERROR',
  
  /** Audio processing error */
  PROCESSING_ERROR = 'PROCESSING_ERROR',
  
  /** Invalid configuration */
  INVALID_CONFIG = 'INVALID_CONFIG',
  
  /** Not supported by browser */
  NOT_SUPPORTED = 'NOT_SUPPORTED'
}

/**
 * Custom error class for audio processor errors
 */
export class AudioProcessorError extends Error {
  constructor(
    message: string,
    public code: AudioProcessorErrorCode,
    public details?: any
  ) {
    super(message);
    this.name = 'AudioProcessorError';
  }
}

/**
 * Type guard to check if a message is an audio chunk message
 */
export function isAudioChunkMessage(message: WorkletMessage): message is AudioChunkMessage {
  return message.type === 'audio_chunk' && 'audioBuffer' in message;
}

/**
 * Type guard to check if a message is a status message
 */
export function isWorkletStatusMessage(message: WorkletMessage): message is WorkletStatusMessage {
  return ['ready', 'started', 'stopped', 'error'].includes(message.type);
}

/**
 * Default audio processor configuration
 */
export const DEFAULT_AUDIO_CONFIG: Required<AudioProcessorConfig> = {
  sampleRate: 16000,
  channelCount: 1,
  bufferSize: 2048,
  workletPath: '/worklets/audio-processor.worklet.js',
  debug: false
};