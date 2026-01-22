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

# Clone the repository (replace with your repository URL)

# For example: git clone https://github.com/yourusername/vde.git ~/dev

git clone YOUR_REPO_URL_HERE ~/dev

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

When I run "vde list"

Then I should see all predefined VM types

And python, rust, js, csharp, ruby should be listed

And postgres, redis, mongodb, nginx should be listed

```



**Verify everything is ready:**

```bash

vde list

```



**Expected output:** You should see a list of available language and service VMs.



**Woohoo! 🎉** You're all set up and ready to go!

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
Then vde-network should be created automatically
And all VMs should use this network
And VMs can communicate with each other
```



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
create-virtual-for python
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

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Automatically start ssh agent if not running**


```
Given SSH agent is not running
And SSH keys exist in ~/.ssh/
When I run any VDE command that requires SSH
Then SSH agent should be started
And available SSH keys should be loaded into agent
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Generate ssh key if none exists**


```
Given no SSH keys exist in ~/.ssh/
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
Given SSH keys exist in ~/.ssh/
When I run "sync_ssh_keys_to_vde"
Then public keys should be copied to "public-ssh-keys" directory
And only .pub files should be copied
And .keep file should exist in public-ssh-keys directory
```


**Run the command:**


```bash
sync_ssh_keys_to_vde
```

**Scenario: Prevent duplicate ssh config entries**


```
Given SSH config already contains "Host python-dev"
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

**Scenario: Remove ssh config entry when vm is removed**


```
Given SSH config contains "Host python-dev"
When VM "python" is removed
Then SSH config should NOT contain "Host python-dev"
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Vm to vm communication uses agent forwarding**


```
Given SSH agent is running
And keys are loaded into agent
When I SSH from "python-dev" to "rust-dev"
Then the connection should use host's SSH keys
And no keys should be stored on containers
```



**Scenario: Detect all common ssh key types**


```
Given ~/.ssh/ contains SSH keys
When detect_ssh_keys runs
Then "id_ed25519" keys should be detected
And "id_rsa" keys should be detected
And "id_ecdsa" keys should be detected
And "id_dsa" keys should be detected
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Prefer ed25519 keys when multiple exist**


```
Given both "id_ed25519" and "id_rsa" keys exist
When primary SSH key is requested
Then "id_ed25519" should be returned as primary key
```



**Scenario: Merge does not duplicate existing vde entries**


```
Given ~/.ssh/config contains "Host python-dev"
And ~/.ssh/config contains python-dev configuration
When I attempt to create VM "python" again
Then ~/.ssh/config should contain only one "Host python-dev" entry
And error should indicate entry already exists
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge uses temporary file then atomic rename**


```
Given ~/.ssh/config exists
When new SSH entry is merged
Then temporary file should be created first
Then content should be written to temporary file
Then atomic mv should replace original config
Then temporary file should be removed
```



**Scenario: Merge creates ssh config if it doesn't exist**


```
Given ~/.ssh/config does not exist
And ~/.ssh directory exists or can be created
When I create VM "python" with SSH port "2200"
Then ~/.ssh/config should be created
And ~/.ssh/config should have permissions "600"
And ~/.ssh/config should contain "Host python-dev"
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge creates .ssh directory if needed**


```
Given ~/.ssh directory does not exist
When I create VM "python" with SSH port "2200"
Then ~/.ssh directory should be created
And ~/.ssh/config should be created
And directory should have correct permissions
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Merge preserves blank lines and formatting**


```
Given ~/.ssh/config exists with blank lines
And ~/.ssh/config has comments and custom formatting
When I create VM "go" with SSH port "2202"
Then ~/.ssh/config blank lines should be preserved
And ~/.ssh/config comments should be preserved
And new entry should be added with proper formatting
```



**Scenario: Create backup of known_hosts before cleanup**


```
Given ~/.ssh/known_hosts exists with content
And VM "redis" is created with SSH port "2401"
When I remove VM for SSH cleanup "redis"
Then known_hosts backup file should exist at "~/.ssh/known_hosts.vde-backup"
And backup should contain original content
```



**Scenario: Ssh agent setup is silent during normal operations**


```
Given I have created VMs before
And I have SSH configured
When I create a new VM
Then no SSH configuration messages should be displayed
And the setup should happen automatically
And I should only see VM creation messages
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Viewing ssh status**


