import React, { useState, useRef } from 'react';
import DragDropOverlay from './DragDropOverlay';
import { cn } from '@/lib/utils';

/**
 * DragDropArea component provides file drag and drop functionality with visual feedback.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render within the drag area
 * @param {Function} props.onFileDrop - Callback when files are dropped
 * @param {boolean} [props.disabled] - Whether drag and drop functionality is disabled
 * @param {string} [props.className] - Additional CSS classes
 */
const DragDropArea = ({ children, onFileDrop, disabled = false, className }) => {
  const [isDraggingOver, setIsDraggingOver] = useState(false);
  const dragCounterRef = useRef(0);

  /**
   * Handles drag enter events
   */
  const handleDragEnter = (e) => {
    if (disabled) return;
    
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current++;
    
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDraggingOver(true);
    }
  };

  /**
   * Handles drag leave events
   */
  const handleDragLeave = (e) => {
    if (disabled) return;
    
    e.preventDefault();
    e.stopPropagation();
    dragCounterRef.current--;
    
    if (dragCounterRef.current === 0) {
      setIsDraggingOver(false);
    }
  };

  /**
   * Handles drag over events
   */
  const handleDragOver = (e) => {
    if (disabled) return;
    
    e.preventDefault();
    e.stopPropagation();
  };

  /**
   * Handles drop events
   */
  const handleDrop = (e) => {
    if (disabled) return;
    
    e.preventDefault();
    e.stopPropagation();
    setIsDraggingOver(false);
    dragCounterRef.current = 0;
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      if (onFileDrop) {
        // Pass all dropped files instead of just the first one
        onFileDrop(e.dataTransfer.files);
      }
    }
  };

  return (
    <div 
      className={cn(
        'relative w-full h-full block',
        disabled && 'opacity-70', // Removed pointer-events-none to allow scrolling while streaming
        className
      )}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Visual overlay when dragging */}
      <DragDropOverlay isDraggingOver={isDraggingOver} />
      
      {/* Pass-through children */}
      {children}
    </div>
  );
};

export default DragDropArea;