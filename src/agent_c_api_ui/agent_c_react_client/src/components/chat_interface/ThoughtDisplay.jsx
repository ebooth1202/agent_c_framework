import React, { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown, ChevronUp, Brain } from "lucide-react";
import { cn } from "@/lib/utils";
import ModelIcon from './ModelIcon';
import CopyButton from './CopyButton';
import MarkdownMessage from "@/components/chat_interface/MarkdownMessage";

/**
 * ThoughtDisplay component displays AI thinking processes in a collapsible container
 * with improved width and user-controlled expansion.
 *
 * @param {Object} props - Component props
 * @param {string} props.content - The thinking content to display
 * @param {string} props.vendor - The AI model vendor
 * @param {string} [props.className] - Optional additional class names
 * @param {boolean} [props.defaultOpen=false] - Whether the thought is expanded by default
 */
const ThoughtDisplay = ({ content, vendor, className, defaultOpen = false }) => {
    const [isOpen, setIsOpen] = useState(defaultOpen);

    // Create a preview of the content (first line or first 100 characters)
    const getPreview = () => {
        if (!content) return "Thinking...";
        const firstLine = content.split('\n')[0];
        return firstLine.length > 100 ? firstLine.substring(0, 100) + "..." : firstLine;
    };

    return (
        <div className={cn("thought-display-wrapper", className)}>
            <div className="flex items-start gap-2 group mb-3">
                <div className="flex-shrink-0 mt-1">
                    <ModelIcon vendor={vendor} />
                </div>

                <Collapsible
                    open={isOpen}
                    onOpenChange={setIsOpen}
                    className="thought-content-collapsible"
                >
                    <Card className="thought-content-wide">
                        <CollapsibleTrigger asChild>
                            <Button
                                variant="ghost"
                                className="thought-trigger-button"
                                aria-label={isOpen ? "Collapse thinking" : "Expand thinking"}
                            >
                                <div className="flex items-center justify-between w-full">
                                    <div className="flex items-center gap-2">
                                        <Brain className="h-4 w-4 text-muted-foreground" />
                                        <span className="text-sm text-muted-foreground font-medium">
                                            Thinking
                                        </span>
                                        {!isOpen && (
                                            <span className="text-xs text-muted-foreground truncate max-w-md">
                                                {getPreview()}
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <CopyButton
                                            content={content}
                                            tooltipText="Copy thinking"
                                            position="left"
                                            variant="ghost"
                                            size="xs"
                                            className="opacity-0 group-hover:opacity-100 transition-opacity"
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                        {isOpen ? (
                                            <ChevronUp className="h-4 w-4" />
                                        ) : (
                                            <ChevronDown className="h-4 w-4" />
                                        )}
                                    </div>
                                </div>
                            </Button>
                        </CollapsibleTrigger>

                        <CollapsibleContent className="thought-collapsible-content">
                            <CardContent className="thought-expanded-content">
                                <MarkdownMessage content={content} />
                            </CardContent>
                        </CollapsibleContent>
                    </Card>
                </Collapsible>
            </div>
        </div>
    );
};

export default ThoughtDisplay;