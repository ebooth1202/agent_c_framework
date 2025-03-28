// src/components/replay_interface/SystemPromptDisplay.jsx
import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronRight, ChevronDown } from 'lucide-react';
import MarkdownMessage from '@/components/chat_interface/MarkdownMessage';

const SystemPromptDisplay = ({ content }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [displayContent, setDisplayContent] = useState('');
  const [useMarkdown, setUseMarkdown] = useState(true);

  useEffect(() => {
    if (!content) {
      setDisplayContent('No system prompt content available');
      return;
    }

    // Ensure content is a string
    const contentStr = typeof content === 'string' ? content : String(content);

    // Check if content starts with what looks like an XML/HTML tag
    const startsWithXmlTag = /^\s*<[a-zA-Z_][a-zA-Z0-9_]*>/.test(contentStr);

    if (startsWithXmlTag) {
      // Content looks like it contains XML tags, use pre-formatted display
      setUseMarkdown(false);
      setDisplayContent(contentStr);
    } else {
      // Content looks like normal markdown, use markdown display
      setUseMarkdown(true);
      setDisplayContent(contentStr);
    }

    console.log('Content processed, using markdown:', !startsWithXmlTag);
  }, [content]);

  return (
    <Card className="p-2 mb-4 border-2 border-blue-500">
      <Collapsible
        open={isOpen}
        onOpenChange={setIsOpen}
        className="w-full"
      >
        <div className="flex items-center">
          <CollapsibleTrigger className="flex items-center">
            {isOpen ? (
              <ChevronDown className="h-4 w-4 text-gray-500" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-500" />
            )}
          </CollapsibleTrigger>
          <Badge variant="secondary">System Prompt</Badge>
          <span className="ml-2 text-xs text-gray-500">
            {displayContent.length > 0 ? `(${displayContent.length} chars)` : '(empty)'}
          </span>
        </div>

        <CollapsibleContent className="mt-2">
          <div className="bg-gray-50 p-2 rounded max-h-96 overflow-auto">
            {displayContent ? (
              useMarkdown ? (
                <MarkdownMessage message={displayContent} />
              ) : (
                <div>
                  <div className="mb-2 text-sm text-gray-500">System prompt content:</div>
                  <pre className="whitespace-pre-wrap text-sm font-mono bg-gray-100 p-3 rounded">{displayContent}</pre>
                </div>
              )
            ) : (
              <div className="text-red-500">No content available</div>
            )}
          </div>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};

export default SystemPromptDisplay;