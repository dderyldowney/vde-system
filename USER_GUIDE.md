<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>

**Every workflow in this guide has been tested and verified to PASS.** Follow the steps, they will work for you too.

---

## Table of Contents

*💡 **Tip:** Click the ▶ triangle next to any section title below to expand or collapse that section.*

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

<details id="1.-installation" data-section="1. Installation">

<summary><h2>1. Installation</h2></summary>

Hey there! 👋 Ready to set up your awesome new development playground?

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

If you don't have Zsh/Bash, git, or Docker Desktop installed yet, that's totally fine! We'll hold your hand through the whole process. Just find your section below — Windows, Mac, or Linux — and follow the steps.

You've got this!

---

## Installing Homebrew (macOS Only)

Homebrew is a free package manager for macOS — think of it as an "app store for the command line" that makes installing developer tools super easy. It's totally optional, but if you plan to use it to install Zsh or Git, set it up here first so it's ready when you need it.

**Why use Homebrew?**

- One simple command installs almost any development tool

- Keeps your tools up to date easily

- Used by the vast majority of Mac developers

**Don't want to use Homebrew?** That's perfectly fine! We'll show you how to install Zsh and Git both with and without it.

> **Note:** Homebrew is macOS-only. Windows users will use Git Bash and the Git installer. Linux users have their own built-in package managers. Just skip this section if you're not on a Mac!

### For macOS Users

**Step 1: Check if Homebrew is already installed**

Open **Terminal** (press Command+Space, type "Terminal", press Enter) and run:

```

brew --version

```

If you see a version number like `Homebrew 4.x.x`, you already have it — **skip ahead to the next section!**

**Step 2: Install Homebrew**

Paste this command into Terminal and press Enter:

```bash

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```

Follow the prompts — you'll need to enter your Mac password when asked. The install may take a few minutes.

**On Apple Silicon (M1/M2/M3 Macs):** Homebrew installs to `/opt/homebrew`. After installation, follow the on-screen instructions to add Homebrew to your PATH. They'll look something like:

```bash

echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile

eval "$(/opt/homebrew/bin/brew shellenv)"

```

**Step 3: Verify Homebrew is working**

```

brew --version

```

You should see something like `Homebrew 4.x.x` — you're all set! 🍺

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

1. If you installed Homebrew (from the section above), install the latest Zsh:

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

If you installed Homebrew (from the section above), open Terminal and run:

```

brew install git

```

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

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Fresh installation on new system**


```
Given I have a new computer with Docker installed
And I have cloned the VDE repository to ~/dev
When I run the initial setup script
Then VDE should be properly installed
And required directories should be created
And I should see success message
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Prerequisites are checked**


```
Given I want to install VDE
When the setup script runs
Then it should verify Docker is installed
And it should verify docker-compose is available
And it should verify zsh is available
And it should report missing dependencies clearly
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Create required directory structure**


```
Given VDE is being installed
When the setup completes
Then configs/ directory should exist
And templates/ directory should exist with templates
And data/ directory should exist for persistent data
And logs/ directory should exist
And projects/ directory should exist for code
And env-files/ directory should exist
And backup/ directory should exist
And cache/ directory should exist
```



**Scenario: Generate or detect ssh keys**


```
Given I'm setting up VDE for the first time
When SSH keys are checked
Then if keys exist, they should be detected
And if no keys exist, ed25519 keys should be generated
And public keys should be copied to public-ssh-keys/
And .keep file should exist in public-ssh-keys/
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Initial ssh configuration**


```
Given VDE is being set up
When setup completes
Then backup/ssh/config should exist as a template
And the template should show proper SSH config format
And I should be able to use it as reference
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Load vm types configuration**


```
Given VDE is installed
When I run list-vms
Then all predefined VM types should be shown
And python, rust, js, csharp, ruby should be listed
And postgres, redis, mongodb, nginx should be listed
And aliases should be shown (py, js, etc.)
```



**Scenario: Set up shell environment**


```
Given I want VDE commands available everywhere
When I add VDE scripts to my PATH
Then I can run vde commands from any directory
And I can run start-virtual, shutdown-virtual, etc.
And tab completion should work
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Verify docker permissions**


```
Given VDE is being installed
When setup checks Docker
Then I should be warned if I can't run Docker without sudo
And instructions should be provided for fixing permissions
And setup should continue with a warning
```



**Scenario: Create docker network**


```
Given VDE is being installed
When the first VM is created
Then vde-testing should be created automatically
And all VMs should use this network
And VMs can communicate with each other
```



**Scenario: Verify installation with health check**


```
Given I've installed VDE
When I run "vde-health" or check status
Then I should see if VDE is properly configured
And any issues should be clearly listed
And I should get fix suggestions for each issue
```


**Run the command:**


```bash
vde-health
```

**Scenario: Upgrade existing installation**


```
Given I have an older version of VDE
When I pull the latest changes
Then my existing VMs should continue working
And new VM types should be available
And my configurations should be preserved
And I should be told about any manual migration needed
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Uninstall or cleanup**


```
Given I no longer want VDE on my system
When I want to remove it
Then I can stop all VMs
And I can remove VDE directories
And my SSH config should be cleaned up
And my project data should be preserved if I want
```


**Stop the VMs:**


```bash
vde stop <vms>
```

**Scenario: Installation on different platforms**


```
Given I'm installing VDE
When the setup detects my OS (Linux/Mac)
Then appropriate paths should be used
And platform-specific adjustments should be made
And the installation should succeed
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Docker image availability**


```
Given I'm setting up VDE for the first time
When I create my first VM
Then required Docker images should be pulled
And base images should be built if needed
And I should see download/build progress
```



**Scenario: Quick start after installation**


```
Given VDE is freshly installed
When I want to start quickly
Then I can run "create-virtual-for python && start-virtual python"
And I should have a working Python environment
And I can start coding immediately
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Documentation is available**


```
Given VDE is installed
When I need help
Then README.md should provide overview
And Technical-Deep-Dive.md should explain internals
And tests/README.md should explain testing
And help text should be available in commands
```



**Scenario: Validate installation**


```
Given VDE has been installed
When I run validation checks
Then all scripts should be executable
And all templates should be present
And vm-types.conf should be valid
And all directories should have correct permissions
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

</details>

<details id="2.-ssh-keys" data-section="2. SSH Keys">

<summary><h2>2. SSH Keys</h2></summary>

### SSH Keys? Automatic! 🔑

Here's some good news: VDE handles SSH keys for you automatically with complete isolation. We wanted to mention this so you know what's happening, but you don't need to do anything. It's like magic! ✨

**What happens:**

1. VDE creates an isolated SSH directory at `~/.ssh/vde/`

2. VDE generates its own SSH key (`~/.ssh/vde/id_ed25519`) automatically

3. The public key is copied to `public-ssh-keys/vde_id_ed25519.pub` for Docker builds

4. VMs are configured to use this isolated VDE key

**What this means for you:**

- ✅ Your personal SSH config (`~/.ssh/config`) is never touched

- ✅ Your personal SSH keys remain private

- ✅ VDE has its own complete SSH setup

- ✅ Easy cleanup: just `rm -rf ~/.ssh/vde`

**You don't need to:**

- Manually create SSH keys

- Edit your SSH config file

- Copy keys to VMs

- Set up SSH agent forwarding

**VDE does all of this for you.** Sit back and relax! ☕

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Report agent unavailable when ssh_auth_sock is not set**


```
Given SSH keys exist in ~/.ssh/vde/
And SSH_AUTH_SOCK is unset in the test environment
When I run any VDE command that requires SSH
Then the command output should indicate no SSH agent is available
And no running SSH agent processes should be terminated
```



**Scenario: Generate ssh key if none exists**


```
Given no SSH keys exist in ~/.ssh/vde/
When I run any VDE command that requires SSH
Then an ed25519 SSH key should be generated
And the public key should be synced to public-ssh-keys directory
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Sync public keys to vde directory**


```
Given SSH keys exist in ~/.ssh/vde/
When I run "sync_ssh_keys_to_vde"
Then public keys should be copied to "public-ssh-keys" directory
And only .pub files should be copied
And .keep file should exist in public-ssh-keys directory
```


**Run the command:**


```bash
sync_ssh_keys_to_vde
```

**Scenario: Validate public key files only**


```
Given public-ssh-keys directory contains files
When private key detection runs
Then non-.pub files should be rejected
And files containing "PRIVATE KEY" should be rejected
```



**Scenario: Create ssh config entry for new vm**


```
Given VM "python" is created with SSH port "2213"
When SSH config is generated
Then SSH config should contain "Host vde-python"
And SSH config should contain "Port 2213"
And SSH config should contain "ForwardAgent yes"
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Ssh config uses correct identity file**


```
Given primary SSH key is "id_ed25519"
When SSH config entry is created for VM "python"
Then SSH config should contain "IdentityFile" pointing to "~/.ssh/vde/id_ed25519"
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Generate vm to vm ssh config entries**


```
Given VM "python" is allocated port "2213"
And VM "rust" is allocated port "2216"
When VM-to-VM SSH config is generated
Then SSH config should contain entry for "vde-python"
And SSH config should contain entry for "vde-rust"
And each entry should use "localhost" as hostname
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Prevent duplicate ssh config entries**


```
Given SSH config already contains "Host vde-python"
When I create VM "python" again
Then duplicate SSH config entry should NOT be created
And command should warn about existing entry
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Atomic ssh config update prevents corruption**


```
Given SSH config file exists
When multiple processes try to update SSH config simultaneously
Then SSH config should remain valid
And no partial updates should occur
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Backup ssh config before modification**


```
Given SSH config file exists
When SSH config is updated
Then backup file should be created in "backup/ssh/" directory
And backup filename should contain timestamp
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Ssh config entries are static and preserved when vm is removed**


```
Given SSH config contains "Host vde-python"
When VM "python" is removed
Then SSH config should still contain "Host vde-python"
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Vm compose file mounts ssh agent socket for agent forwarding**


```
Given VM "python" is created with SSH port "2213"
When I inspect the docker-compose.yml for VM "python"
Then the compose file should mount the SSH agent socket volume
And the compose file should set SSH_AUTH_SOCK environment variable
And SSH config entry for "vde-python" should contain "ForwardAgent yes"
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Prefer ed25519 keys when multiple exist**


```
Given both "id_ed25519" and "id_rsa" keys exist
When primary SSH key is requested
Then "id_ed25519" should be returned as primary key
```



**Scenario: Merge new vm entry with existing ssh config**


```
Given ~/.ssh/vde/config exists with existing host entries
And ~/.ssh/vde/config contains "Host github.com"
And ~/.ssh/vde/config contains "Host myserver"
When I create VM "python" with SSH port "2213"
Then ~/.ssh/vde/config should still contain "Host github.com"
And ~/.ssh/vde/config should still contain "Host myserver"
And ~/.ssh/vde/config should contain new "Host vde-python" entry
And existing entries should be unchanged
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge preserves user's custom ssh settings**


```
Given ~/.ssh/vde/config exists with custom settings
And ~/.ssh/vde/config contains "Host *"
And ~/.ssh/vde/config contains "    User myuser"
And ~/.ssh/vde/config contains "    IdentityFile ~/.ssh/vde/mykey"
When I create VM "rust" with SSH port "2216"
Then ~/.ssh/vde/config should still contain "Host *"
And ~/.ssh/vde/config should still contain "    User myuser"
And ~/.ssh/vde/config should still contain "    IdentityFile ~/.ssh/vde/mykey"
And new "Host vde-rust" entry should be appended to end
```



**Scenario: Merge preserves existing vde entries when adding new vm**


```
Given ~/.ssh/vde/config contains "Host vde-python"
And ~/.ssh/vde/config contains "    Port 2213"
When I create VM "rust" with SSH port "2216"
Then ~/.ssh/vde/config should still contain "Host vde-python"
And ~/.ssh/vde/config should still contain "    Port 2213" under vde-python
And new "Host vde-rust" entry should be added
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge does not duplicate existing vde entries**


