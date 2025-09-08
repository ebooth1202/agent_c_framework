/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  webpack: (config) => {
    // Add aliases for all workspace packages to help resolve them
    config.resolve.alias = {
      ...config.resolve.alias,
      '@agentc/realtime-core': path.resolve(__dirname, '../core/dist'),
      '@agentc/realtime-react': path.resolve(__dirname, '../react/dist'),
      '@agentc/realtime-ui': path.resolve(__dirname, '../ui/dist'),
    };
    return config;
  },
}

module.exports = nextConfig