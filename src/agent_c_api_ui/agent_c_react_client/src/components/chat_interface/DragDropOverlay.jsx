import React from 'react';
import { Upload } from 'lucide-react';
import { cn } from "@/lib/utils";

/**
 * DragDropOverlay component displays a styled overlay when a user is dragging files
 * over the chat interface.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {boolean} props.isDraggingOver - Whether a file is being dragged over the component
 * @param {string} [props.className] - Additional CSS classes
 */
const DragDropOverlay = ({ isDraggingOver, className }) => {
  if (!isDraggingOver) {
    return null;
  }
  
  return (
    <div className={cn(
      'drag-drop-overlay',
      className
    )}>
      <div className="drag-drop-overlay-content">
        <Upload className="drag-drop-overlay-icon" />
        <h3 className="drag-drop-overlay-heading">Drop your file here</h3>
        <p className="drag-drop-overlay-description">Files will be uploaded and processed automatically</p>
      </div>
    </div>
  );
};

export default DragDropOverlay;