// src/components/rag_interface/Upload/index.jsx
import React, { useState, useEffect } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Upload, XCircle, CheckCircle, AlertCircle } from "lucide-react";
import { RAG_API_URL } from "@/config/config";

const UploadContainer = () => {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState('');
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadResults, setUploadResults] = useState({});

  useEffect(() => {
    const fetchCollections = async () => {
      try {
        const response = await fetch(`${RAG_API_URL}/rag/weaviate/collections`);
        if (!response.ok) throw new Error('Failed to fetch collections');
        const data = await response.json();
        setCollections(data.collections || []);
        if (data.collections?.length > 0) {
          setSelectedCollection(data.collections[0]);
        }
      } catch (error) {
        console.error('Error fetching collections:', error);
        setError('Failed to load collections');
      }
    };

    fetchCollections();
  }, []);

  const handleFileChange = (event) => {
    const newFiles = Array.from(event.target.files);
    setFiles(prevFiles => [...prevFiles, ...newFiles]);
    // Reset the input value so the same file can be selected again
    event.target.value = '';
  };

  const removeFile = (fileName) => {
    setFiles(prevFiles => prevFiles.filter(file => file.name !== fileName));
    setUploadResults(prev => {
      const newResults = { ...prev };
      delete newResults[fileName];
      return newResults;
    });
  };

  const handleUpload = async () => {
    if (!selectedCollection || files.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      formData.append('collection_name', selectedCollection);
      formData.append('chunk_size', 500);

      const response = await fetch(`${RAG_API_URL}/rag/weaviate/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const results = await response.json();

      // Process results into a map keyed by filename
      const resultsMap = results.reduce((acc, result) => {
        acc[result.filename] = result;
        return acc;
      }, {});

      setUploadResults(resultsMap);

      // If all files were successful, clear the file list after a delay
      const allSuccessful = results.every(r => r.status === 'success');
      if (allSuccessful) {
        setTimeout(() => {
          setFiles([]);
          setUploadResults({});
        }, 3000);
      }
    } catch (error) {
      setError('Failed to upload files: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  const getFileStatus = (file) => {
    const result = uploadResults[file.name];
    if (!result) return 'pending';
    return result.status;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const getFileStatusText = (file) => {
    const result = uploadResults[file.name];
    if (!result) return '';
    if (result.status === 'success') {
      return `Processed ${result.total_segments} segments (${result.failed_segments} failed)`;
    }
    return result.error_detail || result.message;
  };

  return (
    <div className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-4">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select Collection
            </label>
            <Select
              value={selectedCollection}
              onValueChange={setSelectedCollection}
              disabled={uploading}
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Upload Files
            </label>
            <div className="flex gap-2">
              <Input
                type="file"
                onChange={handleFileChange}
                multiple
                disabled={uploading}
                className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-xl file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100
              focus:outline-none focus:ring-2 focus:ring-blue-200 focus:ring-opacity-50
              rounded-xl
              cursor-pointer
              transition-all
              border border-gray-200
              bg-white/50 backdrop-blur-sm"
              />
              <Button
                onClick={handleUpload}
                disabled={!selectedCollection || files.length === 0 || uploading}
                className="rounded-xl border-gray-200 bg-white/50 backdrop-blur-sm hover:bg-white/80 transition-colors"
              >
                {uploading ? (
                  <span className="flex items-center">
                    Processing...
                  </span>
                ) : (
                  <span className="flex items-center">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload
                  </span>
                )}
              </Button>
            </div>
          </div>
        </div>

        {files.length > 0 && (
          <div className="border rounded-lg p-4 space-y-4">
            <h3 className="font-medium">Selected Files</h3>
            {files.map((file) => {
              const status = getFileStatus(file);
              const statusText = getFileStatusText(file);

              return (
                <div key={file.name} className="flex items-center gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium">{file.name}</p>
                      {getStatusIcon(status)}
                    </div>
                    {statusText && (
                      <p className="text-sm text-gray-500 mt-1">
                        {statusText}
                      </p>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeFile(file.name)}
                    disabled={uploading}
                  >
                    <XCircle className="h-5 w-5 text-gray-500" />
                  </Button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadContainer;