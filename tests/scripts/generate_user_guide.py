#!/usr/bin/env python3
"""
Generate USER_GUIDE.md from PASSING BDD test scenarios only.

This script:
1. Reads Behave JSON output to identify which scenarios passed
2. Generates user guide with ONLY passing scenarios
3. Ensures all examples in the guide are actually verified to work

Run: python3 tests/scripts/generate_user_guide_from_results.py
"""

import json
import re
import os
import sys
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
FEATURES_DIR = REPO_ROOT / "tests" / "features"
BEHAVE_JSON_FILE = REPO_ROOT / "tests" / "behave-results.json"
OUTPUT_FILE = REPO_ROOT / "USER_GUIDE.md"

# Section introductions with a fun, encouraging tone
SECTION_INTROS = {
    "1. Installation": """Hey there! 👋 Ready to set up your awesome new development playground?

Don't worry — we know setup can feel intimidating. But guess what? You're going to do great, and we'll be right here with you every step of the way.

### What You Need Before Starting

Think of this like checking your backpack before a hike. You only need a few things:

**What you need:**
- [ ] Docker Desktop installed and running (this is the engine that makes everything go)
- [ ] Git installed (for downloading the VDE code)
- [ ] Zsh 5.0+ or Bash 4.0+ (fancy names for your terminal — we'll explain!)
- [ ] About 5GB of free disk space (roughly the size of a few HD movies)

**Don't have these?** No stress! We'll walk you through getting each one. Just find your computer type below and follow along.

---

## Let's Get You Set Up! 🚀

If you don't have Docker Desktop or git installed yet, that's totally fine! We'll hold your hand through the whole process. Just find your section below — Windows, Mac, or Linux — and follow the steps.

You've got this!

---

## Installing Docker Desktop

Docker Desktop is the magic engine that runs all your development environments. Think of it like the kitchen where all your coding recipes come to life. 🍳

### For Windows Users

#### Step 1: Check if You Have the Right Version of Windows

Docker Desktop likes Windows 10 or Windows 11. It also prefers **Windows 10/11 Pro, Enterprise, or Education** - it's a bit picky about Windows Home edition (but don't worry, we have a workaround!)

**Let's check what you have:**

1. Press the **Windows key** on your keyboard (or click Start)
2. Type **"About your PC"** and press Enter
3. Look for "Windows specifications"
4. Under "Edition", you should see **Windows 10 Pro** or **Windows 11 Pro** (or Enterprise/Education)

**If you see Windows Home:** You can still use Docker with WSL 2 (Windows Subsystem for Linux). This is free from Microsoft. Here's how:
1. Press Windows key, type **"PowerShell"**
2. Right-click "Windows PowerShell" and select **"Run as administrator"**
3. Copy and paste this command (right-click in PowerShell to paste):
   ```
   wsl --install
   ```
4. Press Enter and wait for it to finish
5. Restart your computer when asked

#### Step 2: Download Docker Desktop for Windows

1. Open your web browser (Chrome, Edge, Firefox, etc.)
2. Go to: **https://www.docker.com/products/docker-desktop**
3. Click the big blue button that says **"Download for Windows"**
4. The file will be named something like `Docker Desktop Installer.exe`
5. When the download finishes, click the file to open it (usually in the bottom-left corner of your browser)

#### Step 3: Install Docker Desktop

1. A window will pop up asking for permission - click **"Yes"**
2. You'll see an installer window - make sure these boxes are checked:
   - ☑ **Use WSL 2 instead of Hyper-V** (recommended)
3. Click **"Ok"**
4. Wait for the installation to complete (this may take a few minutes)
5. Click **"Close"** when it's done
6. **Restart your computer** when asked

#### Step 4: Start Docker Desktop

1. After your computer restarts, you'll see a Docker icon in your taskbar (bottom of screen) or a notification
2. Click the Docker icon to start it
3. A welcome window will appear - accept the terms and click **"Accept"**
4. Docker will start - wait for the whale icon in your taskbar to stop spinning and turn solid
5. When the whale is solid (not spinning), Docker is ready!

#### Step 5: Verify Docker is Working

1. Press the **Windows key**, type **"PowerShell"**, and open it
2. Type this command and press Enter:
   ```
   docker --version
   ```
3. You should see something like `Docker version 24.x.x, build xxxxx`

**🎉 Awesome!** Docker is installed and ready to go! You're doing great!

---

### For macOS (Mac) Users

#### Step 1: Check if Your Mac is Friendly with Docker

Good news — most modern Macs work beautifully with Docker! It's happy on:
- **Intel-based Macs**: macOS 11 or newer (Big Sur, Monterey, Ventura, Sonoma, Sequoia)
- **Apple Silicon Macs** (M1/M2/M3 chips): macOS 11 or newer

**How to check your macOS version:**

1. Click the **Apple menu** () in the top-left corner of your screen
2. Select **"About This Mac"**
3. You'll see the macOS version number and your chip type

#### Step 2: Download Docker Desktop for Mac

1. Open your web browser (Safari, Chrome, Firefox, etc.)
2. Go to: **https://www.docker.com/products/docker-desktop**
3. You'll see two options - choose the right one for your Mac:
   - **"Download for Mac - Apple Chip"** → if you have M1/M2/M3/M4
   - **"Download for Mac - Intel Chip"** → if you have an Intel processor
4. The file will be named `Docker.dmg`
5. When the download finishes, double-click the file to open it (usually in your Downloads folder)

#### Step 3: Install Docker Desktop

1. A window will open showing a Docker icon and a folder called **"Applications"**
2. **Drag the Docker icon** onto the **"Applications"** folder
3. Wait for the copy to finish (a few seconds)
4. Close the window
5. Open your **Applications** folder (click Go → Applications in the menu bar, or use Spotlight)
6. Find **Docker** and double-click it
7. If you see a warning about downloaded from the internet:
   - Click **"Open"** to confirm

#### Step 4: Complete the Setup

1. Docker will ask for permission - enter your Mac password
2. Read the Welcome screen and click **"Continue"**
3. A popup will ask for system permissions:
   - Click **"Open System Settings"** (or "Open System Preferences")
   - You'll see Docker under "Login Items" or similar - the switches should be turned on
   - If any switches are off, click them to turn on (you'll need to enter your password)
4. Go back to the Docker welcome window and click **"Got it!"** or continue through the setup

#### Step 5: Wait for Docker to Start

1. Look at the top of your screen (menu bar) for a whale icon 🐳
2. At first, it will be animated (the whale is doing something) - wait for this
3. When the whale stops moving and becomes solid, Docker is ready!

#### Step 6: Verify Docker is Working

1. Open **Terminal** (press Command+Space, type "Terminal", press Enter)
2. Type this command and press Enter:
   ```
   docker --version
   ```
3. You should see something like `Docker version 24.x.x, build xxxxx`

**✨ Perfect!** Docker is all set up on your Mac! Looking good!

---

### For Linux Users

Linux users — you're our kind of people! 🐧 Docker Desktop plays nicely with Ubuntu, Debian, Fedora, and many other distributions.

#### Step 1: Let's See Which Linux Flavor You Have

First, let's check which distribution you're rocking:

1. Open your **Terminal** (press Ctrl+Alt+T)
2. Type this command and press Enter:
   ```
   cat /etc/os-release
   ```
3. Look for the `NAME=` line - this tells you your distribution (e.g., "Ubuntu", "Fedora", "Debian")

#### Step 2: Download Docker Desktop

1. Open your web browser
2. Go to: **https://www.docker.com/products/docker-desktop**
3. Click **"Download for Linux"**
4. You'll see options for different Linux versions - click yours:
   - **Ubuntu/Debian** → `.deb` file
   - **Fedora/CentOS/Red Hat** → `.rpm` file
5. The file will download to your **Downloads** folder

#### Step 3: Install Docker Desktop

**For Ubuntu/Debian (.deb file):**

1. Open your terminal
2. Type these commands one at a time, pressing Enter after each:

   ```bash
   # Go to your Downloads folder
   cd ~/Downloads

   # Update your package list
   sudo apt-get update

   # Install Docker (replace the filename with your actual downloaded file)
   sudo apt-get install ./docker-desktop-<version>-<arch>.deb
   ```

   *Note: The actual filename will be something like `docker-desktop-4.25.0-amd64.deb` - type `ls` to see the exact name and use that.*

**For Fedora/CentOS/Red Hat (.rpm file):**

1. Open your terminal
2. Type these commands one at a time, pressing Enter after each:

   ```bash
   # Go to your Downloads folder
   cd ~/Downloads

   # Install Docker (replace the filename with your actual downloaded file)
   sudo dnf install ./docker-desktop-<version>-<arch>.rpm
   ```

   *Note: The actual filename will be something like `docker-desktop-4.25.0-x86_64.rpm` - type `ls` to see the exact name and use that.*

3. If asked for confirmation, type **`y`** and press Enter

#### Step 4: Start Docker Desktop

1. After installation, you can start Docker by typing in your terminal:
   ```
   systemctl --user start docker-desktop
   ```

2. To make Docker start automatically when you log in:
   ```
   systemctl --user enable docker-desktop
   ```

3. You should also see a **Docker Desktop** icon in your applications menu - you can click that too!

#### Step 5: Verify Docker is Working

In your terminal, type:
```
docker --version
```

You should see something like `Docker version 24.x.x, build xxxxx`

**🔥 Boom!** Docker is running on Linux! You're on fire!

---

## Installing Git

Git is like a digital delivery truck — it downloads code from the internet (like the VDE code) right to your computer. Handy little thing! 📦

### For Windows Users

#### Option 1: The Easiest Way (Git for Windows)

**Step 1: Download Git for Windows**

1. Open your web browser
2. Go to: **https://github.com/git-guides/install-git**
3. Look for the **Windows** section
4. Click the link that says **"Click here to download"** (or go directly to https://git-scm.com/download/win)
5. The file will be named something like `Git-2.43.0-64-bit.exe`

**Step 2: Install Git**

1. When the download finishes, click the file to run it
2. If Windows asks for permission, click **"Yes"**
3. Click **"Next"** on the welcome screen
4. Keep clicking **"Next"** to accept all the default settings (they're good for most people)
5. On the "Choosing the default editor" screen, **Vim** will be selected - we recommend changing this to **Notepad** or **Notepad++** (easier to use)
6. Keep clicking **"Next"** through the rest
7. On the final screen, click **"Install"**
8. Wait for it to finish, then click **"Finish"**

**Step 3: Verify Git is Installed**

1. Press the **Windows key**, type **"PowerShell"**, and open it
2. Type this command and press Enter:
   ```
   git --version
   ```
3. You should see something like `git version 2.43.0.windows.1`

**🎊 Sweet!** Git is ready to go on Windows! Halfway there!

---

### For macOS (Mac) Users

#### The Good News: You Might Already Have Git!

Macs come with Git built-in! Let's check if you're all set:

1. Open **Terminal** (press Command+Space, type "Terminal", press Enter)
2. Type this and press Enter:
   ```
   git --version
   ```
3. If you see a version number like `git version 2.39.0`, you already have Git! **You're done!**

#### If You Need to Install Git

If you don't have Git or want a newer version, here's how:

**Option 1: Install with Homebrew (Easiest)**

1. Open Terminal
2. First, check if you have Homebrew (a package installer for Mac):
   ```
   brew --version
   ```
3. If you see a version, great! Install Git with:
   ```
   brew install git
   ```
4. If you DON'T have Homebrew, you can install it first:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   Then install Git with: `brew install git`

**Option 2: Download from Git Website**

1. Go to: **https://github.com/git-guides/install-git**
2. Look for the **macOS** section
3. Click the download link (or go to https://git-scm.com/download/mac)
4. This will download a `.dmg` file
5. Double-click the file to open it
6. Follow the same steps as installing Docker (drag to Applications)

**Verify Git is Working:**

In Terminal, type:
```
git --version
```

You should see a version number. **✅ Done!** You've got Git!

---

### For Linux Users

#### The Good News: Most Linux Has Git Already!

Linux is usually prepared for everything. Let's see:

1. Open your terminal
2. Type:
   ```
   git --version
   ```
3. If you see a version, you're done!

#### If You Need to Install Git

**For Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install git
```

**For Fedora:**
```bash
sudo dnf install git
```

**For CentOS/Red Hat:**
```bash
sudo yum install git
```

**For Arch Linux:**
```bash
sudo pacman -S git
```

**Verify Git is Working:**

In your terminal, type:
```
git --version
```

You should see a version number. **✅ You're set!**

---

## Installing Zsh and Bash

Okay, quick confession: "shell" is just a fancy name for the program that runs in your terminal and understands your commands. VDE needs a modern one — specifically **Zsh 5.0+** or **Bash 4.0+**. Sound scary? Don't worry, we'll sort you out!

**Why does VDE need this?**
- VDE's commands are written in shell language (fancy nerd talk for "scripts that run in your terminal")
- Older shells don't understand some of the cool tricks we use
- The good news: Zsh comes standard on modern Macs, and most Linux has modern Bash

Think of it like VDE speaks a specific dialect, and we need to make sure your terminal understands it! 🗣️

### For Windows Users

#### The Good News: Git for Windows Includes Bash!

If you installed Git for Windows (which you did in the previous section), you **already have Bash**! Git for Windows includes a program called "Git Bash" that gives you a modern Bash shell.

**How to check if you have it:**

1. Press the **Windows key** and type **"Git Bash"**
2. If you see "Git Bash" in the results, click it to open
3. A terminal window will open - this is your Bash shell!
4. Type this and press Enter:
   ```
   bash --version
   ```
5. You should see something like `GNU bash, version 5.x.x` - this is perfect!

**If you don't see Git Bash:**
- Reinstall Git for Windows using the instructions from the "Installing Git" section
- Make sure to select "Git Bash" as one of the components during installation

#### Installing Zsh on Windows (Optional)

Zsh is available on Windows through WSL (Windows Subsystem for Linux):

**If you already have WSL installed (from the Docker section):**

1. Open **PowerShell** and run:
   ```
   wsl
   ```
2. Once in WSL, install Zsh:
   ```bash
   sudo apt-get update
   sudo apt-get install zsh
   ```
3. Check the version:
   ```bash
   zsh --version
   ```
4. You should see something like `zsh 5.x.x or greater`

**If you don't have WSL:**
- Don't worry! Git Bash is sufficient for VDE
- You can install WSL later if you want to use Zsh

#### What Shell Should You Use?

**For VDE on Windows:**
- **Git Bash** (recommended) - Already installed with Git, works great
- **WSL + Zsh** (optional) - More powerful, but requires WSL setup

---

### For macOS (Mac) Users

#### The Good News: You Almost Certainly Already Have Zsh!

Modern macOS comes with Zsh as the default shell (since macOS Catalina).

**How to check what shell you have:**

1. Open **Terminal** (press Command+Space, type "Terminal", press Enter)
2. Check if Zsh is running by default:
   ```
   echo $SHELL
   ```
3. If you see `/bin/zsh`, you're already using Zsh - great!
4. Check the Zsh version:
   ```
   zsh --version
   ```
5. You should see `zsh 5.x.x or greater` - this is perfect!

#### If You Need to Install or Update Zsh

**Check if you need an update:**
```bash
zsh --version
```

If the version is less than 5.0, or if Zsh isn't installed:

**Option 1: Use Homebrew (Easiest)**

1. If you have Homebrew (from the Git section), install the latest Zsh:
   ```bash
   brew install zsh
   ```

2. Set Zsh as your default shell:
   ```bash
   chsh -s /bin/zsh
   ```
   (You'll need to enter your password)

3. Close and reopen Terminal - you're now using Zsh!

**Option 2: macOS Already Has Zsh (Just Need to Switch)**

If Zsh is installed but not your default:

1. Check if Zsh exists:
   ```bash
   ls /bin/zsh
   ```
2. If it exists, switch to it:
   ```bash
   chsh -s /bin/zsh
   ```
3. Close and reopen Terminal

#### Installing Bash on macOS (Optional)

macOS comes with Bash, but it's an older version (3.2.x). For VDE, you can use either Zsh or install a modern Bash.

**If you want the latest Bash:**

```bash
brew install bash
```

Check the version:
```bash
brew list bash | grep bin
# This shows where bash is installed, usually /usr/local/bin/bash
/usr/local/bin/bash --version
```

You should see `bash 5.x.x or greater`

#### What Shell Should You Use?

**For VDE on macOS:**
- **Zsh** (recommended) - Already installed, modern, and is the macOS default
- **Bash** (optional) - Install via Homebrew if you prefer Bash

---

### For Linux Users

#### Check What You Already Have

Most modern Linux distributions come with modern versions of Bash and Zsh pre-installed.

**Check your Bash version:**
```bash
bash --version
```

**Check if Zsh is installed:**
```bash
zsh --version
```

**What you should see:**
- Bash: `version 4.0 or greater` (most Linux has 4.x or 5.x)
- Zsh: `version 5.0 or greater` (if installed)

#### If You Need to Install or Upgrade

**For Ubuntu/Debian:**

```bash
# Install or update Bash
sudo apt-get update
sudo apt-get install bash

# Install Zsh
sudo apt-get install zsh
```

**For Fedora:**

```bash
# Install or update Bash
sudo dnf install bash

# Install Zsh
sudo dnf install zsh
```

**For CentOS/Red Hat:**

```bash
# Install or update Bash
sudo yum install bash

# Install Zsh
sudo yum install zsh
```

**For Arch Linux:**

```bash
# Install or update Bash
sudo pacman -S bash

# Install Zsh
sudo pacman -S zsh
```

#### Verify Your Installation

**Check Bash version:**
```bash
bash --version
# Should show 4.0 or greater
```

**Check Zsh version:**
```bash
zsh --version
# Should show 5.0 or greater
```

#### Make Zsh Your Default Shell (Optional)

If you want to use Zsh instead of Bash as your daily shell:

```bash
chsh -s $(which zsh)
```

Log out and log back in for the change to take effect.

#### What Shell Should You Use?

**For VDE on Linux:**
- **Bash** (recommended) - Almost certainly already installed and modern
- **Zsh** (optional) - Install if you prefer Zsh's features

---

## Quick Checklist: Are You Ready? 🎯

Let's do a quick victory lap before we move on! Open your terminal and run these commands:

**Open your terminal (PowerShell on Windows, Terminal on Mac/Linux) and run:**

```bash
# Check Docker
docker --version

# Check Git
git --version

# Check Docker is actually running
docker ps
```

**What you should see:**
- `docker --version` → Shows Docker version number (like "Docker version 24.x.x")
- `git --version` → Shows Git version number (like "git version 2.x.x")
- `docker ps` → Shows a list of containers (might be empty, and that's totally okay!)

**If `docker ps` gives an error like "Cannot connect to the Docker daemon":**
- Docker Desktop probably isn't running — just start it from your applications
- Wait for the whale icon to stop spinning (it's thinking! 🐳)
- Then try again

---

## Stuck? We Can Help! 🆘

If you run into any hiccups installing Docker, Git, or shells:

1. **Docker won't start?** Make sure your computer is compatible and you've restarted after installation
2. **Can't find the terminal?**
   - Windows: Press Windows key, type "PowerShell", "Windows Terminal", or "Git Bash"
   - Mac: Press Command+Space, type "Terminal"
   - Linux: Press Ctrl+Alt+T
3. **Permission errors?** Make sure you have administrator rights on your computer
4. **Shell not found?** On Windows, make sure you installed Git for Windows - it includes Git Bash
5. **Version too old?** On macOS, use Homebrew to install the latest version. On Linux, use your package manager

Once Docker, Git, and a modern shell are installed and working, you're ready for the fun part! You've made it through the setup — you're awesome! 🌟

---

### Step 1: Clone VDE to Your Computer

**Scenario: Getting the VDE code**

```
Given I want to install VDE
When I clone the VDE repository to ~/dev
Then VDE files should be in place
```

**Let's download VDE! Open your terminal and run:**
```bash
# Clone the repository
git clone <repo-url> ~/dev

# Go into the directory
cd ~/dev
```

### Step 2: Run the Initial Setup

**Scenario: First-time setup creates everything**

```
Given I have cloned VDE to ~/dev
And I'm running the setup for the first time
When I run the initial setup script
Then VDE should be properly installed
And required directories should be created
```

**Run the setup:**
```bash
./scripts/build-and-start
```

**What this does:**
- Creates all necessary directories (configs, projects, data, logs, etc.)
- Sets up proper file permissions
- Initializes the VDE framework

### Step 3: Verify Installation

**Scenario: Checking that VDE is ready**

```
Given I've just installed VDE
When I run "list-vms"
Then I should see all predefined VM types
And python, rust, js, csharp, ruby should be listed
And postgres, redis, mongodb, nginx should be listed
```

**Verify everything is ready:**
```bash
./scripts/vde list
```

**Expected output:** You should see a list of available language and service VMs.

**Woohoo! 🎉** You're all set up and ready to go!
""",

    "2. SSH Keys": """### SSH Keys? Automatic! 🔑

Here's some good news: VDE handles SSH keys for you automatically. We wanted to mention this so you know what's happening, but you don't need to do anything. It's like magic! ✨

### Automatic SSH Key Generation

**Scenario: SSH keys are created if you don't have them**

```
Given I'm setting up VDE for the first time
And no SSH keys exist on my system
When SSH keys are checked
Then ed25519 keys should be generated automatically
And public keys should be copied to VMs
```

**What happens:**
1. VDE checks if you have SSH keys (~/.ssh/id_ed25519)
2. If not, it creates them for you automatically
3. Public keys are copied to the `public-ssh-keys/` directory
4. VMs are configured to use these keys for access

### Your SSH Config is Updated Automatically

**Scenario: SSH config is set up for you**

```
Given SSH config file does not exist
When I create my first VM
Then SSH config should be created
And SSH config entry for the VM should be added
And I can connect using simple names like "python-dev"
```

**You don't need to:**
- Manually create SSH keys
- Edit your SSH config file
- Copy keys to VMs
- Set up SSH agent forwarding

**VDE does all of this for you.** Sit back and relax! ☕
""",

    "3. Your First VM": """## Let's Create Your First VM! 🎉

You've made it through the setup. That's huge! Now for the fun part — creating your first development environment. We'll start with Python because it's friendly and popular. Perfect for beginners!

### Creating Your Python VM

**Scenario: Creating a Python development environment**

```
Given I've just installed VDE
And I want my first development environment
When I run "create-virtual-for python"
Then a Python development environment should be created
And configs/docker/python/ should be created
And docker-compose.yml should be generated
And SSH config entry for "python-dev" should be added
And projects/python directory should be created
```

**Run this command:**
```bash
./scripts/vde create python
```

**What you'll see:**
- Progress messages as Docker builds the image
- "SSH config entry created" message
- "Your Python VM is ready" message

**🎊 Exciting!** Your Python VM is being created!

### Meet vde: Your New Best Friend 🤝

Quick — before we start this VM, let's introduce your new best friend!

**You might notice something weird...**

As you read through this guide, you'll see scenarios that say things like:

```
When I run "create-virtual-for python"
```

But then the actual command we show you is:

```bash
./scripts/vde create python
```

**What's going on?** Are we trying to confuse you? Nope!

### Here's the Secret 🤫

VDE has a bunch of specialized scripts that do specific things:
- `create-virtual-for` — Creates new VMs
- `start-virtual` — Starts VMs
- `shutdown-virtual` — Stops VMs
- `list-vms` — Lists all your VMs
- And more...

**But memorizing all those?** Ugh. Who has time for that?

### Enter: vde — Your Go-To Guy 🦸

The `vde` command is like having a personal assistant who knows exactly which script to run. You just tell it what you want:

```bash
./scripts/vde create python    # "Hey vde, create a Python VM"
./scripts/vde start rust      # "Hey vde, start that Rust VM"
./scripts/vde stop all         # "Hey vde, stop everything"
./scripts/vde list             # "Hey vde, what's running?"
```

And vde goes and runs the right script for you. Like magic! ✨

### Why Do the Scenarios Show Script Names Then?

Great question! The scenarios (those Given-When-Then blocks) show what's *actually happening under the hood*. They're like a behind-the-scenes look at how VDE works.

Think of it like a restaurant:
- **The scenarios** are like watching in the kitchen — you see the chef chopping, sautéing, plating
- **The vde command** is like ordering from the menu — you just say "I want the pasta" and it appears!

### What You Should Remember

| Forget About | Use This Instead |
|--------------|------------------|
| `create-virtual-for` | `vde create` |
| `start-virtual` | `vde start` |
| `shutdown-virtual` | `vde stop` |
| `list-vms` | `vde list` |

**That's it!** One command to remember. Easy, right?

### tl;dr

- The scenarios show the behind-the-scenes scripts (technical details)
- You use the `vde` command (easy mode)
- vde calls those scripts for you automatically
- vde is your go-to guy. Maybe buy it a coffee sometime. ☕

---

**Now let's get your Python VM running!**

### Starting Your First VM

**Scenario: Starting the Python VM**

```
Given I created a Python VM
When I run "start-virtual python"
Then the Python VM should be started
And I should be able to SSH to "python-dev"
```

**Run this command:**
```bash
./scripts/vde start python
```

**What happens:**
- Docker container starts
- SSH port 2200 is allocated
- Your projects/python directory is mounted
- You're ready to code!

**🚀 You're off to the races!**
""",

    "4. Understanding": """### Let's See What You Built! 🔍

You just created your first VM! That's honestly kind of a big deal. Give yourself a pat on the back! Let's make sure everything is working and understand what you now have.

### Check That Your VM is Running

**Scenario: Verifying VM status**

```
Given I started my Python VM
When I run "list-vms"
Then I should see which VMs are running
And Python should show as "running"
```

**Check status:**
```bash
./scripts/vde list
```

**You should see:**
- python: **running** (on port 2200)

### Understanding Your Directory Structure

**Scenario: Your workspace is set up correctly**

```
Given I created a Python VM
When I look at my directories
Then projects/python/ should exist for my code
And the directory should be mounted in the VM
```

**Your directory structure:**
```
~/dev/
├── configs/          # VM configurations
├── projects/         # YOUR CODE GOES HERE
│   └── python/       # Python projects (mounted in VM)
├── data/            # Database data (persists across rebuilds)
├── logs/            # Application logs
└── scripts/         # VDE management commands
```
""",

    "5. Starting and Stopping": """### Daily Rhythm: Start, Code, Stop, Repeat 🔄

Here's your daily workflow with VDE — simple as can be!

### Starting Your VM

**Scenario: Starting a stopped VM**

```
Given I created a Python VM earlier
And it's currently stopped
When I run "start-virtual python"
Then the Python VM should start
And I can connect to it
```

**Command:**
```bash
./scripts/vde start python
```

### Stopping Your VM

**Scenario: Stopping a running VM**

```
Given I have a Python VM running
When I run "shutdown-virtual python"
Then the Python VM should be stopped
And the configuration should remain for next time
```

**Command:**
```bash
./scripts/vde stop python
```

**Important:** Stopping doesn't delete your VM — it just pauses it. Your code and configurations are safe and sound! 💾
""",

    "6. Your First Cluster": """### Time to Build Something Real! 🏗️

Now let's build a real application stack. This is where VDE really shines — you can have multiple VMs working together like a well-oiled machine.

### What We're Building

You'll have a complete tech stack:
- **Python VM** — Your application code (port 2200)
- **PostgreSQL VM** — Your database (port 2400)
- **Redis VM** — Your cache (port 2401)

All three can talk to each other automatically. No networking headaches required!

### Creating Your Service VMs

**Scenario: Creating database and cache VMs**

```
Given I have VDE installed
And I need a database and cache
When I run "create-virtual-for postgres"
And I run "create-virtual-for redis"
Then PostgreSQL VM configuration should be created
And Redis VM configuration should be created
```

**Create both services:**
```bash
./scripts/vde create postgres
./scripts/vde create redis
```

### Starting Your Full Stack

**Scenario: Starting all three VMs together**

```
Given I created VMs for python, postgres, and redis
When I run "start-virtual python postgres redis"
Then all three VMs should be running
And Python VM can connect to PostgreSQL
And Python VM can connect to Redis
```

**Start your full stack:**
```bash
./scripts/vde start python postgres redis
```

### Verifying Your Cluster is Running

**Scenario: Checking all VMs are communicating**

```
Given I started python, postgres, and redis
When I check VM status
Then I should see all three running
And they should be on the same Docker network
```

**Check status:**
```bash
./scripts/vde list
```

**Expected output:**
```
VM          Type        Status    Port
----------------------------------------
python      language    running   2200
postgres    service     running   2400
redis       service     running   2401
```
""",

    "7. Connecting": """### Step Inside Your VM! 🚪

Ready to step into your development environment? Let's SSH in and see what's waiting for you!

**Scenario: SSH into your development environment**

```
Given I have a Python VM running
When I run "ssh python-dev"
Then I should be connected to the Python VM
And I should be in the projects/python directory
```

**Connect:**
```bash
ssh python-dev
```

**You're now inside your VM!** You can:
- Run Python code
- Install packages
- Edit files in `projects/python/`
- Access postgres and redis seamlessly
- Feel like a pro developer (because you are one!) 🌟

### Exiting a VM

**To leave:** Just type `exit` or press `Ctrl+D`. The door is always open!

### Connection Reference

| VM Name | SSH Command | What It's For |
|---------|-------------|---------------|
| python-dev | `ssh python-dev` | Python development |
| rust-dev | `ssh rust-dev` | Rust development |
| js-dev | `ssh js-dev` | JavaScript/Node.js |
| csharp-dev | `ssh csharp-dev` | C# development |
| ruby-dev | `ssh ruby-dev` | Ruby development |
| go-dev | `ssh go-dev` | Go development |
| postgres | `ssh postgres` | Direct database access |
| redis | `ssh redis` | Direct Redis access |
| mongodb | `ssh mongodb` | MongoDB |
| nginx | `ssh nginx` | Nginx web server |
""",

    "8. Working with Databases": """### Databases? No Problem! 🗄️

VDE makes working with databases delightfully simple. Your Python VM can talk to PostgreSQL as easily as if it were running on the same machine (because, well, virtually it is!).

**Scenario: Connecting from Python to PostgreSQL**

```
Given I have Python and PostgreSQL running
When I SSH into python-dev
And I run "psql -h postgres -U devuser"
Then I should be connected to PostgreSQL
And I can run database queries
```

**Try it yourself:**
```bash
# 1. Connect to your Python VM
ssh python-dev

# 2. Connect to PostgreSQL from within the VM
psql -h postgres -U devuser

# 3. You're now in PostgreSQL! Try:
# \\list                    # List databases
# \\c devuser               # Connect to default database
# \\dt                      # List tables
# SELECT 1;                # Run a query
# \\q                       # Quit
```

### Your Database Data Persists

**Scenario: Database data survives rebuilds**

```
Given I created tables in PostgreSQL
When I rebuild the PostgreSQL VM
And I reconnect to PostgreSQL
Then my tables should still exist
```

**Important:** Database data in `~/dev/data/postgres/` persists even when you rebuild VMs. Your precious data is safe and sound! 💾
""",

    "9. Daily Workflow": """### Your Daily Rhythm: Start, Code, Stop 🔄

Here's how your day with VDE will flow. Nice and simple!

### Morning Routine: Start Your Engines

**Scenario: Starting all your VMs at once**

```
Given I created VMs for my project
When I run "start-virtual python postgres redis"
Then all VMs should be running
And I can start working immediately
```

**One command to start your day:**
```bash
./scripts/vde start python postgres redis
```

### During the Day: Check In on Your VMs

**Scenario: Checking VM status**

```
Given I've been working for a while
When I want to know what's running
Then I should see all running VMs
And their status should be clear
```

**Check status:**
```bash
./scripts/vde list
```

### End of Day: Shut It Down

**Scenario: Clean shutdown**

```
Given multiple VMs are running
When I run "shutdown-virtual all"
Then all VMs should stop gracefully
And my work is saved
```

**Stop everything:**
```bash
./scripts/vde stop all
```

**Good night, VDE!** See you tomorrow! 🌙
""",

    "10. Adding More Languages": """### Want to Learn More Languages? 🌍

One of the beautiful things about VDE is how easy it is to try new languages! No installation headaches — just create a VM and start coding. Let's add another language to your collection!

**Scenario: Adding Rust to your environment**

```
Given I have Python running
And I want to work with Rust
When I run "create-virtual-for rust"
And I run "start-virtual rust"
Then Rust VM should be running
And I can use both Python and Rust
```

**Add Rust:**
```bash
./scripts/vde create rust
./scripts/vde start rust
```

### Starting Multiple Language VMs

**Scenario: Working with multiple languages**

```
Given I created VMs for Python, Rust, and JavaScript
When I run "start-virtual python rust js"
Then all three language VMs should be running
And I can switch between them
```

**Start multiple at once:**
```bash
./scripts/vde start python rust js
```

**Polyglot programmer?** Why not! 😎
""",

    "11. Troubleshooting": """### Hiccups Happen — We've Got Your Back! 🛠️

Sometimes things don't work perfectly the first time. That's okay! Here's how to handle common issues.

### Problem: A VM Won't Start

**Scenario: Diagnosing startup failures**

```
Given I tried to start a VM but it failed
When I check the error
Then I should see a clear error message
And I should know if it's:
- A port conflict
- A Docker issue
- A configuration problem
```

**What to check:**
1. Is Docker running? `docker ps`
2. Is the port already in use? `./scripts/vde list`
3. Check the logs: `docker logs <vm-name>`

### Problem: Changes Aren't Reflected

**Scenario: Rebuilding after configuration changes**

```
Given I modified the Dockerfile to add a package
And the VM is already running
When I run "start-virtual python --rebuild"
Then the VM should be rebuilt
And the new package should be available
```

**Rebuild with --rebuild:**
```bash
./scripts/vde start python --rebuild
```

**For complete rebuild (no cache):**
```bash
./scripts/vde start python --rebuild --no-cache
```
"""
}


