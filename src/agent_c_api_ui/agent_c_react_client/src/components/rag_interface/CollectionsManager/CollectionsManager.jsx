import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from "@/components/ui/alert";
import CollectionsList from './components/CollectionsList';
import CreateCollectionDialog from './components/CreateCollectionDialog';
import {RAG_API_URL} from "@/config/config";

const CollectionsManager = () => {
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchCollections = async () => {
    try {
      const response = await fetch(`${RAG_API_URL}/rag/weaviate/collections`);
      if (!response.ok) {
        throw new Error('Failed to fetch collections');
      }
      const data = await response.json();
      setCollections(data.collections);
      setError(null);
    } catch (err) {
      setError('Failed to load collections. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (collectionName) => {
    try {
      const response = await fetch(`${RAG_API_URL}/rag/weaviate/collections/${collectionName}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete collection');
      }

      await fetchCollections(); // Refresh the list
      setError(null);
    } catch (err) {
      setError(`Failed to delete collection: ${err.message}`);
    }
  };

  const handleCreateCollection = async (collectionName) => {
    try {
      const response = await fetch(`${RAG_API_URL}/rag/weaviate/collections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: collectionName,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create collection');
      }

      await fetchCollections(); // Refresh the list
      setError(null);
    } catch (err) {
      setError(`Failed to create collection: ${err.message}`);
    }
  };

  useEffect(() => {
    fetchCollections();
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading collections...</div>;
  }

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <CreateCollectionDialog onCreateCollection={handleCreateCollection} />

      <CollectionsList
        collections={collections}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default CollectionsManager;