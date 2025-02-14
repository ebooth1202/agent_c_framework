import React, {createContext, useState, useEffect, useRef} from 'react';
import {API_URL} from '@/config/config';

export const SessionContext = createContext();

export const SessionProvider = ({children}) => {
    // Global session & UI state
    const [sessionId, setSessionId] = useState(null);
    const debouncedUpdateRef = useRef(null);
    const [error, setError] = useState(null);
    const [settingsVersion, setSettingsVersion] = useState(0);
    const [isOptionsOpen, setIsOptionsOpen] = useState(false);
    const [isStreaming, setIsStreaming] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isInitialized, setIsInitialized] = useState(false);
    const [isReady, setIsReady] = useState(false);

    // Agent settings & configuration
    const [persona, setPersona] = useState("");
    const [temperature, setTemperature] = useState(null);
    const [customPrompt, setCustomPrompt] = useState("");
    const [modelConfigs, setModelConfigs] = useState([]);
    const [modelName, setModelName] = useState("");
    const [modelParameters, setModelParameters] = useState({});
    const [selectedModel, setSelectedModel] = useState(null);

    // Data from backend
    const [personas, setPersonas] = useState([]);
    const [availableTools, setAvailableTools] = useState({
        essential_tools: [],
        groups: {},
        categories: []
    });
    const [activeTools, setActiveTools] = useState([]);

    // --- Business Logic Functions ---

    // Fetch initial data (personas, tools, models)
    const fetchInitialData = async () => {
        try {
            setIsLoading(true);
            setIsInitialized(false);

            // Parallel fetching
            const [personasResponse, toolsResponse, modelsResponse] = await Promise.all([
                fetch(`${API_URL}/personas`),
                fetch(`${API_URL}/tools`),
                fetch(`${API_URL}/models`)
            ]);

            if (!personasResponse.ok || !toolsResponse.ok || !modelsResponse.ok) {
                throw new Error('Failed to fetch initial data');
            }

            const [personasData, toolsData, modelsData] = await Promise.all([
                personasResponse.json(),
                toolsResponse.json(),
                modelsResponse.json()
            ]);

            setPersonas(personasData);
            setAvailableTools(toolsData);
            setModelConfigs(modelsData.models);

            if (modelsData.models.length > 0) {
                const initialModel = modelsData.models[0];
                setModelName(initialModel.id);
                setSelectedModel(initialModel);

                const initialTemperature = initialModel.parameters?.temperature?.default ?? 0.3;
                const initialReasoningEffort = initialModel.parameters?.reasoning_effort?.default;
                const initialParameters = {
                    temperature: initialTemperature,
                    reasoning_effort: initialReasoningEffort
                };

                // const initialParameters = {
                //   temperature: initialModel.parameters?.temperature?.default ?? modelParameters.temperature,
                //   reasoning_effort: initialModel.parameters?.reasoning_effort?.default ?? modelParameters.reasoning_effort
                // };
                setModelParameters(initialParameters);

                // Choose a default persona (or fall back to the first)
                if (personasData.length > 0) {
                    const defaultPersona = personasData.find(p => p.name === 'default');
                    const initialPersona = defaultPersona || personasData[0];
                    setPersona(initialPersona.name);
                    setCustomPrompt(initialPersona.content);
                }

                // Initialize a session with the initial model
                await initializeSession(false, initialModel);
                setIsInitialized(true);
            } else {
                throw new Error('No models available');
            }
        } catch (err) {
            console.error('Error fetching initial data:', err);
            setError(`Failed to load initial data: ${err.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    // Initialize (or reinitialize) a session
    const initializeSession = async (forceNew = false, initialModel = null) => {
        setIsReady(false);
        try {
            const currentModel = initialModel || modelConfigs.find(model => model.id === modelName);
            if (!currentModel) throw new Error('Invalid model configuration');

            const currentTemp = temperature ?? currentModel.parameters?.temperature?.default

            const queryParams = new URLSearchParams({
                temperature: currentTemp.toString(),
                model_name: currentModel.id,
                backend: currentModel.backend,
                persona_name: persona || 'default'
            });

            const response = await fetch(`${API_URL}/initialize?${queryParams}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            if (data.session_id) {
                localStorage.setItem("session_id", data.session_id);
                setSessionId(data.session_id);
                setIsReady(true);
                setError(null);
            } else {
                throw new Error("No session_id in response");
            }
        } catch (err) {
            console.error("Session initialization failed:", err);
            setIsReady(false);
            setError(`Session initialization failed: ${err.message}`);
        }
    };

    // Fetch agent tools for the current session
    const fetchAgentTools = async () => {
        if (!sessionId || !isReady) return;
        try {
            const response = await fetch(`${API_URL}/get_agent_tools/${sessionId}`);
            if (!response.ok) throw new Error('Failed to fetch agent tools');
            const data = await response.json();
            if (data.status === 'success' && Array.isArray(data.initialized_tools)) {
                setActiveTools(data.initialized_tools.map(tool => tool.class_name));
            }
        } catch (err) {
            console.error('Error fetching agent tools:', err);
        }
    };

    // Update agent settings (model change, settings update, parameter update)
    const updateAgentSettings = async (updateType, values) => {
        if (!sessionId || !isReady) return;
        try {
            switch (updateType) {
                case 'MODEL_CHANGE': {
                    setIsReady(false);
                    const newModel = modelConfigs.find(model => model.id === values.modelName);
                    if (!newModel) throw new Error('Invalid model configuration');

                    const newParameters = {
                        temperature: newModel.parameters?.temperature?.default ?? modelParameters.temperature,
                        reasoning_effort: newModel.parameters?.reasoning_effort?.default ?? modelParameters.reasoning_effort
                    };

                    setModelName(values.modelName);
                    setSelectedModel(newModel);
                    setModelParameters(newParameters);
                    await initializeSession(false, newModel);
                    setSettingsVersion(v => v + 1);
                    break;
                }
                case 'SETTINGS_UPDATE': {
                    const formData = new FormData();
                    formData.append('session_id', sessionId);
                    const updatedPersona = values.persona_name || persona;
                    const updatedPrompt = values.customPrompt || customPrompt;
                    setPersona(updatedPersona);
                    setCustomPrompt(updatedPrompt);
                    formData.append('persona_name', updatedPersona);
                    formData.append('custom_prompt', updatedPrompt);

                    const response = await fetch(`${API_URL}/update_settings`, {
                        method: 'POST',
                        body: formData
                    });
                    if (!response.ok) throw new Error('Failed to update settings');
                    setSettingsVersion(v => v + 1);
                    break;
                }
                case 'PARAMETER_UPDATE': {
                    if (debouncedUpdateRef.current) {
                        clearTimeout(debouncedUpdateRef.current);
                    }
                    debouncedUpdateRef.current = setTimeout(async () => {
                        const formData = new FormData();
                        formData.append('session_id', sessionId);
                        const updatedParameters = {...modelParameters};

                        if ('temperature' in values) {
                            updatedParameters.temperature = values.temperature;
                            formData.append('temperature', values.temperature);
                        }
                        if ('reasoning_effort' in values) {
                            updatedParameters.reasoning_effort = values.reasoning_effort;
                            formData.append('reasoning_effort', values.reasoning_effort);
                        }

                        setModelParameters(updatedParameters);
                        await fetch(`${API_URL}/update_settings`, {
                            method: 'POST',
                            body: formData
                        });
                        setSettingsVersion(v => v + 1);
                    }, 300);
                    break;
                }
                default:
                    break;
            }
        } catch (err) {
            setError(`Failed to update settings: ${err.message}`);
        }
    };

    // Handle equipping tools
    const handleEquipTools = async (tools) => {
        const formData = new FormData();
        formData.append('session_id', sessionId);
        formData.append('tools', JSON.stringify(tools));
        try {
            const response = await fetch(`${API_URL}/update_tools`, {
                method: 'POST',
                body: formData
            });
            if (!response.ok) throw new Error("Failed to equip tools");
            await fetchAgentTools();
        } catch (err) {
            console.error("Failed to equip tools:", err);
            throw err;
        }
    };

    // Update processing status (for loading/spinner UI)
    const handleProcessingStatus = (status) => {
        setIsStreaming(status);
    };

    // Handle session deletion
    const handleSessionsDeleted = () => {
        localStorage.removeItem("session_id");
        setSessionId(null);
        setIsReady(false);
        setActiveTools([]);
        setError(null);
    };

    // --- Effects ---
    useEffect(() => {
        fetchInitialData();
    }, []);

    useEffect(() => {
        if (sessionId && isReady) {
            fetchAgentTools();
        }
    }, [sessionId, isReady, modelName]);

    return (
        <SessionContext.Provider
            value={{
                sessionId,
                error,
                settingsVersion,
                isOptionsOpen,
                setIsOptionsOpen,
                isStreaming,
                isLoading,
                isInitialized,
                isReady,
                persona,
                temperature,
                customPrompt,
                modelConfigs,
                modelName,
                modelParameters,
                selectedModel,
                personas,
                availableTools,
                activeTools,
                fetchAgentTools,
                updateAgentSettings,
                handleEquipTools,
                handleProcessingStatus,
                handleSessionsDeleted
            }}
        >
            {children}
        </SessionContext.Provider>
    );
};