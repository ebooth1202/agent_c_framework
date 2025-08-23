/**
 * Cross-platform dependency installer
 * This script installs platform-specific dependencies based on the current OS
 */

const { execSync } = require('child_process');
const { platform } = process;

try {
  // Install platform-specific rollup binary
    if (platform === 'win32') {
      console.log('Installing Windows-specific dependencies...');
      execSync('npm install @rollup/rollup-win32-x64-msvc', { stdio: 'inherit' });
    } else if (platform === 'linux') {
      console.log('Installing Linux-specific dependencies...');
      execSync('npm install @rollup/rollup-linux-x64-gnu', { stdio: 'inherit' });
    } else if (platform === 'darwin') {
    console.log('Installing macOS-specific dependencies...');
    const arch = process.arch;
    if (arch === 'arm64') {
      execSync('npm install @rollup/rollup-darwin-arm64', {stdio: 'inherit'});
    } else {
      execSync('npm install @rollup/rollup-darwin-x64', {stdio: 'inherit'});
    }
    } else {
    console.log(`No specific dependencies to install for platform: ${platform}`);
    }

    console.log('Platform-specific installation completed successfully');
} catch (error) {
  console.warn('Optional dependency installation failed:', error.message);
  // Exit with success even if optional dependencies fail
  process.exit(0);
}