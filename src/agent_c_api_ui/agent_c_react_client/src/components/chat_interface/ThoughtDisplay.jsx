import React, {useState, useRef, useEffect, useContext} from 'react';
import { SessionContext } from '@/contexts/SessionContext';
import {ChevronDown} from 'lucide-react';
import {Card} from "@/components/ui/card";
import ModelIcon from './ModelIcon';
import CopyButton from './CopyButton';
import MarkdownMessage from "@/components/chat_interface/MarkdownMessage";

const ThoughtDisplay = ({content, vendor}) => {
    const { theme } = useContext(SessionContext);
    // Define scrollbar colors based on theme
    const isDarkMode = theme === 'dark';
    const scrollbarThumb = isDarkMode ? '#78350f' : '#d97706';
    const scrollbarTrack = isDarkMode ? '#2c1a09' : '#fef3c7';
    const [isExpanded, setIsExpanded] = useState(true);
    const [maxHeight, setMaxHeight] = useState("auto");
    const contentRef = useRef(null);
    const markdownRef = useRef(null);

    // Adjust height based on content length and rendered markdown height
    useEffect(() => {
        if (!contentRef.current || !isExpanded) return;

        // Set a minimum height to ensure sections aren't too short
        const minHeight = 100; // Minimum height in pixels

        // Calculate base height from content lines
        const contentLines = (content || "").split("\n").length;
        const lineBasedHeight = Math.min(contentLines * 24, 400); // 24px line height, max 400px

        // Initial height setting
        let newHeight = Math.max(minHeight, lineBasedHeight);
        setMaxHeight(`${newHeight}px`);

        // Create a ResizeObserver to monitor the actual rendered height of the markdown content
        // This helps with sizing when there are multiple thought sections
        const resizeObserver = new ResizeObserver(entries => {
            if (entries[0] && markdownRef.current) {
                // Get rendered content height
                const renderedHeight = markdownRef.current.scrollHeight;
                // Use the larger of calculated or rendered height, up to max
                const adjustedHeight = Math.min(Math.max(renderedHeight + 20, minHeight), 400);
                setMaxHeight(`${adjustedHeight}px`);
            }
        });

        // Start observing after the markdown content is rendered
        if (markdownRef.current) {
            resizeObserver.observe(markdownRef.current);
        }

        // Always scroll to the bottom when content changes
        contentRef.current.scrollTop = contentRef.current.scrollHeight;

        return () => {
            if (markdownRef.current) {
                resizeObserver.disconnect();
            }
        };
    }, [content, isExpanded]);

    // Handle auto-scrolling for ongoing content streaming
    useEffect(() => {
        if (!contentRef.current || !isExpanded) return;

        // Check if user is scrolled near the bottom (within 100px)
        const isNearBottom =
            contentRef.current.scrollHeight - contentRef.current.scrollTop - contentRef.current.clientHeight < 100;

        // Only auto-scroll if user is already near the bottom
        if (isNearBottom) {
            contentRef.current.scrollTop = contentRef.current.scrollHeight;
        }
    }, [content]);

    return (
        <Card className="bg-amber-50 dark:bg-gray-700/70 border-amber-200 dark:border-gray-600 shadow-sm overflow-hidden mb-3 relative max-w-[80%] ml-8">
            <div className="px-4 py-3 flex items-center justify-between cursor-pointer"
                 onClick={() => setIsExpanded(!isExpanded)}>
                <div className="flex items-center gap-2">
                    <ModelIcon vendor={vendor}/>
                    <span className="font-semibold text-amber-800 dark:text-amber-300 text-sm">Thinking Process</span>
                </div>
                <div className="flex items-center gap-2">
                    <div onClick={(e) => e.stopPropagation()}>
                        <CopyButton
                            content={content}
                            tooltipText="Copy thinking process"
                            variant="ghost"
                            className="text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200 hover:bg-amber-100 dark:hover:bg-amber-900/30"
                        />
                    </div>
                    <ChevronDown className={`h-5 w-5 text-amber-600 dark:text-amber-400 transform transition-transform duration-200 ${
                        isExpanded ? "rotate-180" : ""
                    }`}/>
                </div>
            </div>

            {isExpanded && (
                <div className="border-t border-amber-200 dark:border-gray-700 px-4 py-3">
                    <div
                        ref={contentRef}
                        className="text-amber-700 dark:text-amber-200 text-sm whitespace-pre-wrap font-mono overflow-auto transition-all duration-300 ease-in-out"
                        style={{
                            maxHeight: maxHeight,
                            minHeight: "100px", // Ensure minimum height
                            scrollbarWidth: 'thin',
                            scrollbarColor: `${scrollbarThumb} ${scrollbarTrack}`
                        }}
                    >
                        <div ref={markdownRef}>
                            <MarkdownMessage content={content} />
                        </div>
                    </div>
                </div>
            )}
        </Card>
    );
};

export default ThoughtDisplay;