import React, { useState, useRef, useCallback } from 'react';
import { API_URL } from "@/config/config";
import { cn } from "@/lib/utils";

// Import our standardized FilesPanel
import FilesPanel from './FilesPanel';

/**
 * FileUploadManager handles all file upload functionality including selection,
 * uploading, tracking processing status, and integration with FilesPanel.
 * 
 * @component
 * @param {Object} props - Component props
 * @param {string} props.sessionId - Current session ID
 * @param {Function} props.onFileUploadStart - Callback when file upload starts
 * @param {Function} props.onFileUploadComplete - Callback when file upload completes
 * @param {Function} props.onFileProcessed - Callback when file processing status changes
 * @param {Function} props.onFileError - Callback when file upload or processing errors
 * @param {Function} props.onSelectedFilesChange - Callback when selected files change
 * @param {React.RefObject} [props.fileInputRef] - Optional ref for file input element
 * @param {string} [props.className] - Additional CSS classes
 */
const FileUploadManager = ({
  sessionId,
  onFileUploadStart,
  onFileUploadComplete,
  onFileProcessed,
  onFileError,
  onSelectedFilesChange,
  fileInputRef: externalFileInputRef,
  className
}) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFileForUpload, setSelectedFileForUpload] = useState(null);
  
  // Use external ref if provided, or create our own
  const internalFileInputRef = useRef(null);
  const fileInputRef = externalFileInputRef || internalFileInputRef;

  /**
   * Toggles selection state of a file and updates selected files list
   * @param {string} fileId - ID of the file to toggle
   */
  const toggleFileSelection = (fileId) => {
    setUploadedFiles(prev => prev.map(file => {
      if (file.id === fileId) {
        const newSelected = !file.selected;
        return {...file, selected: newSelected};
      }
      return file;
    }));

    // Update selected files array based on new selection state
    const updatedFiles = uploadedFiles.map(file => {
      if (file.id === fileId) {
        return {...file, selected: !file.selected};
      }
      return file;
    });
    
    const newSelectedFiles = updatedFiles.filter(file => file.selected);
    setSelectedFiles(newSelectedFiles);
    
    // Notify parent component
    if (onSelectedFilesChange) {
      onSelectedFilesChange(newSelectedFiles);
    }
  };

  /**
   * Handles file selection from file input
   * @param {Event} e - Change event from file input
   */
  const handleFileSelection = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFileForUpload(file);
      
      // Automatically upload the file when selected
      setTimeout(() => {
        handleUploadFile(file);
      }, 0);
    } else {
      setSelectedFileForUpload(null);
    }
  };

  /**
   * Opens the file picker dialog
   */
  const openFilePicker = () => {
    fileInputRef.current?.click();
  };

  /**
   * Handles file upload to the server and tracks processing status
   * @param {File} fileToUpload - Optional file to upload, if not provided uses selectedFileForUpload
   * @returns {Promise<void>}
   * @throws {Error} If the file upload fails
   */
  const handleUploadFile = async (fileToUpload = null) => {
    // Use provided file or the selected file from state
    const fileToProcess = fileToUpload || selectedFileForUpload;
    if (!fileToProcess) return;

    setIsUploading(true);
    if (onFileUploadStart) {
      onFileUploadStart(fileToProcess);
    }

    const formData = new FormData();
    formData.append("ui_session_id", sessionId);
    formData.append("file", fileToProcess);

    try {
      // Upload the file
      const response = await fetch(`${API_URL}/upload_file`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add file to state with initial "pending" status
      const newFile = {
        id: data.id,
        name: data.filename,
        type: data.mime_type,
        size: data.size,
        selected: true,
        processing_status: "pending", // Initial status
        processing_error: null
      };

      setUploadedFiles(prev => [...prev, newFile]);
      
      // Add to selected files
      const newSelectedFiles = [...selectedFiles, newFile];
      setSelectedFiles(newSelectedFiles);
      
      // Notify parent of selection change
      if (onSelectedFilesChange) {
        onSelectedFilesChange(newSelectedFiles);
      }

      if (onFileUploadComplete) {
        onFileUploadComplete(newFile);
      }

      // Reset file input and state
      if (fileInputRef.current) {
        fileInputRef.current.value = null;
      }
      setSelectedFileForUpload(null);

      // Check processing status after upload
      checkFileProcessingStatus(data.id);

    } catch (error) {
      console.error("Error uploading file:", error);
      if (onFileError) {
        onFileError(error.message);
      }
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Checks the processing status of a file
   * @param {string} fileId - The ID of the file to check
   */
  const checkFileProcessingStatus = async (fileId) => {
    // Poll the server every 2 seconds to check processing status
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/files/${sessionId}`);
        if (!response.ok) {
          console.error(`Error fetching file status: ${response.status}`);
          return true; // Stop polling on error
        }

        const data = await response.json();

        // Find the file in the response
        const fileData = data.files.find(f => f.id === fileId);
        if (!fileData) return false;

        // Update state with current processing status
        setUploadedFiles(prev => prev.map(file => {
          if (file.id === fileId) {
            // Create updated file object
            const updatedFile = {
              ...file,
              processing_status: fileData.processing_status,
              processing_error: fileData.processing_error
            };
            
            // If status has changed, notify parent
            if (file.processing_status !== fileData.processing_status && onFileProcessed) {
              onFileProcessed(updatedFile);
            }
            
            return updatedFile;
          }
          return file;
        }));

        // If processing is complete or failed, stop polling
        return fileData.processing_status !== "pending";
      } catch (error) {
        console.error("Error checking file status:", error);
        return true; // Stop polling on error
      }
    };

    // Poll until processing completes or fails (max 30 seconds)
    let attempts = 0;
    const maxAttempts = 15; // 15 attempts * 2 seconds = 30 seconds max

    const pollTimer = setInterval(async () => {
      attempts++;
      const shouldStop = await checkStatus();

      if (shouldStop || attempts >= maxAttempts) {
        clearInterval(pollTimer);

        // If we hit max attempts and status is still pending, mark as failed
        if (attempts >= maxAttempts) {
          setUploadedFiles(prev => prev.map(file => {
            if (file.id === fileId && file.processing_status === "pending") {
              const updatedFile = {
                ...file,
                processing_status: "failed",
                processing_error: "Processing timed out"
              };
              
              // Notify parent of processing failure
              if (onFileError) {
                onFileError("Processing timed out", updatedFile);
              }
              
              return updatedFile;
            }
            return file;
          }));
        }
      }
    }, 2000);
  };

  /**
   * Clears all uploaded files state
   */
  const clearUploadedFiles = () => {
    setUploadedFiles([]);
    setSelectedFiles([]);
    if (onSelectedFilesChange) {
      onSelectedFilesChange([]);
    }
  };

  return (
    <div className={cn("flex flex-col w-full", className)}>
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelection}
        className="hidden"
      />
      
      {/* Files panel showing uploaded files */}
      <FilesPanel 
        uploadedFiles={uploadedFiles} 
        toggleFileSelection={toggleFileSelection} 
      />
      
      {/* Expose component API */}
      {React.Children.only(React.createElement('div', {
        className: "hidden",
        'data-file-manager-api': JSON.stringify({
          isUploading,
          fileCount: uploadedFiles.length,
          selectedFileCount: selectedFiles.length,
        }),
      }))}
    </div>
  );
};

// Export methods for external use
FileUploadManager.openFilePicker = (ref) => {
  ref.current?.click();
};

export default FileUploadManager;