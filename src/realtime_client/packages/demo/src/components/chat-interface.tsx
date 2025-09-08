"use client"

import React, { useState } from 'react';
import { useConnection, useChat, useAudio } from '@agentc/realtime-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function ChatInterface() {
  const { connect, disconnect, isConnected, connectionState } = useConnection();
  const { messages, sendMessage, isAgentTyping } = useChat();
  const { startRecording, stopRecording, isRecording, audioLevel } = useAudio();
  const [inputText, setInputText] = useState('');

  const handleConnect = async () => {
    try {
      await connect();
    } catch (error) {
      console.error('Connection failed:', error);
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
    <div className="max-w-4xl mx-auto p-6 space-y-6">
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
                  Recording (Level: {Math.round(audioLevel * 100)}%)
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
              {isConnected ? 'Disconnect' : 'Connect'}
            </Button>
            
            <Button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={!isConnected}
              variant={isRecording ? "destructive" : "secondary"}
            >
              {isRecording ? 'Stop Recording' : 'Start Voice'}
            </Button>
          </div>

          {/* Messages */}
          <div className="border rounded-lg p-4 h-96 overflow-y-auto bg-gray-50">
            {messages.length === 0 ? (
              <p className="text-gray-500 text-center">
                {isConnected ? 'Start a conversation...' : 'Connect to begin chatting'}
              </p>
            ) : (
              messages.map((message, index) => (
                <div
                  key={index}
                  className={`mb-4 p-3 rounded-lg max-w-[80%] ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white ml-auto'
                      : 'bg-white border'
                  }`}
                >
                  <div className="text-sm font-medium mb-1">
                    {message.role === 'user' ? 'You' : 'Agent'}
                  </div>
                  <div>{message.content}</div>
                </div>
              ))
            )}
            {isAgentTyping && (
              <div className="bg-white border p-3 rounded-lg max-w-[80%]">
                <div className="text-sm font-medium mb-1">Agent</div>
                <div className="animate-pulse">Typing...</div>
              </div>
            )}
          </div>

          {/* Text Input */}
          <div className="flex gap-2">
            <Input
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isConnected ? "Type your message..." : "Connect first"}
              disabled={!isConnected}
              className="flex-1"
            />
            <Button
              onClick={handleSendMessage}
              disabled={!isConnected || !inputText.trim()}
            >
              Send
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}