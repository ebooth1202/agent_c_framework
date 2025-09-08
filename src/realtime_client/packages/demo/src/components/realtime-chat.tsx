"use client"

import React, { useState } from 'react';
import { useConnection, useChat, useAudio } from '@agentc/realtime-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

export default function RealtimeChat() {
  const { connect, disconnect, isConnected, connectionState } = useConnection();
  const { messages, sendMessage, isAgentTyping } = useChat();
  const { startRecording, stopRecording, isRecording, audioLevel } = useAudio();
  const [inputText, setInputText] = useState('');

  // Debug logging
  React.useEffect(() => {
    console.log('🔍 RealtimeChat Debug:', {
      connect: typeof connect,
      disconnect: typeof disconnect,
      isConnected,
      connectionState,
      messages: messages?.length || 0
    });
  }, [connect, disconnect, isConnected, connectionState, messages]);

  const handleConnect = async () => {
    console.log('🚀 Attempting to connect to Agent C...');
    console.log('Connect function:', connect);
    
    try {
      if (typeof connect !== 'function') {
        console.error('❌ Connect is not a function:', typeof connect);
        return;
      }
      
      console.log('🔌 Calling connect()...');
      const result = await connect();
      console.log('✅ Connect result:', result);
    } catch (error) {
      console.error('❌ Connection failed:', error);
    }
  };

  const handleSendMessage = () => {
    if (inputText.trim() && isConnected) {
      sendMessage(inputText);
      setInputText('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Agent C Realtime Chat
          <div className="flex gap-2">
            <Badge variant={isConnected ? "default" : "secondary"}>
              {connectionState}
            </Badge>
            {isRecording && (
              <Badge variant="destructive">
                🎤 Recording ({Math.round(audioLevel * 100)}%)
              </Badge>
            )}
            {isAgentTyping && (
              <Badge variant="outline">
                ✨ Agent typing...
              </Badge>
            )}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Connection Controls */}
        <div className="flex gap-2">
          <Button 
            onClick={isConnected ? disconnect : handleConnect}
            variant={isConnected ? "destructive" : "default"}
          >
            {isConnected ? 'Disconnect' : 'Connect to Agent C'}
          </Button>
          
          <Button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={!isConnected}
            variant={isRecording ? "destructive" : "secondary"}
            size="sm"
          >
            {isRecording ? (
              <>
                <MicOff className="w-4 h-4 mr-1" />
                Stop Recording
              </>
            ) : (
              <>
                <Mic className="w-4 h-4 mr-1" />
                Voice Input
              </>
            )}
          </Button>
        </div>

        {/* Messages */}
        <div className="border rounded-lg p-4 h-96 overflow-y-auto bg-gray-50 dark:bg-gray-900">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              {isConnected ? (
                <div>
                  <p className="text-lg font-medium">🤖 Connected to Agent C!</p>
                  <p className="text-sm mt-2">Start a conversation with your AI agent...</p>
                </div>
              ) : (
                <div>
                  <p className="text-lg font-medium">🔌 Ready to Connect</p>
                  <p className="text-sm mt-2">Click &quot;Connect to Agent C&quot; to begin</p>
                </div>
              )}
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`mb-4 p-3 rounded-lg max-w-[80%] ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white ml-auto'
                      : 'bg-white dark:bg-gray-800 border shadow-sm'
                  }`}
                >
                  <div className="text-sm font-medium mb-1">
                    {message.role === 'user' ? '👤 You' : '🤖 Agent'}
                  </div>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                </div>
              ))}
              
              {isAgentTyping && (
                <div className="bg-white dark:bg-gray-800 border shadow-sm p-3 rounded-lg max-w-[80%]">
                  <div className="text-sm font-medium mb-1">🤖 Agent</div>
                  <div className="flex items-center gap-2">
                    <div className="animate-pulse">Thinking...</div>
                    <div className="flex gap-1">
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Text Input */}
        <div className="flex gap-2">
          <Input
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "Type your message to the AI agent..." : "Connect first to start chatting"}
            disabled={!isConnected}
            className="flex-1"
          />
          <Button
            onClick={handleSendMessage}
            disabled={!isConnected || !inputText.trim() || isAgentTyping}
          >
            Send
          </Button>
        </div>
        
        {/* Connection Info */}
        {isConnected && (
          <div className="text-xs text-gray-500 text-center">
            🔗 Connected to Agent C • Real-time AI conversation active
          </div>
        )}
      </CardContent>
    </Card>
  );
}