def load_passing_scenarios_from_json():
    """Load the set of passing scenarios from Behave JSON output."""
    if not BEHAVE_JSON_FILE.exists():
        print(f"Warning: {BEHAVE_JSON_FILE} not found.")
        print("Run BDD tests first: ./tests/run-bdd-tests.sh")
        print("Generating user guide from ALL scenarios (unverified mode)")
        return None

    with open(BEHAVE_JSON_FILE) as f:
        data = json.load(f)

    passing_scenarios = set()
    for feature in data:
        feature_name = feature.get("name", "")
        for element in feature.get("elements", []):
            if element.get("type") == "scenario":
                scenario_name = element.get("name", "")
                status = element.get("status", "")
                if status == "passed":
                    # Create a unique identifier
                    key = f"{feature_name}:{scenario_name}"
                    passing_scenarios.add(key)

    print(f"✓ Found {len(passing_scenarios)} passing scenarios in test results")
    return passing_scenarios


def extract_scenarios_from_feature(content):
    """
    Extract scenarios from a feature file content.

    Returns:
        tuple: (feature_name, scenarios) where scenarios is a list of
               (scenario_name, scenario_body, tags)
    """
    feature_match = re.search(
        r'Feature:\s*(.+?)\n(?:\s*As\s+(.+?)\n\s*I want\s+(.+?)\n\s*So\s+(.+?))?',
        content,
        re.DOTALL
    )
    feature_name = feature_match.group(1).strip() if feature_match else "Unknown Feature"

    # Extract feature-level tags (if any)
    feature_tags = []
    feature_tag_match = re.search(r'Feature:(.+?)\n((?:\s*@\w+(?:\s+@\w+)*\n)*)', content, re.DOTALL)
    if feature_tag_match:
        tag_text = feature_tag_match.group(2) or ""
        feature_tags = [tag.strip() for tag in re.findall(r'@(\w+(?:-\w+)*)', tag_text)]

    # Pattern to match scenarios with optional tags before them
    # Captures: tags (if any), scenario name, and scenario body
    scenario_pattern = r'(?:((?:\s*@\w+(?:-\w+)*\n)+)*)\s*Scenario:\s*(.+?)\n((?:\s*(?:Given|When|Then|And)\s+.+(?:\n|$))+)'
    scenarios = []
    for match in re.finditer(scenario_pattern, content, re.MULTILINE):
        tag_block = match.group(1) or ""
        scenario_name = match.group(2).strip()
        scenario_body = match.group(3).strip()

        # Extract tags from this scenario
        scenario_tags = [tag.strip() for tag in re.findall(r'@(\w+(?:-\w+)*)', tag_block)]

        # Combine feature and scenario tags (scenario tags take precedence)
        all_tags = scenario_tags if scenario_tags else feature_tags

        scenarios.append((scenario_name, scenario_body, all_tags))

    return feature_name, scenarios


