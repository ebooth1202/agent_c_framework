import React from 'react';
import FileItem from './FileItem';
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

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
    <Card className={cn("files-panel", className)}>
      <CardHeader className="files-panel-header p-0 pb-2 space-y-0">
        <CardTitle className="text-xs font-medium text-muted-foreground">
          Uploaded Files
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-0">
        <ScrollArea className="files-panel-list space-y-1 max-h-24">
          {uploadedFiles.map((file) => (
            <FileItem 
              key={file.id} 
              file={file} 
              toggleFileSelection={toggleFileSelection}
            />
          ))}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};

export default FilesPanel;