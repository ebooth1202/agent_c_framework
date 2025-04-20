import React from 'react';
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";
import { ChevronDown, ChevronUp, Settings, Wrench } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import PersonaSelector from './PersonaSelector';
import ToolSelector from './ToolSelector';

/**
 * A collapsible options panel that provides persona and tool selection functionality.
 *
 * @component
 * @param {Object} props
 * @param {boolean} props.isOpen - Current open/closed state of the panel
 * @param {Function} props.setIsOpen - Callback to update open/closed state
 * @param {string} props.persona - Currently selected persona name
 * @param {string} props.customPrompt - Custom prompt text
 * @param {number} props.temperature - Model temperature setting
 * @param {string} props.modelName - Current model name
 * @param {Object} props.modelConfigs - Available model configurations
 * @param {string} props.sessionId - Current session identifier
 * @param {Array} props.personas - Available personas
 * @param {Array} props.availableTools - List of available tools
 * @param {Function} props.onEquipTools - Callback for tool equipment changes
 * @param {Array} props.activeTools - Currently equipped tools
 * @param {boolean} props.isReady - Component ready state
 * @param {Object} props.modelParameters - Current model parameters
 * @param {string} props.selectedModel - Selected model identifier
 * @param {Function} props.onUpdateSettings - Settings update callback
 * @param {boolean} props.isInitialized - Component initialization state
 *
 * @returns {React.ReactElement} A collapsible options panel component
 */
const CollapsibleOptions = ({
                                isOpen,
                                setIsOpen,
                                persona,
                                customPrompt,
                                temperature,
                                modelName,
                                modelConfigs,
                                sessionId,
                                personas,
                                availableTools,
                                onEquipTools,
                                activeTools,
                                isReady,
                                modelParameters,
                                selectedModel,
                                onUpdateSettings,
                                isInitialized
                            }) => {
    return (
        <Card className="w-full mb-2 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border dark:border-gray-700 shadow-sm">
            <Collapsible open={isOpen} onOpenChange={setIsOpen}>
                <div className="py-2 px-3 flex items-center justify-between">
                    <h2 className="text-base font-medium text-gray-900 dark:text-gray-100">Options Panel</h2>
                    <CollapsibleTrigger asChild>
                        <Button variant="ghost" size="sm" className="w-9 p-0">
                            {isOpen ? <ChevronUp className="h-4 w-4"/> : <ChevronDown className="h-4 w-4"/>}
                        </Button>
                    </CollapsibleTrigger>
                </div>
                <CollapsibleContent className="px-4 pb-4">
                    <Tabs defaultValue="settings" className="w-full">
                        <TabsList className="w-full mb-4 border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800/70 p-1 rounded-md shadow-sm">
                            <TabsTrigger 
                                value="settings" 
                                className="flex items-center gap-1 w-1/2 font-medium data-[state=active]:bg-white dark:data-[state=active]:bg-gray-700 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:shadow"
                            >
                                <Settings className="h-4 w-4" />
                                <span>Settings</span>
                            </TabsTrigger>
                            <TabsTrigger 
                                value="tools" 
                                className="flex items-center gap-1 w-1/2 font-medium data-[state=active]:bg-white dark:data-[state=active]:bg-gray-700 data-[state=active]:border-b-2 data-[state=active]:border-blue-500 data-[state=active]:shadow"
                            >
                                <Wrench className="h-4 w-4" />
                                <span>Tools</span>
                            </TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="settings" className="mt-0">
                            <PersonaSelector
                                persona_name={persona}
                                personas={personas}
                                customPrompt={customPrompt}
                                temperature={temperature}
                                modelName={modelName}
                                modelConfigs={modelConfigs}
                                sessionId={sessionId}
                                modelParameters={modelParameters}
                                selectedModel={selectedModel}
                                onUpdateSettings={onUpdateSettings}
                                isInitialized={isInitialized}
                            />
                        </TabsContent>
                        
                        <TabsContent value="tools" className="mt-0">
                            <ToolSelector
                                availableTools={availableTools}
                                onEquipTools={onEquipTools}
                                activeTools={activeTools}
                                sessionId={sessionId}
                                isReady={isReady}
                            />
                        </TabsContent>
                    </Tabs>
                </CollapsibleContent>
            </Collapsible>
        </Card>
    );
};



export default CollapsibleOptions;