```
Given ~/.ssh/vde/config contains "Host vde-python"
And ~/.ssh/vde/config contains vde-python configuration
When I attempt to create VM "python" again
Then ~/.ssh/vde/config should contain only one "Host vde-python" entry
And error should indicate entry already exists
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Atomic merge prevents corruption if interrupted**


```
Given ~/.ssh/vde/config exists with content
When merge_ssh_config_entry starts but is interrupted
Then ~/.ssh/vde/config should either be original or fully updated
And ~/.ssh/vde/config should NOT be partially written
And original config should be preserved in backup
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Merge uses temporary file then atomic rename**


```
Given ~/.ssh/vde/config exists
When new SSH entry is merged
Then temporary file should be created first
Then content should be written to temporary file
Then atomic mv should replace original config
Then temporary file should be removed
```



**Scenario: Merge creates ssh config if it doesn't exist**


```
Given ~/.ssh/vde/config does not exist
And ~/.ssh/vde directory exists or can be created
When I create VM "python" with SSH port "2213"
Then ~/.ssh/vde/config should be created
And ~/.ssh/vde/config should have permissions "600"
And ~/.ssh/vde/config should contain "Host vde-python"
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge creates ~/.ssh/vde directory if needed**


```
Given ~/.ssh/vde directory does not exist
When I create VM "python" with SSH port "2213"
Then ~/.ssh/vde directory should be created
And ~/.ssh/vde/config should be created
And directory should have correct permissions
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge respects file locking for concurrent updates**


```
Given ~/.ssh/vde/config exists
And multiple processes try to add SSH entries simultaneously
When merge operations complete
Then all VM entries should be present
And no entries should be lost
And config file should be valid
```



**Scenario: Merge creates backup before any modification**


```
Given ~/.ssh/vde/config exists
When I create VM "python" with SSH port "2213"
Then backup file should exist at "backup/ssh/config.backup.YYYYMMDD_HHMMSS"
And backup should contain original config content
And backup timestamp should be before modification
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge entry has all required ssh config fields**


```
Given ~/.ssh/vde/config exists
When I create VM "python" with SSH port "2213"
Then merged entry should contain "Host vde-python"
And merged entry should contain "HostName localhost"
And merged entry should contain "Port 2213"
And merged entry should contain "User devuser"
And merged entry should contain "ForwardAgent yes"
And merged entry should contain "StrictHostKeyChecking no"
And merged entry should contain "IdentityFile" pointing to detected key
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Ssh config entries are static and preserved when vm is removed**


```
Given ~/.ssh/vde/config contains "Host vde-python"
And ~/.ssh/vde/config contains "Host vde-rust"
And ~/.ssh/vde/config contains user's "Host github.com" entry
When I remove VM for SSH cleanup "python"
Then ~/.ssh/vde/config should still contain "Host vde-python"
And ~/.ssh/vde/config should still contain "Host vde-rust"
And ~/.ssh/vde/config should still contain "Host github.com"
And user's entries should be preserved
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Remove known_hosts entry when vm is removed**


```
Given VM "python" is created with SSH port "2213"
And ~/.ssh/vde/known_hosts contains entry for "[localhost]:2213"
When I remove VM for SSH cleanup "python"
Then ~/.ssh/vde/known_hosts should NOT contain entry for "[localhost]:2213"
And ~/.ssh/vde/known_hosts should NOT contain entry for "[::1]:2213"
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Remove multiple hostname patterns from known_hosts**


```
Given VM "postgres" is created with SSH port "2404"
And ~/.ssh/vde/known_hosts contains "[localhost]:2404"
And ~/.ssh/vde/known_hosts contains "[::1]:2404"
And ~/.ssh/vde/known_hosts contains "postgres" hostname entry
When I remove VM for SSH cleanup "postgres"
Then ~/.ssh/vde/known_hosts should NOT contain "[localhost]:2404"
And ~/.ssh/vde/known_hosts should NOT contain "[::1]:2404"
And ~/.ssh/vde/known_hosts should NOT contain "postgres" entry
```



