import React, {useRef, useEffect, useContext} from 'react';
import {SessionContext} from '@/contexts/SessionContext';
import {Brain} from 'lucide-react';
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import ModelIcon from './ModelIcon';
import CopyButton from './CopyButton';
import MarkdownMessage from "@/components/chat_interface/MarkdownMessage";

/**
 * ThoughtDisplay component displays AI thinking processes in a visually distinct container
 * with auto-scrolling functionality for streaming content.
 * 
 * @param {Object} props - Component props
 * @param {string} props.content - The thinking content to display
 * @param {string} props.vendor - The AI model vendor
 * @param {string} [props.className] - Optional additional class names
 */
const ThoughtDisplay = ({content, vendor, className}) => {
    const {theme} = useContext(SessionContext);
    // Check if dark mode is enabled
    const isDarkMode = theme === 'dark';
    const contentRef = useRef(null);
    const markdownRef = useRef(null);

    // Handle auto-scrolling for ongoing content streaming
    useEffect(() => {
        if (!contentRef.current) return;

        // Check if user is scrolled near the bottom (within 100px)
        const isNearBottom =
            contentRef.current.scrollHeight - contentRef.current.scrollTop - contentRef.current.clientHeight < 100;

        // Only auto-scroll if user is already near the bottom
        if (isNearBottom) {
            contentRef.current.scrollTop = contentRef.current.scrollHeight;
        }
    }, [content]);

    return (
        <div className={cn("flex justify-start items-start gap-2 group mb-3", className)}>
            <div className="flex-shrink-0 mt-1">
                <ModelIcon vendor={vendor} />
            </div>
            
            <Card className="thought-container" variant="transparent">
                {/* Content area with markdown */}
                <CardContent className="flex justify-between items-start gap-4 p-0">
                    <div
                        ref={contentRef}
                        className={`text-sm font-mono thought-display-content`}
                    >
                        <div ref={markdownRef}>
                            <MarkdownMessage content={content} />
                        </div>
                    </div>
                    <CopyButton
                        content={content}
                        tooltipText="Copy thinking"
                        position="left"
                        variant="secondary"
                        size="xs"
                        className="mt-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity text-amber-700 hover:bg-amber-100 dark:text-amber-300 dark:hover:bg-amber-900/30"
                    />
                </CardContent>
            </Card>
        </div>
    );
};

export default ThoughtDisplay;