import React, { useCallback, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Send, Upload, Settings, Square, Clipboard } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import {Icon} from "@/components/ui/icon";

/**
 * ChatInputArea component provides a styled input area for the chat interface
 * with support for text input, file uploads, and settings.
 *
 * @component
 * @param {Object} props - Component props
 * @param {string} props.inputText - Current input text value
 * @param {Function} props.setInputText - Function to update input text
 * @param {boolean} props.isStreaming - Whether a response is currently streaming
 * @param {boolean} props.isUploading - Whether a file is currently uploading
 * @param {Function} props.handleSendMessage - Function to handle sending a message
 * @param {Function} props.handleKeyPress - Function to handle key presses
 * @param {Function} props.openFilePicker - Function to open the file picker
 * @param {Function} props.toggleOptionsPanel - Function to toggle the options panel
 * @param {React.RefObject} props.fileInputRef - Ref for the file input element
 * @param {Function} props.handleFileSelection - Function to handle file selection
 * @param {Function} props.handleCancelStream - Function to cancel streaming response
 * @param {Function} props.handleClipboardPaste - Function to handle pasted files from clipboard
 * @param {string} [props.className] - Additional CSS classes
 */
const ChatInputArea = ({
  inputText,
  setInputText,
  isStreaming = false,
  isUploading = false,
  handleSendMessage,
  handleKeyPress,
  openFilePicker,
  toggleOptionsPanel,
  fileInputRef,
  handleFileSelection,
  handleCancelStream,
  handleClipboardPaste,
  className
}) => {
  const isInputDisabled = isStreaming;
  const isUploadDisabled = isStreaming || isUploading;
  const isSendDisabled = isStreaming || !inputText.trim();
  
  // Determine if send button should be active
  const sendButtonVariant = isSendDisabled ? "secondary" : "accent";
  
  // State for paste animation
  const [pasteAnimating, setPasteAnimating] = useState(false);
  
  // Reset paste animation after it plays
  useEffect(() => {
    if (pasteAnimating) {
      const timer = setTimeout(() => {
        setPasteAnimating(false);
      }, 1000); // Match animation duration
      return () => clearTimeout(timer);
    }
  }, [pasteAnimating]);
  
  // Handle paste events to capture files
  const handlePaste = useCallback((e) => {
    // Check if we should handle this paste event
    if (isInputDisabled || isUploading) return;
    
    // Get clipboard items
    const items = e.clipboardData?.items;
    if (!items) return;
    
    // Check if there are files in the clipboard
    const files = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      // Look for images or files
      if (item.kind === 'file') {
        const file = item.getAsFile();
        if (file) {
          // If it's an image without a name, give it a name
          if (file.type.startsWith('image/') && (!file.name || file.name === 'image.png')) {
            const fileExtension = file.type.split('/')[1] || 'png';
            const newFile = new File([file], `pasted-image-${new Date().getTime()}.${fileExtension}`, {
              type: file.type
            });
            files.push(newFile);
          } else {
            files.push(file);
          }
        }
      }
    }
    
    // If we found files, handle them
    if (files.length > 0) {
      // Stop propagation to prevent the text from also being pasted if it's an image
      if (files.some(file => file.type.startsWith('image/'))) {
        e.stopPropagation();
        e.preventDefault();
      }
      
      // Activate the paste animation
      setPasteAnimating(true);
      
      // Send files to handler
      handleClipboardPaste(files);
      return;
    }
  }, [isInputDisabled, isUploading, handleClipboardPaste]);
  
  return (
    <div 
      className={cn(
        "chat-input-area",
        "flex flex-col w-full space-y-2",
        className
      )}
      role="region"
      aria-label="Message input area"
    >
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelection}
        className="hidden"
        aria-hidden="true"
        tabIndex="-1"
        accept="*/*" // Accept all file types
      />
      
      {/* Text input with action buttons */}
      <div className={cn(
        "chat-input-container", 
        pasteAnimating && "paste-in-progress"
      )}>
        <Textarea
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyPress}
          onPaste={handlePaste}
          disabled={isInputDisabled}
          rows={2}
          className={cn(
            "chat-input-textarea",
            "min-h-[60px] rounded-lg",
            "resize-none"
          )}
          aria-label="Message input"
          data-paste-enabled="true"
          // Removed data-streaming attribute to prevent scrolling issues
        />
        
        {/* Action buttons container */}
        <div className="chat-input-actions">
          {/* Settings button with tooltip */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={toggleOptionsPanel}
                  variant="ghost"
                  size="icon"
                  className="chat-input-settings-button"
                  aria-label="Message options"
                >
                  <Icon icon="fa-thin fa-sliders" hoverIcon="fa-solid fa-sliders" size="md" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Message options</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          {/* File upload button with tooltip */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={openFilePicker}
                  variant="ghost"
                  size="icon"
                  disabled={isUploadDisabled}
                  className="chat-input-upload-button"
                  aria-label="Upload file"
                >
                  <Icon icon="fa-thin fa-file-arrow-up" hoverIcon="fa-solid fa-file-arrow-up" size="md" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Upload file (or paste from clipboard)</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          {/* Send/Stop button with tooltip */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                {isStreaming ? (
                  <Button
                    onClick={handleCancelStream}
                    size="icon"
                    variant="destructive"
                    className="chat-input-stop-button"
                    aria-label="Stop response"
                  >
                    <Square className="h-4 w-4" aria-hidden="true" />
                  </Button>
                ) : (
                  <Button
                    onClick={handleSendMessage}
                    disabled={isSendDisabled}
                    size="icon"
                    variant={sendButtonVariant}
                    className="chat-input-send-button"
                    aria-label="Send message"
                  >
                    <Icon icon="fa-thin fa-message-arrow-up-right" hoverIcon="fa-solid fa-message-arrow-up-right" size="lg" />
                  </Button>
                )}
              </TooltipTrigger>
              <TooltipContent>
                <p>{isStreaming ? "Stop response" : "Send message"}</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </div>
    </div>
  );
};

ChatInputArea.propTypes = {
  inputText: PropTypes.string.isRequired,
  setInputText: PropTypes.func.isRequired,
  isStreaming: PropTypes.bool,
  isUploading: PropTypes.bool,
  handleSendMessage: PropTypes.func.isRequired,
  handleKeyPress: PropTypes.func.isRequired,
  openFilePicker: PropTypes.func.isRequired,
  toggleOptionsPanel: PropTypes.func.isRequired,
  fileInputRef: PropTypes.oneOfType([PropTypes.func, PropTypes.shape({ current: PropTypes.any })]).isRequired,
  handleFileSelection: PropTypes.func.isRequired,
  handleCancelStream: PropTypes.func.isRequired,
  handleClipboardPaste: PropTypes.func.isRequired,
  className: PropTypes.string
};

// Default props are now handled via parameter destructuring with default values

export default React.memo(ChatInputArea);