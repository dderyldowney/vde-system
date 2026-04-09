<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>

**Every workflow in this guide has been tested and verified to PASS.** Follow the steps, they will work for you too.

---

## Table of Contents

*💡 **Tip:** Click the ▶ triangle next to any section title below to expand or collapse that section.*

1. [1. Installation](#1.-installation)
   - [Installing Homebrew (macOS Only)](#installing-homebrew-(macos-only))
     - [For macOS Users](#for-macos-users)
   - [Installing Zsh](#installing-zsh)
     - [For Windows Users](#for-windows-users)
     - [For macOS (Mac) Users](#for-macos-mac-users)
     - [For Linux Users](#for-linux-users)
   - [Installing Git](#installing-git)
     - [For Windows Users](#for-windows-users-1)
     - [For macOS (Mac) Users](#for-macos-mac-users-1)
     - [For Linux Users](#for-linux-users-1)
   - [Installing Docker Desktop](#installing-docker-desktop)
     - [For Windows Users](#for-windows-users-2)
     - [For macOS (Mac) Users](#for-macos-mac-users-2)
     - [For Linux Users](#for-linux-users-2)
   - [Quick Checklist: Are You Ready?](#quick-checklist-are-you-ready)
2. [2. Your First VM](#2.-your-first-vm)
3. [3. Connecting to your VM](#3.-connecting-to-your-vm)
4. [4. The Magic Behind the Scenes (SSH Keys)](#4.-the-magic-behind-the-scenes-(ssh-keys))
5. [5. Understanding Your Workspace](#5.-understanding-your-workspace)
6. [6. Starting, Stopping, and Restarting](#6.-starting,-stopping,-and-restarting)
7. [7. Your First Cluster (Multi-VM)](#7.-your-first-cluster-(multi-vm))
8. [8. Working with Databases](#8.-working-with-databases)
9. [9. Daily Study Routine](#9.-daily-study-routine)
10. [10. Adding More Languages](#10.-adding-more-languages)
11. [11. Troubleshooting](#11.-troubleshooting)
12. [12. Trial of the Gauntlet](#12.-trial-of-the-gauntlet)

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

- [ ] Zsh 5.0+ (the mandatory shell for the VDE ecosystem)

- [ ] About 5GB of free disk space (roughly the size of a few HD movies)

**Don't have these?** No stress! We'll walk you through getting each one. Just find your computer type below and follow along.

---

## Let's Get You Set Up! 🚀

If you don't have Zsh, git, or Docker Desktop installed yet, that's totally fine! We'll hold your hand through the whole process. Just find your section below — Windows, Mac, or Linux — and follow the steps.

You've got this!

---

## Installing Homebrew (macOS Only)

Homebrew is a free package manager for macOS — think of it as an "app store for the command line" that makes installing developer tools super easy. It's totally optional, but if you plan to use it to install Zsh or Git, set it up here first so it's ready when you need it.

**Why use Homebrew?**

- One simple command installs almost any development tool

- Keeps your tools up to date easily

- Used by the vast majority of Mac developers

**Don't want to use Homebrew?** That's perfectly fine! We'll show you how to install Zsh and Git both with and without it.

> **Note:** Homebrew is macOS-only. Windows users will use WSL or PowerShell. Linux users have their own built-in package managers. Just skip this section if you're not on a Mac!

### For macOS Users

**Step 1: Check if Homebrew is already installed**

Open **Terminal** (press Command+Space, type "Terminal", press Enter) and run:

```zsh

brew --version

```

If you see a version number like `Homebrew 4.x.x`, you already have it — **skip ahead to the next section!**

**Step 2: Install Homebrew**

Paste this command into Terminal and press Enter:

```zsh

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```

Follow the prompts — you'll need to enter your Mac password when asked. The install may take a few minutes.

**On Apple Silicon (M1/M2/M3 Macs):** Homebrew installs to `/opt/homebrew`. After installation, follow the on-screen instructions to add Homebrew to your PATH. They'll look something like:

```zsh

echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile

eval "$(/opt/homebrew/bin/brew shellenv)"

```

**Step 3: Verify Homebrew is working**

```zsh

brew --version

```

You should see something like `Homebrew 4.x.x` — you're all set! 🍺

---

## Installing Zsh

Okay, quick confession: "shell" is just a fancy name for the program that runs in your terminal and understands your commands. VDE needs a specific one — **Zsh 5.0+**. Sound scary? Don't worry, we'll sort you out!

**Why does VDE need this?**

- VDE's commands are written in ZSH language (fancy nerd talk for "scripts that run in your terminal")

- Other shells like Bash are not supported to ensure absolute stability

- The good news: Zsh comes standard on modern Macs and is easily installed on Windows and Linux

Think of it like VDE speaks a specific dialect, and we need to make sure your terminal understands it! 🗣️

---

### For Windows Users

#### Installing Zsh on Windows

Zsh is available on Windows through WSL (Windows Subsystem for Linux). This is the best way to run VDE on Windows.

**If you already have WSL installed (from the Docker section):**

1. Open **PowerShell** and run:

   ```zsh

   wsl

   ```

2. Once in WSL, install Zsh:

   ```zsh

   sudo apt-get update

   sudo apt-get install zsh

   ```

3. Check the version:

   ```zsh

   zsh --version

   ```

4. You should see something like `zsh 5.x.x or greater`

**If you don't have WSL:**

- Please install WSL to use VDE on Windows. It provides a real Linux environment that VDE loves!

#### What Shell Should You Use?

**For VDE on Windows:**

- **WSL + Zsh** (Mandatory) - Provides the power and compatibility VDE requires.

---

### For macOS (Mac) Users

#### The Good News: You Almost Certainly Already Have Zsh!

Modern macOS comes with Zsh as the default shell (since macOS Catalina).

**How to check what shell you have:**

1. Open **Terminal** (press Command+Space, type "Terminal", press Enter)

2. Check if Zsh is running by default:

   ```zsh

   echo $SHELL

   ```

3. If you see `/bin/zsh`, you're already using Zsh - great!

4. Check the Zsh version:

   ```zsh

   zsh --version

   ```

5. You should see `zsh 5.x.x or greater` - this is perfect!

#### If You Need to Install or Update Zsh

**Check if you need an update:**

```zsh

zsh --version

```

If the version is less than 5.0, or if Zsh isn't installed:

**Option 1: Use Homebrew (Easiest)**

1. If you installed Homebrew (from the section above), install the latest Zsh:

   ```zsh

   brew install zsh

   ```

2. Set Zsh as your default shell:

   ```zsh

   chsh -s /bin/zsh

   ```

   (You'll need to enter your password)

3. Close and reopen Terminal - you're now using Zsh!

**Option 2: macOS Already Has Zsh (Just Need to Switch)**

If Zsh is installed but not your default:

1. Check if Zsh exists:

   ```zsh

   ls /bin/zsh

   ```

2. If it exists, switch to it:

   ```zsh

   chsh -s /bin/zsh

   ```

3. Close and reopen Terminal

---

### For Linux Users

#### Check What You Already Have

Most modern Linux distributions come with Zsh available in their package managers.

**Check if Zsh is installed:**

```zsh

zsh --version

```

**What you should see:**

- Zsh: `version 5.0 or greater` (if installed)

#### If You Need to Install or Upgrade

**For Ubuntu/Debian:**

```zsh

# Install Zsh

sudo apt-get update

sudo apt-get install zsh

```

**For Fedora:**

```zsh

# Install Zsh

sudo dnf install zsh

```

**For CentOS/Red Hat:**

```zsh

# Install Zsh

sudo yum install zsh

```

**For Arch Linux:**

```zsh

# Install Zsh

sudo pacman -S zsh

```

#### Verify Your Installation

**Check Zsh version:**

```zsh

zsh --version

# Should show 5.0 or greater

```

#### Make Zsh Your Default Shell

To use Zsh as your daily shell:

```zsh

chsh -s $(which zsh)

```

Log out and log back in for the change to take effect.

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

1. When the download finishes, click the file to open it

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

   ```zsh

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

   ```zsh

   git --version

   ```

3. If you see a version number like `git version 2.39.0`, you already have Git! **You're done!**

#### If You Need to Install Git

If you don't have Git or want a newer version, here's how:

**Option 1: Install with Homebrew (Easiest)**

If you installed Homebrew (from the section above), open Terminal and run:

```zsh

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

```zsh

git --version

```

You should see a version number. **✅ Done!** You've got Git!

---

### For Linux Users

#### The Good News: Most Linux Has Git Already!

Linux is usually prepared for everything. Let's see:

1. Open your terminal

2. Type:

   ```zsh

   git --version

   ```

3. If you see a version, you're done!

#### If You Need to Install Git

**For Ubuntu/Debian:**

```zsh

sudo apt-get update

sudo apt-get install git

```

**For Fedora:**

```zsh

sudo dnf install git

```

**For CentOS/Red Hat:**

```zsh

sudo yum install git

```

**For Arch Linux:**

```zsh

sudo pacman -S git

```

**Verify Git is Working:**

In your terminal, type:

```zsh

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

   ```zsh

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

   ```zsh

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

   ```zsh

   docker --version

   ```

3. You should see something like `docker version 24.x.x, build xxxxx`

**✨ Perfect!** Docker is all set up on your Mac! Looking good!

---

### For Linux Users

Linux users — you're our kind of people! 🐧 Docker Desktop plays nicely with Ubuntu, Debian, Fedora, and many other distributions.

#### Step 1: Let's See Which Linux Flavor You Have

First, let's check which distribution you're rocking:

1. Open your **Terminal** (press Ctrl+Alt+T)

2. Type this command and press Enter:

   ```zsh

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

   ```zsh

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

   ```zsh

   # Go to your Downloads folder

   cd ~/Downloads

   # Install Docker (replace the filename with your actual downloaded file)

   sudo dnf install ./docker-desktop-<version>-<arch>.rpm

   ```

   *Note: The actual filename will be something like `docker-desktop-4.25.0-x86_64.rpm` - type `ls` to see the exact name and use that.*

3. If asked for confirmation, type **`y`** and press Enter

#### Step 4: Start Docker Desktop

1. After installation, you can start Docker by typing in your terminal:

   ```zsh

   systemctl --user start docker-desktop

   ```

2. To make Docker start automatically when you log in:

   ```zsh

   systemctl --user enable docker-desktop

   ```

3. You should also see a **Docker Desktop** icon in your applications menu - you can click that too!

#### Step 5: Verify Docker is Working

In your terminal, type:

```zsh

docker --version

```

You should see something like `docker version 24.x.x, build xxxxx`

**🔥 Boom!** Docker is running on Linux! You're on fire!

---

## Quick Checklist: Are You Ready? 🎯

Let's do a quick victory lap before we move on! Open your terminal and run these commands:

**Open your terminal (PowerShell on Windows, Terminal on Mac/Linux) and run:**

```zsh

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

   - Windows: Press Windows key, type "PowerShell", "Windows Terminal", or "ZSH"

   - Mac: Press Command+Space, type "Terminal"

   - Linux: Press Ctrl+Alt+T

3. **Permission errors?** Make sure you have administrator rights on your computer

4. **Shell not found?** Ensure you have Zsh 5.0+ installed.

5. **Version too old?** Use your package manager or Homebrew to install the latest Zsh.

Once Docker, Git, and Zsh are installed and working, you're ready for the fun part! You've made it through the setup — you're awesome! 🌟

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Verify all registered vms have compliant setup scripts**


```
Given the VDE registry is loaded
Then every VM must have a setup script in scripts/setup/
And every script must have 'set -e' for deterministic error handling
And every script must have 'apt-get clean' to minimize image size
And every script must have 'rm -rf /var/lib/apt/lists/*' to purge ghosts
And every script must have 'export DEBIAN_FRONTEND=noninteractive' to prevent prompts
And every script must follow the 'Forged in Beskar' standardized header ritual
```


**This is handled by the setup script:**


```zsh
./bin/build-and-start
```

</details>

<details id="2.-your-first-vm" data-section="2. Your First VM">

<summary><h2>2. Your First VM</h2></summary>

## Let's Create Your First VM! 🎉

You've made it through the setup. That's huge! Now for the fun part — creating your first development environment. We'll start with Python because it's friendly and popular. Perfect for beginners!

### Meet vde: Your Unified Command Interface 🤖

The `vde` command is your single, unified interface for all VDE operations:

```zsh

vde create python    # Create a new VM

vde start python     # Start the VM

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

| `vde enter <name>` | Drop into VM shell |

| `vde remove <name>` | Remove a VM |

That's it! One simple, consistent command interface.

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Hub to spoke deterministic ignition**


```
Given the VDE Hub "data/vm-types.conf" is the sole authority
And the VDE Registry "data/vm-types.json" is synchronized with the Hub
When I run the one true way to start "python"
Then a VM-level lock should be created during ignition
And the container "vde-python" should be started via direct Docker orchestration
And the container should have been hydrated by "scripts/setup/python-init.zsh"
And the SSH port should be atomically allocated and recorded in the registry
And I should be able to SSH into "vde-python" and verify the environment
```


**Create the VM:**


```zsh
vde create python
```

</details>

<details id="3.-connecting-to-your-vm" data-section="3. Connecting to your VM">

<summary><h2>3. Connecting to your VM</h2></summary>

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

```zsh

vde ssh py    # Short for python

vde ssh rs    # Short for rust

```

</details>

<details id="4.-the-magic-behind-the-scenes-(ssh-keys)" data-section="4. The Magic Behind the Scenes (SSH Keys)">

<summary><h2>4. The Magic Behind the Scenes (SSH Keys)</h2></summary>

### SSH Keys? Automatic! 🔑

Here's some good news: VDE handles SSH keys for you automatically with complete isolation. We wanted to mention this so you know what's happening, but you don't need to do anything. It's like magic! ✨

**What happens:**

1. VDE creates an isolated SSH directory at `~/.ssh/vde/`

2. VDE generates its own SSH key (`~/.ssh/vde/vde_student`) automatically

3. The public key is copied to `public-ssh-keys/vde_student.pub` for Docker builds

4. VMs are configured to use this isolated VDE key

**What this means for you:**

- ✅ Your personal SSH config (`~/.ssh/config`) is never touched

- ✅ Your personal SSH keys remain private

- ✅ VDE has its own complete SSH setup

- ✅ Easy cleanup: just `rm -rf ~/.ssh/vde`

**VDE does all of this for you.** Sit back and relax! ☕

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Ssh agent forwarding verification**


```
Given the VDE system is healthy
And "vde-python" is currently running
And I have identities loaded in my host SSH agent
When I execute "ssh-add -l" inside "vde-python" as "devuser"
Then the command execution should succeed
And the output should contain my host identities
```


**This is handled by the setup script:**


```zsh
./bin/build-and-start
```

</details>

<details id="5.-understanding-your-workspace" data-section="5. Understanding Your Workspace">

<summary><h2>5. Understanding Your Workspace</h2></summary>

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

└── bin/         # VDE management commands

```

</details>

<details id="6.-starting,-stopping,-and-restarting" data-section="6. Starting, Stopping, and Restarting">

<summary><h2>6. Starting, Stopping, and Restarting</h2></summary>

### Daily Rhythm: Start, Code, Stop, Repeat 🔄

Here's your daily workflow with VDE — simple as can be!

**Important:** Stopping doesn't delete your VM — it just pauses it. Your code and configurations are safe and sound! 💾

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Vm lifecycle termination (stop/remove)**


```
Given the VDE Registry is loaded
And "vde-python" is currently running
When I run the one true way to stop "python"
Then the container "vde-python" should be stopped
And the VM-level lock should be released
When I run the one true way to remove "python"
Then the container "vde-python" should be destroyed
And the SSH configuration should be preserved
```


**Stop the VMs:**


```zsh
vde stop <vms>
```

</details>

<details id="7.-your-first-cluster-(multi-vm)" data-section="7. Your First Cluster (Multi-VM)">

<summary><h2>7. Your First Cluster (Multi-VM)</h2></summary>

### Time to Build Something Real! 🏗️

Now let's build a real application stack. This is where VDE really shines — you can have multiple VMs working together like a well-oiled machine.

### What We're Building

You'll have a complete tech stack:

- **Python VM** — Your application code (port 2213)

- **PostgreSQL VM** — Your database (port 2404)

- **Redis VM** — Your cache (port 2406)

All three can talk to each other automatically. No networking headaches required!

</details>

<details id="8.-working-with-databases" data-section="8. Working with Databases">

<summary><h2>8. Working with Databases</h2></summary>

### Databases? No Problem! 🗄️

VDE makes working with databases delightfully simple. Your Python VM can talk to PostgreSQL as easily as if it were running on the same machine (because, well, virtually it is!).

**Important:** Database data in `~/dev/data/postgres/` persists even when you rebuild VMs. Your precious data is safe and sound! 💾

</details>

<details id="9.-daily-study-routine" data-section="9. Daily Study Routine">

<summary><h2>9. Daily Study Routine</h2></summary>

### Your Daily Rhythm: Start, Code, Stop 🔄

Hey student! 👋 Welcome to your daily study routine with VDE. Whether you're learning Python for your CS101 class, setting up a database for your web development project, or experimenting with Go for the first time — VDE makes it easy!

**Think of VDE as your personal computer lab that:**

- Spins up instantly when you need it

- Gives you fresh, clean environments for each project

- Keeps everything organized so you can focus on learning

- Costs nothing to try — no installation, no mess

---

## Ⱇ Your Morning Routine: Starting Your Study Session

Every great study session starts the same way — fire up your environments!

**Step 1: Start Your Docker**

Make sure Docker Desktop is running (check the whale icon in your menu bar).

**Step 2: Start Your VMs**

Need Python for homework? One command gets you ready:

```zsh

vde start python

```

Working on a project that needs a database too?

```zsh

vde start python postgres

```

**Step 3: Connect and Code**

```zsh

vde ssh python

```

---

## Ⱇ Your Study Session: What You Can Do

### Learning New Languages 🐍🦀🐹

Each VM is a complete, isolated environment. Try new languages without messing up your main system:

- **Python** — Data science, web dev, automation

- **JavaScript/Node** — Web development, APIs

- **Go** — Systems programming, cloud apps

- **Rust** — Performance-critical applications

- **Ruby** — Rails development

- And 15+ more!

### Building Projects with Databases 🗄️

Need a database for your project? VDE has you covered:

- **PostgreSQL** — The industry-standard relational database

- **MySQL** — Another popular relational option

- **MongoDB** — Flexible document database

- **Redis** — Lightning-fast caching

**Example: Full-Stack Project Setup**

```zsh

# Start your language VM + database

vde start python postgres

# Code in Python

vde ssh python

# Now you're in your Python environment with PostgreSQL available!

```

### Exploring and Discovering 📚

Not sure what's available? Ask VDE!

```zsh

vde ask what VMs can I create?

vde ask show all languages

vde ask show all services

```

---

## Ⱇ End of Session: Shutting Down

When you're done studying, clean up with one command:

```zsh

vde stop all

```

**That's it!** Your code stays in your project folders, but the VM environments are fresh and ready for next time.

---

## Ⱇ Quick Reference: Your Daily Commands

| What You Need | Command |

|---------------|---------|

| Start Python | `vde start python` |

| Start Multiple | `vde start python postgres redis` |

| Connect to VM | `vde ssh python` |

| See What's Running | `vde list` |

| Stop Everything | `vde stop all` |

| Add New Language | `vde create golang` |

**Pro Tip:** Use `vde ask` to get help in plain English!

```zsh

vde ask how do I connect to Python?

vde ask what's running?

```

</details>

<details id="10.-adding-more-languages" data-section="10. Adding More Languages">

<summary><h2>10. Adding More Languages</h2></summary>

### Want to Learn More Languages? 🌍

One of the beautiful things about VDE is how easy it is to try new languages! No installation headaches — just create a VM and start coding. Let's add another language to your collection!

**Polyglot programmer?** Why not! 😎

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Verify jupyterlab runtime connectivity**


```
When I start the VM "jupyterlab"
Then the VM "vde-jupyterlab" must be running
And the service on port "8888" must be responsive
```


**Start the VMs:**


```zsh
vde start <vms>
```

</details>

<details id="11.-troubleshooting" data-section="11. Troubleshooting">

<summary><h2>11. Troubleshooting</h2></summary>

### Hiccups Happen — We've Got Your Back! 🛠️

Sometimes things don't work perfectly the first time. That's okay! Here's how to handle common issues.

</details>

<details id="12.-trial-of-the-gauntlet" data-section="12. Trial of the Gauntlet">

<summary><h2>12. Trial of the Gauntlet</h2></summary>

### ⚔️ The Law of the Red-Green-Refactor

The VDE Hub is a hardened ecosystem. To ensure absolute stability and security, all new features or bug fixes MUST pass through the **Trial of the Gauntlet**. This is not a suggestion; it is the Way.

**The Three Strikes of the Forge:**

1.  **Strike One: The Red Gauntlet (The Mark)**

    - Before writing any implementation code, you MUST create a physical test file (e.g., `tests/unit/test_feature.zsh`).

    - You MUST execute this test and demonstrate a **RED** failure. This proves the target is marked.

2.  **Strike Two: The Green Victory (The Strike)**

    - Write the **minimal** code required to make the test pass.

    - Execute the test again to achieve a **GREEN** result.

3.  **Strike Three: The Refiner's Fire (The Refactor)**

    - With the test Green, clean up your code. Improve readability and ensure ZSH 5.0+ purity.

    - The test MUST remain Green. If it turns Red, you have failed the trial.

**Why we do this:**

- ✅ **Empirical Proof**: We don't "hope" it works; we prove it.

- ✅ **Anti-Regression**: Your tests protect your work from future changes.

- ✅ **Security**: The Gauntlet forces you to think about edge cases before they become vulnerabilities.

**Every workflow in the Hub is verified. Your contribution must be too.**

</details>

## Quick Reference Card 📇

### Essential Commands (Your Cheat Sheet!)

```zsh
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

```zsh
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
| Go Language | `vde create vde-displaytest` | displaytest |
| Elixir | `vde create vde-elixir` | elixir,ex,iex |
| Flutter | `vde create vde-flutter` | flutter,dart |
| Go | `vde create vde-go` | go,golang |
| Haskell | `vde create vde-haskell` | haskell,ghc |
| Java | `vde create vde-java` | java,jdk |

### Service VMs (for data & infrastructure)

| Service | Command | Port |
|---------|---------|------|
| CouchDB | `vde create vde-couchdb` | zsh /vde/scripts/setup/couchdb-init.zsh |
| MongoDB | `vde create vde-mongodb` | zsh /vde/scripts/setup/mongodb-init.zsh |
| MySQL | `vde create vde-mysql` | zsh /vde/scripts/setup/mysql-init.zsh |
| Nginx | `vde create vde-nginx` | zsh /vde/scripts/setup/nginx-init.zsh |
| PostgreSQL | `vde create vde-postgres` | zsh /vde/scripts/setup/postgres-init.zsh |
| RabbitMQ | `vde create vde-rabbitmq` | zsh /vde/scripts/setup/rabbitmq-init.zsh |
| Redis | `vde create vde-redis` | zsh /vde/scripts/setup/redis-init.zsh |
| JupyterLab Data Science Suite | `vde create vde-jupyterlab` | zsh /vde/scripts/setup/jupyterlab-init.zsh |

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