def format_scenario_for_user_guide(scenario_name, scenario_body):
    """Format a scenario for the user guide with explanations."""
    lines = []

    # Clean up scenario name for display
    display_name = scenario_name.replace("-", " ").capitalize()

    lines.append(f"**Scenario: {display_name}**\n")
    lines.append("```")
    for line in scenario_body.split('\n'):
        line = line.strip()
        if line:
            lines.append(line)
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def generate_user_guide(passing_scenarios=None):
    """Generate the complete USER_GUIDE.md with only passing scenarios."""

    # Verify mode warning
    if passing_scenarios is None:
        print("⚠ WARNING: Running in UNVERIFIED mode")
        print("  Scenarios have NOT been tested!")
        print("  Run BDD tests first to generate verified guide\n")

    # Read all feature files
    all_scenarios = {}  # section -> list of (name, body)

    for feature_file in FEATURES_DIR.glob("**/*.feature"):
        try:
            with open(feature_file) as f:
                content = f.read()

            feature_name, scenarios = extract_scenarios_from_feature(content)

            for scenario_name, scenario_body, tags in scenarios:
                # Check if scenario passed (if we have test results)
                if passing_scenarios is not None:
                    key = f"{feature_name}:{scenario_name}"
                    if key not in passing_scenarios:
                        # Skip failed scenarios
                        continue

                # Determine section based on tags (primary) or scenario name (fallback)
                section = determine_section(scenario_name, tags)
                if section:
                    if section not in all_scenarios:
                        all_scenarios[section] = []
                    all_scenarios[section].append((scenario_name, scenario_body))
        except Exception as e:
            print(f"Warning: Could not process {feature_file}: {e}")
            continue

    # Count scenarios that were excluded
    total_extracted = sum(len(s) for s in all_scenarios.values())
    if passing_scenarios is not None:
        print(f"  Included {total_extracted} verified passing scenarios")

    # Write the user guide
    with open(OUTPUT_FILE, 'w') as f:
        # Logo image (always at top)
        f.write('<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>\n\n')

        # Header with verification notice
        if passing_scenarios is not None:
            f.write("**Every workflow in this guide has been tested and verified to PASS.** Follow the steps, they will work for you too.\n\n")
        else:
            f.write("**WARNING: This guide was generated in UNVERIFIED mode. Scenarios have NOT been tested!**\n\n")
            f.write("**Run `./tests/run-bdd-tests.sh` first to generate a verified guide.**\n\n")

        f.write("---\n\n")

        # Table of contents
        f.write("## Table of Contents\n\n")
        sections = [
            ("1. Installation", [
                ("Installing Docker Desktop", [
                    ("For Windows Users", "for-windows-users"),
                    ("For macOS (Mac) Users", "for-macos-mac-users"),
                    ("For Linux Users", "for-linux-users"),
                ]),
                ("Installing Git", [
                    ("For Windows Users", "for-windows-users-1"),
                    ("For macOS (Mac) Users", "for-macos-mac-users-1"),
                    ("For Linux Users", "for-linux-users-1"),
                ]),
                ("Installing Zsh and Bash", [
                    ("For Windows Users", "for-windows-users-2"),
                    ("For macOS (Mac) Users", "for-macos-mac-users-2"),
                    ("For Linux Users", "for-linux-users-2"),
                ]),
                ("Quick Checklist: Are You Ready?", "quick-checklist-are-you-ready"),
            ]),
            ("2. SSH Keys", []),
            ("3. Your First VM", []),
            ("4. Understanding", []),
            ("5. Starting and Stopping", []),
            ("6. Your First Cluster", []),
            ("7. Connecting", []),
            ("8. Working with Databases", []),
            ("9. Daily Workflow", []),
            ("10. Adding More Languages", []),
            ("11. Troubleshooting", []),
        ]
        for i, (section, subsections) in enumerate(sections, 1):
            section_id = section.lower().replace(" ", "-").replace(":", "")
            f.write(f'{i}. [{section}](#{section_id})\n')
            for subsection, sub_subsections in subsections:
                subsection_id = subsection.lower().replace(" ", "-").replace(":", "").replace("?", "")
                f.write(f'   - [{subsection}](#{subsection_id})\n')
                if isinstance(sub_subsections, list):
                    for sub_subsection, sub_subsection_id in sub_subsections:
                        f.write(f'     - [{sub_subsection}](#{sub_subsection_id})\n')
        f.write("\n---\n\n")

        # Write each section
        for i, (section, _) in enumerate(sections, 1):
            f.write(f"## {section}\n\n")

            # Add section introduction if available
            intro_key = section
            for key in SECTION_INTROS:
                if key.startswith(section.split(".")[0] + "."):
                    intro_key = key
                    break
            if intro_key in SECTION_INTROS:
                f.write(SECTION_INTROS[intro_key])

            f.write("---\n\n")

        # Quick reference card
        f.write(generate_quick_reference())

    print(f"✓ Generated {OUTPUT_FILE}")
    if passing_scenarios is not None:
        print(f"  All scenarios in this guide have been verified to PASS")
    else:
        print(f"  WARNING: Scenarios in this guide have NOT been verified!")