**Scenario: Create backup of known_hosts before cleanup**


```
Given ~/.ssh/vde/known_hosts exists with content
And VM "redis" is created with SSH port "2406"
When I remove VM for SSH cleanup "redis"
Then known_hosts backup file should exist at "~/.ssh/vde/known_hosts.vde-backup"
And backup should contain original content
```



**Scenario: Known_hosts cleanup handles missing file gracefully**


```
Given ~/.ssh/vde/known_hosts does not exist
And VM "python" is created with SSH port "2213"
When I remove VM for SSH cleanup "python"
Then command should succeed without error
And no known_hosts file should be created
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Known_hosts cleanup removes entries by port number**


```
Given ~/.ssh/vde/known_hosts contains multiple port entries
And ~/.ssh/vde/known_hosts contains "[localhost]:2213"
And ~/.ssh/vde/known_hosts contains "[localhost]:2404"
When VM with port "2213" is removed
Then ~/.ssh/vde/known_hosts should NOT contain "[localhost]:2213"
And ~/.ssh/vde/known_hosts should still contain "[localhost]:2404"
```



**Scenario: Recreating vm after removal succeeds without host key warning**


```
Given VM "python" was previously created with SSH port "2213"
And ~/.ssh/vde/known_hosts had old entry for "[localhost]:2213"
When I remove VM for SSH cleanup "python"
And I create VM "python" with SSH port "2213"
Then SSH connection should succeed without host key warning
And ~/.ssh/vde/known_hosts should contain new entry for "[localhost]:2213"
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Initialize ssh environment**


```
Given VDE SSH environment is not initialized
When I run "vde ssh-setup init"
Then the command should succeed
And VDE SSH directory should exist
And VDE SSH key should exist
And SSH key should have correct permissions
And SSH config should be generated
And public key should be synced to build context
And init command should show completion message
```


**Run the setup:**


```bash
vde ssh-setup init
```

</details>

<details id="3.-your-first-vm" data-section="3. Your First VM">

<summary><h2>3. Your First VM</h2></summary>

## Let's Create Your First VM! 🎉

You've made it through the setup. That's huge! Now for the fun part — creating your first development environment. We'll start with Python because it's friendly and popular. Perfect for beginners!

### Meet vde: Your Unified Command Interface 🤖

The `vde` command is your single, unified interface for all VDE operations:

```bash

vde create python    # Create a new VM

vde start rust      # Start a VM

vde stop all        # Stop VMs

vde list            # List all VMs

```

**Available vde Commands:**

| Command | What It Does |

|---------|--------------|

| `vde create <name>` | Create a new VM |

| `vde start <name>` | Start a VM |

| `vde stop <name>` | Stop a VM |

| `vde ssh <name>` | SSH into a VM |

| `vde list` | List all VMs |

| `vde restart <name>` | Restart a VM |

| `vde exec <name> <cmd>` | Execute command in VM |

| `vde remove <name>` | Remove a VM |

That's it! One simple, consistent command interface.

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: First time creation experience**


```
Given I've just installed VDE
When I run "create-virtual-for python"
Then I should see helpful progress messages
And configs/docker/python/ should be created
And docker-compose.yml should be generated
And SSH config should be updated
And I should be told what to do next
```


**Create the VM:**


```bash
vde create python
```

</details>

<details id="4.-understanding" data-section="4. Understanding">

<summary><h2>4. Understanding</h2></summary>

### Let's See What You Built! 🔍

You just created your first VM! That's honestly kind of a big deal. Give yourself a pat on the back! Let's make sure everything is working and understand what you now have.

### Understanding Your Directory Structure

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

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Resolve vm aliases**


```
Given "py" is an alias for "python"
When I parse "start py"
Then VMs should include "python"
```


**Start the VMs:**


```bash
vde start py
```

**Scenario: Configure aliases for vm**


```
Given I want to reference VMs with short names
When I add VM type with aliases "js,node,nodejs"
Then I can use any alias to reference the VM
And "start-virtual js", "start-virtual node", "start-virtual nodejs" all work
And aliases should show in list-vms output
```


