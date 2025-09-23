"use client"

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function SimpleChat() {
  const [messages, setMessages] = useState<Array<{role: string, content: string}>>([]);
  const [inputText, setInputText] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  const handleConnect = () => {
    setIsConnected(!isConnected);
    if (!isConnected) {
      setMessages([{role: 'system', content: 'Connected to Agent C! (Demo mode - SDK integration coming next)'}]);
    }
  };

  const handleSendMessage = () => {
    if (inputText.trim() && isConnected) {
      setMessages(prev => [...prev, {role: 'user', content: inputText}]);
      // Simulate agent response
      setTimeout(() => {
        setMessages(prev => [...prev, {role: 'agent', content: 'Hello! I received your message: "' + inputText + '". The realtime SDK is now built and ready for full integration!'}]);
      }, 1000);
      setInputText('');
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Agent C Realtime Chat (Demo)
          <Button onClick={handleConnect} variant={isConnected ? "destructive" : "default"}>
            {isConnected ? 'Disconnect' : 'Connect'}
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="border rounded-lg p-4 h-96 overflow-y-auto bg-gray-50">
          {messages.length === 0 ? (
            <p className="text-gray-500 text-center">Click Connect to start chatting</p>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`mb-4 p-3 rounded-lg max-w-[80%] ${
                message.role === 'user' ? 'bg-blue-500 text-white ml-auto' : 
                message.role === 'system' ? 'bg-green-100 text-green-800' :
                'bg-white border'
              }`}>
                <div className="text-sm font-medium mb-1">
                  {message.role === 'user' ? 'You' : message.role === 'system' ? 'System' : 'Agent'}
                </div>
                <div>{message.content}</div>
              </div>
            ))
          )}
        </div>
        
        <div className="flex gap-2">
          <Input
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder={isConnected ? "Type your message..." : "Connect first"}
            disabled={!isConnected}
            className="flex-1"
          />
          <Button onClick={handleSendMessage} disabled={!isConnected || !inputText.trim()}>
            Send
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}