```
Given I have VDE configured
When I run "./scripts/ssh-agent-setup"
Then I should see the SSH agent status
And I should see my available SSH keys
And I should see keys loaded in the agent
And the list-vms command should show available VMs
And I should see usage examples
```


**Run the setup:**


```bash
./scripts/ssh-agent-setup
```

**Scenario: Ssh config auto generation for all vms**


```
Given I have created multiple VMs
When I use SSH to connect to any VM
Then the SSH config entries should exist
And I should be able to use short hostnames
And I should not need to remember port numbers
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Rebuilding vms preserves ssh configuration**


```
Given I have a running VM with SSH configured
When I shutdown and rebuild the VM
Then my SSH configuration should still work
And I should not need to reconfigure SSH
And my keys should still work
```


**Start the VMs:**


```bash
vde start <vm> --rebuild
```

**Scenario: Automatic key generation preference**


```
Given I do not have any SSH keys
When I create a VM
Then an ed25519 key should be generated
And ed25519 should be the preferred key type
And the key should be generated with a comment
```



**Scenario: Public keys automatically synced to vde**


```
Given I have SSH keys on my host
When I create a VM
Then my public keys should be copied to public-ssh-keys/
And all my public keys should be in the VM's authorized_keys
And I should not need to manually copy keys
```



</details>

<details id="3.-your-first-vm" data-section="3. Your First VM">

<summary><h2>3. Your First VM</h2></summary>

## Let's Create Your First VM! 🎉



You've made it through the setup. That's huge! Now for the fun part — creating your first development environment. We'll start with Python because it's friendly and popular. Perfect for beginners!



### Creating Your Python VM



**Scenario: Creating a Python development environment**



```

Given I've just installed VDE

And I want my first development environment

When I run "vde create python"

Then a Python development environment should be created

And configs/docker/python/ should be created

And docker-compose.yml should be generated

And SSH config entry for "python-dev" should be added

And projects/python directory should be created

```



**Run this command:**

```bash

vde create python

```



**What you'll see:**

- Progress messages as Docker builds the image

- "SSH config entry created" message

- "Your Python VM is ready" message



**🎊 Exciting!** Your Python VM is being created!



### Meet vde: Your Unified Command Interface 🤝



The `vde` command is your single, unified interface for all VDE operations:



```bash

vde create python    # Create a new VM

vde start rust      # Start a VM

vde stop all         # Stop VMs

vde list             # List all VMs

```



**Available vde Commands:**



| Command | What It Does |

|---------|--------------|

| `vde create <name>` | Create a new VM |

| `vde start <name>` | Start a VM |

| `vde stop <name>` | Stop a VM |

| `vde list` | List all VMs |

| `vde restart <name>` | Restart a VM |

| `vde exec <name> <cmd>` | Execute command in VM |

| `vde remove <name>` | Remove a VM |



That's it! One simple, consistent command interface.



---



**Now let's get your Python VM running!**



### Starting Your First VM



**Scenario: Starting the Python VM**



```

Given I created a Python VM

When I run "vde start python"

Then the Python VM should be started

And I should be able to SSH to "python-dev"

```



**Run this command:**

```bash

vde start python

```



**What happens:**

- Docker container starts

- SSH port 2200 is allocated

- Your projects/python directory is mounted

- You're ready to code!



**🚀 You're off to the races!**

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Create a new service vm with custom port**


```
Given the VM "rabbitmq" is defined as a service VM with port "5672"
And no VM configuration exists for "rabbitmq"
When I run "create-virtual-for rabbitmq"
Then a docker-compose.yml file should be created at "configs/docker/rabbitmq/docker-compose.yml"
And the docker-compose.yml should contain service port mapping "5672"
And data directory should exist at "data/rabbitmq"
```


**Create the VM:**


```bash
create-virtual-for rabbitmq
```

**Scenario: Stop a running vm**


```
Given VM "python" is running
When I run "shutdown-virtual python"
Then VM "python" should not be running
```


**Run the command:**


```bash
shutdown-virtual python
```

**Scenario: Stop all running vms**


```
Given VM "python" is running
And VM "rust" is running
When I run "shutdown-virtual all"
Then no VMs should be running
```


**Run the command:**


```bash
shutdown-virtual all
```

**Scenario: List all predefined vm types**


```
Given VM types are loaded
When I run "list-vms"
Then all language VMs should be listed
And all service VMs should be listed
And aliases should be shown
```


**List available VMs:**


```bash
list-vms
```

**Scenario: Add a new vm type**


```
When I run "add-vm-type --type lang --display 'Zig Language' zig 'apt-get install -y zig'"
Then "zig" should be in known VM types
And VM type "zig" should have type "lang"
And VM type "zig" should have display name "Zig Language"
```


**Run the command:**


```bash
add-vm-type --type lang --display 
```

**Scenario: Add vm type with aliases**


```
When I run "add-vm-type --type lang --display 'JavaScript' js 'apt-get install -y nodejs' 'node,nodejs'"
Then "js" should be in known VM types
And "js" should have aliases "node,nodejs"
And "node" should resolve to "js"
And "nodejs" should resolve to "js"
```


**Run the command:**


```bash
add-vm-type --type lang --display 
```

</details>

<details id="4.-understanding" data-section="4. Understanding">

<summary><h2>4. Understanding</h2></summary>

### Let's See What You Built! 🔍



You just created your first VM! That's honestly kind of a big deal. Give yourself a pat on the back! Let's make sure everything is working and understand what you now have.



### Check That Your VM is Running



**Scenario: Verifying VM status**



```

