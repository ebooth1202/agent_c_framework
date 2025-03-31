import React, {useEffect} from 'react';
import {Card} from "@/components/ui/card";
import {Badge} from "@/components/ui/badge";
import ModelIcon from '../chat_interface/ModelIcon';

/**
 * ModelCardDisplay component displays model information at the start of a conversation
 *
 * @component
 * @param {Object} props
 * @param {string} props.modelName - The name of the model
 * @param {Object} props.modelParameters - The parameters used for the model
 * @param {string[]} props.toolNames - List of tool names available to the model
 */
const ModelCardDisplay = ({modelName, modelParameters, toolNames = []}) => {
    useEffect(() => {
        // console.log('ModelCardDisplay mounted with:', {modelName, modelParameters, toolNames});
    }, [modelName, modelParameters, toolNames]);

    // console.log("Mounted model card with parameters:", modelParameters)

    // Determine vendor from model name (simplified logic)
    const getVendor = (name) => {
        if (!name) return 'unknown';
        name = name.toLowerCase();
        if (name.includes('gpt') || name.includes('o1') || name.includes('o3')) {
            return 'openai';
        } else if (name.includes('claude')) {
            return 'anthropic';
        }
        return 'unknown';
    };

    const vendor = getVendor(modelName);

    if (!modelName) {
        console.error('ModelCardDisplay received empty modelName');
        return (
            <Card className="p-4 mb-4 bg-yellow-50 border border-yellow-300 shadow-sm">
                <div className="text-yellow-700">Model information unavailable</div>
            </Card>
        );
    }

    return (
        <Card className="p-4 mb-4 bg-gray-50 border shadow-sm overflow-hidden">
            <div className="flex items-center gap-3">
                <ModelIcon vendor={vendor}/>
                <div className="flex-1">
                    <h3 className="text-sm font-medium">{modelName}</h3>
                    <div className="flex flex-wrap gap-2 mt-2">
                        {modelParameters && modelParameters.temperature !== undefined && (
                            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                Temperature: {modelParameters.temperature}
                            </Badge>
                        )}
                        {modelParameters && modelParameters.reasoning_effort !== undefined && (
                            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                Reasoning: {modelParameters.reasoning_effort}
                            </Badge>
                        )}
                        {modelParameters && modelParameters.extended_thinking !== undefined && (
                            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                Reasoning: {modelParameters.extended_thinking ? 'Enabled' : 'Disabled'}
                                {modelParameters.budget_tokens !== undefined && ` (${modelParameters.budget_tokens} tokens)`}
                            </Badge>
                        )}
                        {modelParameters && modelParameters.max_tokens !== undefined && (
                            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                Max Tokens: {modelParameters.max_tokens}
                            </Badge>
                        )}
                    </div>

                    {/* Tools section */}
                    {toolNames && toolNames.length > 0 && (
                        <div className="mt-3 border-t pt-2 border-gray-200">
                            <div className="text-xs font-medium text-gray-500 mb-1.5">Available Tools:</div>
                            <div className="flex flex-wrap gap-1.5">
                                {toolNames.map((tool, idx) => (
                                    <Badge
                                        key={`tool-${idx}`}
                                        variant="outline"
                                        className="bg-green-50 text-green-700 border-green-200"
                                    >
                                        {tool}
                                    </Badge>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </Card>
    );
};

export default ModelCardDisplay;