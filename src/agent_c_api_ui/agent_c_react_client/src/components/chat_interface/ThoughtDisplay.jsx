import React, {useRef, useEffect, useContext} from 'react';
import {SessionContext} from '@/contexts/SessionContext';
import {Brain} from 'lucide-react';
import ModelIcon from './ModelIcon';
import CopyButton from './CopyButton';
import MarkdownMessage from "@/components/chat_interface/MarkdownMessage";

const ThoughtDisplay = ({content, vendor}) => {
    const {theme} = useContext(SessionContext);
    // Define scrollbar colors based on theme
    const isDarkMode = theme === 'dark';
    const scrollbarThumb = isDarkMode ? '#78350f' : '#d97706';
    const scrollbarTrack = isDarkMode ? '#2c1a09' : '#fef3c7';
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
        <div className="flex justify-start items-start gap-2 group mb-3">
            <div className="flex-shrink-0 mt-1">
                <ModelIcon vendor={vendor} />
            </div>
            
            <div className="relative max-w-[80%] rounded-2xl px-4 py-3 shadow-sm 
                bg-amber-50 dark:bg-gray-700/70 
                text-amber-700/80 dark:text-amber-200/80 
                border border-amber-200 dark:border-amber-800 
                rounded-bl-sm">
                {/* Content area with markdown */}
                <div className="flex justify-between items-start gap-4">
                    <div
                        ref={contentRef}
                        className="text-sm whitespace-pre-wrap font-mono overflow-auto max-h-[200px] min-h-[50px] flex-1"
                        style={{
                            scrollbarWidth: 'thin',
                            scrollbarColor: `${scrollbarThumb} ${scrollbarTrack}`
                        }}
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
                </div>
            </div>
        </div>
    );
};

export default ThoughtDisplay;