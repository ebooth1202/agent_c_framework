"use client"

/**
 * @fileoverview OutputSelector Component for Agent C Realtime SDK
 * @module @agentc/realtime-ui/components/controls
 */

/**
 * OutputSelector Component
 * 
 * A hierarchical dropdown menu component that allows users to select the output mode
 * for agent responses. Supports three modes:
 * - Text Only: Agent responds with text messages only (no audio)
 * - Voice: Agent responds with synthesized speech using available voices
 * - Avatar: Agent responds with HeyGen streaming avatar (implementation pending)
 * 
 * @component
 * @example
 * ```tsx
 * // Basic usage
 * <OutputSelector />
 * 
 * // With custom configuration
 * <OutputSelector
 *   className="w-[250px]"
 *   showIcon={true}
 *   showErrorAlerts={false}
 *   ariaLabel="Choose how the agent responds"
 * />
 * 
 * // Disabled state
 * <OutputSelector disabled={true} />
 * ```
 * 
 * @remarks
 * This component requires the AgentCProvider context to be available.
 * It integrates with the SDK's voice management system and responds to
 * connection state changes automatically.
 * 
 * The component is fully accessible with ARIA labels, keyboard navigation,
 * and screen reader announcements. It follows CenSuite design patterns
 * and is WCAG 2.1 AA compliant.
 * 
 * @see {@link https://docs.agentc.ai/ui/output-selector} for detailed documentation
 * @since 0.1.0
 */

import * as React from "react"
import { ChevronDown, Type, Mic, User, Loader2, AlertCircle, Check } from "lucide-react"
import { 
  useAgentCData, 
  useInitializationStatus, 
  useVoiceModel, 
  useRealtimeClientSafe,
  useConnection 
} from "@agentc/realtime-react"
import { filterRegularVoices, type Voice } from "@agentc/realtime-core"
import { cn } from "../../lib/utils"
import { Button } from "../ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger
} from "../ui/dropdown-menu"
import { Alert, AlertDescription } from "../ui/alert"

/**
 * Props for the OutputSelector component
 * 
 * @interface OutputSelectorProps
 * @extends {React.HTMLAttributes<HTMLButtonElement>}
 */
export interface OutputSelectorProps {
  /**
   * Additional CSS classes to apply to the root element
   * @default undefined
   */
  className?: string
  
  /**
   * Whether the selector is disabled
   * @default false
   */
  disabled?: boolean
  
  /**
   * Whether to show the mode icon in the button
   * @default true
   */
  showIcon?: boolean
  
  /**
   * Custom aria-label for the selector button
   * Improves accessibility by providing context
   * @default "Output mode selector. Current mode: [current mode]"
   * @example "Select how Virtual Joe responds to you"
   */
  ariaLabel?: string
  
  /**
   * Whether to show error alerts inline below the selector
   * When false, errors are still logged to console
   * @default true
   */
  showErrorAlerts?: boolean
}

/**
 * OutputSelector component for selecting agent output modes
 * 
 * @component
 * @param {OutputSelectorProps} props - Component props
 * @param {React.Ref<HTMLButtonElement>} ref - Forward ref to the trigger button
 * @returns {JSX.Element} The rendered OutputSelector component
 * 
 * @example
 * ```tsx
 * const ref = useRef<HTMLButtonElement>(null);
 * 
 * <OutputSelector
 *   ref={ref}
 *   className="my-selector"
 *   showIcon={true}
 *   disabled={false}
 * />
 * ```
 */
