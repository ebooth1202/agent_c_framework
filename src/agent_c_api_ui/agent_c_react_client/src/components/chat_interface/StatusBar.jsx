import React from 'react';
import { Button } from '@/components/ui/button';
import AgentConfigHoverCard from './AgentConfigHoverCard';
import { Activity, Wrench, Info } from 'lucide-react';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";


const StatusBar = ({
    isReady,
    activeTools = [],
    isInitializing = false,
    isProcessing = false,
    sessionId,
    settingsVersion
}) => {


    const getStatusInfo = () => {
        if (isProcessing) {
            return {
                message: 'Processing...',
                color: 'text-red-500',
                description: 'Agent is processing your request',
                iconClass: 'animate-pulse'
            };
        }
        if (isInitializing) {
            return {
                message: 'Initializing Application...',
                color: 'text-yellow-500',
                description: 'Loading initial application data',
                iconClass: ''
            };
        }
        if (!isReady) {
            return {
                message: 'Initializing Agent...',
                color: 'text-yellow-500',
                description: 'Setting up the agent and tools',
                iconClass: ''
            };
        }
        return {
            message: 'Ready',
            color: 'text-green-500',
            description: 'System is ready to process requests',
            iconClass: ''
        };
    };

    const statusInfo = getStatusInfo();

    return (
        <div className="flex items-center justify-between py-2 px-3 bg-background/95 backdrop-blur-sm rounded-lg shadow-sm border text-sm">
            <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <div className="flex items-center space-x-2">
                                    <Activity
                                        className={`w-4 h-4 ${statusInfo.color} ${statusInfo.iconClass} ${
                                            isProcessing ? 'scale-110 transition-transform duration-200' : ''
                                        }`}
                                    />
                                    <span className="text-sm font-medium">
                                        Status: {statusInfo.message}
                                    </span>
                                </div>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p>{statusInfo.description}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                    {isReady && sessionId && (
                        <AgentConfigHoverCard
                            sessionId={sessionId}
                            className="ml-2"
                            settingsVersion={settingsVersion}
                        />
                    )}
                </div>

                {isReady && activeTools && activeTools.length > 0 && (
                    <div className="flex items-center space-x-2 px-4 py-1.5 bg-blue-50/10 rounded-full border border-blue-200/20 dark:bg-blue-950/20 dark:border-blue-800/30">
                        <Wrench className="w-4 h-4 text-blue-500 dark:text-blue-400" />
                        <span className="text-sm text-blue-700 dark:text-blue-300">
                            Active Tools: {activeTools.length}
                        </span>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Info className="w-4 h-4 text-blue-400 dark:text-blue-300 cursor-help" />
                                </TooltipTrigger>
                                <TooltipContent className="bg-background border shadow-md">
                                    <p className="max-w-xs text-muted-foreground">{activeTools.join(', ')}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StatusBar;