// src/components/rag_interface/Search/index.jsx
import React, { useState } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import SearchForm from './SearchForm';
import SearchResults from './SearchResults';

const SearchContainer = () => {
  const [searchResults, setSearchResults] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = (results) => {
    if (results.error) {
      setError(results.error);
      setSearchResults(null);
    } else {
      setSearchResults(results);
      setError(null);
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <SearchForm onSearch={handleSearch} />

      {searchResults && (
        <SearchResults results={searchResults} />
      )}
    </div>
  );
};

export default SearchContainer;