// src/pages/ChatPage.jsx
import React, { useContext } from 'react';
import { SessionContext } from '@/contexts/SessionContext';
import ChatInterface from '../components/chat_interface/ChatInterface';
// Remove the CollapsibleOptions import since it will be used directly in ChatInterface
// import CollapsibleOptions from '@/components/chat_interface//CollapsibleOptions';
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
  
  console.log("ChatPage is rendering!", { isLoading, sessionId, isInitialized });

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-blue-50">
        <div className="text-lg text-blue-700 animate-pulse bg-blue-100 px-6 py-4 rounded-lg border border-blue-200">
          Initializing session...
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 overflow-hidden bg-blue-50">
      <div className="flex flex-col space-y-2 mb-1 px-4 pt-4">
        {error && (
          <Alert variant="destructive" className="mb-2 bg-red-50 border-red-300 text-red-800">
            <AlertDescription className="flex justify-between items-center">
              {error}
              <button
                onClick={() => {
                  // Clear error if needed (or expose a context setter)
                }}
                className="ml-2 text-sm underline hover:no-underline text-red-700 hover:text-red-900"
              >
                Dismiss
              </button>
            </AlertDescription>
          </Alert>
        )}
      </div>

      {sessionId && isInitialized && (
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden bg-blue-50">
          {/* CollapsibleOptions removed from here since it's now in ChatInterface */}
          
          <div className="flex-1 overflow-hidden flex flex-col bg-white border-t border-blue-200 rounded-t-lg mx-4 shadow-sm">
            <ChatInterface
              sessionId={sessionId}
              customPrompt={customPrompt}
              modelName={modelName}
              modelParameters={modelParameters}
              onProcessingStatus={handleProcessingStatus}
              // Added props for options panel
              persona={persona}
              personas={personas}
              availableTools={availableTools}
              modelConfigs={modelConfigs}
              onEquipTools={handleEquipTools}
              selectedModel={selectedModel}
              onUpdateSettings={updateAgentSettings}
              isInitialized={isInitialized}
            />
            {/* StatusBar moved to ChatInterface component */}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;