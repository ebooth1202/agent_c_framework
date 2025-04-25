import React from 'react';
import { Cpu } from 'lucide-react';
import PropTypes from 'prop-types';

/**
 * TokenUsageDisplay - A component that displays token usage statistics for AI responses
 * Shows prompt tokens, completion tokens, and total tokens used in the interaction
 *
 * @param {Object} props - Component props
 * @param {Object} props.usage - Token usage statistics object
 * @param {number} [props.usage.prompt_tokens=0] - Number of tokens used in the prompt
 * @param {number} [props.usage.completion_tokens=0] - Number of tokens used in the completion
 * @param {number} [props.usage.total_tokens] - Total tokens used (calculated if not provided)
 */
const TokenUsageDisplay = ({ usage }) => {
    // Don't render if no usage data is available
    if (!usage || (!usage.prompt_tokens && !usage.completion_tokens)) return null;

    const {
        prompt_tokens = 0,
        completion_tokens = 0,
        total_tokens = prompt_tokens + completion_tokens
    } = usage;

    return (
        <div 
            className="token-usage-container"
            aria-label="Token usage statistics"
            role="region"
        >
            <Cpu className="token-usage-icon" aria-hidden="true" />
            <div className="token-usage-stats">
                <span 
                    className="token-usage-stat"
                    aria-label={`Prompt tokens: ${prompt_tokens.toLocaleString()}`}
                >
                    <span id="prompt-token-label">Prompt:</span>{' '}
                    <span aria-labelledby="prompt-token-label">{prompt_tokens.toLocaleString()}</span>
                </span>
                
                <span className="token-usage-divider" aria-hidden="true">·</span>
                
                <span 
                    className="token-usage-stat"
                    aria-label={`Completion tokens: ${completion_tokens.toLocaleString()}`}
                >
                    <span id="completion-token-label">Completion:</span>{' '}
                    <span aria-labelledby="completion-token-label">{completion_tokens.toLocaleString()}</span>
                </span>
                
                <span className="token-usage-divider" aria-hidden="true">·</span>
                
                <span 
                    className="token-usage-stat"
                    aria-label={`Total tokens: ${total_tokens.toLocaleString()}`}
                >
                    <span id="total-token-label">Total:</span>{' '}
                    <span aria-labelledby="total-token-label">{total_tokens.toLocaleString()}</span>
                </span>
            </div>
        </div>
    );
};

TokenUsageDisplay.propTypes = {
    usage: PropTypes.shape({
        prompt_tokens: PropTypes.number,
        completion_tokens: PropTypes.number,
        total_tokens: PropTypes.number
    })
};

export default TokenUsageDisplay;