import React from 'react';
import {Link} from 'react-router-dom';
import { ThemeToggle } from './ui/theme-toggle';

const Layout = ({children}) => {
    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
            <header className="container mx-auto px-6 py-4 max-w-7xl flex items-center justify-between">
                <div className="flex items-center">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Agent C Conversational Interface</h1>
                </div>
                <div className="flex items-center gap-4">
                    <ThemeToggle />
                    <nav className="hidden sm:flex">
                        <Link to="/" className="text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100">Home</Link>
                        <Link to="/chat" className="ml-4 text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100">Chat</Link>
                        <Link to="/rag" className="ml-4 text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100">RAG Admin</Link>
                        <Link to="/settings" className="ml-4 text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100">Settings</Link>
                        <Link to="/interactions" className="ml-4 text-gray-700 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100">Sessions</Link>
                    </nav>
                </div>
            </header>
            <main className="container mx-auto px-6 py-4 max-w-7xl text-gray-900 dark:text-gray-100">{children}</main>
            <footer className="container mx-auto px-6 py-4 max-w-7xl text-center text-gray-600 dark:text-gray-400">
                &copy; {new Date().getFullYear()}
            </footer>
        </div>
    );
};

export default Layout;