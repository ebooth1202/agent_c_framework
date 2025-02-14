// src/components/rag_interface/CollectionsManager/CollectionsList.jsx
import React from 'react';
import CollectionItem from './CollectionItem';

const CollectionsList = ({ collections, onDelete }) => {
  if (!collections.length) {
    return (
      <div className="text-center py-8 text-gray-500">
        No collections found. Upload documents to create a new collection.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {collections.map((collection) => (
        <CollectionItem
          key={collection}
          name={collection}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

export default CollectionsList;