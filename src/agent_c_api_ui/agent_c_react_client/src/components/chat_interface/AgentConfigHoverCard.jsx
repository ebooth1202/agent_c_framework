import React, { useState, useEffect, useRef } from 'react';
import { Settings, Info, Server, Thermometer, Zap, Brain, User, Wrench, Key } from 'lucide-react';
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hovercard";
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
      <div className={`inline-flex items-center cursor-wait ${className}`}>
        <Settings className="w-4 h-4 text-gray-400 animate-pulse" />
        <span className="ml-1 text-sm text-gray-400">Loading...</span>
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
        <div className={`inline-flex items-center cursor-help ${className}`}>
          <Settings className="w-4 h-4 text-blue-500 hover:text-blue-600 transition-colors" />
          <span className="ml-1.5 text-sm text-blue-500 hover:text-blue-600 transition-colors font-medium">
            Agent Config
          </span>
        </div>
      </HoverCardTrigger>
      <Portal.Root>
        <HoverCardContent
          side="right"
          align="start"
          className="w-80 p-0 bg-white border shadow-lg rounded-lg z-50"
        >
          <Card className="border-0 shadow-none">
            <CardHeader className="pb-2 space-y-1.5">
              <div className="flex items-center gap-2">
                <ModelIcon vendor={vendor} />
                <CardTitle className="text-base font-semibold">
                  {config.model_info?.name || "Unknown Model"}
                </CardTitle>
              </div>
              <div className="text-xs text-gray-500 flex items-center gap-1.5">
                <Server className="w-3.5 h-3.5" />
                <span>{config.backend || "Unknown Backend"}</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pb-4">
              {/* Parameters Section */}
              <div className="space-y-2">
                <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide">Parameters</h4>
                <div className="flex flex-wrap gap-2">
                  {config.model_info?.temperature != null && (
                    <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200 font-normal flex items-center gap-1">
                      <Thermometer className="w-3 h-3" />
                      {config.model_info.temperature.toFixed(2)}
                    </Badge>
                  )}

                  {config.model_info?.reasoning_effort != null && (
                    <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200 font-normal flex items-center gap-1">
                      <Brain className="w-3 h-3" />
                      {config.model_info.reasoning_effort}
                    </Badge>
                  )}

                  {config.model_info?.extended_thinking != null && (
                    <Badge
                      variant="outline"
                      className={`${
                        typeof config.model_info.extended_thinking === 'object' 
                          ? config.model_info.extended_thinking.enabled 
                          : config.model_info.extended_thinking 
                          ? 'bg-green-50 text-green-700 border-green-200' 
                          : 'bg-gray-50 text-gray-500 border-gray-200'
                      } font-normal flex items-center gap-1`}
                    >
                      <Zap className="w-3 h-3" />
                      {typeof config.model_info.extended_thinking === 'object'
                        ? (config.model_info.extended_thinking.enabled ? "Thinking On" : "Thinking Off")
                        : (config.model_info.extended_thinking ? "Thinking On" : "Thinking Off")}
                    </Badge>
                  )}

                  {(config.model_info?.extended_thinking?.budget_tokens || config.model_info?.budget_tokens) && (
                    <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200 font-normal flex items-center gap-1">
                      <span className="text-xs">⏱️</span>
                      {(config.model_info?.extended_thinking?.budget_tokens || config.model_info?.budget_tokens).toLocaleString()} tokens
                    </Badge>
                  )}
                </div>
              </div>

              {/* Persona Section */}
              <div className="space-y-2">
                <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide">Persona</h4>
                <div className="flex items-center">
                  <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-200 font-normal flex items-center gap-1">
                    <User className="w-3 h-3" />
                    {config.persona_name || "Default"}
                  </Badge>
                </div>
              </div>

              {/* Tools Section */}
              {formattedTools.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide flex items-center gap-1">
                    Tools <span className="text-gray-400">({formattedTools.length})</span>
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {formattedTools.map((tool, idx) => (
                      <Badge
                        key={`tool-${idx}`}
                        variant="outline"
                        className="bg-green-50 text-green-700 border-green-200 font-normal text-xs"
                      >
                        {tool}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {/* Session IDs Section - Collapsible or in smaller text */}
              <div className="pt-1 border-t border-gray-100">
                <div className="text-xs text-gray-500 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">UI Agent Instance:</span>
                    <code className="text-xs bg-gray-50 px-1 py-0.5 rounded">{config.ui_session_id || "undefined"}</code>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-medium">Interaction Session:</span>
                    <code className="text-xs bg-gray-50 px-1 py-0.5 rounded">{config.agent_c_session_id || "undefined"}</code>
                  </div>
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