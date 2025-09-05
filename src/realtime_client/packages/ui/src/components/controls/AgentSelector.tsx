"use client"

/**
 * AgentSelector Component
 * 
 * Provides a select dropdown for choosing between available AI agents.
 * Displays agent name, description, and equipped tools as badges.
 */

import * as React from "react"
import { Bot, ChevronDown } from "lucide-react"
import { useAgentCData, useInitializationStatus, useRealtimeClientSafe } from "@agentc/realtime-react"
import type { Agent } from "@agentc/realtime-react"
import { cn } from "../../lib/utils"
import { Badge } from "../ui/badge"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../ui/select"

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

export const AgentSelector = React.forwardRef<HTMLButtonElement, AgentSelectorProps>(
  ({ className, disabled = false, showIcon = true, placeholder = "Select an agent" }, ref) => {
    const client = useRealtimeClientSafe()
    const { data, isInitialized, isLoading } = useAgentCData()
    const { isInitialized: connectionInitialized } = useInitializationStatus()
    
    const [selectedAgent, setSelectedAgent] = React.useState<string>('')
    const [isChanging, setIsChanging] = React.useState(false)
    
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
    
    const handleAgentSelect = async (agentKey: string) => {
      if (!client || agentKey === selectedAgent) return
      
      setIsChanging(true)
      try {
        client.setAgent(agentKey)
        setSelectedAgent(agentKey)
      } finally {
        // Give UI time to update
        setTimeout(() => setIsChanging(false), 300)
      }
    }
    
    const isDisabled = disabled || !client || !isInitialized || !connectionInitialized || isLoading || isChanging
    
    // Find the current agent details
    const currentAgent = data.agents.find(agent => agent.key === selectedAgent)
    
    return (
      <Select
        value={selectedAgent}
        onValueChange={handleAgentSelect}
        disabled={isDisabled}
      >
        <SelectTrigger 
          ref={ref}
          className={cn("w-[250px]", className)}
          aria-label="Select an agent"
        >
          <div className="flex items-center gap-2">
            {showIcon && <Bot className="h-4 w-4" />}
            <SelectValue placeholder={isLoading ? "Loading agents..." : placeholder} />
          </div>
        </SelectTrigger>
        
        <SelectContent className="w-[350px]">
          <SelectGroup>
            <SelectLabel>Available Agents</SelectLabel>
            {data.agents.map((agent) => (
              <SelectItem 
                key={agent.key} 
                value={agent.key}
                className="py-3"
              >
                <div className="flex flex-col gap-1">
                  {/* Agent name */}
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{agent.name}</span>
                  </div>
                  
                  {/* Agent description */}
                  {agent.agent_description && (
                    <span className="text-xs text-muted-foreground line-clamp-2">
                      {agent.agent_description}
                    </span>
                  )}
                  
                  {/* Tool badges */}
                  {agent.category && agent.category.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {agent.category.map((toolClass) => (
                        <Badge 
                          key={toolClass} 
                          variant="secondary" 
                          className="text-xs py-0 h-5"
                        >
                          {formatToolName(toolClass)}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </SelectItem>
            ))}
            
            {data.agents.length === 0 && (
              <SelectItem value="no-agents" disabled>
                <span className="text-muted-foreground">No agents available</span>
              </SelectItem>
            )}
          </SelectGroup>
        </SelectContent>
      </Select>
    )
  }
)

AgentSelector.displayName = "AgentSelector"