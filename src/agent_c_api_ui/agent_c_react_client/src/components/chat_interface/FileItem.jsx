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
    pending: "file-item-pending",
    complete: "file-item-complete",
    failed: "file-item-failed"
  };
  
  // Get the appropriate status style based on file's processing_status
  const statusStyle = statusStyles[file.processing_status] || statusStyles.pending;
  
  return (
    <div 
      className={cn(
        "file-item",
        statusStyle,
        className
      )}
    >
      <span className="file-item-name truncate max-w-[70%]">
        {file.name}
      </span>
      
      <div className="file-item-actions">
        {/* Status badges */}
        {file.processing_status === 'pending' && (
          <span className="file-item-status-badge file-item-status-badge-pending">
            Processing...
          </span>
        )}
        
        {file.processing_status === 'failed' && (
          <span 
            className="file-item-status-badge file-item-status-badge-failed"
            title={file.processing_error || "Error processing file"}
          >
            Error
          </span>
        )}
        
        {file.processing_status === 'complete' && (
          <span className="file-item-status-badge file-item-status-badge-complete">
            Ready
          </span>
        )}
        
        {/* Selection checkbox */}
        <input
          type="checkbox"
          checked={file.selected}
          onChange={() => toggleFileSelection(file.id)}
          className="file-item-checkbox"
        />
      </div>
    </div>
  );
};

export default FileItem;