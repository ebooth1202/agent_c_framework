# Agent C Framework - Windows Setup Guide
*Complete Setup Guide for Windows Users*

---

## Introduction

Welcome! This guide will walk you through setting up the Agent C Framework on your Windows computer. We've designed this guide for complete beginners, so don't worry if you're not familiar with technical terms - we'll explain everything as we go.

**What you'll be setting up:**
- The Agent C Framework - a powerful AI assistant platform
- Version: Release 1.0 Pre-release

**Time required:** Approximately 30-45 minutes (depending on your internet speed)

---

## Step 1: Clone the Agent C Repository

### What is "cloning"?
Cloning means downloading a complete copy of the Agent C software from the internet to your computer. Think of it like downloading an app, but for developers.

### 1.1 Open Windows PowerShell

PowerShell is a command-line tool built into Windows that lets you control your computer using text commands.

**How to open PowerShell:**

1. Click the **Start** button (Windows logo in the bottom-left corner)
2. Type **"PowerShell"** in the search box
3. Click on **"Windows PowerShell"** (the blue icon) when it appears
4. A window with a blue background and white text will open

### 1.2 Navigate to Your Home Folder

When PowerShell opens, you might already be in your home folder, but let's make sure.

**Type this command and press Enter:**

```powershell
cd ~
```

**What this does:** The `cd` command means "change directory" (move to a different folder), and the `~` symbol is a shortcut for your home folder (usually something like `C:\Users\YourName`).

### 1.3 Clone the Repository

Now we'll download the Agent C Framework to your computer.

**Copy and paste this command into PowerShell, then press Enter:**

```powershell
git clone -b release_1-0-pre https://github.com/centricconsulting/agent_c_framework.git
```

**What this does:**
- `git clone` - Downloads a copy of the software
- `-b release_1-0-pre` - Specifies which version to download (the current release version)
- The URL is where the software is stored online (GitHub)

**What to expect:**
- You'll see text scrolling by showing the download progress
- Messages like "Receiving objects" and percentages
- **This takes 2-5 minutes** depending on your internet speed
- When complete, you'll see "Resolving deltas: 100%" and the command prompt will return

### 1.4 Verify the Download

Let's confirm that Agent C was downloaded successfully.

**Type this command and press Enter:**

```powershell
dir
```

**What to look for:**
- You should see a folder called `agent_c_framework` in the list
- If you see it, congratulations! You've successfully cloned the repository.

---

## Step 2: Navigate to the Use Agent C Folder

### 2.1 Enter the use_agent_c Directory

Now that we've downloaded Agent C, we need to navigate into a specific folder where we'll do the rest of our setup work.

**Type this command and press Enter:**

```powershell
cd use_agent_c
```

**What this does:** This moves you into the `use_agent_c` folder, which contains all the files and scripts you need to set up and run Agent C.

### 2.2 Confirm You're in the Right Place

Let's verify that you're now in the correct directory.

**Type this command and press Enter:**

```powershell
pwd
```

**What this does:** `pwd` stands for "print working directory" - it shows you exactly where you are in your computer's folder structure.

**What you should see:**
The output should show a path ending with `\use_agent_c`, something like:
```
C:\Users\YourName\use_agent_c
```

If you see this, you're in the right place! If not, try the `cd use_agent_c` command again.

---

## Step 3: Build the Agent C Containers

### 3.1 Run the Build Script

Now we're going to build the containers that Agent C needs to run. This is a crucial step that sets up all the necessary components.

**Type this command and press Enter:**

```powershell
.\scripts\build_containers.bat
```

**What this does:** This script downloads and builds all the Docker containers (think of them as self-contained environments) that Agent C needs to operate.

### 3.2 What to Expect

**⏰ This step takes TIME - be patient!**

- **Duration:** 15-20 minutes (or longer with slower internet connections)
- **What you'll see:** Lots of text scrolling by, showing download progress and build steps
- **Messages you might see:**
  - "Pulling image..."
  - "Downloading..."
  - Percentage progress bars
  - "Building..."
  - Various technical messages

**Important notes:**
- ☕ This is a great time to grab a coffee or snack!
- 🚫 **Do NOT close the PowerShell window** while this is running
- ✅ The script is working even if it looks like nothing is happening for a minute or two
- 📶 Make sure you have a stable internet connection

### 3.3 How to Know When It's Complete

The build is finished when:
- The scrolling text stops
- You see the command prompt again (usually ending with `>`)
- No more download or build messages appear

---

## Step 4: Start Agent C and Configure

### 4.1 Run the Start Script

Now that the containers are built, we're ready to start Agent C for the first time!

**Type this command and press Enter:**

```powershell
.\scripts\start_agent_c.bat
```

**What this does:** This script starts up the Agent C system and prepares it for first-time use.

### 4.2 What Happens During First Run

When you run this command for the first time, Agent C will:

1. **Create a configuration folder** in your home directory:
   - A new folder called `.agent_c` will be created at `C:\Users\YourName\.agent_c`
   - This folder will store:
     - Your configuration file
     - User database
     - Chat session index
     - Saved chat files
     - Any custom agents you create

2. **Open a text editor** (like Notepad) automatically
   - This is where you'll configure Agent C with your API keys and other settings

### 4.3 Configure Your API Keys

When the text editor opens, you'll see a configuration file with various settings.

**Important configuration items:**

- **API Keys:** This is where you'll paste your Anthropic API key (or other AI service keys)
- **Other settings:** Various configuration options that control how Agent C behaves

**What to do:**

1. **For now, you can leave the file as-is** if you don't have API keys yet
2. **To add an API key:**
   - Find the line for your API provider (e.g., `ANTHROPIC_API_KEY=`)
   - Paste your API key after the `=` sign
   - Example: `ANTHROPIC_API_KEY=sk-ant-your-key-here`
3. **⚠️ CRITICAL: Save the file** by pressing `Ctrl + S` (or File → Save)
4. **Close the editor**

**Note:** Don't worry if you don't have API keys right now - you can always add them later by editing the configuration file at `C:\Users\YourName\.agent_c\config` (or similar location).

### 4.4 Start Agent C Again

After you save and close the text editor, you'll be back at the PowerShell window.

**Type the start command again and press Enter:**

```powershell
.\scripts\start_agent_c.bat
```

**What to expect:**
- The script will run for a few seconds
- You'll see startup messages in PowerShell
- **The Agent C chat window will automatically launch in your default web browser**

**Success!** When you see the chat window open, Agent C is ready to use!

---

## Step 5: Log In to Agent C

### 5.1 The Login Screen

When the chat window opens in your browser, you'll see a login screen.

### 5.2 Enter Your Credentials

Use these default login credentials:

**Username:** `admin`  
**Password:** `changeme`

**Type these exactly as shown** (all lowercase) and click the login button.

### 5.3 You're In!

Once you log in, you'll see the Agent C chat interface. Congratulations - you've successfully set up Agent C!

---

## Next Steps

*[Additional sections will be added as we continue building this guide]*

---

*Guide in progress - More sections coming soon*
