# Project File Structure

## Overview

This document provides an overview of the Agent C React UI project's file and directory structure, explaining the purpose and organization of key files and folders.

## Contents
- [Root Directory](#root-directory)
- [Source Code Organization](#source-code-organization)
- [Component Organization](#component-organization)
- [Styles Organization](#styles-organization)
- [Configuration Files](#configuration-files)

## Root Directory

The root directory contains configuration files, build scripts, and the source code folder.

```
/
├── public/            # Static assets and HTML template
├── src/               # Source code
├── .env.example       # Example environment variables
├── components.json    # shadcn/ui components configuration
├── index.html         # Entry HTML file
├── postcss.config.js  # PostCSS configuration
├── tailwind.config.js # Tailwind CSS configuration
├── tsconfig.json      # TypeScript configuration
└── vite.config.js     # Vite build configuration
```

## Source Code Organization

The `src` directory contains all the application source code, organized into logical subdirectories:

```
src/
├── components/        # React components
├── config/            # Application configuration
├── contexts/          # React context providers
├── hooks/             # Custom React hooks
├── lib/               # Utility functions and shared logic
├── pages/             # Page components
├── styles/            # CSS stylesheets
├── App.jsx            # Root application component
├── index.css          # Entry CSS file
├── main.jsx           # Application entry point
└── Routes.jsx         # Application routes definition
```

## Component Organization

Components are organized by feature area and component type:

```
components/
├── chat_interface/    # Chat-related components
│   ├── utils/         # Chat-specific utility components
│   ├── ChatInterface.jsx     # Main chat interface component
│   ├── MessageItem.jsx       # Message display component
│   ├── MessagesList.jsx      # List of messages component
│   └── ...            # Other chat components
├── rag_interface/     # RAG-related components
│   ├── Collections/   # Collection management components
│   ├── Search/        # Search interface components
│   └── Upload/        # Upload interface components
├── replay_interface/  # Replay functionality components
├── ui/                # Generic UI components (shadcn/ui)
│   ├── button.jsx     # Button component
│   ├── card.jsx       # Card component
│   └── ...            # Other UI components
├── AppSidebar.jsx     # Main application sidebar
├── Layout.jsx         # Main layout component
└── PageHeader.jsx     # Page header component
```

## Styles Organization

Styles are organized into common styles and component-specific styles:

```
styles/
├── common/            # Shared styles
│   ├── badges.css     # Badge styles
│   ├── cards.css      # Card styles
│   ├── layout.css     # Layout styles
│   ├── reset.css      # CSS reset
│   ├── variables.css  # CSS variables
│   └── ...            # Other common styles
├── components/        # Component-specific styles
│   ├── chat-interface.css    # Chat interface styles
│   ├── layout.css            # Layout component styles
│   ├── message-item.css      # Message item styles
│   └── ...            # Other component styles
├── component-styles.css      # Imports for component styles
├── globals.css        # Global styles
└── main.css           # Main stylesheet
```

## Configuration Files

### Vite Configuration

`vite.config.js` configures the build process, including plugins and build options:

```javascript
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // ... other configuration
});
```

### Tailwind Configuration

`tailwind.config.js` configures Tailwind CSS, including theme extensions and plugins:

```javascript
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
    './app/**/*.{js,jsx}',
    './src/**/*.{js,jsx}',
  ],
  // ... theme configuration
  plugins: [require("tailwindcss-animate")],
}
```

### shadcn/ui Configuration

`components.json` configures shadcn/ui component settings:

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": false,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

## Related Documentation

- [Project Architecture Overview](./architecture-overview.md)
- [Getting Started Guide](./getting-started.md)
- [Installation & Setup](./installation-setup.md)