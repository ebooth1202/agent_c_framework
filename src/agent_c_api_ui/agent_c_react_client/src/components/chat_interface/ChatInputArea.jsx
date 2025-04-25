import React from "react";
import PropTypes from "prop-types";
import { Send, Upload, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";

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
 * @param {string} [props.className] - Additional CSS classes
 */
const ChatInputArea = ({
  inputText,
  setInputText,
  isStreaming,
  isUploading,
  handleSendMessage,
  handleKeyPress,
  openFilePicker,
  toggleOptionsPanel,
  fileInputRef,
  handleFileSelection,
  className
}) => {
  const isInputDisabled = isStreaming;
  const isUploadDisabled = isStreaming || isUploading;
  const isSendDisabled = isStreaming || !inputText.trim();
  
  // Determine if send button should be active
  const sendButtonVariant = isSendDisabled ? "secondary" : "accent";
  
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
      />
      
      {/* Text input with action buttons */}
      <div className="chat-input-container">
        <Textarea
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isInputDisabled}
          rows={2}
          className={cn(
            "chat-input-textarea",
            "min-h-[60px] rounded-lg",
            "resize-none"
          )}
          aria-label="Message input"
          data-streaming={isStreaming ? "true" : "false"}
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
                  <Settings className="h-4 w-4" aria-hidden="true" />
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
                  <Upload className="h-4 w-4" aria-hidden="true" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Upload file</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
          
          {/* Send button with tooltip */}
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  onClick={handleSendMessage}
                  disabled={isSendDisabled}
                  size="icon"
                  variant={sendButtonVariant}
                  className="chat-input-send-button"
                  aria-label="Send message"
                >
                  <Send className="h-4 w-4" aria-hidden="true" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Send message</p>
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
  className: PropTypes.string
};

ChatInputArea.defaultProps = {
  isStreaming: false,
  isUploading: false
};

export default ChatInputArea;