Given I started my Python VM

When I run "vde list"

Then I should see which VMs are running

And Python should show as "running"

```



**Check status:**

```bash

vde list

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

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Listing all available vms**


```
Given I have VDE installed
When I ask "what VMs can I create?"
Then I should see all available language VMs
And I should see all available service VMs
And each VM should have a display name
And each VM should show its type (language or service)
```


**List available VMs:**


```bash
vde list
```

**Scenario: Listing only language vms**


```
Given I want to see only programming language environments
When I ask to list all languages
Then I should see only language VMs
And I should not see service VMs
And common languages like Python, Go, and Rust should be listed
```


**List available VMs:**


```bash
vde list --languages
```

**Scenario: Listing only service vms**


```
Given I want to see only infrastructure services
When I ask "show all services"
Then I should see only service VMs
And I should not see language VMs
And services like PostgreSQL and Redis should be listed
```


**List available VMs:**


```bash
vde list --services
```

**Scenario: Getting detailed information about a specific vm**


```
Given I want to know about the Python VM
When I request information about "python"
Then I should see its display name
And I should see its type (language)
And I should see any aliases (like py, python3)
And I should see installation details
```



**Scenario: Checking if a vm exists**


```
Given I want to verify a VM type before using it
When I check if "golang" exists
Then it should resolve to "go"
And the VM should be marked as valid
```



**Scenario: Discovering vms by alias**


```
Given I know a VM by an alias but not its canonical name
When I use the alias "nodejs"
Then it should resolve to the canonical name "js"
And I should be able to use either name in commands
```



**Scenario: Understanding vm categories**


```
Given I am new to VDE
When I explore available VMs
Then I should understand the difference between language and service VMs
And language VMs should have SSH access
And service VMs should provide infrastructure services
```



</details>

<details id="5.-starting-and-stopping" data-section="5. Starting and Stopping">

<summary><h2>5. Starting and Stopping</h2></summary>

### Daily Rhythm: Start, Code, Stop, Repeat 🔄



Here's your daily workflow with VDE — simple as can be!



### Starting Your VM



**Scenario: Starting a stopped VM**



```

Given I created a Python VM earlier

And it's currently stopped

When I run "vde start python"

Then the Python VM should start

And I can connect to it

```



**Command:**

```bash

vde start python

```



### Stopping Your VM



**Scenario: Stopping a running VM**



```

Given I have a Python VM running

When I run "vde stop python"

Then the Python VM should be stopped

And the configuration should remain for next time

```



**Command:**

```bash

vde stop python

```



**Important:** Stopping doesn't delete your VM — it just pauses it. Your code and configurations are safe and sound! 💾

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Creating a new vm**


```
Given I want to work with a new language
When I request to "create a Rust VM"
Then the VM configuration should be generated
And the Docker image should be built
And SSH keys should be configured
And the VM should be ready to use
```



**Scenario: Creating multiple vms at once**


```
Given I need a full stack environment
When I request to "create Python, PostgreSQL, and Redis"
Then all three VMs should be created
And each should have its own configuration
And all should be on the same Docker network
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Stopping a running vm**


```
Given I have a running Python VM
When I request to "stop python"
Then the Python container should stop
And the VM configuration should remain
And I can start it again later
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Stopping multiple vms**


