import React from 'react';
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

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
  
  // Define badge variants based on processing status
  const badgeVariants = {
    pending: "secondary",
    complete: "success", 
    failed: "destructive"
  };
  
  // Badge text based on processing status
  const badgeText = {
    pending: "Processing...",
    complete: "Ready",
    failed: "Error"
  };
  
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
          <Badge variant={badgeVariants.pending} className="file-item-status-badge">
            {badgeText.pending}
          </Badge>
        )}
        
        {file.processing_status === 'failed' && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge variant={badgeVariants.failed} className="file-item-status-badge">
                {badgeText.failed}
              </Badge>
            </TooltipTrigger>
            <TooltipContent>
              {file.processing_error || "Error processing file"}
            </TooltipContent>
          </Tooltip>
        )}
        
        {file.processing_status === 'complete' && (
          <Badge variant={badgeVariants.complete} className="file-item-status-badge">
            {badgeText.complete}
          </Badge>
        )}
        
        {/* Selection checkbox */}
        <Checkbox
          checked={file.selected}
          onCheckedChange={() => toggleFileSelection(file.id)}
          className="file-item-checkbox"
          id={`file-${file.id}`}
        />
      </div>
    </div>
  );
};

export default FileItem;