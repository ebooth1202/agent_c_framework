import React, {useState} from 'react';
import {ChevronDown} from 'lucide-react';
import {Card} from "@/components/ui/card";
import ModelIcon from './ModelIcon';
import CopyButton from './CopyButton';
import MarkdownMessage from "@/components/chat_interface/MarkdownMessage";

const ThoughtDisplay = ({content, vendor}) => {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <Card className="bg-yellow-50 border-yellow-100 shadow-sm overflow-hidden mb-3 relative">
            <div className="px-4 py-3 flex items-center justify-between cursor-pointer"
                 onClick={() => setIsExpanded(!isExpanded)}>
                <div className="flex items-center gap-2">
                    <ModelIcon vendor={vendor}/>
                    <span className="font-semibold text-yellow-800 text-sm">Thinking Process</span>
                </div>
                <div className="flex items-center gap-2">
                    {/* Copy button - always visible in header */}
                    <div onClick={(e) => e.stopPropagation()}>
                        <CopyButton
                            content={content}
                            tooltipText="Copy thinking process"
                            variant="ghost"
                            className="text-yellow-600 hover:text-yellow-800 hover:bg-yellow-100"
                        />
                    </div>
                    <ChevronDown className={`h-5 w-5 text-yellow-600 transform transition-transform duration-200 ${
                        isExpanded ? "rotate-180" : ""
                    }`}/>
                </div>
            </div>

            {isExpanded && (
                <div className="border-t border-yellow-100 px-4 py-3">
                    <div className="text-yellow-700 text-sm whitespace-pre-wrap font-mono overflow-auto max-h-80">
                        {content}
                        {/*<MarkdownMessage content={content}/>*/}
                    </div>
                </div>
            )}
        </Card>
    );
};

export default ThoughtDisplay;