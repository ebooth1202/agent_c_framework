import React, { useState } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

const CreateCollectionDialog = ({ onCreateCollection }) => {
  const [showDialog, setShowDialog] = useState(false);
  const [collectionName, setCollectionName] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    if (!collectionName.trim()) {
      setError('Collection name is required');
      return;
    }

    // Validate collection name (only alphanumeric and underscores)
    if (!/^[a-zA-Z0-9_]+$/.test(collectionName)) {
      setError('Collection name can only contain letters, numbers, and underscores');
      return;
    }

    onCreateCollection(collectionName);
    setCollectionName('');
    setShowDialog(false);
    setError('');
  };

  return (
    <>
      <Button
        onClick={() => setShowDialog(true)}
        className="mb-4 bg-blue-500 hover:bg-blue-600"
      >
        <Plus className="h-4 w-4 mr-2" />
        Create Collection
      </Button>

      <AlertDialog open={showDialog} onOpenChange={setShowDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Create New Collection</AlertDialogTitle>
            <AlertDialogDescription>
              Enter a name for your new collection. This will be used to store and organize your documents.
            </AlertDialogDescription>
          </AlertDialogHeader>

          <div className="py-4">
            <Input
              value={collectionName}
              onChange={(e) => setCollectionName(e.target.value)}
              placeholder="Enter collection name"
              className="mb-2"
            />
            {error && (
              <p className="text-sm text-red-500 mt-1">{error}</p>
            )}
          </div>

          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => {
              setError('');
              setCollectionName('');
            }}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleSubmit}
              className="bg-blue-500 hover:bg-blue-600"
            >
              Create
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default CreateCollectionDialog;