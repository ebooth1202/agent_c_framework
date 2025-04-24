import React, { useState, useEffect, useRef } from 'react';
import { Settings, Info, Server, Thermometer, Zap, Brain, User, Wrench, Key } from 'lucide-react';
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ModelIcon from '@/components/chat_interface/ModelIcon';
import { API_URL } from "@/config/config";

/**
 * AgentConfigHoverCard is a component that fetches and displays agent configuration
 * information in an aesthetically pleasing hover card interface.
 *
 * @component
 * @param {Object} props
 * @param {string} props.sessionId - Session identifier for fetching configuration
 * @param {string} [props.className=""] - Additional CSS classes to apply
 * @param {number} props.settingsVersion - Version identifier that triggers config refresh
 */
const AgentConfigHoverCard = ({ sessionId, className = "", settingsVersion }) => {
  const [config, setConfig] = useState(null);
  const [error, setError] = useState(null);
  const lastFetchRef = useRef(null);

  useEffect(() => {
    if (sessionId) {
      setConfig(null);
    }

    const fetchConfig = async () => {
      try {
        if (!sessionId) {
          console.log('No sessionId provided, skipping fetch');
          return;
        }

        const fetchKey = `${sessionId}-${settingsVersion}`;

        if (lastFetchRef.current === fetchKey) {
          console.log('Duplicate fetch detected, skipping');
          return;
        }

        console.log('Fetching config... settingsVersion:', settingsVersion);
        const url = `${API_URL}/get_agent_config/${sessionId}`;

        const response = await fetch(url, {
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          }
        });

        if (!response.ok) {
          throw new Error(`Failed to fetch agent configuration: ${response.status}`);
        }

        const data = await response.json();
        console.log('Received new config for agent:', data);

        lastFetchRef.current = fetchKey;

        setConfig(data.config);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching agent config:', err);
      }
    };

    console.log('Triggering config fetch, settingsVersion:', settingsVersion);
    fetchConfig();
  }, [sessionId, settingsVersion]);

  if (!sessionId) {
    return null;
  }

  if (error) {
    console.error("Error in AgentConfigHoverCard:", error);
    return null;
  }

  if (!config) {
    return (
      <div className={`agent-config-container agent-config-loading ${className}`}>
        <Settings className="agent-config-loading-icon animate-pulse" />
        <span className="agent-config-loading-text">Loading...</span>
      </div>
    );
  }

  // Determine vendor from model name
  const getVendor = (name) => {
    if (!name) return 'unknown';
    name = name.toLowerCase();
    if (name.includes('gpt') || name.includes('o1') || name.includes('o3')) {
      return 'openai';
    } else if (name.includes('claude')) {
      return 'anthropic';
    }
    return 'unknown';
  };

  const vendor = getVendor(config.model_info?.name);

  // Format initialized tools for display
  const formattedTools = config.initialized_tools?.map(tool => tool.class_name) || [];

  return (
    <HoverCard openDelay={200} closeDelay={100}>
      <HoverCardTrigger asChild>
        <div className={`agent-config-hover-card-trigger ${className}`}>
          <Settings className="agent-config-hover-card-icon" />
          <span className="agent-config-hover-card-text">
            Session Info
          </span>
        </div>
      </HoverCardTrigger>
      <HoverCardContent
        side="right"
        align="start"
        className="agent-config-hover-card-content w-96 p-0"
        sideOffset={5}
      >
        <Card className="border-0 shadow-none">
          <CardHeader className="agent-config-hover-card-header pb-2">
            <div className="agent-config-hover-card-model-container">
              <ModelIcon vendor={vendor} />
              <CardTitle className="text-base">
                {config.model_info?.name || "Unknown Model"}
              </CardTitle>
            </div>
            <div className="flex items-center text-xs text-muted-foreground gap-3">
              <Server className="w-3.5 h-3.5" />
              <span>{config.backend || "Unknown Backend"}</span>
            </div>
          </CardHeader>
          <CardContent className="pt-0 flex flex-col gap-4">
            {/* Parameters Section */}
            <div className="flex flex-col gap-2">
              <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Parameters
              </h4>
              <div className="flex flex-wrap gap-2">
                {config.model_info?.temperature != null && (
                  <Badge variant="outline" className="flex items-center gap-1 bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/30 dark:text-blue-300 dark:border-blue-800/30">
                    <Thermometer className="w-3 h-3" />
                    {config.model_info.temperature.toFixed(2)}
                  </Badge>
                )}

                {config.model_info?.reasoning_effort != null && (
                  <Badge variant="outline" className="flex items-center gap-1 bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/20 dark:text-purple-300 dark:border-purple-800/30">
                    <Brain className="w-3 h-3" />
                    {config.model_info.reasoning_effort}
                  </Badge>
                )}

                {config.model_info?.extended_thinking != null && (
                  <Badge
                    variant="outline"
                    className={`flex items-center gap-1 ${(
                      typeof config.model_info.extended_thinking === 'object'
                        ? config.model_info.extended_thinking.enabled
                        : config.model_info.extended_thinking
                    )
                      ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-950/20 dark:text-green-300 dark:border-green-800/30'
                      : 'bg-gray-100 text-gray-500 border-gray-200 dark:bg-gray-800/30 dark:text-gray-400 dark:border-gray-700/40'
                    }`}
                  >
                    <Zap className="w-3 h-3" />
                    {typeof config.model_info.extended_thinking === 'object'
                      ? (config.model_info.extended_thinking.enabled ? "Thinking On" : "Thinking Off")
                      : (config.model_info.extended_thinking ? "Thinking On" : "Thinking Off")}
                  </Badge>
                )}

                {(config.model_info?.extended_thinking?.budget_tokens || config.model_info?.budget_tokens) && (
                  <Badge variant="outline" className="flex items-center gap-1 bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-300 dark:border-amber-800/30">
                    <span className="text-xs">⏱️</span>
                    {(config.model_info?.extended_thinking?.budget_tokens || config.model_info?.budget_tokens).toLocaleString()} tokens
                  </Badge>
                )}
              </div>
            </div>

            {/* Persona Section */}
            <div className="flex flex-col gap-2">
              <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                Persona
              </h4>
              <div className="flex items-center">
                <Badge variant="outline" className="flex items-center gap-1 bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/20 dark:text-purple-300 dark:border-purple-800/30">
                  <User className="w-3 h-3" />
                  {config.persona_name || "Default"}
                </Badge>
              </div>
            </div>

            {/* Tools Section */}
            {formattedTools.length > 0 && (
              <div className="flex flex-col gap-2">
                <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide flex items-center gap-1">
                  Tools <span className="text-muted-foreground/70">({formattedTools.length})</span>
                </h4>
                <div className="flex flex-wrap gap-2">
                  {formattedTools.map((tool, idx) => (
                    <Badge
                      key={`tool-${idx}`}
                      variant="outline"
                      className="text-[0.65rem] bg-green-50 text-green-700 border-green-200 dark:bg-green-950/20 dark:text-green-300 dark:border-green-800/30"
                    >
                      {tool}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Session IDs Section */}
            <div className="pt-1 border-t border-border text-xs text-muted-foreground flex flex-col gap-1">
              <div className="flex items-center justify-between">
                <span className="font-medium">UI Agent Instance:</span>
                <code className="text-[0.65rem] bg-muted px-1 py-0.5 rounded font-mono">
                  {config.ui_session_id || "undefined"}
                </code>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">Interaction Session:</span>
                <code className="text-[0.65rem] bg-muted px-1 py-0.5 rounded font-mono">
                  {config.agent_c_session_id || "undefined"}
                </code>
              </div>
            </div>
          </CardContent>
        </Card>
      </HoverCardContent>
    </HoverCard>
  );
};

export default AgentConfigHoverCard;