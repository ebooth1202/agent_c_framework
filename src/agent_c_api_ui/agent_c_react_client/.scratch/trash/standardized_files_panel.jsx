import React from 'react';
import FileItem from './FileItem';
import { cn } from "../../lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { ScrollArea } from "../ui/scroll-area";

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
    <Card 
      className={cn(
        "w-full mt-2 mb-2 bg-background/80 shadow-sm border-border",
        className
      )}
    >
      <CardHeader className="p-3 pb-2 space-y-0">
        <CardTitle className="text-xs font-medium text-muted-foreground">
          Uploaded Files
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-0 px-3 pb-3">
        <ScrollArea className="max-h-24 space-y-1">
          <div className="flex flex-col gap-1">
            {uploadedFiles.map((file) => (
              <FileItem 
                key={file.id} 
                file={file} 
                toggleFileSelection={toggleFileSelection}
              />
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default FilesPanel;