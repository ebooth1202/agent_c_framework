import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    exclude: [
      '**/node_modules/**',
      '**/.trash/**',
      '**/dist/**',
      '**/coverage/**'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/**',
        'dist/**',
        '**/*.config.*',
        '**/*.d.ts',
        '**/test/**',
        '**/tests/**',
        '**/__tests__/**',
        '**/__mocks__/**',
        '**/examples/**',
        '**/docs/**',
        '.scratch/**',
        'InteractiveAvatarNextJSDemo/**',
        'worklets/**',
        'coverage/**'
      ],
      thresholds: {
        // Temporarily set to 0 during test infrastructure reset
        // TODO: Restore to 70% when actual tests are written
        branches: 0,
        functions: 0,
        lines: 0,
        statements: 0
      }
    },
    setupFiles: ['./test/setup.ts'],
    testTimeout: 10000,
    hookTimeout: 10000,
    isolate: true,
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        isolate: true
      }
    }
  },
  resolve: {
    alias: {
      '@agentc/realtime-core': resolve(__dirname, './packages/core/src'),
      '@agentc/realtime-react': resolve(__dirname, './packages/react/src'),
      '@test': resolve(__dirname, './test')
    }
  }
});