/**
 * OutputSelector Component
 * 
 * Provides hierarchical selection for output modes:
 * - Text Only
 * - Voice (with vendor/voice submenu)
 * - Avatar (with avatar selection submenu)
 */

import * as React from "react"
import { ChevronDown, Type, Mic, User } from "lucide-react"
import { useAgentCData, useInitializationStatus, useVoiceModel } from "@agentc/realtime-react"
import { useRealtimeClient } from "@agentc/realtime-react"
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
  DropdownMenuTrigger,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem
} from "../ui/dropdown-menu"

export interface OutputSelectorProps {
  className?: string
  disabled?: boolean
  showIcon?: boolean
}

type OutputMode = 'text' | 'voice' | 'avatar'

interface SelectedOutput {
  mode: OutputMode
  id: string
  label: string
}

export const OutputSelector = React.forwardRef<HTMLButtonElement, OutputSelectorProps>(
  ({ className, disabled = false, showIcon = true }, ref) => {
    const client = useRealtimeClient()
    const { data, isInitialized, isLoading } = useAgentCData()
    const { isInitialized: connectionInitialized } = useInitializationStatus()
    const { currentVoice } = useVoiceModel()
    
    const [selectedOutput, setSelectedOutput] = React.useState<SelectedOutput>({
      mode: 'text',
      id: 'none',
      label: 'Text Only'
    })
    
    const [isChanging, setIsChanging] = React.useState(false)

    // Update selected output based on current voice
    React.useEffect(() => {
      if (!currentVoice) {
        setSelectedOutput({
          mode: 'text',
          id: 'none',
          label: 'Text Only'
        })
      } else if (currentVoice.voice_id === 'avatar') {
        // Find the current avatar if in avatar mode
        const avatarId = client?.getAvatarManager()?.getAvatarId()
        const avatar = data.avatars.find(a => a.avatar_id === avatarId)
        setSelectedOutput({
          mode: 'avatar',
          id: avatarId || 'avatar',
          label: avatar ? `${avatar.pose_name}` : 'Avatar'
        })
      } else {
        // Voice mode
        setSelectedOutput({
          mode: 'voice',
          id: currentVoice.voice_id,
          label: `${currentVoice.vendor} - ${currentVoice.voice_id}`
        })
      }
    }, [currentVoice, data.avatars, client])

    // Group voices by vendor for better organization
    const voicesByVendor = React.useMemo(() => {
      const grouped: Record<string, typeof data.voices> = {}
      data.voices.forEach(voice => {
        if (!grouped[voice.vendor]) {
          grouped[voice.vendor] = []
        }
        grouped[voice.vendor].push(voice)
      })
      return grouped
    }, [data.voices])

    // Filter only active public avatars
    const activeAvatars = React.useMemo(() => {
      return data.avatars.filter(
        avatar => avatar.status === 'active' && avatar.is_public
      )
    }, [data.avatars])

    const handleTextOnlySelect = async () => {
      if (!client) return
      
      setIsChanging(true)
      try {
        client.setAgentVoice('none')
        setSelectedOutput({
          mode: 'text',
          id: 'none',
          label: 'Text Only'
        })
      } finally {
        setIsChanging(false)
      }
    }

    const handleVoiceSelect = async (voiceId: string) => {
      if (!client) return
      
      setIsChanging(true)
      try {
        client.setAgentVoice(voiceId)
        const voice = data.voices.find(v => v.voice_id === voiceId)
        if (voice) {
          setSelectedOutput({
            mode: 'voice',
            id: voiceId,
            label: `${voice.vendor} - ${voice.voice_id}`
          })
        }
      } finally {
        setIsChanging(false)
      }
    }

    const handleAvatarSelect = async (avatarId: string) => {
      if (!client) return
      
      setIsChanging(true)
      try {
        // For avatar selection, we need to integrate with HeyGen SDK
        // This is a placeholder - actual HeyGen integration would be done here
        // For now, we'll just set the avatar session
        const avatar = activeAvatars.find(a => a.avatar_id === avatarId)
        
        // In a real implementation, you would:
        // 1. Initialize HeyGen streaming avatar SDK
        // 2. Create a streaming session with the avatar
        // 3. Wait for STREAM_READY event
        // 4. Call client.setAvatarSession(sessionId, avatarId)
        
        // For now, we'll simulate this:
        console.warn('Avatar selection requires HeyGen SDK integration')
        // client.setAvatarSession('session-id-from-heygen', avatarId)
        
        if (avatar) {
          setSelectedOutput({
            mode: 'avatar',
            id: avatarId,
            label: avatar.pose_name
          })
        }
      } finally {
        setIsChanging(false)
      }
    }

    const getIcon = () => {
      switch (selectedOutput.mode) {
        case 'text':
          return <Type className="h-4 w-4" />
        case 'voice':
          return <Mic className="h-4 w-4" />
        case 'avatar':
          return <User className="h-4 w-4" />
      }
    }

    const isDisabled = disabled || !isInitialized || !connectionInitialized || isLoading || isChanging

    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            ref={ref}
            variant="outline"
            className={cn(
              "w-[200px] justify-between",
              className
            )}
            disabled={isDisabled}
          >
            <span className="flex items-center gap-2">
              {showIcon && getIcon()}
              <span className="truncate">
                {isLoading ? "Loading..." : selectedOutput.label}
              </span>
            </span>
            <ChevronDown className="h-4 w-4 opacity-50" />
          </Button>
        </DropdownMenuTrigger>
        
        <DropdownMenuContent className="w-[200px]" align="start">
          <DropdownMenuLabel>Output Mode</DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {/* Text Only Option */}
          <DropdownMenuItem 
            onClick={handleTextOnlySelect}
            className="flex items-center gap-2"
          >
            <Type className="h-4 w-4" />
            <span>Text Only</span>
            {selectedOutput.mode === 'text' && (
              <span className="ml-auto text-xs">✓</span>
            )}
          </DropdownMenuItem>
          
          {/* Voice Submenu */}
          <DropdownMenuSub>
            <DropdownMenuSubTrigger className="flex items-center gap-2">
              <Mic className="h-4 w-4" />
              <span>Voice</span>
            </DropdownMenuSubTrigger>
            <DropdownMenuSubContent className="w-[250px]">
              {Object.entries(voicesByVendor).map(([vendor, voices]) => (
                <React.Fragment key={vendor}>
                  <DropdownMenuLabel className="text-xs">{vendor}</DropdownMenuLabel>
                  {voices.map(voice => (
                    <DropdownMenuItem
                      key={voice.voice_id}
                      onClick={() => handleVoiceSelect(voice.voice_id)}
                      className="flex flex-col items-start py-2"
                    >
                      <div className="flex items-center justify-between w-full">
                        <span className="text-sm font-medium">{voice.voice_id}</span>
                        {selectedOutput.mode === 'voice' && selectedOutput.id === voice.voice_id && (
                          <span className="text-xs">✓</span>
                        )}
                      </div>
                      {voice.description && (
                        <span className="text-xs text-muted-foreground mt-1">
                          {voice.description}
                        </span>
                      )}
                    </DropdownMenuItem>
                  ))}
                  {vendor !== Object.keys(voicesByVendor)[Object.keys(voicesByVendor).length - 1] && (
                    <DropdownMenuSeparator />
                  )}
                </React.Fragment>
              ))}
            </DropdownMenuSubContent>
          </DropdownMenuSub>
          
          {/* Avatar Submenu */}
          {activeAvatars.length > 0 && (
            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex items-center gap-2">
                <User className="h-4 w-4" />
                <span>Avatar</span>
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent className="w-[250px]">
                <DropdownMenuLabel className="text-xs">Available Avatars</DropdownMenuLabel>
                {activeAvatars.map(avatar => (
                  <DropdownMenuItem
                    key={avatar.avatar_id}
                    onClick={() => handleAvatarSelect(avatar.avatar_id)}
                    className="flex items-center justify-between py-2"
                  >
                    <span className="text-sm">
                      {avatar.avatar_id} - {avatar.pose_name}
                    </span>
                    {selectedOutput.mode === 'avatar' && selectedOutput.id === avatar.avatar_id && (
                      <span className="text-xs">✓</span>
                    )}
                  </DropdownMenuItem>
                ))}
                {activeAvatars.length === 0 && (
                  <DropdownMenuItem disabled className="text-muted-foreground text-sm">
                    No avatars available
                  </DropdownMenuItem>
                )}
              </DropdownMenuSubContent>
            </DropdownMenuSub>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    )
  }
)

OutputSelector.displayName = "OutputSelector"