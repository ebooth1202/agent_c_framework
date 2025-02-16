export const API_URL = import.meta.env.VITE_API_URL;
export const RAG_API_URL = import.meta.env.VITE_RAG_API_URL;

console.log('Environment Variables:', {
    VITE_API_URL: import.meta.env.VITE_API_URL,
    VITE_RAG_API_URL: import.meta.env.VITE_RAG_API_URL,
    MODE: import.meta.env.MODE,
    DEV: import.meta.env.DEV,
});