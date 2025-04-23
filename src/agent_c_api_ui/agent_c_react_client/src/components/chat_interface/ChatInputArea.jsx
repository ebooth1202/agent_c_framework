import React, { useRef, useState } from "react";
import { Send, Upload, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

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
    <div className={`chat-input-container ${className || ''}`}>
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelection}
        className="hidden"
      />
      
      {/* Text input with action buttons */}
      <div className="chat-input-wrapper relative flex-1">
        <Textarea
          placeholder="Type your message..."
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isStreaming}
          rows={2}
          className="chat-input-textarea"
        />
        
        {/* Settings button */}
        <Button
          onClick={toggleOptionsPanel}
          variant="ghost"
          size="icon"
          className="chat-input-settings-button"
        >
          <Settings className="h-4 w-4" />
        </Button>
        
        {/* File upload button */}
        <Button
          onClick={openFilePicker}
          variant="ghost"
          size="icon"
          disabled={isStreaming || isUploading}
          className="chat-input-upload-button"
        >
          <Upload className="h-4 w-4" />
        </Button>
        
        {/* Send button */}
        <Button
          onClick={handleSendMessage}
          disabled={isStreaming}
          size="icon"
          className="chat-input-send-button"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default ChatInputArea;