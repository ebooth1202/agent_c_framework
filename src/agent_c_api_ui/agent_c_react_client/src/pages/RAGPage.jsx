// src/pages/RAGPage.jsx
import React, { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import CollectionsManager from '../components/rag_interface/CollectionsManager';
import SearchContainer from '../components/rag_interface/Search/SearchContainer';
import UploadContainer from '../components/rag_interface/Upload/UploadContainer';

const RAGPage = () => {
  const [activeTab, setActiveTab] = useState('collections');

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Knowledge Base Management</h1>
          <p className="mt-2 text-gray-600">
            Manage your document collections, perform semantic searches, and upload new documents.
          </p>
        </div>

        <Card className="mt-6">
          <CardContent className="p-6">
            <Tabs
              defaultValue="collections"
              value={activeTab}
              onValueChange={setActiveTab}
              className="w-full"
            >
              <TabsList className="grid grid-cols-3 w-full mb-8">
                <TabsTrigger value="collections">Collections</TabsTrigger>
                <TabsTrigger value="search">Search</TabsTrigger>
                <TabsTrigger value="upload">Upload</TabsTrigger>
              </TabsList>

              <TabsContent value="collections" className="mt-6">
                <div className="space-y-4">
                  <h2 className="text-xl font-semibold text-gray-900">Document Collections</h2>
                  <p className="text-gray-600">Manage your existing document collections and their contents.</p>
                  <CollectionsManager />
                </div>
              </TabsContent>

              <TabsContent value="search" className="mt-6">
                <div className="space-y-4">
                  <h2 className="text-xl font-semibold text-gray-900">Semantic Search</h2>
                  <p className="text-gray-600">Search through your document collections using natural language.</p>
                 <SearchContainer />
                </div>
              </TabsContent>

              <TabsContent value="upload" className="mt-6">
                <div className="space-y-4">
                  <h2 className="text-xl font-semibold text-gray-900">Document Upload</h2>
                  <p className="text-gray-600">Upload and index new documents into your collections.</p>
                  <UploadContainer />
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default RAGPage;