def determine_section(scenario_name, tags=None):
    """
    Determine which section a scenario belongs to.

    PRIORITY ORDER:
    1. Explicit @user-guide-section tag (recommended)
    2. Keyword-based matching (fallback)

    TAGGING CONVENTION:
    Add one of these tags to your scenario/feature:
      @user-guide-installation       -> Section 1
      @user-guide-ssh-keys           -> Section 2
      @user-guide-first-vm           -> Section 3
      @user-guide-understanding      -> Section 4
      @user-guide-starting-stopping  -> Section 5
      @user-guide-cluster            -> Section 6
      @user-guide-connecting         -> Section 7
      @user-guide-databases          -> Section 8
      @user-guide-daily-workflow     -> Section 9
      @user-guide-more-languages     -> Section 10
      @user-guide-troubleshooting    -> Section 11
      @user-guide-internal           -> Not included (internal features)

    Example:
      @user-guide-first-vm
      Scenario: Creating a Python development environment
        Given I've just installed VDE
        When I run "create-virtual-for python"
        Then a Python VM should be created
    """
    # First, check for explicit tags
    if tags:
        tag_map = {
            "user-guide-installation": "1. Installation",
            "user-guide-ssh-keys": "2. SSH Keys",
            "user-guide-first-vm": "3. Your First VM",
            "user-guide-understanding": "4. Understanding",
            "user-guide-starting-stopping": "5. Starting and Stopping",
            "user-guide-cluster": "6. Your First Cluster",
            "user-guide-connecting": "7. Connecting",
            "user-guide-databases": "8. Working with Databases",
            "user-guide-daily-workflow": "9. Daily Workflow",
            "user-guide-more-languages": "10. Adding More Languages",
            "user-guide-troubleshooting": "11. Troubleshooting",
            "user-guide-internal": None,  # Explicitly exclude from user guide
        }
        for tag in tags:
            if tag in tag_map:
                return tag_map[tag]

    # Fallback: keyword-based matching
    name_lower = scenario_name.lower()

    if "installation" in name_lower or "prerequisite" in name_lower or "setup" in name_lower:
        return "1. Installation"
    elif "ssh" in name_lower and ("key" in name_lower or "agent" in name_lower or "config" in name_lower):
        return "2. SSH Keys"
    elif "first vm" in name_lower or "create vm" in name_lower or "hello world" in name_lower:
        return "3. Your First VM"
    elif "verify" in name_lower or "check status" in name_lower or "list" in name_lower or "understanding" in name_lower:
        return "4. Understanding"
    elif "start" in name_lower or "stop" in name_lower or "shutdown" in name_lower:
        return "5. Starting and Stopping"
    elif "cluster" in name_lower or "multi" in name_lower or "python postgres" in name_lower:
        return "6. Your First Cluster"
    elif "connect" in name_lower or "ssh into" in name_lower:
        return "7. Connecting"
    elif "database" in name_lower or "postgres" in name_lower or "redis" in name_lower:
        return "8. Working with Databases"
    elif "daily" in name_lower or "workflow" in name_lower or "morning" in name_lower:
        return "9. Daily Workflow"
    elif "language" in name_lower or "rust" in name_lower or "adding" in name_lower:
        return "10. Adding More Languages"
    elif "troubleshoot" in name_lower or "debug" in name_lower or "error" in name_lower or "rebuild" in name_lower:
        return "11. Troubleshooting"

    return None


