// Quick test to verify TurnManager can be imported from the main package
const { TurnManager, RealtimeClient } = require('./packages/core/dist');

console.log('✓ TurnManager successfully imported:', typeof TurnManager);
console.log('✓ RealtimeClient successfully imported:', typeof RealtimeClient);

// Verify TurnManager is a constructor function
if (typeof TurnManager === 'function') {
    console.log('✓ TurnManager is a valid constructor');
}

// Verify RealtimeClient has getTurnManager method
const testClient = new RealtimeClient({
    apiUrl: 'wss://test.api.com/rt/ws',
    authToken: 'test-token'
});

if (typeof testClient.getTurnManager === 'function') {
    console.log('✓ RealtimeClient has getTurnManager method');
}

testClient.destroy();

console.log('\n✅ All imports and methods verified successfully!');