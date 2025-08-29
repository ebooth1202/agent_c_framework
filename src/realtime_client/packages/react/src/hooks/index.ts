/**
 * React hooks for the Agent C Realtime SDK
 * Audio-related and other utility hooks
 */

// Audio control hook
export { useAudio } from './useAudio';
export type { UseAudioOptions, UseAudioReturn } from './useAudio';

// Turn state monitoring hook
export { useTurnState } from './useTurnState';
export type { UseTurnStateOptions, UseTurnStateReturn, TurnStateEvent } from './useTurnState';