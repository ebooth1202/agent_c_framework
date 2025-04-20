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
        <div className="relative">
            {allowFullscreen && (
                <button
                    onClick={toggleFullscreen}
                    className="absolute top-2 right-2 p-1 rounded-lg bg-background/80 hover:bg-background shadow-sm transition-colors"
                >
                    <Maximize2 className="h-4 w-4 text-blue-600 dark:text-blue-400"/>
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
                    <div dangerouslySetInnerHTML={{__html: message.content}}/>
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
                        className="w-full h-auto rounded shadow-lg object-contain"
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
            <div className="mt-4 pt-3 border-t border-amber-100 dark:border-amber-900/30 flex items-center gap-2 text-xs text-amber-600 dark:text-amber-400">
                <Info className="h-4 w-4 shrink-0"/>
                <span className="font-medium">
                    {sent_by_class}
                    {sent_by_class && sent_by_function && <span className="mx-2">•</span>}
                    {sent_by_function}
                </span>
            </div>
        );
    };

    const FullscreenDialog = () => (
        <Dialog open={isFullscreen} onOpenChange={setIsFullscreen}>
            <DialogContent className="p-0 overflow-hidden max-w-7xl">
                <div className="w-full h-full flex items-center justify-center bg-card p-4 dark:bg-gray-900">
                    {message.contentType === 'image/svg+xml' ? (
                        <div
                            className="w-full h-full flex items-center justify-center"
                            dangerouslySetInnerHTML={{__html: message.content}}
                        />
                    ) : message.contentType?.startsWith('image/') ? (
                        <img
                            src={`data:${message.contentType};base64,${message.content}`}
                            alt="Generated content"
                            className="max-w-full max-h-[80vh] object-contain rounded shadow-lg"
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
            <Card className={`bg-card shadow-sm overflow-hidden ml-8 ${isExpanded ? 'max-w-[80%]' : 'w-fit'}`}>
                <div
                    className="flex items-center justify-between px-4 py-3 cursor-pointer bg-amber-50/80 dark:bg-amber-900/20 hover:bg-amber-100/90 dark:hover:bg-amber-900/30 transition-colors"
                    onClick={() => setIsExpanded(!isExpanded)}
                >
                    <div className="flex items-center gap-2">
                        <Monitor className="h-5 w-5 text-amber-600 dark:text-amber-400"/>
                        <span className="font-semibold text-amber-800 dark:text-amber-300">
                            {getContentTypeDisplay()}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {/* Copy button that stops event propagation */}
                        <div onClick={(e) => e.stopPropagation()}>
                            <CopyButton
                                content={getCopyContent}
                                tooltipText={`Copy ${message.contentType.split('/')[1]}`}
                                variant="ghost"
                                className="text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-300 hover:bg-amber-100/90 dark:hover:bg-amber-900/30"
                            />
                        </div>
                        <ChevronDown
                            className={`h-5 w-5 text-amber-600 dark:text-amber-400 transform transition-transform duration-200 ${
                                isExpanded ? "rotate-180" : ""
                            }`}
                        />
                    </div>
                </div>

                {isExpanded && (
                    <div className="border-t border-amber-100 dark:border-amber-900/30 p-4 bg-card">
                        <div className="max-h-96 overflow-auto">
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