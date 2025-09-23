import { NextRequest, NextResponse } from 'next/server';
<<<<<<< HEAD
import { env } from '@/env.mjs';
import axios from 'axios';
import https from 'node:https';
import { Logger } from '@/utils/logger';
=======

// Development mode flag - set to true to use mock data instead of backend
const DEVELOPMENT_MODE = false;
>>>>>>> 6b21e21a84ec28e76be5ccee55f32886d58d8245

/**
 * Attempt HTTPS request with specific SSL configuration
 */
async function attemptHttpsRequest(backendUrl: string, credentials: any, sslOptions: any) {
  const https = require('https');
  const { URL } = require('url');
  
  const url = new URL(backendUrl);
  const postData = JSON.stringify(credentials);
  
  const options = {
    hostname: url.hostname,
    port: url.port || 443,
    path: url.pathname,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData)
    },
    ...sslOptions
  };
<<<<<<< HEAD
  agents: Array<{
    name: string;
    key: string;
    agent_description: string | null;
    category: string[];
  }>;
  avatars: Array<{
    avatar_id: string;
    created_at: number;
    default_voice: string;
    is_public: boolean;
    normal_preview: string;
    pose_name: string;
    status: string;
  }>;
  tools: Array<{
    name: string;
    key: string;
    description: string | null;
    category: string[];
  }>;
  voices: Array<{
    voice_id: string;
    vendor: string;
    description: string;
    output_format: string;
  }>;
  ui_session_id: string;
=======
  
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res: any) => {
      let data = '';
      res.on('data', (chunk: any) => data += chunk);
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          statusText: res.statusMessage,
          ok: res.statusCode >= 200 && res.statusCode < 300,
          text: async () => data,
          json: async () => JSON.parse(data)
        });
      });
    });
    
    req.on('error', (error: any) => {
      reject(error);
    });
    
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.write(postData);
    req.end();
  });
>>>>>>> 6b21e21a84ec28e76be5ccee55f32886d58d8245
}

// Create a properly formatted JWT token for development
// JWT structure: header.payload.signature (all base64 encoded)
function createMockJWT() {
  const header = {
    "alg": "HS256",
    "typ": "JWT"
  };
  
  const payload = {
    "sub": "demo-user",
    "permissions": ["demo"],
    "exp": Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours from now
    "iat": Math.floor(Date.now() / 1000)
  };
  
  // Base64 encode each part
  const encodedHeader = btoa(JSON.stringify(header));
  const encodedPayload = btoa(JSON.stringify(payload));
  const signature = "demo-signature-for-development";
  
  return `${encodedHeader}.${encodedPayload}.${signature}`;
}

// Mock login data for development
const MOCK_LOGIN_RESPONSE = {
  "agent_c_token": createMockJWT(),
  "heygen_token": "demo-heygen-token",
  "ui_session_id": "demo-session",
  "user": {
    "user_id": "demo-user",
    "user_name": "demo",
    "email": "demo@example.com",
    "first_name": "Demo",
    "last_name": "User",
    "is_active": true,
    "roles": ["demo"],
    "groups": [],
    "created_at": new Date().toISOString(),
    "last_login": null
  },
  "agents": [
    {
      "name": "Demo Agent",
      "key": "demo_agent",
      "agent_description": "A demo agent for testing the realtime client.",
      "category": ["domo", "agent_assist"]
    }
  ],
  "avatars": [
    {
      "avatar_id": "demo_avatar",
      "created_at": Date.now(),
      "default_voice": "alloy",
      "is_public": true,
      "normal_preview": "https://via.placeholder.com/150",
      "pose_name": "Demo Avatar",
      "status": "ACTIVE"
    }
  ],
  "toolsets": [],
  "voices": [
    {
      "voice_id": "none",
      "vendor": "system",
      "description": "No Voice (text only)",
      "output_format": "none"
    },
    {
      "voice_id": "alloy",
      "vendor": "openai",
      "description": "OpenAI Alloy Voice",
      "output_format": "pcm16"
    },
    {
      "voice_id": "echo",
      "vendor": "openai",
      "description": "OpenAI Echo Voice",
      "output_format": "pcm16"
    },
    {
      "voice_id": "nova",
      "vendor": "openai",
      "description": "OpenAI Nova Voice",
      "output_format": "pcm16"
    }
  ],
  "sessions": {
    "chat_sessions": [],
    "total_sessions": 0,
    "offset": 0
  }
};