**Start the VMs:**


```bash
vde start <vms>
```

</details>

<details id="5.-starting-and-stopping" data-section="5. Starting and Stopping">

<summary><h2>5. Starting and Stopping</h2></summary>

### Daily Rhythm: Start, Code, Stop, Repeat 🔄

Here's your daily workflow with VDE — simple as can be!

**Important:** Stopping doesn't delete your VM — it just pauses it. Your code and configurations are safe and sound! 💾

</details>

<details id="6.-your-first-cluster" data-section="6. Your First Cluster">

<summary><h2>6. Your First Cluster</h2></summary>

### Time to Build Something Real! 🏗️

Now let's build a real application stack. This is where VDE really shines — you can have multiple VMs working together like a well-oiled machine.

### What We're Building

You'll have a complete tech stack:

- **Python VM** — Your application code (port 2213)

- **PostgreSQL VM** — Your database (port 2404)

- **Redis VM** — Your cache (port 2406)

All three can talk to each other automatically. No networking headaches required!

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Detect start all vms intent**


```
When I parse "start everything"
Then intent should be "start_vm"
And VMs should include all known VMs
```


**Start the VMs:**


```bash
vde start everything
```

</details>

<details id="7.-connecting" data-section="7. Connecting">

<summary><h2>7. Connecting</h2></summary>

### Step Inside Your VM! 🚪

Ready to step into your development environment? Let's SSH in and see what's waiting for you!

### Exiting a VM

**To leave:** Just type `exit` or press `Ctrl+D`. The door is always open!

### Connection Reference

| VM Name | SSH Command | What It's For |

|---------|-------------|---------------|

| vde-python | `vde ssh python` | Python development |

| vde-rust | `vde ssh rust` | Rust development |

| vde-js | `vde ssh js` | JavaScript/Node.js |

| vde-csharp | `vde ssh csharp` | C# development |

| vde-ruby | `vde ssh ruby` | Ruby development |

| vde-go | `vde ssh go` | Go development |

| postgres | `vde ssh postgres` | Direct database access |

| redis | `vde ssh redis` | Direct Redis access |

| mongodb | `vde ssh mongodb` | MongoDB |

| nginx | `vde ssh nginx` | Nginx web server |

**Note:** The `vde ssh` command automatically uses VDE's isolated SSH configuration. You can also use VM aliases:

```bash

vde ssh py    # Short for python

vde ssh rs    # Short for rust

```

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Cloning a private repository from within a vm**


```
Given I have a Python VM running
And I have a private repository on GitHub
When I SSH into the Python VM
And I run "git clone git@github.com:myuser/private-repo.git"
Then the repository should be cloned
And I should not be prompted for a password
And my host's SSH keys should be used for authentication
```



**Scenario: Pushing code to github from a vm**


```
Given I have a Go VM running
And I have cloned a repository in the Go VM
And I have made changes to the code
When I run "git commit -am 'Add new feature'"
And I run "git push origin main"
Then the changes should be pushed to GitHub
And my host's SSH keys should be used
And no password should be required
```


**Run the command:**


```bash
git commit -am 
```

**Scenario: Pulling from multiple git hosts**


```
Given I have a Python VM running
And I have repositories on both GitHub and GitLab
And I have SSH keys configured for both hosts
When I SSH into the Python VM
And I run "git pull" in the GitHub repository
And I run "git pull" in the GitLab repository
Then both repositories should update
And each should use the appropriate SSH key from my host
```



**Scenario: Using git submodules**


```
Given I have a Rust VM running
And I have a repository with Git submodules
And the submodules are from GitHub
When I SSH into the Rust VM
And I run "git submodule update --init"
Then the submodules should be cloned
And authentication should use my host's SSH keys
```



**Scenario: Git operations in microservices architecture**


```
Given I have multiple VMs for different services
And each service has its own repository
And all repositories use SSH authentication
When I SSH to each VM
And I run "git pull" in each service directory
Then all repositories should update
And all should use my host's SSH keys
And no configuration should be needed in any VM
```



