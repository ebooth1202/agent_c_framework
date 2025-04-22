import React from 'react';
import { cn } from "@/lib/utils";

/**
 * FileItem component displays an individual file with its status and a checkbox
 * for selection.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {Object} props.file - File information object
 * @param {string} props.file.id - Unique ID of the file
 * @param {string} props.file.name - Name of the file
 * @param {string} props.file.processing_status - Processing status: 'pending', 'complete', 'failed'
 * @param {string} [props.file.processing_error] - Error message if processing failed
 * @param {boolean} props.file.selected - Whether the file is selected
 * @param {Function} props.toggleFileSelection - Function to toggle file selection
 * @param {string} [props.className] - Additional CSS classes
 */
const FileItem = ({ file, toggleFileSelection, className }) => {
  // Define status-specific styles based on processing status
  const statusStyles = {
    pending: "file-item-pending bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
    complete: "file-item-complete bg-success/10 border-success/30",
    failed: "file-item-failed bg-destructive/10 border-destructive/30"
  };
  
  // Get the appropriate status style based on file's processing_status
  const statusStyle = statusStyles[file.processing_status] || statusStyles.pending;
  
  return (
    <div 
      className={cn(
        "file-item flex items-center justify-between p-2 rounded-md border mb-1 transition-colors",
        statusStyle,
        className
      )}
    >
      <span className="file-item-name text-sm truncate max-w-[70%]">
        {file.name}
      </span>
      
      <div className="file-item-actions flex items-center space-x-2">
        {/* Status badges */}
        {file.processing_status === 'pending' && (
          <span className="file-item-status-badge text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/70 text-blue-700 dark:text-blue-300 rounded-full">
            Processing...
          </span>
        )}
        
        {file.processing_status === 'failed' && (
          <span 
            className="file-item-status-badge text-xs px-2 py-0.5 bg-destructive/20 text-destructive rounded-full"
            title={file.processing_error || "Error processing file"}
          >
            Error
          </span>
        )}
        
        {file.processing_status === 'complete' && (
          <span className="file-item-status-badge text-xs px-2 py-0.5 bg-success/20 text-success rounded-full">
            Ready
          </span>
        )}
        
        {/* Selection checkbox */}
        <input
          type="checkbox"
          checked={file.selected}
          onChange={() => toggleFileSelection(file.id)}
          className="file-item-checkbox h-4 w-4 text-primary rounded border-input focus:ring-primary/50"
        />
      </div>
    </div>
  );
};

export default FileItem;