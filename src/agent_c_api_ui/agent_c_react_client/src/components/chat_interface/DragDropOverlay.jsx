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
      'absolute inset-0 bg-primary/10 dark:bg-primary/20 backdrop-blur-sm z-50 rounded-xl',
      'flex items-center justify-center border-2 border-primary border-dashed',
      className
    )}>
      <div className="text-center p-6 bg-background/80 dark:bg-gray-800/80 rounded-xl shadow-lg">
        <Upload className="h-10 w-10 text-primary mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-primary-900 dark:text-primary-300">
          Drop your file here
        </h3>
        <p className="text-sm text-muted-foreground mt-1">
          Files will be uploaded and processed automatically
        </p>
      </div>
    </div>
  );
};

export default DragDropOverlay;