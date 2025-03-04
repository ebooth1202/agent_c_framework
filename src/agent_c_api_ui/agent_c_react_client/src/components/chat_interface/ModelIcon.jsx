import React from 'react';
import {Sparkles, HelpCircle, Brain} from 'lucide-react';
import {Tooltip, TooltipTrigger, TooltipContent, TooltipProvider} from '@/components/ui/tooltip';

const ModelIcon = ({vendor}) => {
    const commonClasses = "h-6 w-6 p-0.5 rounded-full";

    switch (vendor?.toLowerCase()) {
        case 'anthropic':
            return (
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="relative">
                                <Brain className={`${commonClasses} text-gray-600`}/>
                                <div
                                    className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-teal-500 rounded-full border border-white"/>
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>Claude (Anthropic)</TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            );
        case 'openai':
            return (
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="relative">
                                <Sparkles className={`${commonClasses} text-gray-600`}/>
                                <div
                                    className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-teal-500 rounded-full border border-white"/>
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>GPT (OpenAI)</TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            );
        default:
            return (
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <HelpCircle className={`${commonClasses} text-gray-600`}/>
                        </TooltipTrigger>
                        <TooltipContent>AI Assistant</TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            );
    }
};

export default ModelIcon;
