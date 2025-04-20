// src/pages/ChatPage.jsx
import React, { useContext } from 'react';
import { SessionContext } from '@/contexts/SessionContext';
import ChatInterface from '../components/chat_interface/ChatInterface';
import CollapsibleOptions from '@/components/chat_interface//CollapsibleOptions';
// StatusBar now moved to ChatInterface component
import { Alert, AlertDescription } from '@/components/ui/alert';

const ChatPage = () => {
  const {
    sessionId,
    error,
    isLoading,
    isInitialized,
    isReady,
    isStreaming,
    activeTools,
    settingsVersion,
    handleSessionsDeleted,
    persona,
    personas,
    availableTools,
    customPrompt,
    temperature,
    modelName,
    modelConfigs,
    updateAgentSettings,
    handleEquipTools,
    modelParameters,
    selectedModel,
    handleProcessingStatus,
    isOptionsOpen,
    setIsOptionsOpen
  } = useContext(SessionContext);

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-lg text-muted-foreground animate-pulse">
          Initializing session...
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] overflow-hidden">
      <div className="flex flex-col space-y-4 mb-4">
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription className="flex justify-between items-center">
              {error}
              <button
                onClick={() => {
                  // Clear error if needed (or expose a context setter)
                }}
                className="ml-2 text-sm underline hover:no-underline"
              >
                Dismiss
              </button>
            </AlertDescription>
          </Alert>
        )}
      </div>

      {sessionId && isInitialized && (
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <div className="flex-shrink-0">
            <CollapsibleOptions
              isOpen={isOptionsOpen}
              setIsOpen={setIsOptionsOpen}
              persona={persona}
              personas={personas}
              availableTools={availableTools}
              customPrompt={customPrompt}
              temperature={temperature}
              modelName={modelName}
              modelConfigs={modelConfigs}
              sessionId={sessionId}
              isReady={isReady}
              onEquipTools={handleEquipTools}
              activeTools={activeTools}
              modelParameters={modelParameters}
              selectedModel={selectedModel}
              onUpdateSettings={updateAgentSettings}
              isInitialized={isInitialized}
              onProcessingStatus={handleProcessingStatus}
            />
          </div>

          <div className="flex-1 overflow-hidden flex flex-col">
            <ChatInterface
              sessionId={sessionId}
              customPrompt={customPrompt}
              modelName={modelName}
              modelParameters={modelParameters}
              selectedModel={selectedModel}
              onProcessingStatus={handleProcessingStatus}
            />
            {/* StatusBar moved to ChatInterface component */}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;
