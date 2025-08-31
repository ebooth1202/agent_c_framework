import { NextRequest, NextResponse } from 'next/server';
import { env } from '@/env.mjs';
import axios from 'axios';
import https from 'node:https';

/**
 * Login credentials for the API
 */
interface LoginCredentials {
  username?: string;
  email?: string;
  password: string;
}

/**
 * Login response from the Agent C API
 */
interface LoginResponse {
  token: string;
  heyGenToken?: string;
  voices?: Array<{
    id: string;
    name?: string;
    format: string;
    sampleRate: number;
  }>;
  avatars?: Array<{
    id: string;
    name: string;
  }>;
}

/**
 * POST /api/auth/login
 * Proxies authentication requests to the Agent C API
 */
export async function POST(request: NextRequest) {
  try {
    // Parse the request body
    const credentials: LoginCredentials = await request.json();

    // Validate credentials
    if (!credentials.password) {
      return NextResponse.json(
        { error: 'Password is required' },
        { status: 400 }
      );
    }

    if (!credentials.username && !credentials.email) {
      return NextResponse.json(
        { error: 'Username or email is required' },
        { status: 400 }
      );
    }

    // Get the Agent C API URL from server-side environment variable
    const agentCApiUrl = env.AGENT_C_API_URL || process.env.AGENT_C_API_URL;
    
    if (!agentCApiUrl) {
      console.error('AGENT_C_API_URL is not configured');
      return NextResponse.json(
        { error: 'Server configuration error' },
        { status: 500 }
      );
    }

    // Construct the full URL for the Agent C login endpoint
    const loginUrl = `${agentCApiUrl}/api/rt/login`;

    // In development, handle self-signed certificates
    const isDevelopment = process.env.NODE_ENV === 'development';

    // Create an HTTPS agent that accepts self-signed certificates in development
    const httpsAgent = isDevelopment && loginUrl.startsWith('https://') 
      ? new https.Agent({ rejectUnauthorized: false })
      : undefined;

    // Use axios instead of fetch to properly support custom HTTPS agents
    const response = await axios.post(loginUrl, credentials, {
      headers: {
        'Content-Type': 'application/json',
      },
      httpsAgent: httpsAgent,
      validateStatus: () => true, // Don't throw on non-2xx status codes
    });

    // Get the response data
    const responseData = response.data;

    // If the request failed, return the error
    if (response.status >= 400) {
      return NextResponse.json(
        responseData || { error: `Login failed: ${response.statusText}` },
        { status: response.status }
      );
    }

    // Validate the response has a token
    const loginResponse = responseData as LoginResponse;
    if (!loginResponse.token) {
      return NextResponse.json(
        { error: 'No token received from authentication server' },
        { status: 500 }
      );
    }

    // Return the successful response
    // The client will handle storing the token in cookies
    return NextResponse.json(loginResponse, { status: 200 });

  } catch (error) {
    console.error('Login proxy error:', error);
    
    // Handle axios errors
    if (axios.isAxiosError(error)) {
      // Network or connection errors
      if (error.code === 'ECONNREFUSED' || error.code === 'ENOTFOUND') {
        return NextResponse.json(
          { error: 'Unable to connect to authentication server' },
          { status: 503 }
        );
      }
      
      // Certificate errors should now be handled by the httpsAgent
      if (error.code === 'UNABLE_TO_VERIFY_LEAF_SIGNATURE') {
        return NextResponse.json(
          { error: 'Certificate verification failed. Please check server configuration.' },
          { status: 503 }
        );
      }
    }

    // Generic error response
    return NextResponse.json(
      { error: 'An unexpected error occurred during login' },
      { status: 500 }
    );
  }
}