export const OutputSelector = React.forwardRef<HTMLButtonElement, OutputSelectorProps>(
  ({ className, disabled = false, showIcon = true, ariaLabel, showErrorAlerts = true }, ref) => {
    const client = useRealtimeClientSafe()
    const { data, isInitialized, isLoading } = useAgentCData()
    const { isInitialized: connectionInitialized } = useInitializationStatus()
    const { currentVoice, isLoading: voiceLoading, error: voiceError } = useVoiceModel()
    const { isConnected } = useConnection()
    
    const [isChanging, setIsChanging] = React.useState(false)
    const [error, setError] = React.useState<string | null>(null)
    const [isMenuOpen, setIsMenuOpen] = React.useState(false)
    
    // Live region for screen reader announcements
    const [announcement, setAnnouncement] = React.useState<string>('')

    // Derive current mode from SDK state
    const currentMode = React.useMemo(() => {
      if (!currentVoice || currentVoice.voice_id === 'none') {
        return {
          type: 'text',
          label: 'Text Only',
          icon: Type
        }
      }
      
      if (currentVoice.voice_id === 'avatar') {
        // Avatar mode
        const avatarId = client?.getAvatarManager?.()?.getAvatarId?.()
        const avatar = data.avatars.find(a => a.avatar_id === avatarId)
        return {
          type: 'avatar',
          label: avatar ? `${avatar.avatar_id} - ${avatar.pose_name}` : 'Avatar Mode',
          icon: User
        }
      }
      
      // Voice mode - use description or fallback to vendor + voice_id
      return {
        type: 'voice',
        label: currentVoice.description || `${currentVoice.vendor} - ${currentVoice.voice_id}`,
        icon: Mic
      }
    }, [currentVoice, data.avatars, client])

    // Filter only public avatars (remove overly restrictive status check)
    const activeAvatars = React.useMemo(() => {
      if (!data.avatars || !Array.isArray(data.avatars)) return []
      return data.avatars.filter(
        avatar => avatar.is_public
      )
    }, [data.avatars])
    
    // Filter regular voices (exclude system voices like 'none' and 'avatar')
    const filteredVoices = React.useMemo(() => {
      if (!data.voices || !Array.isArray(data.voices)) return []
      return filterRegularVoices(data.voices)
    }, [data.voices])

    /**
     * Handle Text Only mode selection
     * Sends 'none' as voice_id to disable audio output
     */
    const handleTextOnly = React.useCallback(async () => {
      if (!client) return
      
      setIsChanging(true)
      setError(null)
      setAnnouncement('Switching to text-only mode...')
      
      try {
        await client.setAgentVoice('none')
        setAnnouncement('Text-only mode activated')
      } catch (error) {
        const errorMessage = 'Failed to set text mode'
        console.error(errorMessage, error)
        setError(errorMessage)
        setAnnouncement('Failed to switch to text-only mode')
      } finally {
        setIsChanging(false)
      }
    }, [client])

    /**
     * Handle voice selection
     * @param {string} voiceId - The ID of the voice to select
     */
    const handleVoiceSelect = React.useCallback(async (voiceId: string) => {
      if (!client) return
      
      const voice = filteredVoices.find(v => v.voice_id === voiceId)
      const voiceLabel = voice?.description || `${voice?.vendor} - ${voiceId}`
      
      setIsChanging(true)
      setError(null)
      setAnnouncement(`Switching to ${voiceLabel}...`)
      
      try {
        await client.setAgentVoice(voiceId)
        setAnnouncement(`Voice changed to ${voiceLabel}`)
      } catch (error) {
        const errorMessage = `Failed to set voice: ${voiceId}`
        console.error(errorMessage, error)
        setError(errorMessage)
        setAnnouncement(`Failed to switch to ${voiceLabel}`)
      } finally {
        setIsChanging(false)
      }
    }, [client, filteredVoices])

    /**
     * Handle avatar selection (currently deferred)
     * @param {string} avatarId - The ID of the avatar to select
     * @todo Implement HeyGen avatar integration
     */
    const handleAvatarSelect = React.useCallback((avatarId: string) => {
      // Deferred implementation - log selection only
      const avatar = data.avatars.find(a => a.avatar_id === avatarId)
      const avatarLabel = avatar ? `${avatar.avatar_id} - ${avatar.pose_name}` : avatarId
      
      // Avatar selection is deferred - will be implemented with HeyGen integration
      setAnnouncement(`Avatar ${avatarLabel} selection is not yet available`)
    }, [data.avatars])

    // Listen for voice change confirmations and clear errors
    React.useEffect(() => {
      if (!client) return

      const handleVoiceChanged = () => {
        // Voice successfully changed, clear any previous errors
        setError(null) // Clear any previous errors on successful change
      }

      client.on('agent_voice_changed', handleVoiceChanged)
      
      return () => {
        client.off('agent_voice_changed', handleVoiceChanged)
      }
    }, [client])
    
    // Clear error after timeout
    React.useEffect(() => {
      if (error) {
        const timer = setTimeout(() => setError(null), 5000)
        return () => clearTimeout(timer)
      }
    }, [error])

    // Check if a voice is currently selected
    const isVoiceSelected = (voiceId: string) => {
      return currentVoice?.voice_id === voiceId && currentMode.type === 'voice'
    }

    // Check if text mode is selected
    const isTextModeSelected = () => {
      return !currentVoice || currentVoice.voice_id === 'none' || currentMode.type === 'text'
    }

    // Check if an avatar is selected
    const isAvatarSelected = (avatarId: string) => {
      if (currentMode.type !== 'avatar') return false
      const currentAvatarId = client?.getAvatarManager?.()?.getAvatarId?.()
      return currentAvatarId === avatarId
    }

    // Connection state awareness - only disable when actually changing or not connected
    const isDisabled = disabled || !client || !isConnected || isChanging
    
    // Combined error state
    const displayError = error || voiceError
    
    // Determine button label - only show Loading when actually changing
    const buttonLabel = React.useMemo(() => {
      if (isChanging) return 'Loading...'
      // Show current mode even if initial loading is happening
      return currentMode.label
    }, [isChanging, currentMode.label])
    
    // Determine button icon
    const ButtonIcon = React.useMemo(() => {
      if (isChanging) return Loader2
      if (displayError) return AlertCircle
      return currentMode.icon
    }, [isChanging, displayError, currentMode.icon])

    return (
      <div className="relative">
        {/* Error Alert */}
        {showErrorAlerts && displayError && (
          <Alert variant="destructive" className="mb-2">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{displayError}</AlertDescription>
          </Alert>
        )}
        
        {/* Screen reader live region for announcements */}
        <div 
          role="status" 
          aria-live="polite" 
          aria-atomic="true" 
          className="sr-only"
        >
          {announcement}
        </div>
        
        <DropdownMenu open={isMenuOpen} onOpenChange={setIsMenuOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              ref={ref}
              variant={displayError ? "destructive" : "outline"}
              className={cn(
                "min-w-[180px] sm:w-[200px] justify-between transition-all duration-200",
                "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                "hover:bg-accent hover:text-accent-foreground",
                "active:scale-[0.98]",
                isDisabled && "opacity-50 cursor-not-allowed",
                className
              )}
              disabled={isDisabled}
              aria-label={ariaLabel || `Output mode selector. Current mode: ${buttonLabel}`}
              aria-expanded={isMenuOpen}
              aria-haspopup="menu"
            >
              <span className="flex items-center gap-2">
                {showIcon && (
                  <ButtonIcon 
                    className={cn(
                      "h-4 w-4",
                      (isChanging || voiceLoading) && "animate-spin"
                    )} 
                  />
                )}
                <span className="truncate">
                  {buttonLabel}
                </span>
              </span>
              <ChevronDown 
                className={cn(
                  "h-4 w-4 opacity-50 transition-transform duration-200",
                  isMenuOpen && "rotate-180"
                )} 
              />
            </Button>
          </DropdownMenuTrigger>
        
          <DropdownMenuContent 
            className="min-w-[180px] sm:w-[200px] animate-in fade-in-0 zoom-in-95" 
            align="start"
            sideOffset={5}
          >
            <DropdownMenuLabel id="output-mode-label">Output Mode</DropdownMenuLabel>
            <DropdownMenuSeparator />
            
            {/* Text Only Option - At root level */}
            <DropdownMenuItem 
              onClick={handleTextOnly}
              disabled={isChanging}
              className={cn(
                "flex items-center gap-2 transition-colors",
                "focus:bg-accent focus:text-accent-foreground",
                isTextModeSelected() && "bg-accent/50"
              )}
              aria-label="Text only mode"
            >
              <Type className="h-4 w-4" aria-hidden="true" />
              <span className="flex-1">Text Only</span>
              {isTextModeSelected() && (
                <Check className="h-3 w-3 ml-auto" aria-label="Currently selected" />
              )}
            </DropdownMenuItem>
          
            {/* Voices Submenu - Filter out system voices */}
            <DropdownMenuSub>
              <DropdownMenuSubTrigger 
                className={cn(
                  "flex items-center gap-2",
                  "focus:bg-accent focus:text-accent-foreground"
                )}
                disabled={isChanging || filteredVoices.length === 0}
                aria-label={`Voice options. ${filteredVoices.length} voices available`}
              >
                <Mic className="h-4 w-4" aria-hidden="true" />
                <span>Voices</span>
                <span className="ml-auto text-xs text-muted-foreground">
                  {filteredVoices.length}
                </span>
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent 
                className="w-[250px] sm:w-[280px] max-h-[300px] sm:max-h-[400px] overflow-y-auto animate-in slide-in-from-left-1"
                sideOffset={2}
                alignOffset={-5}
              >
                <DropdownMenuLabel id="voices-label">Available Voices</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {filteredVoices.length > 0 ? (
                  <div role="group" aria-labelledby="voices-label">
                    {filteredVoices.map(voice => (
                      <DropdownMenuItem
                        key={voice.voice_id}
                        onClick={() => handleVoiceSelect(voice.voice_id)}
                        disabled={isChanging}
                        className={cn(
                          "flex flex-col items-start py-2.5 px-3 transition-colors",
                          "focus:bg-accent focus:text-accent-foreground",
                          "hover:bg-accent/50",
                          isVoiceSelected(voice.voice_id) && "bg-accent/50"
                        )}
                        aria-label={`${voice.vendor} ${voice.voice_id}. ${voice.description || 'No description'}`}
                      >
                        <div className="flex items-center justify-between w-full">
                          <span className="text-sm font-medium">
                            {voice.vendor} - {voice.voice_id}
                          </span>
                          {isVoiceSelected(voice.voice_id) && (
                            <Check className="h-3 w-3 ml-2" aria-label="Currently selected" />
                          )}
                        </div>
                        {voice.description && (
                          <span className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {voice.description}
                          </span>
                        )}
                      </DropdownMenuItem>
                    ))}
                  </div>
                ) : (
                  <DropdownMenuItem disabled className="text-muted-foreground text-sm">
                    No voices available
                  </DropdownMenuItem>
                )}
              </DropdownMenuSubContent>
            </DropdownMenuSub>
          
            {/* Avatar Submenu */}
            {activeAvatars.length > 0 && (
              <DropdownMenuSub>
                <DropdownMenuSubTrigger 
                  className={cn(
                    "flex items-center gap-2",
                    "focus:bg-accent focus:text-accent-foreground"
                  )}
                  disabled={isChanging}
                  aria-label={`Avatar options. ${activeAvatars.length} avatars available`}
                >
                  <User className="h-4 w-4" aria-hidden="true" />
                  <span>Avatar</span>
                  <span className="ml-auto text-xs text-muted-foreground">
                    {activeAvatars.length}
                  </span>
                </DropdownMenuSubTrigger>
                <DropdownMenuSubContent 
                  className="w-[250px] sm:w-[280px] max-h-[300px] sm:max-h-[400px] overflow-y-auto animate-in slide-in-from-left-1"
                  sideOffset={2}
                  alignOffset={-5}
                >
                  <DropdownMenuLabel id="avatars-label">Available Avatars</DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <div role="group" aria-labelledby="avatars-label">
                    {activeAvatars.map(avatar => (
                      <DropdownMenuItem
                        key={avatar.avatar_id}
                        onClick={() => handleAvatarSelect(avatar.avatar_id)}
                        disabled={isChanging}
                        className={cn(
                          "flex items-center justify-between py-2.5 px-3 transition-colors",
                          "focus:bg-accent focus:text-accent-foreground",
                          "hover:bg-accent/50",
                          isAvatarSelected(avatar.avatar_id) && "bg-accent/50"
                        )}
                        aria-label={`Avatar ${avatar.avatar_id}, ${avatar.pose_name}`}
                      >
                        <span className="text-sm">
                          {avatar.avatar_id} - {avatar.pose_name}
                        </span>
                        {isAvatarSelected(avatar.avatar_id) && (
                          <Check className="h-3 w-3 ml-2" aria-label="Currently selected" />
                        )}
                      </DropdownMenuItem>
                    ))}
                  </div>
                  <DropdownMenuSeparator className="mt-2" />
                  <div className="px-3 py-2">
                    <p className="text-xs text-muted-foreground">
                      Avatar support coming soon
                    </p>
                  </div>
                </DropdownMenuSubContent>
              </DropdownMenuSub>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    )
  }
)

OutputSelector.displayName = "OutputSelector"