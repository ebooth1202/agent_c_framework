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
import * as Portal from '@radix-ui/react-portal';
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
      <Portal.Root>
        <HoverCardContent
          side="right"
          align="start"
          className="agent-config-hover-card-content"
        >
          <Card className="border-0 shadow-none">
            <CardHeader className="agent-config-hover-card-header">
              <div className="agent-config-hover-card-model-container">
                <ModelIcon vendor={vendor} />
                <CardTitle className="agent-config-hover-card-title">
                  {config.model_info?.name || "Unknown Model"}
                </CardTitle>
              </div>
              <div className="agent-config-hover-card-backend">
                <Server className="agent-config-hover-card-backend-icon" />
                <span>{config.backend || "Unknown Backend"}</span>
              </div>
            </CardHeader>
            <CardContent className="agent-config-hover-card-body">
              {/* Parameters Section */}
              <div className="agent-config-hover-card-section">
                <h4 className="agent-config-hover-card-section-title">Parameters</h4>
                <div className="agent-config-hover-card-badges">
                  {config.model_info?.temperature != null && (
                    <Badge variant="outline" className="agent-config-hover-card-badge agent-config-hover-card-badge-temperature">
                      <Thermometer className="w-3 h-3" />
                      {config.model_info.temperature.toFixed(2)}
                    </Badge>
                  )}

                  {config.model_info?.reasoning_effort != null && (
                    <Badge variant="outline" className="agent-config-hover-card-badge agent-config-hover-card-badge-reasoning">
                      <Brain className="w-3 h-3" />
                      {config.model_info.reasoning_effort}
                    </Badge>
                  )}

                  {config.model_info?.extended_thinking != null && (
                    <Badge
                      variant="outline"
                      className={`agent-config-hover-card-badge ${
                        typeof config.model_info.extended_thinking === 'object' 
                          ? config.model_info.extended_thinking.enabled 
                          : config.model_info.extended_thinking 
                          ? 'agent-config-hover-card-badge-thinking-enabled' 
                          : 'agent-config-hover-card-badge-thinking-disabled'
                      }`}
                    >
                      <Zap className="w-3 h-3" />
                      {typeof config.model_info.extended_thinking === 'object'
                        ? (config.model_info.extended_thinking.enabled ? "Thinking On" : "Thinking Off")
                        : (config.model_info.extended_thinking ? "Thinking On" : "Thinking Off")}
                    </Badge>
                  )}

                  {(config.model_info?.extended_thinking?.budget_tokens || config.model_info?.budget_tokens) && (
                    <Badge variant="outline" className="agent-config-hover-card-badge agent-config-hover-card-badge-budget">
                      <span className="text-xs">⏱️</span>
                      {(config.model_info?.extended_thinking?.budget_tokens || config.model_info?.budget_tokens).toLocaleString()} tokens
                    </Badge>
                  )}
                </div>
              </div>

              {/* Persona Section */}
              <div className="agent-config-hover-card-section">
                <h4 className="agent-config-hover-card-section-title">Persona</h4>
                <div className="flex items-center">
                  <Badge variant="outline" className="agent-config-hover-card-badge agent-config-hover-card-badge-persona">
                    <User className="w-3 h-3" />
                    {config.persona_name || "Default"}
                  </Badge>
                </div>
              </div>

              {/* Tools Section */}
              {formattedTools.length > 0 && (
                <div className="agent-config-hover-card-section">
                  <h4 className="agent-config-hover-card-section-title flex items-center gap-1">
                    Tools <span className="text-gray-400">({formattedTools.length})</span>
                  </h4>
                  <div className="agent-config-hover-card-badges">
                    {formattedTools.map((tool, idx) => (
                      <Badge
                        key={`tool-${idx}`}
                        variant="outline"
                        className="agent-config-hover-card-badge agent-config-hover-card-badge-tool"
                      >
                        {tool}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Session IDs Section */}
              <div className="agent-config-hover-card-session-info">
                <div className="agent-config-hover-card-session-row">
                  <span className="agent-config-hover-card-session-label">UI Agent Instance:</span>
                  <code className="agent-config-hover-card-session-id">{config.ui_session_id || "undefined"}</code>
                </div>
                <div className="agent-config-hover-card-session-row">
                  <span className="agent-config-hover-card-session-label">Interaction Session:</span>
                  <code className="agent-config-hover-card-session-id">{config.agent_c_session_id || "undefined"}</code>
                </div>
              </div>
            </CardContent>
          </Card>
        </HoverCardContent>
      </Portal.Root>
    </HoverCard>
  );
};

export default AgentConfigHoverCard;