# Shadcn UI Introduction

Created: 2025-04-24
Source: index.mdx

## Overview

Shadcn UI is not a traditional component library but a code distribution platform that provides the actual component code for you to customize. It follows an "open code" philosophy where you directly control and modify the component code rather than using black-box imports.

## Core Principles

### Open Code
- Provides the actual component source code
- Full transparency into implementation
- Direct customization without wrappers or workarounds
- Makes components accessible to LLMs for analysis and improvement

### Composition
- All components share a common, predictable interface
- Consistent API across all components, including third-party ones
- Makes components predictable for both developers and AI models

### Distribution
- Defines a flat-file schema for component definitions
- Includes CLI tools for cross-framework component installation
- Schema enables AI-based component generation

### Beautiful Defaults
- Carefully designed default styles for immediate use
- Components designed to work together as a cohesive system
- Minimal but sufficient styling foundation

### AI-Ready
- Open code allows AI models to read and understand components
- Consistent patterns make AI-assisted development more effective
- Enables AI to suggest improvements or generate compatible components

## Common Questions

### How to handle upstream updates?
Shadcn UI follows a headless component architecture where:
- Core functionality comes from dependencies that can be updated normally
- The design system layer remains open for modification
- Updates to core libraries (like Radix UI) can be pulled in while preserving your custom styling