**Scenario: Deploying code from vm to external server**


```
Given I have a deployment server
And I have SSH keys configured for the deployment server
And I have a Python VM where I build my application
When I SSH into the Python VM
And I run "scp app.tar.gz deploy-server:/tmp/"
And I run "ssh deploy-server '/tmp/deploy.sh'"
Then the application should be deployed
And my host's SSH keys should be used for both operations
```



**Scenario: Multiple github accounts**


```
Given I have multiple GitHub accounts
And I have different SSH keys for each account
And all keys are loaded in my SSH agent
When I SSH into a VM
And I clone a repository from account1
And I clone a repository from account2
Then both repositories should be cloned
And each should use the correct SSH key
And the agent should automatically select the right key
```



**Scenario: Ssh key passed through to child processes**


```
Given I have a Node.js VM running
And I have an npm script that runs Git commands
When I SSH into the Node.js VM
And I run "npm run deploy" which uses Git internally
Then the deployment should succeed
And the Git commands should use my host's SSH keys
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Git operations in automated workflows**


```
Given I have a CI/CD script in a VM
And the script performs Git operations
When I run the CI/CD script
Then all Git operations should succeed
And my host's SSH keys should be used
And no manual intervention should be required
```



**Scenario: No key copying to vms required**


```
Given I have a new VM that needs Git access
And I have SSH keys on my host
When I create and start the VM
And I SSH into the VM
And I run "git clone git@github.com:user/repo.git"
Then the clone should succeed
And I should not have copied any keys to the VM
And only the SSH agent socket should be forwarded
```



</details>

<details id="8.-working-with-databases" data-section="8. Working with Databases">

<summary><h2>8. Working with Databases</h2></summary>

### Databases? No Problem! 🗄️

VDE makes working with databases delightfully simple. Your Python VM can talk to PostgreSQL as easily as if it were running on the same machine (because, well, virtually it is!).

**Important:** Database data in `~/dev/data/postgres/` persists even when you rebuild VMs. Your precious data is safe and sound! 💾

</details>

<details id="9.-daily-workflow" data-section="9. Daily Workflow">

<summary><h2>9. Daily Workflow</h2></summary>

### Your Daily Rhythm: Start, Code, Stop 🔄

Here's how your day with VDE will flow. Nice and simple!

</details>

<details id="10.-adding-more-languages" data-section="10. Adding More Languages">

<summary><h2>10. Adding More Languages</h2></summary>

### Want to Learn More Languages? 🌍

One of the beautiful things about VDE is how easy it is to try new languages! No installation headaches — just create a VM and start coding. Let's add another language to your collection!

**Polyglot programmer?** Why not! 😎

</details>

<details id="11.-troubleshooting" data-section="11. Troubleshooting">

<summary><h2>11. Troubleshooting</h2></summary>

### Hiccups Happen — We've Got Your Back! 🛠️

Sometimes things don't work perfectly the first time. That's okay! Here's how to handle common issues.

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Check ssh environment status**


```
When I run "vde ssh-setup status"
Then the command should succeed
And status command should show SSH environment state
```


**Run the setup:**


```bash
vde ssh-setup status
```

</details>

## Quick Reference Card 📇

### Essential Commands (Your Cheat Sheet!)

```bash
# See what VMs are available
vde list

# Create a new VM
vde create <name>

# Start VMs
vde start <vm1> <vm2> ...

# Stop VMs
vde stop <vm1> <vm2> ...

# Stop everything
vde stop all

# Rebuild a VM (when you make config changes)
vde start <vm> --rebuild
```

### SSH Connections

```bash
# VDE SSH - Simple connections to your VMs
vde ssh python     # Python development
vde ssh rust       # Rust development
vde ssh js         # JavaScript/Node.js
vde ssh csharp     # C# development
vde ssh ruby       # Ruby development
vde ssh go         # Go development

