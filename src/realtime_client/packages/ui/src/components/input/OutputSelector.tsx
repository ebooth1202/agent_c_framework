import * as React from 'react'
import { ChevronDown, MessageSquare, Volume2, User, Check } from 'lucide-react'
import { cn } from '../../lib/utils'
import { Button } from '../ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
  DropdownMenuLabel,
  DropdownMenuSeparator
} from '../ui/dropdown-menu'
import type { OutputOption } from './types'

export interface OutputSelectorProps {
  selectedOption: OutputOption | null
  onOptionSelect: (option: OutputOption) => void
  voiceOptions?: OutputOption[]    // From useVoiceModel hook
  avatarOptions?: OutputOption[]   // From useAvatar hook
  disabled?: boolean
  className?: string
}

// Default voice options if none provided
const defaultVoiceOptions: OutputOption[] = [
  { id: 'alloy', name: 'Alloy', type: 'voice', available: true, metadata: { voiceId: 'alloy' }},
  { id: 'echo', name: 'Echo', type: 'voice', available: true, metadata: { voiceId: 'echo' }},
  { id: 'fable', name: 'Fable', type: 'voice', available: true, metadata: { voiceId: 'fable' }},
  { id: 'nova', name: 'Nova', type: 'voice', available: true, metadata: { voiceId: 'nova' }},
  { id: 'onyx', name: 'Onyx', type: 'voice', available: true, metadata: { voiceId: 'onyx' }},
  { id: 'shimmer', name: 'Shimmer', type: 'voice', available: true, metadata: { voiceId: 'shimmer' }}
]

// Default avatar options if none provided
const defaultAvatarOptions: OutputOption[] = [
  { id: 'josh', name: 'Josh', type: 'avatar', available: true, metadata: { avatarId: 'josh_lite3_20230714' }},
  { id: 'anna', name: 'Anna', type: 'avatar', available: true, metadata: { avatarId: 'anna_public_20240108' }}
]

// Text-only option (always available)
const textOnlyOption: OutputOption = {
  id: 'text-only',
  name: 'Text Only',
  type: 'text',
  available: true
}

export const OutputSelector = React.forwardRef<HTMLButtonElement, OutputSelectorProps>(
  ({ 
    selectedOption, 
    onOptionSelect, 
    voiceOptions = defaultVoiceOptions, 
    avatarOptions = defaultAvatarOptions,
    disabled = false,
    className 
  }, ref) => {
    const [open, setOpen] = React.useState(false)

    // Get the appropriate icon for the current mode
    const getModeIcon = React.useCallback(() => {
      if (!selectedOption) return <MessageSquare className="h-4 w-4" />
      
      switch (selectedOption.type) {
        case 'text':
          return <MessageSquare className="h-4 w-4" />
        case 'voice':
          return <Volume2 className="h-4 w-4" />
        case 'avatar':
          return <User className="h-4 w-4" />
        default:
          return <MessageSquare className="h-4 w-4" />
      }
    }, [selectedOption])

    // Get the display label for the current mode
    const getModeLabel = React.useCallback(() => {
      if (!selectedOption) return 'Text Only'
      
      if (selectedOption.type === 'text') {
        return 'Text Only'
      } else if (selectedOption.type === 'voice') {
        return `Voice: ${selectedOption.name}`
      } else if (selectedOption.type === 'avatar') {
        return `Avatar: ${selectedOption.name}`
      }
      return selectedOption.name
    }, [selectedOption])

    // Handle option selection
    const handleOptionSelect = React.useCallback((option: OutputOption) => {
      onOptionSelect(option)
      setOpen(false)
    }, [onOptionSelect])

    // Check if an option is currently selected
    const isOptionSelected = React.useCallback((option: OutputOption) => {
      if (!selectedOption) return option.type === 'text' && option.id === 'text-only'
      return selectedOption.id === option.id
    }, [selectedOption])

    return (
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            ref={ref}
            variant="ghost"
            size="sm"
            disabled={disabled}
            className={cn(
              "h-9 px-3 gap-2 font-medium",
              "hover:bg-accent hover:text-accent-foreground",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              className
            )}
            aria-label="Select agent response mode"
            aria-haspopup="true"
            aria-expanded={open}
          >
            {getModeIcon()}
            <span className="text-sm">{getModeLabel()}</span>
            <ChevronDown 
              className={cn(
                "h-4 w-4 transition-transform duration-200",
                open && "rotate-180"
              )} 
            />
          </Button>
        </DropdownMenuTrigger>
        
        <DropdownMenuContent 
          align="start" 
          className="w-56"
          sideOffset={5}
        >
          <DropdownMenuLabel className="text-xs font-semibold text-muted-foreground">
            Agent Response Mode
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          
          {/* Text Only Option */}
          <DropdownMenuItem
            onClick={() => handleOptionSelect(textOnlyOption)}
            disabled={!textOnlyOption.available}
            className="flex items-center justify-between cursor-pointer"
          >
            <div className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              <span>Text Only</span>
            </div>
            {isOptionSelected(textOnlyOption) && (
              <Check className="h-4 w-4 text-primary" aria-label="Selected" />
            )}
          </DropdownMenuItem>

          {/* Voice Responses Submenu */}
          {voiceOptions && voiceOptions.length > 0 && (
            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex items-center gap-2">
                <Volume2 className="h-4 w-4" />
                <span>Voice Responses</span>
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent className="w-48">
                {voiceOptions.map((voice) => (
                  <DropdownMenuItem
                    key={voice.id}
                    onClick={() => handleOptionSelect(voice)}
                    disabled={!voice.available}
                    className="flex items-center justify-between cursor-pointer"
                  >
                    <span>{voice.name}</span>
                    {isOptionSelected(voice) && (
                      <Check className="h-4 w-4 text-primary" aria-label="Selected" />
                    )}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>
          )}

          {/* Avatar Responses Submenu */}
          {avatarOptions && avatarOptions.length > 0 && (
            <DropdownMenuSub>
              <DropdownMenuSubTrigger className="flex items-center gap-2">
                <User className="h-4 w-4" />
                <span>Avatar Responses</span>
              </DropdownMenuSubTrigger>
              <DropdownMenuSubContent className="w-48">
                {avatarOptions.map((avatar) => (
                  <DropdownMenuItem
                    key={avatar.id}
                    onClick={() => handleOptionSelect(avatar)}
                    disabled={!avatar.available}
                    className="flex items-center justify-between cursor-pointer"
                  >
                    <span>{avatar.name}</span>
                    {isOptionSelected(avatar) && (
                      <Check className="h-4 w-4 text-primary" aria-label="Selected" />
                    )}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuSubContent>
            </DropdownMenuSub>
          )}
        </DropdownMenuContent>
      </DropdownMenu>
    )
  }
)

OutputSelector.displayName = 'OutputSelector'

export default OutputSelector