import React, {useState} from 'react';
import {Monitor, ChevronDown, Maximize2, Info} from 'lucide-react';
import {Dialog, DialogContent} from "@/components/ui/dialog";
import {Card} from "@/components/ui/card";
import CopyButton from './CopyButton';
import MarkdownMessage from "@/components/chat_interface/MarkdownMessage";

const MediaMessage = ({message}) => {
    const [isExpanded, setIsExpanded] = useState(true);
    const [isFullscreen, setIsFullscreen] = useState(false);

    if (!message?.content || !message?.contentType) {
        console.warn('MediaMessage: Invalid message structure', message);
        return null;
    }

    const toggleFullscreen = (e) => {
        e.stopPropagation();
        setIsFullscreen(!isFullscreen);
    };

    // Get content to copy based on media type
    const getCopyContent = () => {
        // For SVG, return the SVG code
        if (message.contentType === 'image/svg+xml') {
            return message.content;
        }
        // For HTML, return the HTML code
        if (message.contentType === "text/html") {
            return message.content;
        }
        if (message.contentType === "text/markdown") {
            return message.content; // Return raw markdown for copying
        }
        // For images, we can't copy the binary data directly,
        // so we'll create a data URL that could be used in an img tag
        if (message.contentType?.startsWith('image/')) {
            return `data:${message.contentType};base64,${message.content}`;
        }
        return message.content;
    };

    const MediaContentWrapper = ({children, allowFullscreen = false}) => (
        <div className="media-message-media-wrapper">
            {allowFullscreen && (
                <button
                    onClick={toggleFullscreen}
                    className="media-message-fullscreen-button"
                >
                    <Maximize2 className="media-message-fullscreen-icon"/>
                </button>
            )}
            {children}
        </div>
    );

    const renderContent = () => {
        if (message.contentType === 'image/svg+xml') {
            return (
                <MediaContentWrapper allowFullscreen>
                    <div
                        className="w-full"
                        dangerouslySetInnerHTML={{__html: message.content}}
                    />
                </MediaContentWrapper>
            );
        }

        if (message.contentType === "text/html") {
            return (
                <MediaContentWrapper>
                    <div className="media-message-html-content" dangerouslySetInnerHTML={{__html: message.content}}/>
                </MediaContentWrapper>
            );
        }
        if (message.contentType === "text/markdown") {
            return (
                <MediaContentWrapper>
                    <div className="markdown-content">
                        <MarkdownMessage content={message.content}/>
                    </div>
                </MediaContentWrapper>
            );
        }

        if (message.contentType?.startsWith('image/')) {
            return (
                <MediaContentWrapper allowFullscreen>
                    <img
                        src={`data:${message.contentType};base64,${message.content}`}
                        alt="Generated Content"
                        className="media-message-image"
                        loading="lazy"
                    />
                </MediaContentWrapper>
            );
        }

        return null;
    };

    const renderMetadata = () => {
        if (!message.metadata) return null;

        const {sent_by_class, sent_by_function} = message.metadata;
        if (!sent_by_class && !sent_by_function) return null;

        return (
            <div className="media-message-metadata">
                <Info className="media-message-metadata-icon"/>
                <span className="media-message-metadata-text">
                    {sent_by_class}
                    {sent_by_class && sent_by_function && <span className="media-message-metadata-separator">{"\u2022"}</span>}
                    {sent_by_function}
                </span>
            </div>
        );
    };

    const FullscreenDialog = () => (
        <Dialog open={isFullscreen} onOpenChange={setIsFullscreen}>
            <DialogContent className="p-0 overflow-hidden max-w-7xl" style={{ backgroundColor: 'var(--media-message-background)' }}>
                <div className="media-message-fullscreen-content">
                    {message.contentType === 'image/svg+xml' ? (
                        <div
                            className="w-full h-full flex items-center justify-center"
                            dangerouslySetInnerHTML={{__html: message.content}}
                        />
                    ) : message.contentType?.startsWith('image/') ? (
                        <img
                            src={`data:${message.contentType};base64,${message.content}`}
                            alt="Generated content"
                            className="media-message-fullscreen-image"
                        />
                    ) : (
                        <div dangerouslySetInnerHTML={{__html: message.content}}/>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );

    const getContentTypeDisplay = () => {
        // Handle both full MIME types and short versions
        if (message.contentType.includes('/')) {
            return message.contentType.split('/')[1].toUpperCase();
        }
        return message.contentType.toUpperCase();
    };

    return (
        <>
            <Card className={`media-message-card ${isExpanded ? 'media-message-card-expanded' : 'media-message-card-collapsed'}`}>
                <div
                    className="media-message-header"
                    onClick={() => setIsExpanded(!isExpanded)}
                >
                    <div className="media-message-header-content">
                        <Monitor className="media-message-header-icon"/>
                        <span className="media-message-header-title">
                            {getContentTypeDisplay()}
                        </span>
                    </div>
                    <div className="media-message-header-actions">
                        {/* Copy button that stops event propagation */}
                        <div onClick={(e) => e.stopPropagation()}>
                            <CopyButton
                                content={getCopyContent}
                                tooltipText={`Copy ${message.contentType.split('/')[1]}`}
                                variant="ghost"
                                className="media-message-copy-button"
                            />
                        </div>
                        <ChevronDown
                            className={`media-message-expand-icon ${isExpanded ? "media-message-expand-icon-expanded" : ""}`}
                        />
                    </div>
                </div>

                {isExpanded && (
                    <div className="media-message-content">
                        <div className="media-message-content-wrapper">
                            {renderContent()}
                        </div>
                        {renderMetadata()}
                    </div>
                )}
            </Card>

            {isFullscreen && <FullscreenDialog/>}
        </>
    );
};

export default MediaMessage;