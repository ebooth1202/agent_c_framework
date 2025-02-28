import React, {useState, useEffect} from 'react';
import {Label} from '@/components/ui/label';
import {Slider} from '@/components/ui/slider';
import {Switch} from '@/components/ui/switch';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';

/**
 * ModelParameterControls provides an interface for adjusting AI model parameters
 * including temperature and reasoning effort controls.
 *
 * @component
 * @param {Object} props
 * @param {Object} props.selectedModel - Selected model configuration
 * @param {Object} props.selectedModel.parameters - Model parameter configurations
 * @param {Function} props.onParameterChange - Callback for parameter changes
 * @param {Object} [props.currentParameters={}] - Current parameter values
 */
const ModelParameterControls = ({
                                    selectedModel,
                                    onParameterChange,
                                    currentParameters = {},
                                }) => {
    // For temperature settings - Used by non-reasoning models
    const [temperature, setTemperature] = useState(currentParameters?.temperature);
    const [localTemperature, setLocalTemperature] = useState(currentParameters?.temperature);

    // For reasoning effort settings - OpenAI
    const [reasoningEffort, setReasoningEffort] = useState(currentParameters?.reasoning_effort);


    // Extended thinking states for Anthropic
    const [extendedThinkingEnabled, setExtendedThinkingEnabled] = useState(
        currentParameters?.extended_thinking === true ||
        (selectedModel?.parameters?.extended_thinking?.enabled === true &&
            currentParameters?.extended_thinking !== false)
    );
    const [budgetTokens, setBudgetTokens] = useState(
        (currentParameters?.extended_thinking && currentParameters?.budget_tokens) ||
        (selectedModel?.parameters?.extended_thinking?.enabled === true ?
            selectedModel?.parameters?.extended_thinking?.budget_tokens?.default : 0) || 0
    );

    /**
     * Handles real-time temperature slider changes
     * @param {number[]} value - Array containing single temperature value
     */
    const handleTemperatureChange = (value) => {
        // console.log('Temperature Change:', value);
        const temp = value[0];
        setLocalTemperature(temp);
    };

    /**
     * Commits temperature changes to the backend
     * @param {number[]} value - Array containing single temperature value
     */
    const handleTemperatureCommit = (value) => {
        // console.log('Temperature Commit:', value);
        const temp = value[0];
        setTemperature(temp);  // Update the main temperature state
        onParameterChange('temperature', temp);
    };

    /**
     * Handles toggling the extended thinking feature
     * @param {boolean} enabled - Whether extended thinking is enabled
     */
    const handleExtendedThinkingChange = (enabled) => {
        // Update the UI state first
        setExtendedThinkingEnabled(enabled);

        // Update the parent with the enabled state
        onParameterChange('extended_thinking', enabled);

        // If disabled, set budget_tokens to 0
        if (!enabled) {
            setBudgetTokens(0);
            onParameterChange('budget_tokens', 0);
        } else {
            // When enabling, set to default value
            const defaultValue = selectedModel?.parameters?.extended_thinking?.budget_tokens?.default || 5000;
            setBudgetTokens(defaultValue);
            onParameterChange('budget_tokens', defaultValue);
        }
    };

    /**
     * Handles changes to the budget tokens slider
     * @param {number[]} value - Array containing single budget tokens value
     */
    const handleBudgetTokensChange = (value) => {
        const tokens = value[0];
        setBudgetTokens(tokens);
    };

    /**
     * Commits budget tokens changes to the backend
     * @param {number[]} value - Array containing single budget tokens value
     */
    const handleBudgetTokensCommit = (value) => {
        const tokens = value[0];
        if (tokens === 0) {
            setExtendedThinkingEnabled(false);
            // Notify parent of both changes
            onParameterChange('extended_thinking', false);
            setBudgetTokens(0);
            onParameterChange('budget_tokens', 0);
        } else {
            // Normal case - just update budget tokens
            setBudgetTokens(tokens);
            onParameterChange('budget_tokens', tokens);
        }
    };

    useEffect(() => {
        // console.log('Current Parameters:', currentParameters);
        // console.log('Selected Model Parameters:', selectedModel?.parameters);
        if (selectedModel?.parameters) {
            // Set temperature based on current or default value
            const defaultTemp = selectedModel.parameters?.temperature?.default;
            console.log('Default Temperature:', defaultTemp);
            setLocalTemperature(currentParameters?.temperature ?? defaultTemp);

            // Set reasoning effort based on current or default value
            const defaultEffort = selectedModel.parameters?.reasoning_effort?.default;
            setReasoningEffort(currentParameters?.reasoning_effort ?? defaultEffort);

            // Set extended thinking parameters based on model config or default
            if (selectedModel.parameters?.extended_thinking) {
                const defaultEnabled = selectedModel.parameters.extended_thinking.enabled === true;
                const currentEnabled = currentParameters?.extended_thinking;
                setExtendedThinkingEnabled(currentEnabled !== undefined ? currentEnabled : defaultEnabled);

                const defaultBudget = selectedModel.parameters.extended_thinking.budget_tokens?.default || 5000;
                const currentBudget = currentParameters?.budget_tokens;
                setBudgetTokens(currentEnabled === false ? 0 : (currentBudget !== undefined ? currentBudget : defaultBudget));
            } else {
                setExtendedThinkingEnabled(false);
                setBudgetTokens(0);
            }
        }
    }, [selectedModel, currentParameters]);

    if (!selectedModel?.parameters) return null;

    /**
     * Temperature slider configuration
     * @type {Object}
     * @property {number} min - Minimum temperature value
     * @property {number} max - Maximum temperature value
     * @property {number} step - Temperature adjustment increment, fixed at 0.1
     * @property {number} default - Default temperature value
     */
    const temperatureConfig = {
        min: selectedModel.parameters?.temperature?.min,
        max: selectedModel.parameters?.temperature?.max,
        step: 0.1,
        default: selectedModel.parameters?.temperature?.default
    };
    // console.log('Temperature Config:', temperatureConfig);
    // console.log('Slider Props:', {
    //     min: temperatureConfig.min,
    //     max: temperatureConfig.max,
    //     step: temperatureConfig.step,
    //     value: localTemperature
    // });

    /**
     * Retrieves reasoning effort options from model configuration
     * @returns {string[]|null} Array of reasoning effort options or null if not configured
     */
    const getReasoningEffortOptions = () => {
        const config = selectedModel.parameters?.reasoning_effort;
        if (!config) return null;
        if (Array.isArray(config.options)) return config.options;
        if (Array.isArray(config)) return config;
        if (typeof config === 'object') {
            return config.values || config.choices || ['low', 'medium', 'high'];
        }
        return ['low', 'medium', 'high'];
    };

    const reasoningEffortOptions = getReasoningEffortOptions();

    /**
     * Handles changes to reasoning effort selection - OpenAI
     * @param {string} value - Selected reasoning effort level
     */
    const handleReasoningEffortChange = (value) => {
        setReasoningEffort(value);
        onParameterChange('reasoning_effort', value);
    };


    /**
     * Budget tokens slider configuration
     * @type {Object}
     * @property {number} min - Minimum budget tokens value
     * @property {number} max - Maximum budget tokens value
     * @property {number} step - Budget tokens adjustment increment
     * @property {number} default - Default budget tokens value
     */
    const budgetTokensConfig = {
        min: selectedModel.parameters?.extended_thinking?.budget_tokens?.min,
        max: selectedModel.parameters?.extended_thinking?.budget_tokens?.max,
        step: 500,
        default: selectedModel.parameters?.extended_thinking?.budget_tokens?.default
    };

    return (
        <div className="space-y-4">
            {selectedModel.parameters?.temperature && (
                <div className="space-y-2">
                    <div className="flex items-center justify-between">
                        <Label className="text-sm font-medium">Temperature</Label>
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-xl text-sm font-medium">
                            {localTemperature.toFixed(1)}
                        </span>
                    </div>
                    <div className="relative pt-1">
                        <div className="flex justify-between text-xs text-muted-foreground mb-2">
                            <span className="text-left">Focused</span>
                            <span className="text-center">Balanced</span>
                            <span className="text-right">Creative</span>
                        </div>
                        <div className="absolute w-full flex justify-between px-[2px] pointer-events-none">
                            <div className="w-[2px] h-2 bg-muted-foreground/20"></div>
                            <div className="w-[2px] h-2 bg-muted-foreground/20"></div>
                            <div className="w-[2px] h-2 bg-muted-foreground/20"></div>
                            <div className="w-[2px] h-2 bg-muted-foreground/20"></div>
                            <div className="w-[2px] h-2 bg-muted-foreground/20"></div>
                        </div>
                        <Slider
                            id="temperature-slider"
                            min={temperatureConfig.min}
                            max={temperatureConfig.max}
                            step={temperatureConfig.step}
                            value={[localTemperature]}
                            onValueChange={handleTemperatureChange}  // Smooth UI updates
                            onValueCommit={handleTemperatureCommit}  // Backend update on finish
                            className="w-full"
                        />
                    </div>
                    <div className="text-xs text-muted-foreground italic">
                        Higher values make output more creative but less predictable
                    </div>
                </div>
            )}

            {selectedModel.parameters?.reasoning_effort && reasoningEffortOptions && (
                <div className="space-y-2">
                    <Label htmlFor="reasoning-effort">Reasoning Effort</Label>
                    <Select
                        value={reasoningEffort}
                        onValueChange={handleReasoningEffortChange}
                    >
                        <SelectTrigger
                            id="reasoning-effort"
                            className="w-full rounded-xl border-gray-200 bg-white/50 backdrop-blur-sm"
                        >
                            <SelectValue placeholder="Select reasoning effort"/>
                        </SelectTrigger>
                        <SelectContent className="bg-white/95 backdrop-blur-sm border shadow-lg rounded-xl">
                            {reasoningEffortOptions.map(option => (
                                <SelectItem
                                    key={option}
                                    value={option}
                                    className="hover:bg-blue-50/80 focus:bg-blue-50 transition-colors rounded-lg mx-1 my-0.5"
                                >
                                    {option.charAt(0).toUpperCase() + option.slice(1)}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>
            )}

            {selectedModel.parameters?.extended_thinking && (
                <div className="space-y-2">
                    <div className="flex items-center justify-between">
                        <Label htmlFor="extended-thinking" className="text-sm font-medium">
                            Extended Thinking
                        </Label>
                        <Switch
                            id="extended-thinking"
                            checked={extendedThinkingEnabled}
                            onCheckedChange={handleExtendedThinkingChange}
                        />
                    </div>
                    <div className="text-xs text-muted-foreground italic">
                        Enable deep reasoning for complex problems
                    </div>

                    {extendedThinkingEnabled && (
                        <div className="mt-3 space-y-2">
                            <div className="flex items-center justify-between">
                                <Label className="text-sm font-medium">Thinking Budget</Label>
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-xl text-sm font-medium">
                                    {budgetTokens.toLocaleString()} tokens
                                </span>
                            </div>
                            <Slider
                                id="budget-tokens-slider"
                                min={budgetTokensConfig.min}
                                max={budgetTokensConfig.max}
                                step={budgetTokensConfig.step}
                                value={[budgetTokens]}
                                onValueChange={handleBudgetTokensChange}
                                onValueCommit={handleBudgetTokensCommit}
                                className="w-full"
                            />
                            <div className="text-xs text-muted-foreground italic">
                                Higher values allow more thorough analysis but may take longer
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ModelParameterControls;