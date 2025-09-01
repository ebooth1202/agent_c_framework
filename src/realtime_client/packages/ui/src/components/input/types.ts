/**
 * Shared types for input components
 */

export interface Agent {
  id: string
  name: string
  description?: string
  avatar?: string | React.ReactNode
  available?: boolean
}

export type OutputMode = 'text' | 'voice' | 'avatar'

export interface OutputOption {
  id: string
  name: string
  type: 'voice' | 'avatar'
  available?: boolean
  metadata?: {
    voiceId?: string
    avatarId?: string
    previewUrl?: string
  }
}