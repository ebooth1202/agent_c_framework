import React from 'react';
import {Link} from 'react-router-dom';
import { ThemeToggle } from './ui/theme-toggle';
import { Button } from './ui/button';
import { Card } from './ui/card';
// CSS already imported through main.css

const Layout = ({children}) => {
    return (
        <div className="layout-container">
            <header className="layout-header">
                <Card className="w-full bg-transparent shadow-none border-0">
                    <div className="flex justify-between items-center p-2">
                        <div className="layout-title-container">
                            <h1 className="layout-title">Agent C Conversational Interface</h1>
                        </div>
                        <div className="layout-controls">
                            <ThemeToggle />
                            <nav className="layout-nav">
                                <Link to="/" className="layout-nav-link">
                                    <Button variant="ghost" className="px-2">Home</Button>
                                </Link>
                                <Link to="/chat" className="layout-nav-link layout-nav-link-spacing">
                                    <Button variant="ghost" className="px-2">Chat</Button>
                                </Link>
                                <Link to="/rag" className="layout-nav-link layout-nav-link-spacing">
                                    <Button variant="ghost" className="px-2">RAG Admin</Button>
                                </Link>
                                <Link to="/settings" className="layout-nav-link layout-nav-link-spacing">
                                    <Button variant="ghost" className="px-2">Settings</Button>
                                </Link>
                                <Link to="/interactions" className="layout-nav-link layout-nav-link-spacing">
                                    <Button variant="ghost" className="px-2">Sessions</Button>
                                </Link>
                            </nav>
                        </div>
                    </div>
                </Card>
            </header>
            <main className="layout-main">{children}</main>
        </div>
    );
};

export default Layout;