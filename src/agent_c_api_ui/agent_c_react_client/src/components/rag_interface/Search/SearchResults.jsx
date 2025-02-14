// src/components/rag_interface/Search/SearchResults.jsx
import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";

const SearchResults = ({ results }) => {
  if (!results) {
    return null;
  }

  if (!results.text) {
    return (
      <div className="text-center py-8 text-gray-500">
        No results found. Try adjusting your search query.
      </div>
    );
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Search Results</h3>
            <span className="text-sm text-gray-500">
              {results.result_count || 0} matches found
            </span>
          </div>
          <ScrollArea className="h-96">
            <div className="space-y-4">
              <div className="prose max-w-none">
                {results.text.split('\n').map((paragraph, index) => (
                  paragraph.trim() && (
                    <p key={index} className="text-gray-700">
                      {paragraph}
                    </p>
                  )
                ))}
              </div>
            </div>
          </ScrollArea>
        </div>
      </CardContent>
    </Card>
  );
};

export default SearchResults;