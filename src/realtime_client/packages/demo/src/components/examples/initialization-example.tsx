'use client';

import React from 'react';
import { useAgentCData, useInitializationStatus, useRealtimeClient } from '@agentc/realtime-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

/**
 * Example component demonstrating the new initialization hooks
 * Shows how to access data that comes from WebSocket events
 */
export function InitializationExample() {
  const client = useRealtimeClient();
  const { isInitialized, receivedEvents, pendingEvents } = useInitializationStatus();
  const { user, agents, avatars, voices, toolsets, currentSession } = useAgentCData();

  return (
    <div className="space-y-6">
      {/* Initialization Status */}
      <Card>
        <CardHeader>
          <CardTitle>Initialization Status</CardTitle>
          <CardDescription>
            Data loaded from WebSocket events after connection
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Status:</span>
              <Badge 
                variant={isInitialized ? "default" : "secondary"}
                className={isInitialized ? "bg-green-500 text-white hover:bg-green-600" : ""}
              >
                {isInitialized ? "Fully Initialized" : "Initializing..."}
              </Badge>
            </div>
            
            <div>
              <span className="text-sm font-medium">Received Events:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {Array.from(receivedEvents).map((event) => (
                  <Badge key={event} variant="outline" className="text-xs">
                    {event}
                  </Badge>
                ))}
              </div>
            </div>
            
            {pendingEvents.length > 0 && (
              <div>
                <span className="text-sm font-medium">Pending Events:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {pendingEvents.map((event) => (
                    <Badge key={event} variant="secondary" className="text-xs">
                      {event}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* User Data */}
      <Card>
        <CardHeader>
          <CardTitle>User Profile</CardTitle>
          <CardDescription>
            From chat_user_data event
          </CardDescription>
        </CardHeader>
        <CardContent>
          {user ? (
            <div className="space-y-2 text-sm">
              <div><strong>ID:</strong> {user.user_id}</div>
              <div><strong>Username:</strong> {user.user_name}</div>
              <div><strong>Email:</strong> {user.email || 'N/A'}</div>
              <div><strong>Name:</strong> {user.first_name} {user.last_name}</div>
              <div><strong>Active:</strong> {user.is_active ? 'Yes' : 'No'}</div>
            </div>
          ) : (
            <p className="text-muted-foreground">Waiting for user data...</p>
          )}
        </CardContent>
      </Card>

      {/* Available Resources */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Agents */}
        <Card>
          <CardHeader>
            <CardTitle>Available Agents ({agents.length})</CardTitle>
            <CardDescription>From agent_list event</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-40">
              {agents.length > 0 ? (
                <div className="space-y-2">
                  {agents.map((agent) => (
                    <div key={agent.key} className="text-sm">
                      <div className="font-medium">{agent.name}</div>
                      <div className="text-xs text-muted-foreground">{agent.key}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No agents loaded yet</p>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Voices */}
        <Card>
          <CardHeader>
            <CardTitle>Available Voices ({voices.length})</CardTitle>
            <CardDescription>From voice_list event</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-40">
              {voices.length > 0 ? (
                <div className="space-y-2">
                  {voices.slice(0, 10).map((voice) => (
                    <div key={voice.voice_id} className="text-sm">
                      <div className="font-medium">{voice.description}</div>
                      <div className="text-xs text-muted-foreground">
                        {voice.vendor} - {voice.voice_id}
                      </div>
                    </div>
                  ))}
                  {voices.length > 10 && (
                    <p className="text-xs text-muted-foreground">
                      ...and {voices.length - 10} more
                    </p>
                  )}
                </div>
              ) : (
                <p className="text-muted-foreground">No voices loaded yet</p>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Avatars */}
        <Card>
          <CardHeader>
            <CardTitle>Available Avatars ({avatars.length})</CardTitle>
            <CardDescription>From avatar_list event</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-40">
              {avatars.length > 0 ? (
                <div className="space-y-2">
                  {avatars.map((avatar) => (
                    <div key={avatar.avatar_id} className="text-sm">
                      <div className="font-medium">{avatar.pose_name}</div>
                      <div className="text-xs text-muted-foreground">
                        {avatar.avatar_id}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No avatars loaded yet</p>
              )}
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Toolsets */}
        <Card>
          <CardHeader>
            <CardTitle>Available Toolsets ({toolsets.length})</CardTitle>
            <CardDescription>From tool_catalog event</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-40">
              {toolsets.length > 0 ? (
                <div className="space-y-2">
                  {toolsets.map((toolset) => (
                    <div key={toolset.name} className="text-sm">
                      <div className="font-medium">{toolset.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {toolset.description}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground">No toolsets loaded yet</p>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Current Session */}
      <Card>
        <CardHeader>
          <CardTitle>Current Session</CardTitle>
          <CardDescription>
            From chat_session_changed event
          </CardDescription>
        </CardHeader>
        <CardContent>
          {currentSession ? (
            <div className="space-y-2 text-sm">
              <div><strong>ID:</strong> {currentSession.session_id}</div>
              <div><strong>Name:</strong> {currentSession.session_name || 'Unnamed'}</div>
              <div><strong>Agent:</strong> {currentSession.agent_config?.name || currentSession.agent_config?.key}</div>
              <div><strong>Created:</strong> {new Date(currentSession.created_at || '').toLocaleString()}</div>
            </div>
          ) : (
            <p className="text-muted-foreground">No active session</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}