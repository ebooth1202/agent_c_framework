#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// Run vitest
const vitest = spawn('node', [
  path.join(__dirname, 'node_modules', '.bin', 'vitest'),
  'run',
  '--reporter=verbose'
], {
  cwd: __dirname,
  stdio: 'inherit',
  shell: true
});

vitest.on('close', (code) => {
  process.exit(code);
});