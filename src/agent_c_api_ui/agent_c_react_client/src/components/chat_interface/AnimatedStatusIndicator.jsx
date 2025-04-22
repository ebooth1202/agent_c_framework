import React from 'react';

const AnimatedStatusIndicator = ({ isProcessing, className = '' }) => {
  return (
    <div className="status-indicator-container">
      <div
        className={`
          status-indicator-dot
          ${className}
          ${isProcessing ? 'status-indicator-dot-processing' : 'status-indicator-dot-idle'}
        `}
      >
        {/* Ripple effect when processing */}
        {isProcessing && (
          <>
            <div className={`status-indicator-ping ${className}`} />
            <div className={`status-indicator-pulse ${className}`} />
          </>
        )}
      </div>
    </div>
  );
};

export default AnimatedStatusIndicator;