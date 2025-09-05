"use client"

/**
 * AgentSelector Component
 * 
 * Provides a dropdown menu for choosing between available AI agents.
 * Displays agent name, description (truncated with tooltip), and equipped tools as badges.
 */

import * as React from "react"
import { Bot, ChevronDown, Check, Loader2 } from "lucide-react"
import { useAgentCData, useConnection, useRealtimeClientSafe } from "@agentc/realtime-react"
import type { Agent } from "@agentc/realtime-react"
import { cn } from "../../lib/utils"
import { Badge } from "../ui/badge"
import { Button } from "../ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip"

export interface AgentSelectorProps {
  className?: string
  disabled?: boolean
  showIcon?: boolean
  placeholder?: string
}

/**
 * Format tool class names for display
 * Removes "Tools" suffix and adds spaces between capital letters
 * Examples: ThinkTools → Think, WorkspacePlanningTools → Workspace Planning
 */
function formatToolName(toolClass: string): string {
  // Remove "Tools" suffix
  let formatted = toolClass.replace(/Tools$/, '')
  
  // Add spaces between capital letters
  formatted = formatted.replace(/([A-Z])/g, ' $1').trim()
  
  return formatted
}

/**
 * Get first sentence from description for list view
 */
function getFirstSentence(text: string): string {
  if (!text) return ''
  
  // Clean up the text first - remove extra whitespace and newlines
  const cleanText = text.replace(/\s+/g, ' ').trim()
  
  // Match first sentence ending with . ! or ?
  // Updated regex to handle sentences properly
  const match = cleanText.match(/^[^.!?]*[.!?]/)
  if (match) {
    return match[0].trim()
  }
  
  // If no sentence ending found, truncate at reasonable length
  if (cleanText.length > 100) {
    // Try to break at a word boundary
    const truncated = cleanText.substring(0, 100)
    const lastSpace = truncated.lastIndexOf(' ')
    if (lastSpace > 80) {
      return truncated.substring(0, lastSpace) + '...'
    }
    return truncated + '...'
  }
  
  return cleanText
}

