import React, { useEffect, useState } from 'react';

const AnimatedStatusIndicator = ({ isProcessing, className = '' }) => {
  const [isVisible, setIsVisible] = useState(true);
  
  // Pause animations when tab is not active to save CPU
  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);
  
  // Only show animations if processing AND tab is visible
  const shouldAnimate = isProcessing && isVisible;
  
  return (
    <div className="status-indicator-container">
      <div
        className={`
          status-indicator-dot
          ${className}
          ${isProcessing ? 'status-indicator-dot-processing' : 'status-indicator-dot-idle'}
        `}
      >
        {/* Ripple effect when processing AND visible */}
        {shouldAnimate && (
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