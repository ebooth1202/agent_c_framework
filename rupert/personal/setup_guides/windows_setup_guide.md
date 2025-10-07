# Agent C Realtime Client Windows Setup Guide
*Complete Setup for the NEW Agent C Realtime Client with Voice Support*

---

## Quick Navigation

- [Prerequisites](#prerequisites)
- [Step 1: Install All Software](#step-1-install-all-software)
- [Step 2: Verify Installations](#step-2-verify-installations)
- [Step 3: Download Agent C](#step-3-download-agent-c)
- [Step 4: Configure Git for HTTPS](#step-4-configure-git-for-https)
- [Step 5: Install Package Managers](#step-5-install-package-managers)
- [Step 6: Run Backend Setup](#step-6-run-backend-setup)
- [Step 7: Get Your AI API Key](#step-7-get-your-ai-api-key)
- [Step 8: Configure Backend Environment](#step-8-configure-backend-environment)
- [Step 9: Set Up Realtime Client](#step-9-set-up-realtime-client)
- [Step 10: Start Agent C Realtime Client](#step-10-start-agent-c-realtime-client)
- [Step 11: Access Agent C](#step-11-access-agent-c)
- [Daily Use: Starting and Stopping](#daily-use-starting-and-stopping)
- [Updating Agent C](#updating-agent-c)
- [Troubleshooting](#troubleshooting)
- [Quick Reference](#quick-reference)

---

## Prerequisites

**System Requirements:**
- Windows 10 (version 1809+) or Windows 11
- At least 8GB RAM
- At least 15GB free disk space
- Stable internet connection
- Administrator access to install software
- **Chrome, Firefox, or Edge browser** (for microphone access)

**What You're Setting Up:**
- **NEW Agent C Realtime Client** with voice support
- Runs on **HTTPS** (https://localhost:5173)
- Supports real-time voice conversations and text chat
- **NOT** the old Agent C UI

---

## Step 1: Install All Software

### 1.1 Open Windows PowerShell as Administrator

1. Press `Windows + X`
2. Select **"Windows PowerShell (Admin)"** or **"Windows Terminal (Admin)"**
3. Click **"Yes"** when prompted for administrator access

### 1.2 Install All Prerequisites

Copy and paste each command one at a time, pressing Enter after each:

```powershell
winget install Git.Git
```

```powershell
winget install Python.Python.3.12
```

```powershell
winget install Microsoft.VisualStudio.2022.BuildTools
```

```powershell
winget install Rustlang.Rustup
```

```powershell
winget install OpenJS.NodeJS
```

```powershell
winget install Gyan.FFmpeg
```

### 1.3 Wait for Installations

- Each command will take 1-5 minutes to complete
- Visual Studio Build Tools requires approximately 4.55GB of download
- Do not close PowerShell until all installations are finished

### 1.4 Restart Your Computer

1. Close PowerShell
2. Restart your computer to ensure all PATH variables are updated
3. Wait for Windows to fully boot up

---

## Step 2: Verify Installations

### 2.1 Open New PowerShell

1. Press `Windows + X`
2. Select **"Windows PowerShell"** (regular, not admin)

### 2.2 Test Each Installation

Run each command and verify you see version information:

```powershell
git --version
```
Should show: `git version 2.x.x.windows.1`

```powershell
python --version
```
Should show: `Python 3.12.x`

```powershell
node --version
```
Should show: `v20.x.x` or `v22.x.x`

```powershell
npm --version
```
Should show: `10.x.x` or higher

```powershell
rustc --version
```
Should show: `rustc 1.x.x`

```powershell
ffmpeg -version
```
Should show: `ffmpeg version x.x.x`

### 2.3 If Any Commands Fail

1. Restart your computer again
2. Try the verification commands again
3. If still failing, see Troubleshooting section

---

## Step 3: Download Agent C

### 3.1 Open PowerShell and Navigate to Home Directory

```powershell
cd $env:USERPROFILE
```

### 3.2 Clone the Agent C Repository

```powershell
git clone https://github.com/centricconsulting/agent_c_framework.git agent_c
```

### 3.3 Navigate to Project Directory

```powershell
cd agent_c
```

---

## Step 4: Configure Git for HTTPS

### 4.1 Fix Git Authentication Issues

```powershell
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

This prevents SSH authentication errors during package installations.

---

## Step 5: Install Package Managers

### 5.1 Install pnpm

```powershell
npm install -g pnpm
```

### 5.2 Verify pnpm Installation

```powershell
pnpm --version
```
Should show: `9.x.x` or higher

---

## Step 6: Run Backend Setup

### 6.1 Run Initial Setup Script

```powershell
.\scripts\initial_setup.bat
```

### 6.2 What Happens During Setup

The script will:
1. Create a Python virtual environment (`.venv` folder)
2. Copy `example.env` to `.env` and open it in Notepad
3. Install Python dependencies (this takes 10-20 minutes)
4. **When Notepad opens**: Close it without making changes for now

### 6.3 Wait for Completion

Look for: **"Initial setup completed successfully"**

**If you get lerna errors**: This is normal - we'll handle the realtime client separately.

---

## Step 7: Get Your AI API Key

### 7.1 Create Anthropic Account

1. Go to: https://console.anthropic.com/
2. Click **"Sign Up"**
3. Create your account and verify your email

### 7.2 Add Payment Method

1. After logging in, click **"Billing"** in the left sidebar
2. Click **"Add Payment Method"**
3. Enter your credit card information
4. Add initial credits (start with $20)

### 7.3 Create API Key

1. Click **"API Keys"** in the left sidebar
2. Click **"Create Key"**
3. Give it a name like "Agent C Realtime"
4. Click **"Create Key"**
5. **IMPORTANT**: Copy the key that appears (starts with `sk-ant-...`)
6. Save it in Notepad temporarily

---

## Step 8: Configure Backend Environment

### 8.1 Edit the Main Environment File

```powershell
notepad .env
```

### 8.2 Configure Your API Key

1. In the `.env` file, find this line:
   ```
   #ANTHROPIC_API_KEY=FROM-ANTHROPIC
   ```

2. Remove the `#` and replace `FROM-ANTHROPIC` with your actual API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
   ```

### 8.3 Update User ID

1. Find this line:
   ```
   CLI_CHAT_USER_ID=Taytay
   ```

2. Replace `Taytay` with your preferred username:
   ```
   CLI_CHAT_USER_ID=YourName
   ```

### 8.4 Save and Close

1. Press `Ctrl + S` to save
2. Close Notepad

---

## Step 9: Set Up Realtime Client

### 9.1 Navigate to Realtime Client Directory

```powershell
cd src\realtime_client
```

### 9.2 Install Realtime Client Dependencies

```powershell
pnpm install
```

**This will take 5-10 minutes and may show some warnings - this is normal.**

### 9.3 Build the Realtime Client

```powershell
pnpm build
```

### 9.4 Set Up Demo Environment

```powershell
cd packages\demo
```

```powershell
copy .env.example .env.local
```

### 9.5 Return to Main Directory

```powershell
cd $env:USERPROFILE\agent_c
```

---

## Step 10: Start Agent C Realtime Client

### 10.1 Start the Backend API Server

In your current PowerShell window:

```powershell
.\.venv\Scripts\activate
```

```powershell
.\scripts\start_api.bat
```

**Wait for**: **"Application startup complete"**

**Keep this window open** - the API server must stay running.

### 10.2 Start the Realtime Client (New PowerShell Window)

1. Open a **new PowerShell window**: Press `Windows + X` → **"Windows PowerShell"**

2. Navigate to Agent C directory:
   ```powershell
   cd $env:USERPROFILE\agent_c
   ```

3. Start the realtime client:
   ```powershell
   .\scripts\start_realtime_client.bat
   ```

4. **Wait for**: **"Ready - started server on https://localhost:5173"**

**Keep this window open** - the realtime client must stay running.

### 10.3 Verify Both Services Are Running

You should now have:
- **PowerShell Window 1**: API server running (shows "Application startup complete")
- **PowerShell Window 2**: Realtime client running (shows "Ready - started server on https://localhost:5173")

---

## Step 11: Access Agent C

### 11.1 Open Browser

1. Open **Chrome**, **Firefox**, or **Edge**
2. Go to: **https://localhost:5173**
   - **Note**: This is **HTTPS**, not HTTP
   - **Note**: This is the NEW realtime client, not the old UI

### 11.2 Accept SSL Certificate Warning

Since we're using self-signed certificates:

**Chrome/Edge:**
1. Click **"Advanced"**
2. Click **"Proceed to localhost (unsafe)"**

**Firefox:**
1. Click **"Advanced"**
2. Click **"Accept the Risk and Continue"**

### 11.3 Log In

Use these default credentials:
- **Username**: `admin`
- **Password**: `changeme`

Click **"Sign In"**

### 11.4 Change Your Password

1. Click your profile icon (top-right corner)
2. Select **"Settings"** or **"Change Password"**
3. Create a new, secure password
4. Save your new password

### 11.5 Allow Microphone Access

When prompted by your browser:
1. Click **"Allow"** to enable microphone access
2. This enables voice conversations with the AI

---

## Daily Use: Starting and Stopping

### Starting Agent C Realtime Client

**Terminal 1 (API Server):**
```powershell
cd $env:USERPROFILE\agent_c
.\.venv\Scripts\activate
.\scripts\start_api.bat
```

**Terminal 2 (Realtime Client):**
```powershell
cd $env:USERPROFILE\agent_c
.\scripts\start_realtime_client.bat
```

**Browser:**
Go to: **https://localhost:5173**

### Stopping Agent C

1. In both PowerShell windows, press `Ctrl + C`
2. Close both PowerShell windows
3. Close your browser

---

## Updating Agent C

### Update Process

1. Open PowerShell and navigate to project:
   ```powershell
   cd $env:USERPROFILE\agent_c
   ```

2. Activate virtual environment:
   ```powershell
   .\.venv\Scripts\activate
   ```

3. Pull latest changes:
   ```powershell
   git pull
   ```

4. Update Python dependencies:
   ```powershell
   .\scripts\install_deps.bat
   ```

5. Update realtime client:
   ```powershell
   cd src\realtime_client
   pnpm install
   pnpm build
   cd ..\..
   ```

---

## Troubleshooting

### Commands Not Found After Installation

**Error**: `'python' is not recognized` or similar

**Solution**:
1. Restart your computer
2. Try the verification commands again
3. If still failing, reinstall:
   ```powershell
   winget install --force Python.Python.3.12
   ```

### winget Command Not Found

**Error**: `'winget' is not recognized`

**Solution**:
1. Update Windows to the latest version
2. Install "App Installer" from Microsoft Store

### Git SSH Authentication Errors

**Error**: `Host key verification failed`

**Solution**: Make sure you ran this command:
```powershell
git config --global url."https://github.com/".insteadOf "git@github.com:"
```

### File Locking Errors (EBUSY)

**Error**: `EBUSY: resource busy or locked`

**Solution**:
1. Close all IDEs and file explorers
2. Kill Node processes:
   ```powershell
   taskkill /f /im node.exe
   taskkill /f /im pnpm.exe
   ```
3. Restart your computer
4. Try again

### Browser Says "Not Secure"

**Problem**: SSL certificate warnings

**Solution**: This is normal for local development. Click "Advanced" → "Proceed to localhost (unsafe)"

### Microphone Not Working

**Problem**: No voice input detected

**Solution**:
1. Make sure you're using HTTPS (https://localhost:5173)
2. Check browser microphone permissions
3. Allow microphone access when prompted
4. Check Windows microphone privacy settings

### Port Already in Use

**Error**: `Port 5173 is already in use`

**Solution**:
1. Close any running Agent C instances
2. Kill processes using the port:
   ```powershell
   netstat -ano | findstr :5173
   taskkill /pid [PID_NUMBER] /f
   ```
3. Restart your computer

### API Server Connection Failed

**Error**: WebSocket connection fails

**Solution**:
1. Make sure API server is running (Terminal 1)
2. Look for "Application startup complete" message
3. Make sure you're using the correct credentials
4. Check that .env file has your API key

### pnpm Install Fails

**Error**: Package installation errors

**Solution**:
1. Clear pnpm cache:
   ```powershell
   pnpm store path
   rmdir /s "path-shown-above"
   ```
2. Try install again:
   ```powershell
   pnpm install --frozen-lockfile
   ```

---

## Quick Reference

### Essential Commands

**Start API Server:**
```powershell
cd $env:USERPROFILE\agent_c
.\.venv\Scripts\activate
.\scripts\start_api.bat
```

**Start Realtime Client:**
```powershell
cd $env:USERPROFILE\agent_c
.\scripts\start_realtime_client.bat
```

**Stop Servers:**
```
Ctrl + C (in each PowerShell window)
```

### Important URLs

- **Agent C Realtime Client**: https://localhost:5173
- **Anthropic API Console**: https://console.anthropic.com/

### Default Login

- **Username**: `admin`
- **Password**: `changeme` (change immediately!)

### File Locations

- **Project Directory**: `C:\Users\YourUsername\agent_c`
- **Main Environment**: `C:\Users\YourUsername\agent_c\.env`
- **Demo Environment**: `C:\Users\YourUsername\agent_c\src\realtime_client\packages\demo\.env.local`

---

## Features of the Realtime Client

Once setup is complete, you can:

- **Voice Conversations**: Talk directly to AI agents using your microphone
- **Text Chat**: Type messages like traditional chat
- **Real-time Responses**: Get immediate AI responses
- **Multiple Agents**: Switch between different AI personalities
- **File Upload**: Share documents with the AI
- **Session Memory**: Conversations are remembered during your session

**Remember**: This is the NEW Agent C Realtime Client with voice support, not the original web UI.

---

*Setup complete! Your Agent C Realtime Client is ready for voice and text conversations.*