export async function POST(request: NextRequest) {
  try {
    console.log('🔍 Login API route called');
    console.log('🌍 Environment check:', {
      DEVELOPMENT_MODE,
      AGENT_C_API_URL: process.env.AGENT_C_API_URL,
      NODE_ENV: process.env.NODE_ENV
    });
    
<<<<<<< HEAD
    if (!agentCApiUrl) {
      Logger.error('AGENT_C_API_URL is not configured');
=======
    const credentials = await request.json();
    console.log('📝 Credentials received:', { username: credentials.username, hasPassword: !!credentials.password });
    
    // Development mode - return mock data
    if (DEVELOPMENT_MODE) {
      console.log('🧪 Development mode: Using mock login data');
      
      // Simple credential validation for demo
      if (credentials.username === 'demo' && credentials.password === 'password123') {
        console.log('✅ Mock login successful');
        return NextResponse.json(MOCK_LOGIN_RESPONSE);
      } else {
        console.log('❌ Invalid demo credentials');
        return NextResponse.json(
          { error: 'Invalid credentials. Use demo/password123 for development.' },
          { status: 401 }
        );
      }
    }
    
    // Production mode - call actual backend
    const apiUrl = process.env.AGENT_C_API_URL;
    if (!apiUrl) {
      console.error('❌ AGENT_C_API_URL environment variable not configured!');
>>>>>>> 6b21e21a84ec28e76be5ccee55f32886d58d8245
      return NextResponse.json(
        { error: 'Server configuration error: AGENT_C_API_URL not set' },
        { status: 500 }
      );
    }
    
    const backendUrl = apiUrl + '/api/rt/login';
    console.log('🌐 Calling backend:', backendUrl);
    
    // Quick connectivity test first
    console.log('🔍 Testing basic connectivity...');
    try {
      const testUrl = apiUrl.replace('https://', 'http://') + '/health';
      const testResponse = await Promise.race([
        fetch(testUrl, { method: 'GET' }),
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 3000))
      ]).catch(() => null);
      
      if (testResponse) {
        console.log('✅ Server is reachable via HTTP');
      } else {
        console.log('⚠️ Server health check failed or timed out, continuing with login attempt');
      }
    } catch (testError) {
      console.log('🤷 Connectivity test inconclusive, proceeding with login');
    }
    
    // Try multiple connection strategies
    let response;
    let lastError;
    let connectionLog: string[] = [];
    
    // Strategy 1: Try HTTPS with multiple SSL configurations
    if (backendUrl.startsWith('https:')) {
      console.log('🔐 Attempting HTTPS connection...');
      connectionLog.push('Starting HTTPS attempts');
      
      const httpsStrategies = [
        {
          name: 'Default SSL (self-signed bypass)',
          options: {
            rejectUnauthorized: false,
            timeout: 5000
          }
        },
        {
          name: 'TLS v1.2 with relaxed ciphers',
          options: {
            rejectUnauthorized: false,
            secureProtocol: 'TLSv1_2_method',
            ciphers: 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:AES128-GCM-SHA256:AES256-GCM-SHA384',
            timeout: 5000
          }
        },
        {
          name: 'TLS v1.3 only',
          options: {
            rejectUnauthorized: false,
            secureProtocol: 'TLSv1_3_method',
            timeout: 5000
          }
        },
        {
          name: 'Legacy SSL (all protocols)',
          options: {
            rejectUnauthorized: false,
            secureProtocol: 'SSLv23_method',
            timeout: 5000
          }
        },
        {
          name: 'Minimum TLS v1.0',
          options: {
            rejectUnauthorized: false,
            secureProtocol: 'TLSv1_method',
            ciphers: 'ALL:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP:!CAMELLIA',
            timeout: 5000
          }
        }
      ];
      
      for (const strategy of httpsStrategies) {
        try {
          console.log(`🔄 Trying HTTPS strategy: ${strategy.name}`);
          connectionLog.push(`Attempting: ${strategy.name}`);
          response = await attemptHttpsRequest(backendUrl, credentials, strategy.options);
          console.log(`✅ HTTPS connection successful with: ${strategy.name}`);
          connectionLog.push(`SUCCESS: ${strategy.name}`);
          break;
        } catch (error: any) {
          const errorInfo = `${strategy.name} failed: ${error.code} - ${error.message?.substring(0, 80)}`;
          console.log(`❌ ${errorInfo}`);
          connectionLog.push(errorInfo);
          lastError = error;
          
          // If we get EPROTO, this strongly suggests HTTP server on HTTPS port
          if (error.code === 'EPROTO') {
            console.log('🚨 EPROTO detected - server is likely HTTP-only, will try HTTP immediately');
            connectionLog.push('EPROTO detected - switching to HTTP strategy');
            break;
          }
        }
      }
    }
    
    // Strategy 2: HTTP fallback if HTTPS failed
    if (!response) {
      const httpUrl = backendUrl.replace('https://', 'http://');
      console.log('🔄 Falling back to HTTP:', httpUrl);
      connectionLog.push(`Trying HTTP fallback: ${httpUrl}`);
      
      try {
        // Create timeout controller for fetch request
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);
        
        try {
          response = await fetch(httpUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
            signal: controller.signal
          });
          clearTimeout(timeoutId);
        } catch (fetchError: any) {
          clearTimeout(timeoutId);
          throw fetchError;
        }
        console.log('✅ HTTP fallback successful - server is HTTP-only!');
        connectionLog.push('SUCCESS: HTTP fallback worked');
      } catch (error: any) {
        const errorMsg = `HTTP fallback failed: ${error.message}`;
        console.error(`❌ ${errorMsg}`);
        connectionLog.push(errorMsg);
        lastError = error;
      }
    }
    
    // Strategy 3: Try alternative endpoints if main endpoint failed
    if (!response || !response.ok) {
      console.log('🔄 Trying alternative endpoints...');
      
      const alternativeEndpoints = [
        '/api/v1/rt/login',
        '/api/auth/login',
        '/rt/login',
        '/login'
      ];
      
      for (const endpoint of alternativeEndpoints) {
        const altUrl = apiUrl + endpoint;
        console.log(`🔄 Trying alternative endpoint: ${altUrl}`);
        
        try {
          // Try HTTP first for alternatives (faster)
          const httpAltUrl = altUrl.replace('https://', 'http://');
          const altResponse = await fetch(httpAltUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials)
          });
          
          if (altResponse.ok) {
            console.log(`✅ Alternative endpoint successful: ${endpoint}`);
            response = altResponse;
            break;
          } else {
            console.log(`❌ Alternative endpoint ${endpoint} returned:`, altResponse.status);
          }
        } catch (error: any) {
          console.log(`❌ Alternative endpoint ${endpoint} failed:`, error.message);
        }
      }
    }
    
    if (!response) {
      console.error('💥 All connection strategies exhausted');
      console.error('📃 Connection attempts log:', connectionLog);
      throw new Error(`All connection strategies failed. Connection log: ${connectionLog.join(' | ')}. Last error: ${lastError?.message || 'Unknown error'}`);
    }
    
    console.log('🎆 Final connection summary:', connectionLog);
    
    console.log('📡 Backend response status:', response.status, response.statusText);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Backend error:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('✅ Backend success:', Object.keys(data));
    
    return NextResponse.json(data);
    
  } catch (error: any) {
    console.error('💥 Login API route error:', {
      message: error.message,
      stack: error.stack,
      name: error.name,
      code: error.code
    });
    
    // Provide more specific error messages
    let errorMessage = error.message;
    let troubleshooting = [];
    
    if (error.code === 'ECONNREFUSED') {
      errorMessage = `Cannot connect to Agent C backend at ${process.env.AGENT_C_API_URL} - connection refused`;
      troubleshooting.push('Is the Agent C server running?', 'Check if the port is correct', 'Verify firewall settings');
    } else if (error.code === 'ENOTFOUND') {
      errorMessage = `Cannot resolve hostname for Agent C backend: ${process.env.AGENT_C_API_URL}`;
      troubleshooting.push('Check the hostname/domain name', 'Verify DNS resolution', 'Try using IP address instead');
    } else if (error.code === 'ETIMEDOUT') {
      errorMessage = `Connection timeout to Agent C backend: ${process.env.AGENT_C_API_URL}`;
      troubleshooting.push('Server might be slow to respond', 'Check network connectivity', 'Try increasing timeout');
    } else if (error.code === 'EPROTO') {
      errorMessage = `SSL/TLS protocol error connecting to Agent C backend`;
      troubleshooting.push(
        'Server might be HTTP-only (not HTTPS)',
        'SSL certificate or cipher suite incompatibility',
        'Check if server supports the TLS version being used',
        'Try connecting via browser to verify SSL setup'
      );
    } else if (error.message?.includes('All connection strategies failed')) {
      errorMessage = 'Could not establish connection to Agent C backend using any method';
      troubleshooting.push(
        'Check server configuration (HTTP vs HTTPS)',
        'Verify the correct API endpoint path',
        'Check server logs for connection attempts',
        'Try accessing the API directly via curl or browser'
      );
    }
<<<<<<< HEAD

    // Return the successful response
    // The client will handle storing the token in cookies
    return NextResponse.json(loginResponse, { status: 200 });

  } catch (error) {
    Logger.error('Login proxy error:', error);
=======
>>>>>>> 6b21e21a84ec28e76be5ccee55f32886d58d8245
    
    return NextResponse.json(
      { 
        error: `Server error: ${errorMessage}`,
        troubleshooting: troubleshooting,
        debug: {
          originalError: error.message,
          code: error.code,
          backendUrl: process.env.AGENT_C_API_URL,
          connectionLog: error.message?.includes('Connection log:') ? 
            error.message.split('Connection log: ')[1]?.split('. Last error:')[0] : 
            'No connection log available',
          timestamp: new Date().toISOString()
        }
      },
      { status: 500 }
    );
  }
}