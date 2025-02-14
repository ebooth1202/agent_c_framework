// src/components/rag_interface/Search/SearchForm.jsx
import React, { useState, useEffect } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search as SearchIcon } from "lucide-react";
import {RAG_API_URL} from "@/config/config";

const SearchForm = ({ onSearch }) => {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const response = await fetch(`${RAG_API_URL}/rag/weaviate/collections`);
        if (!response.ok) throw new Error('Failed to fetch collections');
        const data = await response.json();
        setCollections(data.collections);
        if (data.collections.length > 0) {
          setSelectedCollection(data.collections[0]);
        }
      } catch (error) {
        console.error('Error fetching collections:', error);
      }
    };

    fetchCollections();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim() || !selectedCollection) return;

    setLoading(true);
    try {
      const response = await fetch(`${RAG_API_URL}/rag/weaviate/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: searchQuery,
          collection_name: selectedCollection,
          result_limit: 10,
          token_limit: 5000
        }),
      });

      if (!response.ok) throw new Error('Search failed');
      const data = await response.json();
      onSearch(data);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="md:col-span-1">
          <Select
            value={selectedCollection}
            onValueChange={setSelectedCollection}
          >
            <SelectTrigger className="rounded-xl border-gray-200 bg-white/50 backdrop-blur-sm transition-colors hover:bg-white/80 focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50">
              <SelectValue placeholder="Select collection" />
            </SelectTrigger>
            <SelectContent className="hover:bg-blue-50/80 focus:bg-blue-50 transition-colors rounded-lg mx-1 my-0.5">
              {collections.map((collection) => (
                <SelectItem key={collection} value={collection} className="bg-white/95 backdrop-blur-sm border shadow-lg rounded-xl">
                  {collection}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="md:col-span-3 flex gap-2">
          <Input
            type="text"
            placeholder="Enter your search query..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 rounded-xl border-gray-200 bg-white/50 backdrop-blur-sm transition-colors
              hover:bg-white/80 focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50
              placeholder-gray-400"
          />
          <Button type="submit" disabled={loading || !searchQuery.trim() || !selectedCollection} className=" rounded-xl bg-blue-500 hover:bg-blue-600 transition-colors">
            {loading ? (
              <span className="flex items-center">Searching...</span>
            ) : (
              <span className="flex items-center">
                <SearchIcon className="h-4 w-4 mr-2" />
                Search
              </span>
            )}
          </Button>
        </div>
      </div>
    </form>
  );
};

export default SearchForm;