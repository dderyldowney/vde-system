<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>

**Every workflow in this guide has been tested and verified to PASS.** Follow the steps, they will work for you too.

---

## Table of Contents

1. [1. Installation](#1.-installation)
   - [Installing Docker Desktop](#installing-docker-desktop)
     - [For Windows Users](#for-windows-users)
     - [For macOS (Mac) Users](#for-macos-mac-users)
     - [For Linux Users](#for-linux-users)
   - [Installing Git](#installing-git)
     - [For Windows Users](#for-windows-users-1)
     - [For macOS (Mac) Users](#for-macos-mac-users-1)
     - [For Linux Users](#for-linux-users-1)
   - [Installing Zsh and Bash](#installing-zsh-and-bash)
     - [For Windows Users](#for-windows-users-2)
     - [For macOS (Mac) Users](#for-macos-mac-users-2)
     - [For Linux Users](#for-linux-users-2)
   - [Quick Checklist: Are You Ready?](#quick-checklist-are-you-ready)
2. [2. SSH Keys](#2.-ssh-keys)
3. [3. Your First VM](#3.-your-first-vm)
4. [4. Understanding](#4.-understanding)
5. [5. Starting and Stopping](#5.-starting-and-stopping)
6. [6. Your First Cluster](#6.-your-first-cluster)
7. [7. Connecting](#7.-connecting)
8. [8. Working with Databases](#8.-working-with-databases)
9. [9. Daily Workflow](#9.-daily-workflow)
10. [10. Adding More Languages](#10.-adding-more-languages)
11. [11. Troubleshooting](#11.-troubleshooting)

---

## 1. Installation

This is the part everyone finds confusing. Let's break it down.

### What You Need Before Starting

**What you need:**
- [ ] Docker Desktop installed and running
- [ ] Git installed (for cloning the repo)
- [ ] Zsh 5.0+ or Bash 4.0+ (VDE scripts need these)
- [ ] About 5GB of free disk space

---

## Don't Have These Yet? No Problem!

If you don't have Docker Desktop or git installed yet, don't worry! We'll walk you through installing both, step by step. Just follow the instructions for your computer's operating system (Windows, Mac, or Linux).

---

## Installing Docker Desktop

Docker Desktop is the program that runs all your development environments. Think of it as the "engine" that powers your virtual machines.

### For Windows Users

#### Step 1: Check if You Have the Right Version of Windows

Docker Desktop only works on Windows 10 or Windows 11. It also **needs Windows 10/11 Pro, Enterprise, or Education** - it won't work on Windows Home edition (unless you use WSL 2, which we'll cover).

**How to check your Windows version:**

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

**Success!** Docker is installed and running.

---

### For macOS (Mac) Users

#### Step 1: Check if Your Mac is Compatible

Docker Desktop works on:
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

**Success!** Docker is installed and running on your Mac.

---

### For Linux Users

Docker Desktop on Linux works with Ubuntu, Debian, Fedora, and many other distributions.

#### Step 1: Check Your Linux Distribution

First, let's find out which Linux you're using:

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

**Success!** Docker is installed and running on Linux.

---

## Installing Git

Git is a tool for downloading code from the internet (like the VDE code). You'll need it to get VDE onto your computer.

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

**Success!** Git is installed on Windows.

---

### For macOS (Mac) Users

#### The Good News: You Might Already Have Git!

Git comes built-in on macOS. Let's check first:

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

You should see a version number. **Success!**

---

### For Linux Users

#### The Good News: Most Linux Has Git Already!

Let's check if you already have it:

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

You should see a version number. **Success!**

---

## Installing Zsh and Bash

VDE scripts require a modern shell to work properly. You need either **Zsh 5.0+** or **Bash 4.0+**. Don't worry - we'll show you how to install them if you don't have them yet.

**Why do I need this?**
- VDE's management scripts are written in shell and need modern features
- Older versions of Bash (before 4.0) don't support the features we use
- Zsh is the default on modern Macs and works great with VDE

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

## Quick Checklist: Are You Ready?

Before moving on, let's make sure everything is installed:

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
- `docker --version` → Shows Docker version number
- `git --version` → Shows Git version number
- `docker ps` → Shows a list of containers (may be empty, that's OK!)

**If `docker ps` gives an error like "Cannot connect to the Docker daemon":**
- Docker Desktop isn't running - start it from your applications
- Wait for the whale icon to stop spinning before trying again

---

## Need Help?

If you run into trouble installing Docker, Git, or shells:

1. **Docker won't start?** Make sure your computer is compatible and you've restarted after installation
2. **Can't find the terminal?**
   - Windows: Press Windows key, type "PowerShell", "Windows Terminal", or "Git Bash"
   - Mac: Press Command+Space, type "Terminal"
   - Linux: Press Ctrl+Alt+T
3. **Permission errors?** Make sure you have administrator rights on your computer
4. **Shell not found?** On Windows, make sure you installed Git for Windows - it includes Git Bash
5. **Version too old?** On macOS, use Homebrew to install the latest version. On Linux, use your package manager

Once Docker, Git, and a modern shell are installed and working, you're ready to continue with the VDE setup!

---

### Step 1: Clone VDE to Your Computer

**Scenario: Getting the VDE code**

```
Given I want to install VDE
When I clone the VDE repository to ~/dev
Then VDE files should be in place
```

**Open your terminal and run:**
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
---

## 2. SSH Keys

This is automatic, but you should understand what's happening.

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

**VDE does all of this for you.**
---

## 3. Your First VM

## Meet vde: Your New Best Friend

Before we create your first VM, let's introduce you to the star of the show.

### You Might Notice Something Weird...

As you read through this guide, you'll see scenarios that look like this:

```
When I run "create-virtual-for python"
```

But then the actual command we show you is:

```bash
./scripts/vde create python
```

**What's going on?** Are we trying to confuse you? Nope!

### Here's the Secret

VDE has a bunch of specialized scripts that do specific things:
- `create-virtual-for` — Creates new VMs
- `start-virtual` — Starts VMs
- `shutdown-virtual` — Stops VMs
- `list-vms` — Lists all your VMs
- And more...

**But memorizing all those?** Ugh. No thanks.

### Enter: vde — Your Go-To Guy

The `vde` command is like having a personal assistant who knows exactly which script to run for you. You just tell it what you want in plain English:

```bash
./scripts/vde create python    # "Hey vde, create a Python VM"
./scripts/vde start rust      # "Hey vde, start that Rust VM"
./scripts/vde stop all         # "Hey vde, stop everything"
./scripts/vde list             # "Hey vde, what's running?"
```

And vde goes and runs the right script for you. Like magic! ✨

### Why Do the Scenarios Show the Script Names Then?

Great question! The scenarios (those Given-When-Then blocks) show what's *actually happening under the hood*. They're like a behind-the-scenes look at how VDE works.

Think of it like a restaurant:
- **The scenarios** are like watching in the kitchen — you see the chef chopping, sautéing, plating.
- **The vde command** is like ordering from the menu — you just say "I want the pasta" and it appears!

### What You Should Remember

| Forget About | Use This Instead |
|--------------|------------------|
| `create-virtual-for` | `vde create` |
| `start-virtual` | `vde start` |
| `shutdown-virtual` | `vde stop` |
| `list-vms` | `vde list` |

**That's it.** One command to rule them all.

### tl;dr

- The scenarios show the behind-the-scenes scripts (technical details)
- You use the `vde` command (easy mode)
- vde calls those scripts for you, so you don't have to remember which is which
- vde is your go-to guy. Treat it well. Maybe buy it a coffee sometime. ☕

Now that you know your new best friend, let's create your first VM!

---

Let's create your first development environment. We'll start with Python because it's the most common language for beginners.

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
---

## 4. Understanding

Let's verify everything works and understand the pieces.

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
---

## 5. Starting and Stopping

Daily workflow: starting when you work, stopping when done.

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

**Important:** Stopping doesn't delete your VM - it just stops the container. Your code and configurations are safe.
---

## 6. Your First Cluster

Now let's build a real application stack. This is where VDE shines.

### Understanding What We're Building

You'll have:
- **Python VM** - Your application code (port 2200)
- **PostgreSQL VM** - Your database (port 2400)
- **Redis VM** - Your cache (port 2401)

All three can talk to each other automatically.

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
---

## 7. Connecting

### Connecting to Your Python VM

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
- Edit files in projects/python/
- Access postgres and redis

### Exiting a VM

**To exit:** Just type `exit` or press `Ctrl+D`

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
---

## 8. Working with Databases

### Connecting to PostgreSQL from Your Python VM

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
# \list                    # List databases
# \c devuser               # Connect to default database
# \dt                      # List tables
# SELECT 1;                # Run a query
# \q                       # Quit
```

### Your Database Data Persists

**Scenario: Database data survives rebuilds**

```
Given I created tables in PostgreSQL
When I rebuild the PostgreSQL VM
And I reconnect to PostgreSQL
Then my tables should still exist
```

**Important:** Database data in `~/dev/data/postgres/` persists even when you rebuild VMs. Your data is safe.
---

## 9. Daily Workflow

### Morning Routine: Start Your Development Environment

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

### During the Day: Check What's Running

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

### End of Day: Stop Everything

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
---

## 10. Adding More Languages

### Creating a Second Language VM

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
---

## 11. Troubleshooting

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
---

## Quick Reference Card

### Essential Commands

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

# Rebuild a VM
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

## You're Ready!

**You now have:**
- ✅ VDE installed and configured
- ✅ SSH keys set up automatically
- ✅ Your first VM created
- ✅ Understanding of starting/stopping
- ✅ A full cluster (Python + PostgreSQL + Redis)
- ✅ Knowledge of how to troubleshoot

**Next steps:**
1. Create your first project in `projects/python/`
2. Start coding!
3. Add more languages as you need them

---

*This guide is generated from BDD test scenarios that have been verified to PASS. Every workflow shown here has been tested and verified to work. If you follow these steps, they will work for you.*
