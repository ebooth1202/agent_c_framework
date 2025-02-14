import React from 'react';
import { Link } from 'react-router-dom';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <header className="container mx-auto px-6 py-4 max-w-7xl flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Agent C Conversational Interface</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/chat" className="ml-4">Chat</Link>
          <Link to="/rag" className="ml-4">RAG Admin</Link>
          <Link to="/settings" className="ml-4">Settings</Link>
        </nav>
      </header>
      <main className="container mx-auto px-6 py-4 max-w-7xl">{children}</main>
      <footer className="container mx-auto px-6 py-4 max-w-7xl text-center">
        &copy; {new Date().getFullYear()} Agent C
      </footer>
    </div>
  );
};

export default Layout;