export const AgentSelector = React.forwardRef<HTMLButtonElement, AgentSelectorProps>(
  ({ className, disabled = false, showIcon = true, placeholder = "Select an agent" }, ref) => {
    const client = useRealtimeClientSafe()
    const { data, isInitialized, isLoading } = useAgentCData()
    const { isConnected } = useConnection()
    
    const [selectedAgent, setSelectedAgent] = React.useState<string>('')
    const [isChanging, setIsChanging] = React.useState(false)
    const [isMenuOpen, setIsMenuOpen] = React.useState(false)
    
    // Listen for agent configuration changes from server
    React.useEffect(() => {
      if (!client) return
      
      const handleAgentConfigChanged = (event: any) => {
        if (event.agent_config?.key) {
          setSelectedAgent(event.agent_config.key)
        }
      }
      
      const handleChatSessionChanged = (event: any) => {
        if (event.chat_session?.agent_config?.key) {
          setSelectedAgent(event.chat_session.agent_config.key)
        }
      }
      
      // Subscribe to events
      client.on('agent_configuration_changed' as any, handleAgentConfigChanged)
      client.on('chat_session_changed' as any, handleChatSessionChanged)
      
      return () => {
        client.off('agent_configuration_changed' as any, handleAgentConfigChanged)
        client.off('chat_session_changed' as any, handleChatSessionChanged)
      }
    }, [client])
    
    // Initialize with current agent from session if available
    React.useEffect(() => {
      if (!client || !isInitialized) return
      
      const sessionManager = client.getSessionManager()
      const currentSession = sessionManager?.getCurrentSession()
      
      if (currentSession?.agent_config?.key) {
        setSelectedAgent(currentSession.agent_config.key)
      }
    }, [client, isInitialized])
    
    // Also sync with currentAgentConfig from hook
    React.useEffect(() => {
      if (data.currentAgentConfig?.key) {
        setSelectedAgent(data.currentAgentConfig.key)
      }
    }, [data.currentAgentConfig])
    
    const handleAgentSelect = async (agentKey: string) => {
      if (!client || agentKey === selectedAgent) return
      
      setIsChanging(true)
      setIsMenuOpen(false)
      try {
        client.setAgent(agentKey)
        setSelectedAgent(agentKey)
      } finally {
        // Give UI time to update
        setTimeout(() => setIsChanging(false), 300)
      }
    }
    
    // Match OutputSelector's disabled logic pattern - only disable when truly necessary
    const isDisabled = disabled || !client || !isConnected || isChanging
    
    // Find the current agent details
    const currentAgent = data.agents.find(agent => agent.key === selectedAgent)
    
    // Determine button icon
    const ButtonIcon = isChanging ? Loader2 : Bot
    
    return (
      <TooltipProvider>
        <DropdownMenu open={isMenuOpen} onOpenChange={setIsMenuOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              ref={ref}
              variant="outline"
              className={cn(
                "min-w-[180px] sm:w-[200px] justify-between",
                "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                isDisabled && "opacity-50 cursor-not-allowed",
                className
              )}
              disabled={isDisabled}
              aria-label={`Agent selector. Current agent: ${currentAgent?.name || 'None selected'}`}
              aria-expanded={isMenuOpen}
              aria-haspopup="menu"
            >
              <span className="flex items-center gap-2 truncate">
                {showIcon && (
                  <ButtonIcon 
                    className={cn(
                      "h-4 w-4 flex-shrink-0",
                      isChanging && "animate-spin"
                    )} 
                  />
                )}
                <span className="truncate">
                  {currentAgent ? (
                    currentAgent.name || currentAgent.key
                  ) : (
                    isLoading ? "Loading agents..." : placeholder
                  )}
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
            className={cn(
              "w-[350px]",
              "bg-background border border-border shadow-lg", // Explicit opaque background
              "animate-in fade-in-0 zoom-in-95"
            )}
            align="start"
            sideOffset={5}
            style={{
              backgroundColor: 'hsl(var(--background))', // Force opaque background
              maxHeight: '400px', // Set max-height in style to override Radix positioning
            }}
          >
            <DropdownMenuLabel>Available Agents</DropdownMenuLabel>
            <DropdownMenuSeparator />
            
            {data.agents.length > 0 ? (
              <div className="px-1 max-h-[350px] overflow-y-auto">
                {data.agents.map((agent) => {
                  const isSelected = agent.key === selectedAgent
                  const firstSentence = getFirstSentence(agent.agent_description || '')
                  
                  return (
                    <Tooltip key={agent.key} delayDuration={500}>
                      <TooltipTrigger asChild>
                        <DropdownMenuItem
                          onClick={() => handleAgentSelect(agent.key)}
                          disabled={isChanging}
                          className={cn(
                            "flex flex-col items-start py-2.5 px-3 cursor-pointer",
                            "focus:bg-accent focus:text-accent-foreground",
                            "hover:bg-accent/50",
                            isSelected && "bg-accent/50"
                          )}
                          aria-label={`Agent: ${agent.name}. ${agent.agent_description || 'No description'}`}
                        >
                          {/* Agent name and selection indicator */}
                          <div className="flex items-center justify-between w-full mb-1">
                            <span className="font-medium">
                              {agent.name || agent.key}
                            </span>
                            {isSelected && (
                              <Check className="h-3 w-3 ml-2" aria-label="Currently selected" />
                            )}
                          </div>
                          
                          {/* First sentence of description */}
                          {firstSentence && (
                            <span className="text-xs text-muted-foreground mb-1.5">
                              {firstSentence}
                            </span>
                          )}
                          
                          {/* Tool badges - check multiple possible field names */}
                          {(() => {
                            // Check for tools in different possible fields
                            const tools = agent.tools || 
                                        (agent as any).tool_classes || 
                                        (agent as any).toolClasses || 
                                        (agent as any).equipped_tools ||
                                        []
                            
                            if (Array.isArray(tools) && tools.length > 0) {
                              return (
                                <div className="flex flex-wrap gap-1">
                                  {tools.slice(0, 3).map((toolClass, index) => (
                                    <Badge 
                                      key={`${toolClass}-${index}`} 
                                      variant="secondary" 
                                      className="text-xs py-0 h-5"
                                    >
                                      {formatToolName(toolClass)}
                                    </Badge>
                                  ))}
                                  {tools.length > 3 && (
                                    <Badge 
                                      variant="outline" 
                                      className="text-xs py-0 h-5"
                                    >
                                      +{tools.length - 3} more
                                    </Badge>
                                  )}
                                </div>
                              )
                            }
                            return null
                          })()}
                        </DropdownMenuItem>
                      </TooltipTrigger>
                      
                      {/* Full description tooltip */}
                      {agent.agent_description && agent.agent_description !== firstSentence && (
                        <TooltipContent 
                          side="right" 
                          className="max-w-[400px] p-3"
                          sideOffset={5}
                        >
                          <div className="space-y-2">
                            <p className="font-medium">{agent.name}</p>
                            <p className="text-sm">{agent.agent_description}</p>
                          </div>
                        </TooltipContent>
                      )}
                    </Tooltip>
                  )
                })}
              </div>
            ) : (
              <DropdownMenuItem disabled className="text-muted-foreground text-sm">
                {isLoading ? "Loading agents..." : "No agents available"}
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
      </TooltipProvider>
    )
  }
)

AgentSelector.displayName = "AgentSelector"