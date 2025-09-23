# 🔧 Agent C Framework Setup Guide - Desktop Updates

## 📋 **Complete Fix Synopsis for Desktop Application**

Here's everything you need to do on your desktop to replicate the fixes we made:

---

## 🚨 **Issue 1: Workspace System Fix**

### **Problem Identified:**
- Agent C was looking for `.local_workspaces.json` (with dot prefix) in the project root
- We had `local_workspaces.json` (without dot) which wasn't being found
- This caused "No workspace found" errors for all configured workspaces

### **Solution Steps:**

#### **Step 1: Copy and Rename Workspace Configuration**
```bash
# Navigate to your Agent C Framework root directory
cd /path/to/your/agent_c_framework

# Copy local_workspaces.json to .local_workspaces.json (note the dot prefix)
cp local_workspaces.json .local_workspaces.json
```

#### **Step 2: Update Workspace Paths to Relative Paths**
Edit your `.local_workspaces.json` file to use relative paths instead of absolute paths:

**BEFORE (absolute paths):**
```json
{
    "name": "tools",
    "workspace_path": "/Users/yourusername/agent_c_framework/src/agent_c_tools",
    "description": "Agent C - Tools project"
}
```

**AFTER (relative paths):**
```json
{
    "name": "tools", 
    "workspace_path": "src/agent_c_tools",
    "description": "Agent C - Tools project"
}
```

**Apply this change to all workspaces that should be relative to the project root:**
- `tools`: `"src/agent_c_tools"`
- `core`: `"src/agent_c_core"` 
- `api`: `"src/agent_c_api_ui/agent_c_api"`
- `ui`: `"src/agent_c_api_ui/agent_c_react_client"`
- `realtime_client`: `"src/realtime_client"`

---

## 🔴 **Issue 2: Redis Connection Fix**

### **Problem Identified:**
- Agent C expects Redis to be running on `localhost:6379`
- Redis provides session persistence, user data storage, and chat history caching
- Without Redis, system falls back to memory-only storage with limited functionality

### **Solution Steps:**

#### **Step 1: Install Redis**
```bash
# Install Redis via Homebrew (macOS)
brew install redis
```

#### **Step 2: Start Redis Service**
```bash
# Option A: Start as a service (recommended - runs automatically on boot)
brew services start redis

# Option B: Run manually (for testing only)
# redis-server
```

#### **Step 3: Verify Redis Installation**
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Check Redis service status
brew services list | grep redis
# Should show: redis started
```

---

## 🔄 **Final Steps**

### **Step 3: Restart Agent C API Server**
After making both changes, restart your Agent C server:

```bash
# Stop the current server (Ctrl+C if running in terminal)
# Then restart using your normal startup script
cd /path/to/your/agent_c_framework
./scripts/start_api.sh
```

---

## ✅ **Verification Tests**

After restarting, verify everything works:

### **Test 1: Workspace Access**
In the Agent C UI, these should now work:
- Access to `//tools/` workspace
- Access to `//core/` workspace  
- Access to `//api/` workspace
- File listing and reading operations

### **Test 2: Redis Connection**
Check that Redis is working:
```bash
redis-cli ping
# Should return: PONG
```

### **Test 3: UI Functionality**
- Agent C UI loads properly
- All agents available in dropdown
- Chat functionality works without session issues

---

## 📁 **File Changes Summary**

### **Files Modified/Created:**
1. **`.local_workspaces.json`** - Created by copying and renaming `local_workspaces.json`
2. **Updated workspace paths** - Changed absolute paths to relative paths in the config

### **Services Installed:**
1. **Redis** - Installed via Homebrew and started as a service

---

## 🎯 **Expected Outcomes After Fix**

### **✅ Working Features:**
- All workspace commands functional (`workspace_ls`, `workspace_read`, etc.)
- Session persistence between browser sessions
- Chat history retained across restarts
- User data storage working properly
- All agents accessible and functional

### **🚫 No More Errors:**
- ~~"No workspace found" errors~~
- ~~"Redis connection failed" warnings~~
- ~~"Sessions will be memory-only" warnings~~

### **✅ Success Indicators:**
- Workspace commands return actual directory contents
- Redis connection logs show success in startup
- UI fully functional with all agents available
- Chat conversations persist across sessions

---

## 🆘 **Troubleshooting**

### **If Workspaces Still Don't Work:**
1. Verify `.local_workspaces.json` exists in project root (with dot prefix)
2. Check that paths in the file are relative, not absolute
3. Ensure server is restarted after changes

### **If Redis Issues Persist:**
```bash
# Check if Redis is running
brew services list | grep redis

# Restart Redis if needed
brew services restart redis

# Test connection
redis-cli ping
```

### **If Agent Config Warnings Appear:**
- These are likely non-critical warnings that don't affect functionality
- If UI and agents work normally, these can be safely ignored

---

## 🎊 **Final Result**
You should have a fully functional Agent C Framework with:
- ✅ Complete workspace system access
- ✅ Persistent sessions via Redis
- ✅ All agents operational
- ✅ Seamless UI experience

**This gives you the exact same working setup we achieved on your laptop!** 🚀

---

## 📝 **Technical Details - Root Cause Analysis**

### **Workspace System Root Cause:**
The `AgentBridge.__init_workspaces()` method in `/src/agent_c_api_ui/agent_c_api/src/agent_c_api/core/agent_bridge.py` was hardcoded to look for `LOCAL_WORKSPACES_FILE = '.local_workspaces.json'` in the current working directory. The environment variables we initially tried to set were not being used by this code path.

### **Redis Connection Root Cause:**
The Redis configuration in `/src/agent_c_api_ui/agent_c_api/src/agent_c_api/config/redis_config.py` expects Redis to be running on localhost:6379 for session management, user data storage, and chat history caching. Without Redis, the system gracefully degrades to memory-only storage but logs warnings.

### **Environment Variables (Not Used):**
These environment variables were set but not actually used by the workspace loading code:
```bash
export LOCAL_WORKSPACES_FILE=/Users/ethanbooth/agent_c_framework/local_workspaces.json
export COMPOSE_WORKSPACES_FILE=/Users/ethanbooth/agent_c_framework/compose_workspaces.json
export AGENT_C_WORKSPACE_CONFIG=/Users/ethanbooth/agent_c_framework/local_workspaces.json
export WORKSPACE_CONFIG_DIR=/Users/ethanbooth/agent_c_framework/
```

The actual fix required placing the file in the expected location with the expected name, rather than configuring the system to look elsewhere.

---

*Guide created: January 14, 2025*  
*Agent C Framework Version: Latest*  
*Platform: macOS with Homebrew*