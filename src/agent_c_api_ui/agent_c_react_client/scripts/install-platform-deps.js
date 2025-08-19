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
    if (process.arch === 'arm64') {
      console.log('Installing macOS-specific dependencies for Apple Silicon...');
      execSync('npm install @rollup/rollup-darwin-arm64', { stdio: 'inherit' });
    } else if (process.arch === 'x64') {
      console.log('Installing macOS-specific dependencies for Intel...');
      execSync('npm install @rollup/rollup-darwin-x64', { stdio: 'inherit' });
    } else {
      console.log(`No specific rollup dependencies available for macOS ${process.arch}`);
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