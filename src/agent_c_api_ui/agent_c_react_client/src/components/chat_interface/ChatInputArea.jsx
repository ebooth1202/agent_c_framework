import React from "react";
import { Send, Upload, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
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
  return (
    <div className={cn(
      "flex flex-col w-full space-y-2",
      className
    )}>
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelection}
        className="hidden"
      />
      
      {/* Text input with action buttons */}
      <div className="relative flex w-full">
        <Textarea
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isStreaming}
          rows={2}
          className={cn(
            "pr-28 min-h-[60px] rounded-xl backdrop-blur-sm",
            "resize-none transition-colors", 
            "focus-visible:ring-primary focus-visible:ring-opacity-20",
            "border-muted-foreground/20"
          )}
        />
        
        {/* Action buttons container */}
        <div className="absolute right-2 bottom-2 flex items-center space-x-1">
          {/* Settings button */}
          <Button
            onClick={toggleOptionsPanel}
            variant="ghost"
            size="icon"
            className="h-8 w-8 rounded-full text-muted-foreground hover:text-primary hover:bg-primary/10"
          >
            <Settings className="h-4 w-4" />
          </Button>
          
          {/* File upload button */}
          <Button
            onClick={openFilePicker}
            variant="ghost"
            size="icon"
            disabled={isStreaming || isUploading}
            className="h-8 w-8 rounded-full text-muted-foreground hover:text-primary hover:bg-primary/10"
          >
            <Upload className="h-4 w-4" />
          </Button>
          
          {/* Send button */}
          <Button
            onClick={handleSendMessage}
            disabled={isStreaming}
            size="icon"
            className="h-8 w-8 rounded-full bg-primary hover:bg-primary/90"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInputArea;