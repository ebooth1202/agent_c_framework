/** @type {import('next').NextConfig} */
const path = require('path');

const nextConfig = {
<<<<<<< HEAD
  // Transpile the UI package to handle framer-motion properly
  transpilePackages: ['@agentc/realtime-ui'],
  
  // Configure source maps for development (disabled in production for security)
  productionBrowserSourceMaps: false,
  
  webpack: (config, { dev, isServer }) => {
    // Add alias for @agentc packages to help resolve them when imported by UI package
=======
  webpack: (config) => {
    // Add aliases for all workspace packages to help resolve them
>>>>>>> 6b21e21a84ec28e76be5ccee55f32886d58d8245
    config.resolve.alias = {
      ...config.resolve.alias,
      '@agentc/realtime-core': path.resolve(__dirname, '../core/dist'),
      '@agentc/realtime-react': path.resolve(__dirname, '../react/dist'),
      '@agentc/realtime-ui': path.resolve(__dirname, '../ui/dist'),
    };
    
    // Ensure source maps are properly configured in development
    if (dev && !isServer) {
      config.devtool = 'eval-source-map'; // Fast rebuild, good debugging
    }
    
    // Ignore source map warnings for browser extension files (React DevTools)
    config.ignoreWarnings = [
      ...(config.ignoreWarnings || []),
      {
        module: /installHook/,
      },
      {
        message: /Failed to parse source map/,
      },
    ];
    
    return config;
  },
}

module.exports = nextConfig