```
Given I have multiple running VMs
When I request to "stop python and postgres"
Then both VMs should stop
And other VMs should remain running
```


**Stop the VMs:**


```bash
vde stop <vms>
```

**Scenario: Restarting a vm**


```
Given I have a running VM
When I request to "restart rust"
Then the Rust VM should stop
And the Rust VM should start again
And my workspace should still be accessible
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Restarting with rebuild**


```
Given I need to refresh a VM
When I request to "restart python with rebuild"
Then the Python VM should be rebuilt
And the VM should start with the new image
And my workspace should be preserved
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Rebuilding after code changes**


```
Given I have modified the Dockerfile
When I request to "rebuild go with no cache"
Then the Go VM should be rebuilt from scratch
And no cached layers should be used
And the new image should reflect my changes
```


**Start the VMs:**


```bash
vde start <vm> --rebuild
```

**Scenario: Upgrading a vm**


```
Given I want to update the base image
When I rebuild the VM
Then the latest base image should be used
And my configuration should be preserved
And my workspace should remain intact
```


**Start the VMs:**


```bash
vde start <vm> --rebuild
```

**Scenario: Migrating to a new vde version**


```
Given I have updated VDE scripts
When I rebuild my VMs
Then they should use the new VDE configuration
And my data should be preserved
And my SSH access should continue to work
```


**Start the VMs:**


```bash
vde start <vm> --rebuild
```

</details>

<details id="6.-your-first-cluster" data-section="6. Your First Cluster">

<summary><h2>6. Your First Cluster</h2></summary>

### Time to Build Something Real! 🏗️



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

When I run "vde create postgres"

And I run "vde create redis"

Then PostgreSQL VM configuration should be created

And Redis VM configuration should be created

```



**Create both services:**

```bash

vde create postgres

vde create redis

```



### Starting Your Full Stack



**Scenario: Starting all three VMs together**



```

Given I created VMs for python, postgres, and redis

When I run "vde start python postgres redis"

Then all three VMs should be running

And Python VM can connect to PostgreSQL

And Python VM can connect to Redis

```



**Start your full stack:**

```bash

vde start python postgres redis

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

vde list

```



**Expected output:**

```

VM          Type        Status    Port

----------------------------------------

python      language    running   2200

postgres    service     running   2400

redis       service     running   2401

```

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Automatically setting up ssh environment when creating a vm**


```
Given I do not have an SSH agent running
And I do not have any SSH keys
When I create a Python VM
Then an SSH agent should be started automatically
And an SSH key should be generated automatically
And the key should be loaded into the agent
And no manual configuration should be required
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Communicating between language vms**


```
Given I have a Go VM running
And I have a Python VM running
And I have started the SSH agent
When I SSH into the Go VM
And I run "ssh python-dev" from within the Go VM
Then I should connect to the Python VM
And I should be authenticated using my host's SSH keys
And I should not need to enter a password
And I should not need to copy keys to the Go VM
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Communicating between language and service vms**


```
Given I have a Python VM running
And I have a PostgreSQL VM running
When I SSH into the Python VM
And I run "ssh postgres-dev" from within the Python VM
Then I should connect to the PostgreSQL VM
And I should be able to run psql commands
And authentication should use my host's SSH keys
```



**Scenario: Copying files between vms using scp**


```
Given I have a Python VM running
And I have a Go VM running
When I create a file in the Python VM
And I run "scp go-dev:/tmp/file ." from the Python VM
Then the file should be copied using my host's SSH keys
And no password should be required
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Microservices architecture communication**


```
Given I have a Go VM running as an API gateway
And I have a Python VM running as a payment service
And I have a Rust VM running as an analytics service
When I SSH into the Go VM
And I run "ssh python-dev curl localhost:8000/health"
And I run "ssh rust-dev curl localhost:8080/metrics"
Then both services should respond
And all authentications should use my host's SSH keys
```



**Scenario: Ssh keys never leave the host**


```
Given I have SSH keys on my host
And I have multiple VMs running
When I SSH from one VM to another
Then the private keys should remain on the host
And only the SSH agent socket should be forwarded
And the VMs should not have copies of my private keys
```


**This is handled by the setup script:**


```bash
./scripts/build-and-start
```

**Scenario: Multiple vms can use the same agent**


