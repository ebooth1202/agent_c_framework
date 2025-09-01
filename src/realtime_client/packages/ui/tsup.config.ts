import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: {
    resolve: true,
    entry: './src/index.ts',
  },
  splitting: false,
  sourcemap: true,
  clean: true,
  external: ['react', 'react-dom', '@agentc/realtime-react', 'tailwindcss'],
  tsconfig: './tsconfig.json',
});