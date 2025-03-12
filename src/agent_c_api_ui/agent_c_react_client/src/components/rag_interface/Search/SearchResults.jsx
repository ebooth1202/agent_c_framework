// src/components/rag_interface/Search/SearchResults.jsx
import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

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

  // Define badge colors based on search type
  const getBadgeColor = (searchType) => {
    switch (searchType) {
      case 'hybrid':
        return "bg-purple-100 text-purple-800 hover:bg-purple-200";
      case 'bm25':
        return "bg-amber-100 text-amber-800 hover:bg-amber-200";
      case 'similarity':
      default:
        return "bg-blue-100 text-blue-800 hover:bg-blue-200";
    }
  };

  // Get search type from query parameter or default to "similarity"
  const searchType = new URLSearchParams(window.location.search).get('search_type') || 'similarity';

  // Map internal names to display names
  const searchTypeLabels = {
    'similarity': 'Similarity (Near Text)',
    'hybrid': 'Hybrid Search',
    'bm25': 'BM25 (Keyword)'
  };

  return (
    <Card>
      <CardContent className="p-6">
        <div className="space-y-4">
          <div className="flex flex-wrap justify-between items-center gap-2">
            <h3 className="text-lg font-medium">Search Results</h3>
            <div className="flex items-center gap-2">
              <Badge className={getBadgeColor(results.search_type || searchType)}>
                {searchTypeLabels[results.search_type || searchType]}
              </Badge>
              <span className="text-sm text-gray-500">
                {results.segment_count || 0} matches found
              </span>
            </div>
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