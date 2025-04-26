# Getting Started with Agent C React UI

## Overview

This guide will help you set up your development environment and get started with the Agent C React UI project. It covers installation, configuration, and basic development workflows.

## Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Configuration](#project-configuration)
- [Development Workflow](#development-workflow)
- [Running the Application](#running-the-application)
- [Key Commands](#key-commands)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16.0.0 or later)
- **npm** (v7.0.0 or later) or **yarn** (v1.22.0 or later)
- **Git** for version control

## Installation

1. **Clone the repository**

   ```bash
   git clone [repository-url]
   cd agent-c-react-ui
   ```

2. **Install dependencies**

   Using npm:

   ```bash
   npm install
   ```

   Or using yarn:

   ```bash
   yarn install
   ```

3. **Install shadcn/ui components**

   The project uses shadcn/ui components. To ensure all components are properly installed, run:

   ```bash
   # On Windows
   install_shadcn.bat
   
   # On Unix/Linux/MacOS
   # Follow the manual installation steps for required components
   ```

## Project Configuration

### Environment Variables

Copy the example environment file to create your local configuration:

```bash
cp .env.example .env
```

Edit the `.env` file to configure your environment variables. Key variables include:

- API endpoints
- Feature flags
- Environment mode

### Tailwind Configuration

The project uses Tailwind CSS with a custom configuration. Key files:

- `tailwind.config.js`: Configure theme, plugins, and content paths
- `components.json`: Configure shadcn/ui component settings

## Development Workflow

### Directory Structure

Familiarize yourself with the project structure:

```
/
├── src/               # Source code
│   ├── components/    # React components
│   ├── contexts/      # Context providers
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utility functions
│   ├── pages/         # Page components
│   ├── styles/        # CSS styles
│   ├── App.jsx        # Root component
│   ├── main.jsx       # Entry point
│   └── Routes.jsx     # Application routes
├── docs/              # Documentation
├── public/            # Static assets
├── vite.config.js     # Vite configuration
└── tailwind.config.js # Tailwind configuration
```

### Adding New Components

When adding new components:

1. Create the component file in the appropriate directory under `src/components/`
2. Create a corresponding CSS file in `src/styles/components/` if needed
3. Export the component from its directory's index file (if applicable)
4. Import and use the component where needed

## Running the Application

To start the development server:

```bash
# Using npm
npm run dev

# Using yarn
yarn dev
```

The application will be available at `http://localhost:5173` by default.

## Key Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start the development server |
| `npm run build` | Build the production application |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint to check for code issues |

## Next Steps

Now that you have the application running, you might want to:

1. Explore the [Project Architecture Overview](./architecture-overview.md) to understand the design
2. Review the [Component Documentation](../components/README.md) to learn about available components
3. Check the [Styling Guide](../style/styling-guide.md) to understand the CSS approach

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are installed correctly
2. Verify your Node.js version is compatible
3. Check that environment variables are properly configured
4. Review the console for error messages

## Related Documentation

- [Project Architecture Overview](./architecture-overview.md)
- [Installation & Setup](./installation-setup.md)
- [Project File Structure](./file-structure.md)