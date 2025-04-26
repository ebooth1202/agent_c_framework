# Registry

**Source:** Original from `shadcn-ui/registry/index.mdx`  
**Created:** April 24, 2025  

## Overview
The shadcn/ui registry system allows you to run your own component registry for distributing custom components, hooks, pages, and other files to any React project.

> **Note:** This feature is currently experimental. Help improve it by testing and providing feedback.

## Core Concept
The registry allows you to distribute reusable code to React projects through the shadcn CLI. Components and other registry items can be installed just like the built-in shadcn/ui components.

## Requirements

Registry implementations can be designed and hosted according to your needs, with one critical requirement:

- All registry items must be valid JSON files that conform to the registry-item schema specification

A template project for creating your own registry is available at: https://github.com/shadcn-ui/registry-template

## Key Benefits
- Distribute custom components across multiple projects
- Maintain style and behavior consistency across applications
- Automatically compatible with the `shadcn` CLI
- Support for the "Open in v0" functionality
- Works with various React frameworks and integrations

## Related Documentation
- See registry-item.json for the schema specification of registry items