/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
  webpack: (config) => {
    // Add alias for @agentc/realtime-core to help resolve it when imported by UI package
    config.resolve.alias = {
      ...config.resolve.alias,
      '@agentc/realtime-core': path.resolve(__dirname, '../core/dist'),
      '@agentc/realtime-react': path.resolve(__dirname, '../react/dist'),
    };
    return config;
  },
}

module.exports = nextConfig