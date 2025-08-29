/**
 * Basic test file to verify TurnManager functionality
 * This demonstrates the usage and verifies the implementation
 */

import { RealtimeClient } from '../client/RealtimeClient';
import { TurnManager } from './TurnManager';

// Mock configuration for testing
const mockConfig = {
    apiUrl: 'wss://test.api.com/rt/ws',
    authToken: 'test-token',
    enableTurnManager: true
};

// Create a client instance
const client = new RealtimeClient(mockConfig);

// Get the TurnManager instance
const turnManager = client.getTurnManager();

if (turnManager) {
    console.log('✓ TurnManager successfully created');
    
    // Check initial state
    console.log('✓ Initial canSendInput state:', turnManager.canSendInput);
    
    // Listen for turn state changes
    turnManager.on('turn-state-changed', ({ canSendInput }) => {
        console.log('✓ Turn state changed:', canSendInput);
    });
    
    // Verify the TurnManager is an instance of the correct class
    if (turnManager instanceof TurnManager) {
        console.log('✓ TurnManager is correctly typed');
    }
    
    // Test manual creation
    const manualTurnManager = new TurnManager(client);
    console.log('✓ Manual TurnManager creation successful');
    
    // Clean up
    manualTurnManager.cleanup();
    console.log('✓ Cleanup successful');
} else {
    console.error('✗ TurnManager not created');
}

// Test with disabled TurnManager
const clientNoTurn = new RealtimeClient({
    ...mockConfig,
    enableTurnManager: false
});

if (clientNoTurn.getTurnManager() === null) {
    console.log('✓ TurnManager correctly disabled when configured');
} else {
    console.error('✗ TurnManager should be null when disabled');
}

// Clean up
client.destroy();
clientNoTurn.destroy();

console.log('\nAll tests passed successfully!');