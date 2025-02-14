import React, { useState, useEffect } from 'react';
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
import { Trash2, Database } from "lucide-react";
import { RAG_API_URL } from "@/config/config";

const CollectionItem = ({ name, onDelete }) => {
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${RAG_API_URL}/rag/weaviate/collections/${name}/stats`);
        if (!response.ok) throw new Error('Failed to fetch stats');
        const data = await response.json();
        setStats(data);
        setError(null);
      } catch (err) {
        setError('Failed to load statistics');
        console.error('Error fetching stats:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [name]);

  return (
    <div className="flex items-center justify-between p-4 border rounded-lg bg-white hover:bg-gray-50">
      <div className="flex-1">
        <div className="flex items-center space-x-2">
          <Database className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-medium text-gray-900">{name}</h3>
        </div>

        <div className="mt-2 text-sm text-gray-500">
          {loading ? (
            <p>Loading statistics...</p>
          ) : error ? (
            <p className="text-red-500">{error}</p>
          ) : (
            <p>
              Total segments: {stats?.segment_count || 0}
            </p>
          )}
        </div>
      </div>

      <div className="ml-4">
        <button
          onClick={() => setShowDeleteDialog(true)}
          className="p-2 text-gray-400 hover:text-red-500 rounded-full hover:bg-gray-100"
        >
          <Trash2 className="h-5 w-5" />
        </button>
      </div>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Collection</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the collection "{name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-500 hover:bg-red-600"
              onClick={() => {
                onDelete(name);
                setShowDeleteDialog(false);
              }}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default CollectionItem;