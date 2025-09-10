/**
 * Test helper utilities for auth tests
 */

/**
 * Create a mock JWT token with specified payload and expiry
 */
export function createMockJWT(payload: Record<string, any>, expiresInSeconds: number): string {
  const header = {
    alg: 'HS256',
    typ: 'JWT'
  };
  
  const now = Math.floor(Date.now() / 1000);
  const fullPayload = {
    ...payload,
    iat: now,
    exp: now + expiresInSeconds
  };
  
  // Create a simple mock JWT structure (base64 encoded)
  const encodedHeader = btoa(JSON.stringify(header));
  const encodedPayload = btoa(JSON.stringify(fullPayload));
  const signature = 'mock-signature';
  
  return `${encodedHeader}.${encodedPayload}.${signature}`;
}

/**
 * Simple sleep utility for tests
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}