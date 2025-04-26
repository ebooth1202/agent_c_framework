import React, {useMemo, useRef} from 'react';
import ReactMarkdown from 'react-markdown';
import {Prism as SyntaxHighlighter} from 'react-syntax-highlighter';
import {oneDark} from 'react-syntax-highlighter/dist/esm/styles/prism';
import CopyButton from './CopyButton';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

const MarkdownMessage = ({content}) => {
    const markdownRef = useRef(null);
    // Memoize the markdown content to prevent unnecessary re-renders
    const memoizedContent = useMemo(() => {
        if (content === undefined || content === null) {
            return '';
        }
        
        // For thought display, we want minimal processing to avoid excessive newlines
        // Check if this component is inside a thought container
        const isThoughtContent = content.includes('Thinking Process') || 
                               (document.querySelector('.thought-container') !== null &&
                               markdownRef?.current?.closest('.thought-container') !== null);
        
        if (isThoughtContent) {
            // Minimal processing for thought content
            return typeof content === 'string' ? content : String(content);
        }
        
        // For regular markdown messages, ensure proper spacing around headers
        // Use minimal newlines to avoid excessive spacing
        let processedContent = content.replace(/\n(#{1,6})\s*([^\n]+)/g, '\n$1 $2\n');

        // Ensure proper list formatting
        processedContent = processedContent.replace(/^\s*[-*]\s/gm, '* ');
        
        // Don't add extra newlines before lists - it causes too much spacing
        // processedContent = processedContent.replace(/(?<![-*]\s.*?)\n[-*]/g, '\n\n*');

        return typeof processedContent === 'string' ? processedContent : String(processedContent);
    }, [content]);

    return (
        <Card ref={markdownRef} className={cn("prose prose-sm max-w-none prose-p:my-1 prose-headings:mt-2 prose-headings:mb-1 prose-ul:my-1 markdown-container", "no-shadow")}>
            <CardContent className="p-0"> {/* Remove default padding to match original design */}
                {/* Main content */}
                <div className="markdown-content">

                <ReactMarkdown
                    components={{
                        h1: ({node, ...props}) => <h1 className="markdown-h1" {...props} />,
                        h2: ({node, ...props}) => <h2 className="markdown-h2" {...props} />,
                        h3: ({node, ...props}) => <h3 className="markdown-h3" {...props} />,
                        h4: ({node, ...props}) => <h4 className="markdown-h4" {...props} />,
                        // Enhanced list rendering - reduced margins
                        ul: ({node, ...props}) => (
                            <ul className="markdown-ul" {...props} />
                        ),
                        li: ({node, ...props}) => (
                            <li className="markdown-li" {...props} />
                        ),
                        // Enhanced bold text rendering
                        strong: ({node, ...props}) => (
                            <strong className="markdown-strong" {...props} />
                        ),
                        // Enhanced code block rendering with copy button
                        code: ({node, inline, className, children, ...props}) => {
                            const match = /language-(\w+)/.exec(className || '');
                            const language = match ? match[1] : '';
                            const codeString = String(children).replace(/\n$/, '');

                            // Enhanced inline detection
                            // If ReactMarkdown says it's inline OR our additional checks suggest it should be inline
                            const shouldBeInline = inline ||
                                (!language && // No language specified
                                    codeString.length < 50 && // Short content
                                    !codeString.includes('\n')); // No newlines

                            return !shouldBeInline ? (
                                // Code block (triple backticks) formatting
                                <div className="markdown-code-block-container">
                                    <div className="markdown-code-block-copy-button">
                                        <CopyButton
                                            content={codeString}
                                            tooltipText="Copy code"
                                            variant="secondary"
                                            className="markdown-code-block-copy-button-style"
                                        />
                                    </div>
                                    <ScrollArea className="w-full max-h-[500px]" type="always" scrollHideDelay={0}>
                                        <SyntaxHighlighter
                                            style={oneDark}
                                            language={language || 'text'}
                                            PreTag="div"
                                            className="!my-0"
                                            showLineNumbers={true}
                                            {...props}
                                        >
                                            {codeString}
                                        </SyntaxHighlighter>
                                    </ScrollArea>
                                </div>
                            ) : (
                                // Inline code (single backticks) formatting
                                <code className="markdown-inline-code" {...props}>
                                    {children}
                                </code>
                            );
                        },
                        // Enhanced blockquote rendering
                        blockquote: ({node, ...props}) => (
                            <blockquote className="markdown-blockquote" {...props} />
                        ),
                        // Enhance paragraph rendering with reduced spacing
                        p: ({node, ...props}) => (
                            <p className="markdown-paragraph" {...props} />
                        ),
                        // Enhanced horizontal rule using Separator
                        hr: ({node, ...props}) => (
                            <Separator className="markdown-hr" {...props} />
                        ),
                    }}
                >
                    {memoizedContent}
                </ReactMarkdown>
                </div>
                {/* Copy button that appears on hover */}
                <div className="markdown-copy-button-container">
                    <CopyButton
                        content={content}
                        tooltipText="Copy markdown"
                        position="left"
                    />
                </div>
            </CardContent>
        </Card>
    );
};

export default MarkdownMessage;