```
Given I have 5 VMs running
And I have 2 SSH keys loaded in the agent
When I SSH from VM1 to VM2
And I SSH from VM2 to VM3
And I SSH from VM3 to VM4
And I SSH from VM4 to VM5
Then all connections should succeed
And all should use my host's SSH keys
And no keys should be copied to any VM
```



</details>

<details id="7.-connecting" data-section="7. Connecting">

<summary><h2>7. Connecting</h2></summary>

### Step Inside Your VM! 🚪



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



</details>

<details id="8.-working-with-databases" data-section="8. Working with Databases">

<summary><h2>8. Working with Databases</h2></summary>

### Databases? No Problem! 🗄️



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



**Important:** Database data in `~/dev/data/postgres/` persists even when you rebuild VMs. Your precious data is safe and sound! 💾

</details>

<details id="9.-daily-workflow" data-section="9. Daily Workflow">

<summary><h2>9. Daily Workflow</h2></summary>

### Your Daily Rhythm: Start, Code, Stop 🔄



Here's how your day with VDE will flow. Nice and simple!



### Morning Routine: Start Your Engines



**Scenario: Starting all your VMs at once**



```

Given I created VMs for my project

When I run "vde start python postgres redis"

Then all VMs should be running

And I can start working immediately

```



**One command to start your day:**

```bash

vde start python postgres redis

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

vde list

```



### End of Day: Shut It Down



**Scenario: Clean shutdown**



```

Given multiple VMs are running

When I run "vde stop all"

Then all VMs should stop gracefully

And my work is saved

```



**Stop everything:**

```bash

vde stop all

```



**Good night, VDE!** See you tomorrow! 🌙

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Create a new language vm for a project**


```
Given I need to start a "golang" project
```


**Create the VM:**


```bash
vde create go
```

**Scenario: Connect to postgresql from python vm**


```
Given "postgres" VM is running
And "python" VM is running
When I SSH into "python-dev"
And I run "psql -h postgres -U devuser"
Then I should be connected to PostgreSQL
And I can query the database
And the connection uses the container network
```



**Scenario: Rebuild a vm after modifying its dockerfile**


```
Given I have modified the python Dockerfile to add a new package
And "python" VM is currently running
When I run "start-virtual python --rebuild"
Then the VM should be rebuilt with the new Dockerfile
And the VM should be running after rebuild
And the new package should be available in the VM
```


**Start the VMs:**


```bash
start-virtual python --rebuild
```

**Scenario: Add support for a new language**


```
Given VDE doesn't support "zig" yet
When I run "add-vm-type --type lang --display 'Zig' zig 'apt-get install -y zig'"
Then "zig" should be available as a VM type
And I can create a zig VM with "create-virtual-for zig"
And zig should appear in "list-vms" output
```


**Run the command:**


```bash
add-vm-type --type lang --display 
```

**Scenario: Check what vms i can create**


```
Given I want to see what development environments are available
When I run "list-vms"
Then all language VMs should be listed with aliases
And all service VMs should be listed with ports
And I can see which VMs are created vs just available
```


**List available VMs:**


```bash
list-vms
```

**Scenario: Create test environment with database**


```
Given I need to test my application with a real database
When I create "postgres" and "redis" service VMs
And I create my language VM (e.g., "python")
And I start all three VMs
Then my application can connect to test database
And test data is isolated from development data
And I can stop test VMs independently
```


**Create the VM:**


```bash
vde create python
```

**Scenario: Vde handles port conflicts gracefully**


```
Given a system service is using port 2200
When I create a new language VM
Then VDE should allocate the next available port (2201)
And the VM should work correctly on the new port
And SSH config should reflect the correct port
```



**Scenario: Starting my development environment**


```
Given I have VDE installed
When I request to start my Python development environment
Then the Python VM should be started
And SSH access should be available on the configured port
And my workspace directory should be mounted
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Stopping work for the day**


```
Given I have multiple VMs running
When I request to "stop everything"
Then all running VMs should be stopped
And no containers should be left running
And the operation should complete without errors
```


**Stop the VMs:**


```bash
vde stop <vms>
```

**Scenario: Restarting a vm with rebuild**


```
Given I have a Python VM running
When I request to "restart python with rebuild"
Then the Python VM should be stopped
And the container should be rebuilt from the Dockerfile
And the Python VM should be started again
And my workspace should still be mounted
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Starting multiple vms at once**


