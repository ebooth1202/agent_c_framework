# Agent C Setup Guide for Mac Users
*A Simple, Step-by-Step Guide for Non-Technical Users*

---

## Quick Navigation

- [What is Agent C?](#what-is-agent-c)
- [What You'll Need](#what-youll-need)
- [Step 1: Install Docker Desktop](#step-1-install-docker-desktop)
- [Step 2: Download Agent C](#step-2-download-agent-c)
- [Step 3: Get Your AI API Key](#step-3-get-your-ai-api-key)
- [Step 4: Start Agent C](#step-4-start-agent-c)
- [Step 5: Access Agent C](#step-5-access-agent-c)
- [Step 6: Using Agent C](#step-6-using-agent-c)
- [Updating Agent C](#updating-agent-c)
- [Managing Custom Agents](#managing-custom-agents)
- [Daily Use: Starting and Stopping](#daily-use-starting-and-stopping-agent-c)
- [Troubleshooting](#troubleshooting-common-issues)
- [Tips for Success](#tips-for-success)
- [Quick Reference Card](#quick-reference-card)

---

## What is Agent C?

Agent C is an AI assistant that can help you with complex tasks like research, analysis, writing, and problem-solving. It's more powerful than ChatGPT because it can use tools, work with files on your computer, and maintain long-term memory of your conversations.

This guide will help you install and run Agent C on your Mac, even if you've never used technical software before.

---

## What You'll Need

Before starting, make sure you have:

1. **A Mac computer** running macOS 10.15 (Catalina) or newer
   - To check: Click the Apple logo (🍎) in the top-left corner → "About This Mac"
   
2. **At least 10GB of free storage space**
   - Check in "About This Mac" → "Storage" tab

3. **A stable internet connection** for downloading software and using AI features

4. **An AI API Key** (we'll help you get this in Step 3)

5. **About 30 minutes** for the complete setup

---

## Step 1: Install Docker Desktop

Docker is a program that creates a safe, isolated environment for Agent C to run in. Think of it like a virtual computer inside your Mac.

### 1.1 Download Docker Desktop

1. Open Safari or your preferred browser
2. Go to: https://www.docker.com/products/docker-desktop/
3. Click the blue **"Download for Mac"** button
4. **Important**: Choose the right version for your Mac:
   
   **How to know which version you need:**
   - Click the Apple logo (🍎) → "About This Mac"
   - Look for "Processor" or "Chip"
   - If it says "Intel" → Download **Mac with Intel chip**
   - If it says "M1", "M2", or "M3" → Download **Mac with Apple silicon**

5. The download will appear in your Downloads folder as `Docker.dmg`

### 1.2 Install Docker

1. Open Finder and go to your Downloads folder
2. Double-click `Docker.dmg`
3. A window will open showing the Docker icon and an Applications folder
4. **Drag the Docker whale icon** to the Applications folder
5. Wait for the copy to complete (you'll see a progress bar)

### 1.3 Start Docker for the First Time

1. Open your Applications folder (Finder → Applications)
2. Double-click **Docker** (look for the whale icon 🐳)
3. You'll see a security prompt: "Docker Desktop wants to make changes"
   - Enter your Mac password and click **OK**
4. Docker will open and show a welcome screen
5. **Skip the tutorial**: Click "Skip" or close the tutorial window
6. **Skip sign-in**: If asked to sign in, click "Skip" (you don't need an account)

### 1.4 Verify Docker is Running

Look at the top-right corner of your screen (menu bar). You should see a whale icon (🐳).
- If the whale is **not moving**: Docker is ready!
- If the whale is **animated/moving**: Docker is still starting. Wait 1-2 minutes.

**Troubleshooting**: If you don't see the whale icon, open Docker from Applications again.

---

## Step 2: Download Agent C

### 2.1 Download the Agent C Package

1. Open your web browser
2. Go to: https://github.com/centricconsulting/agent_c_framework
3. Look for a green button that says **"<> Code"**
4. Click it and select **"Download ZIP"**
5. The file `agent_c_framework-main.zip` will download to your Downloads folder

### 2.2 Extract and Move Agent C

1. Open Finder and go to Downloads
2. Double-click `agent_c_framework-main.zip`
   - This creates a folder called `agent_c_framework-main`
3. **Rename the folder** (right-click → "Rename") to just: `agent_c`
   - This makes it easier to find later
4. **Move to your home folder**:
   - Drag the `agent_c` folder to your name in the Finder sidebar
   - Or move it to: Macintosh HD → Users → [Your Name]

**Result**: You should now have an `agent_c` folder in your home directory.

---

## Step 3: Get Your AI API Key

Agent C needs an API key to connect to AI services. We'll use OpenAI (the makers of ChatGPT).

### 3.1 Create an OpenAI Account

1. Go to: https://platform.openai.com/signup
2. Sign up using your email or Google account
3. Verify your email if requested

### 3.2 Add Payment Method

**Important**: API usage costs money (typically $5-20/month for regular use)

1. After signing in, go to: https://platform.openai.com/account/billing
2. Click **"Add payment method"**
3. Enter your credit card information
4. Add an initial credit (start with $10-20)

### 3.3 Create Your API Key

1. Go to: https://platform.openai.com/api-keys
2. Click **"+ Create new secret key"**
3. Give it a name like "Agent C"
4. Click **"Create secret key"**
5. **IMPORTANT**: Copy the key that appears (starts with `sk-...`)
   - Save it somewhere safe - you won't be able to see it again!
   - You can paste it in Notes app temporarily

---

## Step 4: Start Agent C

### 4.1 Open Terminal

Terminal is a text-based way to control your Mac. Don't worry, we'll make it simple!

1. Press `Command + Space` to open Spotlight search
2. Type: `Terminal`
3. Press Enter to open Terminal
4. You'll see a window with text and a blinking cursor

### 4.2 Navigate to Agent C

In Terminal, type these commands exactly (press Enter after each line):

```bash
cd agent_c
cd dockerfiles
```

**What this does**: 
- `cd` means "change directory" (like opening a folder)
- This takes you to the Agent C dockerfiles folder

**Tip**: If you get "No such file or directory", make sure:
- You moved the agent_c folder to your home directory
- You renamed it to exactly `agent_c` (no spaces, all lowercase)

### 4.3 Make the Script Executable

Type this command and press Enter:

```bash
chmod +x start_agent_c.sh
```

**What this does**: Gives permission for the startup script to run (Mac security feature)

You won't see any output - that's normal!

### 4.4 Run Agent C for the First Time

Type this command and press Enter:

```bash
./start_agent_c.sh
```

**What happens next:**

1. **Configuration Setup** (first time only):
   - You'll be asked: "Please enter your OpenAI API key:"
   - Paste your API key (from Step 3.3) and press Enter
   - For other API keys, just press Enter to skip them
   - For "Enter your user ID", type your name and press Enter

2. **Docker Downloads** (first time only):
   - You'll see lots of text scrolling - this is normal!
   - Docker is downloading Agent C components
   - This takes 10-20 minutes depending on internet speed
   - Look for "Pulling" and progress bars

3. **Wait for "Services are ready!"**
   - Keep waiting until you see this message
   - Your browser might open automatically
   - If not, continue to the next step

---

## Step 5: Access Agent C

### 5.1 Open Agent C in Your Browser

1. Open Safari, Chrome, or Firefox
2. In the address bar, type exactly: `http://localhost:5173`
3. Press Enter

**What you should see**: The Agent C login page

### 5.2 Log In

Use these default credentials:
- **Username**: `admin`
- **Password**: `changeme`

Click **"Sign In"**

### 5.3 Change Your Password (Important!)

1. After logging in, click your profile icon (top-right corner)
2. Select "Change Password" or "Settings"
3. Create a new, secure password
4. Save it somewhere safe

---

## Step 6: Using Agent C

### 6.1 Starting a Conversation

1. You'll see a chat interface similar to ChatGPT
2. Type your message in the text box at the bottom
3. Press Enter to send

### 6.2 Selecting an Agent Persona

1. Click the **"Options"** or **"Settings"** panel
2. Under "Load Persona Prompt", choose an agent type:
   - **General Assistant**: Good for most tasks
   - **Research Assistant**: For in-depth research
   - **Writing Assistant**: For content creation
   - And many more specialized options

### 6.3 Enabling Tools

In the Options panel, you can give your agent extra capabilities:
- **Web Search**: Let the agent search the internet
- **File Access**: Work with files on your computer
- **Memory**: Remember things between conversations

Select the tools you want and click **"Equip Selected Tools"**

---

## Updating Agent C

As Agent C improves, you'll want to get the latest features and bug fixes. Here's how to update your installation.

### When to Update

Consider updating when:
- New features are announced
- Bug fixes are released  
- You experience issues that might be fixed in newer versions
- Every few weeks for general improvements

### Method 1: Updating from ZIP Download (What You Used)

Since you originally downloaded Agent C as a ZIP file, here's how to update:

#### Step 1: Backup Your Settings

**Important**: Save your configuration and custom agents first!

1. Open Terminal
2. Create a backup of your settings:
   ```bash
   cp -r ~/.agent_c ~/Desktop/agent_c_backup
   ```
   This copies your settings to your Desktop

#### Step 2: Download the Latest Version

1. Go to: https://github.com/centricconsulting/agent_c_framework
2. Click the green **"<> Code"** button
3. Select **"Download ZIP"**
4. Save to Downloads

#### Step 3: Replace Your Agent C Folder

1. Open Finder
2. Go to your home folder
3. **Delete or rename** your old `agent_c` folder:
   - Right-click → "Move to Trash", or
   - Rename it to `agent_c_old`
4. Extract the new ZIP file in Downloads
5. Rename `agent_c_framework-main` to `agent_c`
6. Move it to your home folder

#### Step 4: Restore Your Settings

1. Your configuration is already saved in `~/.agent_c`, so it's preserved!
2. No action needed - your API keys and settings remain intact

#### Step 5: Update Docker Images

1. Open Terminal
2. Navigate to dockerfiles:
   ```bash
   cd ~/agent_c/dockerfiles
   chmod +x start_agent_c.sh
   ```
3. Pull the latest Docker images:
   ```bash
   docker-compose -p agent_c pull
   ```
   This downloads updated Agent C components

4. Start Agent C normally:
   ```bash
   ./start_agent_c.sh
   ```

### Method 2: Future Updates with Git (Easier!)

For easier future updates, consider switching to Git:

#### One-Time Setup

1. Open Terminal
2. Remove your current agent_c folder:
   ```bash
   rm -rf ~/agent_c
   ```
3. Clone with Git instead:
   ```bash
   cd ~
   git clone https://github.com/centricconsulting/agent_c_framework.git agent_c
   ```

#### Future Updates (Much Simpler!)

1. Open Terminal
2. Update with one command:
   ```bash
   cd ~/agent_c
   git pull
   ```
3. Update Docker images:
   ```bash
   cd dockerfiles
   docker-compose -p agent_c pull
   ```
4. Restart Agent C:
   ```bash
   ./start_agent_c.sh
   ```

That's it! Much easier than downloading ZIPs.

### Checking Your Current Version

To see what version you're running:

1. Log into Agent C
2. Look at the bottom of the page for version info
3. Or check the GitHub repository for the latest release date

---

## Managing Custom Agents

One of Agent C's powerful features is the ability to create and save custom AI agents with specific personalities and capabilities.

### What Are Custom Agents?

Custom agents are AI assistants you design for specific tasks:
- A writing coach with your preferred style
- A research assistant for your field
- A coding helper for your programming language
- A creative brainstorming partner

### Where Custom Agents Live

Your custom agents are stored separately from Agent C's code:
- **Location**: `~/.agent_c/personas/`
- **Format**: Text files (YAML format)
- **Persistence**: They survive Agent C updates!

### Creating a Custom Agent

#### Method 1: Using the Web Interface

1. Log into Agent C
2. Click **"Options"** or **"Settings"**
3. Find **"Customize Persona Instructions"**
4. Write or modify the agent's instructions
5. Save with a memorable name

#### Method 2: Using Bobb the Steward

Bobb is a special agent that helps you create other agents:

1. Select **"Bobb the Steward"** from the persona dropdown
2. Tell Bobb what kind of agent you want:
   ```
   I need an agent that helps me write marketing emails.
   It should be friendly but professional.
   ```
3. Answer Bobb's questions about your needs
4. Bobb will create the agent for you
5. Save the new agent when prompted

### Viewing Your Custom Agents

To see all your custom agents:

1. Open Terminal
2. Type:
   ```bash
   ls ~/.agent_c/personas/
   ```
3. You'll see a list of your custom agent files

Or in Finder:
1. Press `Command + Shift + G`
2. Type: `~/.agent_c/personas`
3. Press Enter

### Backing Up Custom Agents

**Important**: Always backup your custom agents before updates!

#### Quick Backup

1. Open Terminal
2. Create a backup:
   ```bash
   cp -r ~/.agent_c/personas ~/Desktop/my_agents_backup
   ```
3. This saves all agents to your Desktop

#### Restore from Backup

1. Open Terminal
2. Restore your agents:
   ```bash
   cp -r ~/Desktop/my_agents_backup/* ~/.agent_c/personas/
   ```

### Sharing Custom Agents

You can share agents with colleagues:

#### To Export an Agent

1. Find the agent file in `~/.agent_c/personas/`
2. Copy it to share via email or cloud storage
3. It's just a text file - safe to share!

#### To Import an Agent

1. Get the agent file from your colleague
2. Open Terminal
3. Copy it to your personas folder:
   ```bash
   cp ~/Downloads/agent_name.yaml ~/.agent_c/personas/
   ```
4. Restart Agent C
5. The new agent appears in your dropdown menu

### Organizing Your Agents

As you create more agents:

1. **Name them clearly**: "Research_Assistant_Biology" not "Agent1"
2. **Add descriptions**: Include what they do in the agent's instructions
3. **Test regularly**: Make sure they still work after updates
4. **Delete unused ones**: Keep your list manageable

### Troubleshooting Custom Agents

#### Agent Doesn't Appear in Dropdown

**Solution**:
1. Check the file is in `~/.agent_c/personas/`
2. Restart Agent C completely
3. Make sure the file ends in `.yaml` or `.yml`

#### Agent Behaves Strangely

**Solution**:
1. Review the agent's instructions for errors
2. Try simplifying complex instructions
3. Test with a fresh conversation

#### Lost an Agent After Update

**Solution**:
1. Check your backup (you made one, right?)
2. Look in `~/.agent_c/personas/` - it might still be there
3. Check `~/Desktop/agent_c_backup/personas/` if you followed our backup steps

---

## Daily Use: Starting and Stopping Agent C

### Starting Agent C

1. Make sure Docker is running (whale icon in menu bar)
2. Open Terminal
3. Type:
   ```bash
   cd ~/agent_c/dockerfiles
   ./start_agent_c.sh
   ```
4. Wait for "Services are ready!"
5. Open browser to: http://localhost:5173

### Stopping Agent C

1. In Terminal, press `Control + C`
2. Type:
   ```bash
   docker-compose -p agent_c down
   ```
3. Press Enter

Or simply quit Docker Desktop (right-click whale icon → Quit Docker Desktop)

---

## Troubleshooting Common Issues

### "Command not found" in Terminal

**Problem**: Terminal says `cd: no such file or directory`

**Solution**: 
1. Make sure the agent_c folder is in your home directory
2. In Terminal, type `ls` to see available folders
3. Look for `agent_c` in the list

### Docker Won't Start

**Problem**: Docker Desktop won't open or crashes

**Solution**:
1. Restart your Mac
2. Open Docker Desktop from Applications
3. If it still fails, reinstall Docker Desktop

### "Port 5173 already in use"

**Problem**: Another program is using the same port

**Solution**:
1. Restart your Mac (easiest solution)
2. Or in Terminal: `lsof -i :5173` to find what's using it

### "Invalid API Key" Error

**Problem**: Agent C says your API key is invalid

**Solution**:
1. Make sure you copied the entire key (starts with `sk-`)
2. Check you have credits in your OpenAI account
3. Edit the config file:
   ```bash
   open ~/.agent_c/agent_c.config
   ```
4. Find the line with `OPENAI_API_KEY=` and update it

### Browser Shows "Cannot Connect"

**Problem**: http://localhost:5173 won't load

**Solution**:
1. Wait 2-3 minutes after starting - it takes time to initialize
2. Make sure Docker is running (check whale icon)
3. Try refreshing the browser (Command + R)
4. Check Terminal for error messages

### Out of Memory Errors

**Problem**: Docker says it's out of memory

**Solution**:
1. Click the Docker whale icon → Preferences → Resources
2. Increase Memory to at least 4GB
3. Click "Apply & restart"

---

## Tips for Success

### Best Practices

1. **Always start Docker first** before running Agent C
2. **Keep your API key secret** - never share it with anyone
3. **Monitor your usage** at https://platform.openai.com/usage
4. **Save important conversations** - Agent C can lose data if not properly shut down

### Working with Files

Agent C can access files in these folders on your Mac:
- Desktop
- Documents  
- Downloads

To have Agent C work with a file:
1. Put the file in one of these folders
2. Tell Agent C: "Please look at the file 'example.pdf' in my Documents folder"

### Getting Help

- **Agent C Issues**: Visit https://github.com/centricconsulting/agent_c_framework/issues
- **API/Billing Issues**: Contact OpenAI support
- **Docker Issues**: Visit Docker's help center

---

## Quick Reference Card

### Essential Commands

**Start Agent C:**
```bash
cd ~/agent_c/dockerfiles
./start_agent_c.sh
```

**Stop Agent C:**
```bash
docker-compose -p agent_c down
```

**Check Docker Status:**
Look for whale icon (🐳) in menu bar

**Edit Configuration:**
```bash
open ~/.agent_c/agent_c.config
```

### Important URLs

- **Agent C Interface**: http://localhost:5173
- **API Usage/Billing**: https://platform.openai.com/usage
- **Get Help**: https://github.com/centricconsulting/agent_c_framework/issues

### Default Login
- Username: `admin`
- Password: `changeme` (change immediately!)

---

## Next Steps

Once Agent C is running:

1. **Explore different personas** to find what works best for your needs
2. **Try enabling different tools** to expand capabilities
3. **Start with simple requests** and gradually try more complex tasks
4. **Join the community** for tips and support

---

*Congratulations! You've successfully set up Agent C on your Mac. Enjoy your new AI assistant!*