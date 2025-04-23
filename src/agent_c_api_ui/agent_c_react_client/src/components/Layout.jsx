import React from 'react';
import {Link} from 'react-router-dom';
import { ThemeToggle } from './ui/theme-toggle';
// CSS already imported through main.css

const Layout = ({children}) => {
    return (
        <div className="layout-container">
            <header className="layout-header">
                <div className="layout-title-container">
                    <h1 className="layout-title">Agent C Conversational Interface</h1>
                </div>
                <div className="layout-controls">
                    <ThemeToggle />
                    <nav className="layout-nav">
                        <Link to="/" className="layout-nav-link">Home</Link>
                        <Link to="/chat" className="layout-nav-link layout-nav-link-spacing">Chat</Link>
                        <Link to="/rag" className="layout-nav-link layout-nav-link-spacing">RAG Admin</Link>
                        <Link to="/settings" className="layout-nav-link layout-nav-link-spacing">Settings</Link>
                        <Link to="/interactions" className="layout-nav-link layout-nav-link-spacing">Sessions</Link>
                    </nav>
                </div>
            </header>
            <main className="layout-main">{children}</main>
        </div>
    );
};

export default Layout;