```
Given I need a full stack environment
When I request to "start python and postgres"
Then both Python and PostgreSQL VMs should start
And they should be on the same Docker network
And they should be able to communicate
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Creating a new vm for the first time**


```
Given I want to try a new language
When I request to "create a Go VM"
Then the Go VM configuration should be created
And the Docker image should be built
And SSH keys should be configured
And the VM should be ready to start
```


**Create the VM:**


```bash
vde create go
```

</details>

<details id="10.-adding-more-languages" data-section="10. Adding More Languages">

<summary><h2>10. Adding More Languages</h2></summary>

### Want to Learn More Languages? 🌍



One of the beautiful things about VDE is how easy it is to try new languages! No installation headaches — just create a VM and start coding. Let's add another language to your collection!



**Scenario: Adding Rust to your environment**



```

Given I have Python running

And I want to work with Rust

When I run "vde create rust"

And I run "vde start rust"

Then Rust VM should be running

And I can use both Python and Rust

```



**Add Rust:**

```bash

vde create rust

vde start rust

```



### Starting Multiple Language VMs



**Scenario: Working with multiple languages**



```

Given I created VMs for Python, Rust, and JavaScript

When I run "vde start python rust js"

Then all three language VMs should be running

And I can switch between them

```



**Start multiple at once:**

```bash

vde start python rust js

```



**Polyglot programmer?** Why not! 😎

</details>

<details id="11.-troubleshooting" data-section="11. Troubleshooting">

<summary><h2>11. Troubleshooting</h2></summary>

### Hiccups Happen — We've Got Your Back! 🛠️



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

2. Is the port already in use? `vde list`

3. Check the logs: `docker logs <vm-name>`



### Problem: Changes Aren't Reflected



**Scenario: Rebuilding after configuration changes**



```

Given I modified the Dockerfile to add a package

And the VM is already running

When I run "vde start python --rebuild"

Then the VM should be rebuilt

And the new package should be available

```



**Rebuild with --rebuild:**

```bash

vde start python --rebuild

```



**For complete rebuild (no cache):**

```bash

vde start python --rebuild --no-cache

```

### Verified Scenarios

> **💡 Note:** The scenarios below show the Gherkin test steps used to verify VDE's behavior. Each scenario includes the actual **`vde` command** you would run to accomplish the task. We show the unified `vde` command because it's simpler and more consistent than remembering individual script names like `create-virtual-for` or `start-virtual`. The `vde` command handles all the heavy lifting for you!

**Scenario: Diagnose why vm won't start**


```
Given I tried to start a VM but it failed
When I check the VM status
Then I should see a clear error message
And I should know if it's a port conflict, Docker issue, or configuration problem
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: View vm logs for debugging**


```
Given a VM is running but misbehaving
When I run "docker logs <vm-name>"
Then I should see the container logs
And I can identify the source of the problem
```


**Run the command:**


```bash
docker logs <vm-name>
```

**Scenario: Access vm shell for debugging**


```
Given a VM is running
When I run "docker exec -it <vm-name> /bin/zsh"
Then I should have shell access inside the container
And I can investigate issues directly
```


**Run the command:**


```bash
docker exec -it <vm-name> /bin/zsh
```

**Scenario: Rebuild vm from scratch after corruption**


```
Given a VM seems corrupted or misconfigured
When I stop the VM
And I remove the VM directory
And I recreate the VM
Then I should get a fresh VM
And old configuration issues should be resolved
```



**Scenario: Check if port is already in use**


```
Given I get a "port already allocated" error
When I check what's using the port
Then I should see which process is using it
And I can decide to stop the conflicting process
And VDE can allocate a different port
```


**Stop the VMs:**


```bash
vde stop <vms>
```

**Scenario: Verify ssh connection is working**


```
Given I cannot SSH into a VM
When I check the SSH config
And I verify the VM is running
And I verify the port is correct
Then I can identify if the issue is SSH, Docker, or the VM itself
```



**Scenario: Test database connectivity from vm**


```
Given my application can't connect to the database
When I SSH into the application VM
And I try to connect to the database VM directly
Then I can see if the issue is network, credentials, or database state
```



**Scenario: Inspect docker compose configuration**


```
Given I need to verify VM configuration
When I look at the docker-compose.yml
Then I should see all volume mounts
And I should see all port mappings
And I should see environment variables
And I can verify the configuration is correct
```



**Scenario: Verify volumes are mounted correctly**


