// Update ThoughtDisplay.jsx to include collapsible functionality
import React, {useState} from 'react';
import {Lightbulb, ChevronDown} from 'lucide-react';
import {Card} from "@/components/ui/card";
import ModelIcon from './ModelIcon';

const ThoughtDisplay = ({content, vendor}) => {
    const [isExpanded, setIsExpanded] = useState(true);

    return (
        <Card className="bg-yellow-50 border-yellow-100 shadow-sm overflow-hidden mb-3">
            <div className="px-4 py-3 flex items-center justify-between cursor-pointer"
                 onClick={() => setIsExpanded(!isExpanded)}>
                <div className="flex items-center gap-2">
                    <ModelIcon vendor={vendor}/>
                    {/*<Lightbulb className="h-5 w-5 text-yellow-600"/>*/}
                    <span className="font-semibold text-yellow-800 text-sm">Thinking Process</span>
                </div>
                <ChevronDown className={`h-5 w-5 text-yellow-600 transform transition-transform duration-200 ${
                    isExpanded ? "rotate-180" : ""
                }`}/>
            </div>

            {isExpanded && (
                <div className="border-t border-yellow-100 px-4 py-3">
                    <div className="text-yellow-700 text-sm whitespace-pre-wrap font-mono overflow-auto max-h-80">
                        {content}
                    </div>
                </div>
            )}
        </Card>
    );
};

export default ThoughtDisplay;