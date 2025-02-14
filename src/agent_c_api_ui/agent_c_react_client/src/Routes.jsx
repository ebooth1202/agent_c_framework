// src/Routes.jsx
import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';

// Lazy load pages
const HomePage = lazy(() => import('@/pages/HomePage'));
const ChatPage = lazy(() => import('@/pages/ChatPage'));
const SettingsPage = lazy(() => import('@/pages/SettingsPage'));
const RagPage = lazy(() => import('@/pages/RAGPage'));

const AppRoutes = () => {
  return (
    <Layout>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/home" element={<ChatPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/" element={<HomePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/rag" element={<RagPage />} />
        </Routes>
      </Suspense>
    </Layout>
  );
};

export default AppRoutes;