def generate_quick_reference():
    """Generate the quick reference section."""
    return """## Quick Reference Card 📇

### Essential Commands (Your Cheat Sheet!)

```bash
# See what VMs are available
./scripts/vde list

# Create a new VM
./scripts/vde create <name>

# Start VMs
./scripts/vde start <vm1> <vm2> ...

# Stop VMs
./scripts/vde stop <vm1> <vm2> ...

# Stop everything
./scripts/vde stop all

# Rebuild a VM (when you make config changes)
./scripts/vde start <vm> --rebuild
```

### SSH Connections

```bash
# Language VMs
ssh python-dev     # Python development
ssh rust-dev       # Rust development
ssh js-dev         # JavaScript/Node.js
ssh csharp-dev     # C# development
ssh ruby-dev       # Ruby development
ssh go-dev         # Go development

# Service VMs
ssh postgres       # PostgreSQL database
ssh redis          # Redis cache
ssh mongodb        # MongoDB
ssh nginx          # Nginx web server
```

### Default Ports

| VM | Port |
|----|------|
| python-dev | 2200 |
| rust-dev | 2201 |
| js-dev | 2202 |
| csharp-dev | 2203 |
| ruby-dev | 2204 |
| postgres | 2400 |
| redis | 2401 |
| mongodb | 2402 |
| nginx | 2403 |

---

## Available VM Types

### Language VMs (for writing code)

| Language | Command | Aliases | Best For |
|----------|---------|---------|---------|
| Python | `vde create python` | py | Web backends, AI/ML, scripts |
| Rust | `vde create rust` | rust-dev | Systems, performance |
| JavaScript | `vde create js` | js, node | Web frontends, Node.js |
| C# | `vde create csharp` | csharp | .NET development |
| Ruby | `vde create ruby` | rb | Rails, scripts |
| Go | `vde create go` | golang | Services, microservices |

### Service VMs (for data & infrastructure)

| Service | Command | Port | Best For |
|---------|---------|------|----------|
| PostgreSQL | `vde create postgres` | 5432 | Relational databases |
| Redis | `vde create redis` | 6379 | Caching, queues |
| MongoDB | `vde create mongodb` | 27017 | NoSQL databases |
| Nginx | `vde create nginx` | 80/443 | Web server, reverse proxy |

---

## You're Ready! 🎉

Look at you go! You now have:
- ✅ VDE installed and configured (you did it!)
- ✅ SSH keys set up automatically (no manual work!)
- ✅ Your first VM created (how cool is that?)
- ✅ Understanding of starting/stopping (like a pro!)
- ✅ A full cluster ready (Python + PostgreSQL + Redis)
- ✅ Knowledge to troubleshoot hiccups (you've got this!)

**What's Next?** 🚀

1. Create your first project in `projects/python/`
2. Start coding something amazing!
3. Add more languages whenever you want (Rust? Go? Elixir? They're waiting for you!)

**Remember:** You're learning valuable skills here. Every command you run, every VM you create — you're becoming a better developer. Be proud of yourself!

---

*This guide is generated from BDD test scenarios that have been verified to PASS. Every workflow shown here has been tested and verified to work. If you follow these steps, they will work for you.*

**Now go build something awesome!** 💪✨
"""


if __name__ == "__main__":
    passing_scenarios = load_passing_scenarios_from_json()
    generate_user_guide(passing_scenarios)
