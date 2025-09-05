import * as React from 'react'
import { ChevronDown, Check, Bot, User } from 'lucide-react'
import { cn } from '../../lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
} from '../ui/dropdown-menu'
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar'
import { Badge } from '../ui/badge'
import { Button } from '../ui/button'
import type { Agent, AgentTool } from './types'

export interface AgentSelectorProps {
  agents?: Agent[]
  selectedAgent: Agent | null
  onAgentSelect: (agent: Agent) => void
  disabled?: boolean
  className?: string
  variant?: 'dropdown' | 'modal'
}

// Default agents for testing
const defaultAgents: Agent[] = [
  {
    id: 'general',
    name: 'General Assistant',
    description: 'A helpful AI assistant for general tasks and conversations',
    tools: [
      { id: 'search', name: 'Search' },
      { id: 'calculate', name: 'Calculate' }
    ],
    capabilities: ['General Q&A', 'Basic reasoning', 'Information synthesis']
  },
  {
    id: 'coder',
    name: 'Code Expert',
    description: 'Specialized in programming, debugging, and software architecture',
    tools: [
      { id: 'code', name: 'Code' },
      { id: 'debug', name: 'Debug' },
      { id: 'test', name: 'Test' },
      { id: 'review', name: 'Review' }
    ],
    capabilities: ['Code generation', 'Bug fixing', 'Code review', 'Architecture design']
  },
  {
    id: 'writer',
    name: 'Writing Assistant',
    description: 'Expert in creative writing, editing, and content creation',
    tools: [
      { id: 'write', name: 'Write' },
      { id: 'edit', name: 'Edit' },
      { id: 'format', name: 'Format' }
    ],
    capabilities: ['Creative writing', 'Editing', 'Proofreading', 'Content optimization']
  }
]

// Internal AgentCard component
const AgentCard: React.FC<{ 
  agent: Agent
  isSelected: boolean
  onClick: () => void
  disabled?: boolean
}> = ({ agent, isSelected, onClick, disabled }) => {
  return (
    <div
      className={cn(
        "relative p-3 rounded-lg border cursor-pointer transition-all duration-200",
        isSelected 
          ? "bg-accent border-accent shadow-sm" 
          : "hover:bg-accent/50 hover:border-accent/50",
        disabled && "opacity-50 cursor-not-allowed"
      )}
      onClick={!disabled ? onClick : undefined}
      role="option"
      aria-selected={isSelected}
      tabIndex={disabled ? -1 : 0}
      onKeyDown={(e) => {
        if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault()
          onClick()
        }
      }}
    >
      {/* Selected indicator */}
      {isSelected && (
        <div className="absolute top-2 right-2">
          <Check className="h-4 w-4 text-primary" aria-label="Selected" />
        </div>
      )}
      
      {/* Agent info section */}
      <div className="flex items-start gap-3 mb-2">
        <Avatar className="h-8 w-8 flex-shrink-0">
          <AvatarImage src={agent.avatar} alt={`${agent.name} avatar`} />
          <AvatarFallback className="bg-primary/10 text-primary">
            {agent.name.substring(0, 2).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm truncate pr-6">
            {agent.name}
          </h4>
          <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
            {agent.description}
          </p>
        </div>
      </div>
      
      {/* Tool badges section */}
      {agent.tools.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {agent.tools.slice(0, 3).map(tool => (
            <Badge 
              key={tool.id} 
              variant="secondary" 
              className="text-xs px-1.5 py-0 h-5"
            >
              {tool.name}
            </Badge>
          ))}
          {agent.tools.length > 3 && (
            <Badge 
              variant="outline" 
              className="text-xs px-1.5 py-0 h-5"
            >
              +{agent.tools.length - 3}
            </Badge>
          )}
        </div>
      )}
    </div>
  )
}

// Main AgentSelector component
const AgentSelector = React.forwardRef<HTMLButtonElement, AgentSelectorProps>(
  ({ 
    agents = defaultAgents, 
    selectedAgent, 
    onAgentSelect, 
    disabled = false, 
    className,
    variant = 'dropdown' 
  }, ref) => {
    const [open, setOpen] = React.useState(false)
    const [searchQuery, setSearchQuery] = React.useState('')
    
    // Filter agents based on search query
    const filteredAgents = React.useMemo(() => {
      if (!searchQuery) return agents
      
      const query = searchQuery.toLowerCase()
      return agents.filter(agent => 
        agent.name.toLowerCase().includes(query) ||
        agent.description.toLowerCase().includes(query) ||
        agent.tools.some(tool => tool.name.toLowerCase().includes(query))
      )
    }, [agents, searchQuery])
    
    // Handle agent selection
    const handleAgentSelect = React.useCallback((agent: Agent) => {
      onAgentSelect(agent)
      setOpen(false)
      setSearchQuery('')
    }, [onAgentSelect])
    
    if (variant === 'dropdown') {
      return (
        <DropdownMenu open={open} onOpenChange={setOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              ref={ref}
              variant="outline"
              role="combobox"
              aria-expanded={open}
              aria-haspopup="listbox"
              aria-label="Select an agent"
              disabled={disabled}
              className={cn(
                "w-full justify-between",
                className
              )}
            >
              <div className="flex items-center gap-2 truncate">
                {selectedAgent ? (
                  <>
                    <Avatar className="h-5 w-5">
                      <AvatarImage src={selectedAgent.avatar} />
                      <AvatarFallback className="text-xs bg-primary/10 text-primary">
                        {selectedAgent.name.substring(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <span className="truncate">{selectedAgent.name}</span>
                  </>
                ) : (
                  <>
                    <Bot className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Select Agent</span>
                  </>
                )}
              </div>
              <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          
          <DropdownMenuContent 
            className="w-[350px] p-2"
            align="start"
            sideOffset={5}
          >
            <DropdownMenuLabel className="px-2 py-1.5 text-sm font-semibold">
              Select Agent
            </DropdownMenuLabel>
            
            {/* Search input (optional for v1) */}
            {agents.length > 5 && (
              <>
                <div className="px-2 py-1.5">
                  <input
                    type="text"
                    placeholder="Search agents..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full px-2 py-1 text-sm border rounded-md focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-1"
                    aria-label="Search agents"
                  />
                </div>
                <DropdownMenuSeparator />
              </>
            )}
            
            {/* Agent list */}
            <div 
              className="max-h-[400px] overflow-y-auto py-1"
              role="listbox"
              aria-label="Available agents"
            >
              {filteredAgents.length > 0 ? (
                filteredAgents.map((agent) => (
                  <DropdownMenuItem
                    key={agent.id}
                    className="p-1 focus:bg-transparent"
                    onSelect={(e) => {
                      e.preventDefault() // Prevent closing on click
                    }}
                  >
                    <AgentCard
                      agent={agent}
                      isSelected={selectedAgent?.id === agent.id}
                      onClick={() => handleAgentSelect(agent)}
                      disabled={disabled}
                    />
                  </DropdownMenuItem>
                ))
              ) : (
                <div className="px-2 py-4 text-center text-sm text-muted-foreground">
                  No agents found
                </div>
              )}
            </div>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    }
    
    // Modal variant placeholder for future implementation
    return (
      <div className={cn("text-sm text-muted-foreground", className)}>
        Modal variant not yet implemented
      </div>
    )
  }
)

AgentSelector.displayName = 'AgentSelector'

export { AgentSelector, defaultAgents }