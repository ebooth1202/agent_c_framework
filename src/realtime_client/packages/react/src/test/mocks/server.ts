/**
 * MSW Server Setup for React Package
 * Configure Mock Service Worker for React components testing
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

/**
 * Setup MSW server with React package handlers
 */
export const server = setupServer(...handlers);

/**
 * Export server instance and helpers
 */
export default server;