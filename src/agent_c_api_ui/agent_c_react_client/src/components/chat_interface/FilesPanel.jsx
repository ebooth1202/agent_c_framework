import React from 'react';
import FileItem from './FileItem';
import { cn } from "@/lib/utils";

/**
 * FilesPanel component displays a list of uploaded files with their status
 * and allows selection/deselection.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {Array<Object>} props.uploadedFiles - List of uploaded file objects
 * @param {Function} props.toggleFileSelection - Function to toggle file selection
 * @param {string} [props.className] - Additional CSS classes
 */
const FilesPanel = ({ uploadedFiles, toggleFileSelection, className }) => {
  if (!uploadedFiles || uploadedFiles.length === 0) {
    return null;
  }
  
  return (
    <div
      className={cn(
        "files-panel my-2 p-3 bg-background/80 dark:bg-gray-800/80 rounded-lg max-h-32 overflow-y-auto border border-input shadow-sm",
        className
      )}
    >
      <div className="files-panel-header text-xs font-medium text-muted-foreground mb-2">
        Uploaded Files
      </div>
      
      <div className="files-panel-list space-y-1">
        {uploadedFiles.map((file) => (
          <FileItem 
            key={file.id} 
            file={file} 
            toggleFileSelection={toggleFileSelection}
          />
        ))}
      </div>
    </div>
  );
};

export default FilesPanel;