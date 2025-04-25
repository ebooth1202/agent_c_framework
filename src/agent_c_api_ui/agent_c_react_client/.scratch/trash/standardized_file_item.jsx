import React from 'react';
import { cn } from "../../lib/utils";
import { Badge } from "../ui/badge";
import { Checkbox } from "../ui/checkbox";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";

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
  // Status-specific text and styling
  const statusConfig = {
    pending: {
      text: "Processing...",
      variant: "secondary",
      textColor: "text-muted-foreground"
    },
    complete: {
      text: "Ready",
      variant: "success",
      textColor: "text-primary-foreground"
    },
    failed: {
      text: "Error",
      variant: "destructive",
      textColor: "text-destructive-foreground"
    }
  };
  
  // Get the current status configuration
  const currentStatus = statusConfig[file.processing_status] || statusConfig.pending;
  
  return (
    <div 
      className={cn(
        "flex items-center p-2 border-b border-border transition-colors",
        "hover:bg-muted/50",
        file.processing_status === 'pending' && "text-muted-foreground",
        file.processing_status === 'complete' && "text-foreground",
        file.processing_status === 'failed' && "text-destructive",
        className
      )}
    >
      <span className="flex-1 truncate text-sm ml-2 max-w-[70%]">
        {file.name}
      </span>
      
      <div className="flex items-center gap-2">
        {/* Status badges with appropriate styling */}
        {file.processing_status === 'pending' && (
          <Badge variant={currentStatus.variant} className="text-xs font-medium whitespace-nowrap">
            {currentStatus.text}
          </Badge>
        )}
        
        {file.processing_status === 'failed' && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge variant={currentStatus.variant} className="text-xs font-medium whitespace-nowrap">
                {currentStatus.text}
              </Badge>
            </TooltipTrigger>
            <TooltipContent>
              {file.processing_error || "Error processing file"}
            </TooltipContent>
          </Tooltip>
        )}
        
        {file.processing_status === 'complete' && (
          <Badge variant={currentStatus.variant} className="text-xs font-medium whitespace-nowrap">
            {currentStatus.text}
          </Badge>
        )}
        
        {/* Selection checkbox */}
        <Checkbox
          checked={file.selected}
          onCheckedChange={() => toggleFileSelection(file.id)}
          className="h-4 w-4 rounded border border-input transition-colors hover:border-primary"
          id={`file-${file.id}`}
        />
      </div>
    </div>
  );
};

export default FileItem;