# Service VMs
vde ssh postgres   # PostgreSQL database
vde ssh redis      # Redis cache
vde ssh mongodb    # MongoDB
vde ssh nginx      # Nginx web server
```

**Note:** The `vde ssh` command automatically uses VDE's isolated SSH configuration at `~/.ssh/vde/config`. You can also use VM aliases (e.g., `vde ssh py` for Python, `vde ssh rs` for Rust).

### Default Ports

| VM | Port |
|----|------|
| vde-python | 2213 |
| vde-rust | 2216 |
| vde-js | 2209 |
| vde-csharp | 2203 |
| vde-ruby | 2215 |
| postgres | 2404 |
| redis | 2406 |
| mongodb | 2401 |
| nginx | 2403 |

---

## Available VM Types

### Language VMs (for writing code)

| Language | Command | Aliases |
|----------|---------|---------|
| Assembler | `vde create vde-asm` | asm,assembler,nasm |
| C | `vde create vde-c` | c |
| C++ | `vde create vde-cpp` | cpp,c++,gcc |
| C# | `vde create vde-csharp` | csharp,dotnet |
| Elixir | `vde create vde-elixir` | elixir |
| Flutter | `vde create vde-flutter` | flutter,dart |
| Go | `vde create vde-go` | go,golang |
| Haskell | `vde create vde-haskell` | haskell,ghc |
| Java | `vde create vde-java` | java,jdk |
| JavaScript | `vde create vde-js` | js,node,nodejs,javascript |

### Service VMs (for data & infrastructure)

| Service | Command | Port |
|---------|---------|------|
| CouchDB | `vde create vde-couchdb` | 5984 |
| MongoDB | `vde create vde-mongodb` | 27017 |
| MySQL | `vde create vde-mysql` | 3306 |
| Nginx | `vde create vde-nginx` | 80,443 |
| PostgreSQL | `vde create vde-postgres` | 5432 |
| RabbitMQ | `vde create vde-rabbitmq` | 5672,15672 |
| Redis | `vde create vde-redis` | 6379 |

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

<script>
// Collapsible sections with TOC navigation
(function() {
    // Intercept all TOC links
    document.addEventListener('DOMContentLoaded', function() {
        // Storage key for remembering last open section
        const STORAGE_KEY = 'vde-user-guide-last-section';

        // Function to expand a specific section and collapse others
        function expandSection(sectionId) {
            const targetSection = document.querySelector(`details[id="${sectionId}"]`);
            if (targetSection) {
                targetSection.setAttribute('open', '');
                // Remember this section
                localStorage.setItem(STORAGE_KEY, sectionId);
                // Update URL hash without jumping
                history.replaceState(null, null, '#' + sectionId);
                // Collapse all other sections
                const allSections = document.querySelectorAll('details');
                allSections.forEach(function(section) {
                    if (section !== targetSection) {
                        section.removeAttribute('open');
                    }
                });
                // Scroll to the section
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        // On page load, check for URL hash first, then localStorage
        // This preserves the section view on browser refresh
        let targetSectionId = window.location.hash.substring(1);
        if (!targetSectionId) {
            // No hash? Check if we remember the last section
            targetSectionId = localStorage.getItem(STORAGE_KEY) || '';
        }
        if (targetSectionId) {
            // Small delay to ensure DOM is ready
            setTimeout(function() {
                expandSection(targetSectionId);
            }, 100);
        }

        // TOC link click handlers
        const tocLinks = document.querySelectorAll('a[href^="#"]');

        tocLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                const targetId = link.getAttribute('href').substring(1);
                const targetSection = document.querySelector(`details[id="${targetId}"]`);

                if (targetSection) {
                    e.preventDefault();
                    expandSection(targetId);
                }
            });
        });

        // Also save section when user manually expands/collapses
        const allSections = document.querySelectorAll('details');
        allSections.forEach(function(section) {
            section.addEventListener('toggle', function() {
                if (this.open) {
                    const sectionId = this.getAttribute('id');
                    if (sectionId) {
                        localStorage.setItem(STORAGE_KEY, sectionId);
                        history.replaceState(null, null, '#' + sectionId);
                    }
                }
            });
        });
    });
})();
</script>