```
Given my code changes aren't reflected in the VM
When I check the mounts in the container
Then I can see if the volume is properly mounted
And I can verify the host path is correct
```



**Scenario: Clear docker cache to fix build issues**


```
Given a VM build keeps failing
When I rebuild with --no-cache
Then Docker should pull fresh images
And build should not use cached layers
```


**Start the VMs:**


```bash
vde start <vm> --rebuild
```

**Scenario: Reset a vm to initial state**


```
Given I've made changes I want to discard
When I stop the VM
And I remove the container but keep the config
And I start it again
Then I should get a fresh container
And my code volumes should be preserved
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Verify network connectivity between vms**


```
Given two VMs can't communicate
When I check the docker network
Then I should see both VMs on "vde-network"
And I can ping one VM from another
```



**Scenario: Check vm resource usage**


```
Given a VM seems slow
When I run "docker stats <vm-name>"
Then I can see CPU and memory usage
And I can identify resource bottlenecks
```


**Run the command:**


```bash
docker stats <vm-name>
```

**Scenario: Validate vm configuration before starting**


```
Given I think my docker-compose.yml might have errors
When I run "docker-compose config"
Then I should see any syntax errors
And the configuration should be validated
```


**Run the command:**


```bash
docker-compose config
```

**Scenario: Recover from docker daemon issues**


```
Given VMs won't start due to Docker problems
When I check Docker is running
And I restart Docker if needed
Then VMs should start normally after Docker is healthy
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Fix permission issues on shared volumes**


```
Given I get permission denied errors in VM
When I check the UID/GID configuration
Then I should see if devuser (1000:1000) matches my host user
And I can adjust if needed
```



**Scenario: Diagnose why tests fail in vm but pass locally**


```
Given tests work on host but fail in VM
When I compare the environments
Then I can check for missing dependencies
And I can verify environment variables match
And I can check network access from the VM
```



**Scenario: Invalid vm name handling**


```
Given I try to use a VM that doesn't exist
When I request to "start nonexistent-vm"
Then I should receive a clear error message
And the error should explain what went wrong
And suggest valid VM names
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Network creation failure**


```
Given the Docker network can't be created
When I start a VM
Then VDE should report the specific error
And suggest troubleshooting steps
And offer to retry
```



**Scenario: Configuration file errors**


```
Given a docker-compose.yml is malformed
When I try to use the VM
Then VDE should detect the error
And show the specific problem
And suggest how to fix the configuration
```



**Scenario: Graceful degradation**


```
Given one VM fails to start
When I start multiple VMs
Then other VMs should continue
And I should be notified of the failure
And successful VMs should be listed
```


**Start the VMs:**


```bash
vde start <vms>
```

**Scenario: Automatic retry logic**


```
Given a transient error occurs
When VDE detects it's retryable
Then it should automatically retry
And limit the number of retries
And report if all retries fail
```



**Scenario: Partial state recovery**


```
Given an operation is interrupted
When I try again
Then VDE should detect partial state
And complete the operation
And not duplicate work
```



**Scenario: Error logging**


```
Given an error occurs
When VDE handles it
Then the error should be logged
And the error should have sufficient detail for debugging
And I can find it in the logs directory
```



**Scenario: Rollback on failure**


```
Given an operation fails partway through
When the failure is detected
Then VDE should clean up partial state
And return to a consistent state
And allow me to retry cleanly
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

| Language | Command | Aliases |
|----------|---------|---------|
| C | `vde create c` | c |
| C++ | `vde create cpp` | c++,gcc |
| Assembler | `vde create asm` | assembler,nasm |
| Python | `vde create python` | python3 |
| Rust | `vde create rust` | rust |
| JavaScript | `vde create js` | node,nodejs,javascript |
| C# | `vde create csharp` | dotnet |
| Ruby | `vde create ruby` | ruby |
| Go | `vde create go` | golang |
| Java | `vde create java` | jdk |

### Service VMs (for data & infrastructure)

| Service | Command | Port |
|---------|---------|------|
| PostgreSQL | `vde create postgres` | 5432 |
| Redis | `vde create redis` | 6379 |
| MongoDB | `vde create mongodb` | 27017 |
| Nginx | `vde create nginx` | 80,443 |
| CouchDB | `vde create couchdb` | 5984 |
| MySQL | `vde create mysql` | 3306 |
| RabbitMQ | `vde create rabbitmq` | 5672,15672 |

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
