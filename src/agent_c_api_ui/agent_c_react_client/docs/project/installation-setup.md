# Installation & Setup

## Overview

This document provides detailed instructions for installing and setting up the Agent C React UI development environment. It covers system requirements, installation steps, troubleshooting common issues, and configuration options.

## Contents

- [System Requirements](#system-requirements)
- [Installation Process](#installation-process)
- [Environment Configuration](#environment-configuration)
- [shadcn/ui Component Installation](#shadcnui-component-installation)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Node.js**: v16.0.0 or later
- **npm**: v7.0.0 or later or **yarn**: v1.22.0 or later
- **Disk Space**: At least 1GB of free space
- **Memory**: 4GB RAM minimum, 8GB recommended

### Recommended Development Tools

- **Code Editor**: Visual Studio Code with the following extensions:
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense
  - PostCSS Language Support
- **Browser**: Chrome with React Developer Tools extension

## Installation Process

### 1. Clone the Repository

```bash
git clone [repository-url]
cd agent-c-react-ui
```

### 2. Install Dependencies

Using npm:

```bash
npm install
```

Using yarn:

```bash
yarn install
```

### 3. Set Up Environment Variables

Create a local environment file:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your environment variables according to your needs.

### 4. Install shadcn/ui Components

On Windows, use the provided batch file:

```bash
install_shadcn.bat
```

On Unix/Linux/MacOS, you might need to install components manually using the following pattern:

```bash
npx shadcn-ui@latest add [component-name]
```

Replace `[component-name]` with the name of each required component.

## Environment Configuration

### Environment Variables

The application uses the following environment variables that can be configured in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Base URL for the API | `http://localhost:8000` |
| `VITE_APP_ENV` | Application environment | `development` |

### Tailwind Configuration

The `tailwind.config.js` file contains theme settings and other Tailwind CSS configurations. Key areas to be aware of:

- **Theme**: Colors, spacing, typography, and other design tokens
- **Plugins**: Additional Tailwind plugins used by the project
- **Content Paths**: Files to be scanned for Tailwind class usage

### Vite Configuration

The `vite.config.js` file contains build and development server configurations. Notable settings include:

- **Plugins**: Vite plugins used in the project
- **Resolve Aliases**: Path aliases for cleaner imports
- **Server Options**: Development server configuration
- **Build Options**: Production build settings

## shadcn/ui Component Installation

### Understanding the Component System

shadcn/ui is not a traditional component library. It's a collection of reusable components built on Radix UI primitives that you install directly into your project, allowing full customization.

### Adding New Components

To add new shadcn/ui components:

```bash
npx shadcn-ui@latest add [component-name]
```

Popular components include:

- `button`
- `dialog`
- `dropdown-menu`
- `tabs`
- `toast`

### Customizing Components

Once installed, components can be found in the `src/components/ui` directory. Feel free to modify these files to match your project's design requirements.

### Components Configuration

The `components.json` file contains configuration settings for shadcn/ui, including:

- **Style**: CSS or Tailwind variants
- **Component Directory**: Where components are installed
- **Utility Library**: CSS utility configurations

## Troubleshooting

### Common Installation Issues

1. **Node Version Conflicts**
   - **Symptom**: Error messages about incompatible Node versions
   - **Solution**: Use nvm (Node Version Manager) to install and use the required Node version

2. **Package Installation Failures**
   - **Symptom**: npm/yarn install errors
   - **Solution**: Clear npm/yarn cache and retry installation:
     ```bash
     npm cache clean --force
     npm install
     ```

3. **Vite Build Errors**
   - **Symptom**: Build fails with syntax or import errors
   - **Solution**: Check for mismatched imports or unsupported syntax

4. **shadcn/ui Component Conflicts**
   - **Symptom**: Component styling issues or runtime errors
   - **Solution**: Ensure Tailwind and component configurations match

### Getting Help

If you encounter issues not covered here:

1. Check the project's issue tracker for similar problems
2. Review the [shadcn/ui documentation](https://ui.shadcn.com) for component-specific guidance
3. Consult the React and Vite documentation for framework-level issues

## Related Documentation

- [Getting Started Guide](./getting-started.md)
- [Project Architecture Overview](./architecture-overview.md)
- [Component Usage Guide](../components/README.md)