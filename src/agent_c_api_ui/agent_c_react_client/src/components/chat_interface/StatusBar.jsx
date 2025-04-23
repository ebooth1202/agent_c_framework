import React from 'react';
import { Button } from '@/components/ui/button';
import AgentConfigHoverCard from './AgentConfigHoverCard';
import { Activity, Wrench, Info, Copy, Download } from 'lucide-react';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";
import CopyButton from './CopyButton';
import ExportHTMLButton from './ExportHTMLButton';


const StatusBar = ({
    isReady,
    activeTools = [],
    isInitializing = false,
    isProcessing = false,
    sessionId,
    settingsVersion,
    getChatCopyContent,
    getChatCopyHTML,
    messages
}) => {


    const getStatusInfo = () => {
        if (isProcessing) {
            return {
                message: 'Processing...',
                description: 'Agent is processing your request'
            };
        }
        if (isInitializing) {
            return {
                message: 'Initializing Application...',
                description: 'Loading initial application data'
            };
        }
        if (!isReady) {
            return {
                message: 'Initializing Agent...',
                description: 'Setting up the agent and tools'
            };
        }
        return {
            message: 'Ready',
            description: 'System is ready to process requests'
        };
    };

    const statusInfo = getStatusInfo();

    return (
        <div className="status-bar">
            <div className="status-bar-section">
                <div className="status-indicator-section">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <div className="status-indicator-wrapper">
                                    <Activity
                                        className={isProcessing 
                                            ? 'status-indicator-icon-processing' 
                                            : isInitializing || !isReady 
                                                ? 'status-indicator-icon-initializing' 
                                                : 'status-indicator-icon-ready'
                                        }
                                    />
                                    <span className="status-text">
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
                    <div className="tools-badge">
                        <Wrench className="tools-icon" />
                        <span className="tools-count-text">
                            Active Tools: {activeTools.length}
                        </span>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <Info className="tools-info-icon" />
                                </TooltipTrigger>
                                <TooltipContent className="tools-tooltip-content">
                                    <p className="max-w-xs text-muted-foreground">{activeTools.join(', ')}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </div>
                )}
            </div>
            
            {/* Chat export actions */}
            <div className="chat-export-actions">
                <CopyButton
                    content={getChatCopyContent}
                    htmlContent={getChatCopyHTML}
                    tooltipText="Copy entire chat"
                    successText="Chat copied!"
                    size="sm"
                    variant="ghost"
                    className="chat-export-button"
                    icon={<Copy className="chat-export-icon" />}
                    iconOnly
                />
                <ExportHTMLButton
                    messages={messages}
                    tooltipText="Export as HTML"
                    filename={`chat-export-${new Date().toISOString().slice(0, 10)}.html`}
                    size="sm"
                    variant="ghost"
                    className="chat-export-button"
                    icon={<Download className="chat-export-icon" />}
                    iconOnly
                />
            </div>
        </div>
    );
};

export default StatusBar;