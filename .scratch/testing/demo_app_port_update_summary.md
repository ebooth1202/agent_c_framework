# Demo App Port Update Summary

## ✅ Changes Made

Updated the Agent C Realtime Demo App to use port 8001 instead of 8000.

### Files Updated:

1. **`.env.local`** - Local development environment
   - `AGENT_C_API_URL`: `https://localhost:8000` → `http://localhost:8001`
   - `NEXT_PUBLIC_AGENTC_API_URL`: `wss://localhost:8000` → `ws://localhost:8001`

2. **`.env.example`** - Example environment template  
   - `AGENT_C_API_URL`: `https://localhost:8000` → `http://localhost:8001`
   - `NEXT_PUBLIC_AGENTC_API_URL`: `wss://localhost:8000` → `ws://localhost:8001`

### Protocol Changes:
- **HTTP**: Changed from `https://` to `http://` (matches our server configuration)
- **WebSocket**: Changed from `wss://` to `ws://` (matches our server configuration)

## 🔧 Configuration Details

### Server-side API calls (Next.js API routes):
- Uses `AGENT_C_API_URL=http://localhost:8001`
- For authentication and server-side requests

### Client-side WebSocket connections:
- Uses `NEXT_PUBLIC_AGENTC_API_URL=ws://localhost:8001` 
- For realtime chat and audio streaming

### Credentials (unchanged):
- `NEXT_PUBLIC_AGENTC_USERNAME=demo`
- `NEXT_PUBLIC_AGENTC_PASSWORD=password123`

## 🚀 Next Steps

1. **Restart the demo app** if it's currently running:
   ```bash
   cd /Users/ethanbooth/agent_c_framework/src/realtime_client/packages/demo
   pnpm dev
   ```

2. **Test the connection**:
   - Demo app: http://localhost:3000
   - Should now connect to Agent C API on port 8001
   - Should successfully authenticate and establish WebSocket connection

## 🧪 Verification

The demo app should now:
- ✅ Connect to `http://localhost:8001/api/rt/login` for authentication
- ✅ Establish WebSocket connection to `ws://localhost:8001/api/rt/ws`
- ✅ No more 404 errors from realtime API endpoints
- ✅ Full realtime chat and audio functionality

## 📝 Notes

- The fallback URL in `client-provider.tsx` remains `wss://agent-c-prod.censius.ai` but won't be used since environment variables take precedence
- All hardcoded references checked - no additional changes needed
- Protocol changed to HTTP/WS to match our development server configuration