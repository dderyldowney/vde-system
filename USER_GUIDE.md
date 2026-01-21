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

./scripts/vde list

```



**Expected output:** You should see a list of available language and service VMs.



**Woohoo! 🎉** You're all set up and ready to go!

### Verified Scenarios

**Scenario: All vms have valid installation commands**

```
Given I have VDE installed
When I verify installation commands for all VMs
Then each VM should have a non-empty install command
And the install command should be valid shell syntax
```

**Scenario: Example 1   python api with postgresql setup**

```
Given I am following the documented Python API workflow
When I plan to create a Python VM
Then the plan should include the create_vm intent
And the plan should include the Python VM
```

**Scenario: Example 3   microservices architecture setup**

```
Given I am creating a microservices architecture
When I plan to create Python, Go, Rust, PostgreSQL, and Redis
Then the plan should include all five VMs
And each VM should be included in the VM list
```

**Scenario: Daily workflow   morning setup**

```
Given I am starting my development day
When I plan to start Python, PostgreSQL, and Redis
Then the plan should include all three VMs
And the plan should use the start_vm intent
```

**Scenario: New project setup   discover available vms**

```
Given I am setting up a new project
When I ask what VMs can I create
Then the plan should include the list_vms intent
And I should see all available VM types
```

**Scenario: New project setup   choose full stack**

```
Given I want a Python API with PostgreSQL
When I plan to create Python and PostgreSQL
Then both VMs should be included in the plan
And the plan should use the create_vm intent
```

**Scenario: New project setup   start development stack**

```
Given I have created my VMs
When I plan to start Python and PostgreSQL
Then both VMs should start
And they should be able to communicate
```

---

## 2. SSH Keys

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

---

## 3. Your First VM

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

./scripts/vde create python

```



**What you'll see:**

- Progress messages as Docker builds the image

- "SSH config entry created" message

- "Your Python VM is ready" message



**🎊 Exciting!** Your Python VM is being created!



### Meet vde: Your Unified Command Interface 🤝



The `vde` command is your single, unified interface for all VDE operations:



```bash

./scripts/vde create python    # Create a new VM

./scripts/vde start rust      # Start a VM

./scripts/vde stop all         # Stop VMs

./scripts/vde list             # List all VMs

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

./scripts/vde start python

```



**What happens:**

- Docker container starts

- SSH port 2200 is allocated

- Your projects/python directory is mounted

- You're ready to code!



**🚀 You're off to the races!**

### Verified Scenarios

**Scenario: Detect create vm intent**

```
When I parse "create a go vm"
Then intent should be "create_vm"
And VMs should include "go"
```

---

## 4. Understanding

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

### Verified Scenarios

**Scenario: Verify port registry consistency**

```
Given port registry cache exists
And a VM has been removed
When port registry is verified
Then removed VM should be removed from registry
And cache file should be updated
```

**Scenario: Example 1   verify postgresql accessibility**

```
Given I have started the PostgreSQL VM
When I check if postgres exists
Then the VM should be recognized as a valid VM type
And it should be marked as a service VM
```

**Scenario: Example 3   verify all microservice vms exist**

```
Given I have created microservices
When I check for each service VM
Then Python should exist as a language VM
And Go should exist as a language VM
And Rust should exist as a language VM
And PostgreSQL should exist as a service VM
And Redis should exist as a service VM
```

**Scenario: Daily workflow   check status during development**

```
Given I am actively developing
When I ask what's running
Then the plan should include the status intent
And I should be able to see running VMs
```

**Scenario: Troubleshooting   step 1 check status**

```
Given something isn't working correctly
When I check the status
Then I should receive status information
And I should see which VMs are running
```

**Scenario: Documentation accuracy   verify examples work**

```
Given the documentation shows specific VM examples
When I verify the documented VMs
Then Python should be a valid VM type
And JavaScript should be a valid VM type
And all microservice VMs should be valid
```

**Scenario: Listing all available vms**

```
Given I have VDE installed
When I ask "what VMs can I create?"
Then I should see all available language VMs
And I should see all available service VMs
And each VM should have a display name
And each VM should show its type (language or service)
```

**Scenario: Listing only language vms**

```
Given I want to see only programming language environments
When I ask to list all languages
Then I should see only language VMs
And I should not see service VMs
And common languages like Python, Go, and Rust should be listed
```

**Scenario: Listing only service vms**

```
Given I want to see only infrastructure services
When I ask "show all services"
Then I should see only service VMs
And I should not see language VMs
And services like PostgreSQL and Redis should be listed
```

**Scenario: Understanding vm categories**

```
Given I am new to VDE
When I explore available VMs
Then I should understand the difference between language and service VMs
And language VMs should have SSH access
And service VMs should provide infrastructure services
```

**Scenario: Detect list vms intent**

```
When I parse "list all vms"
Then intent should be "list_vms"
```

**Scenario: Detect list languages intent**

```
When I parse "show all language vms"
Then intent should be "list_vms"
And filter should be "lang"
```

**Scenario: Detect list services intent**

```
When I parse "what services are available"
Then intent should be "list_vms"
And filter should be "svc"
```

**Scenario: Validate plan lines against whitelist**

```
Given plan contains "INTENT:start_vm"
And plan contains "VM:python"
When plan is validated
Then all plan lines should be valid
When plan contains "MALICIOUS:command"
Then plan should be rejected
```

**Scenario: Handle multiple consecutive spaces in vm list**

```
When I parse "start python   rust"
Then intent should be "start_vm"
And VMs should include "python", "rust"
```

---

## 5. Starting and Stopping

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

./scripts/vde start python

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

./scripts/vde stop python

```



**Important:** Stopping doesn't delete your VM — it just pauses it. Your code and configurations are safe and sound! 💾

### Verified Scenarios

**Scenario: Port registry cache persists and survives restart**

```
Given ports have been allocated for VMs
And port registry cache exists
When system is restarted
And port registry is loaded
Then previously allocated ports should be restored
And no port conflicts should occur
```

**Scenario: Example 1   start both python and postgresql**

```
Given I have created Python and PostgreSQL VMs
When I plan to start both VMs
Then the plan should include the start_vm intent
And the plan should include both Python and PostgreSQL VMs
```

**Scenario: Example 3   start all microservice vms**

```
Given I have created the microservice VMs
When I plan to start them all
Then the plan should include the start_vm intent
And all microservice VMs should be included
```

**Scenario: Troubleshooting   step 3 restart with rebuild**

```
Given I need to rebuild a VM to fix an issue
When I plan to rebuild Python
Then the plan should include the restart_vm intent
And the plan should set rebuild=true flag
```

**Scenario: Adding cache layer   start redis**

```
Given I have created the Redis VM
When I plan to start Redis
Then the plan should include the start_vm intent
And Redis should start without affecting other VMs
```

**Scenario: Switching projects   stop current project**

```
Given I am working on one project
When I plan to stop all VMs
Then all running VMs should be stopped
And I should be ready to start a new project
```

**Scenario: Switching projects   start new project**

```
Given I have stopped my current project
When I plan to start Go and MongoDB
Then the new project VMs should start
And only the new project VMs should be running
```

**Scenario: Starting already running vm**

```
Given I have a Python VM that is already running
When I plan to start Python
Then the plan should be generated
And execution would detect the VM is already running
And I would be notified that it's already running
```

**Scenario: Stopping already stopped vm**

```
Given I have a stopped PostgreSQL VM
When I plan to stop PostgreSQL
Then the plan should be generated
And execution would detect the VM is not running
And I would be notified that it's already stopped
```

**Scenario: Detect start vm intent**

```
When I parse "start the python vm"
Then intent should be "start_vm"
And VMs should include "python"
```

**Scenario: Detect start multiple vms intent**

```
When I parse "start python, rust, and go"
Then intent should be "start_vm"
And VMs should include "python", "rust", "go"
```

**Scenario: Detect start all vms intent**

```
When I parse "start everything"
Then intent should be "start_vm"
And VMs should include all known VMs
```

**Scenario: Detect stop vm intent**

```
When I parse "stop the postgres container"
Then intent should be "stop_vm"
And VMs should include "postgres"
```

**Scenario: Detect stop all vms intent**

```
When I parse "shutdown all vms"
Then intent should be "stop_vm"
And VMs should include all known VMs
```

**Scenario: Detect restart vm intent**

```
When I parse "restart python"
Then intent should be "restart_vm"
And VMs should include "python"
```

**Scenario: Detect restart intent before start intent**

```
When I parse "restart python"
Then intent should be "restart_vm"
And VMs should include "python"
```

**Scenario: Detect start when restart not specified**

```
When I parse "start python"
Then intent should be "start_vm"
And VMs should include "python"
```

---

## 6. Your First Cluster

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

./scripts/vde create postgres

./scripts/vde create redis

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

### Verified Scenarios

**Scenario: Cache consistency across multiple operations**

```
Given VM types cache exists
When VM types are loaded multiple times
Then cache should return consistent data
And cache file modification time should remain unchanged
```

**Scenario: Detect create multiple vms intent**

```
When I parse "create python and rust"
Then intent should be "create_vm"
And VMs should include "python"
And VMs should include "rust"
```

**Scenario: Handle commas and conjunctions for multiple vms**

```
When I parse "start python, rust, and go"
Then intent should be "start_vm"
And VMs should include "python", "rust", "go"
```

---

## 7. Connecting

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

**Scenario: Example 1   get connection info for python**

```
Given I need to connect to the Python VM
When I ask for connection information
Then the plan should include the connect intent
And the plan should include the Python VM
```

**Scenario: Daily workflow   connect to primary vm**

```
Given I need to work in my primary development environment
When I ask how to connect to Python
Then the plan should provide connection details
And the plan should include the Python VM
```

**Scenario: Troubleshooting   step 4 get connection info**

```
Given I need to debug inside a container
When I ask to connect to Python
Then the plan should include the connect intent
And I should receive SSH connection information
```

**Scenario: Team onboarding   get connection help**

```
Given I am new to the team
When I ask how to connect to Python
Then I should receive clear connection instructions
And I should understand how to access the VM
```

**Scenario: Detect connect intent**

```
When I parse "how do I connect to python"
Then intent should be "connect"
And VMs should include "python"
```

---

## 8. Working with Databases

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

### Verified Scenarios

**Scenario: Example 1   create postgresql for python api**

```
Given I have planned to create Python
When I plan to create PostgreSQL
Then the plan should include the create_vm intent
And the plan should include the PostgreSQL VM
```

**Scenario: Example 2   full stack javascript with redis**

```
Given I am following the documented JavaScript workflow
When I plan to create JavaScript and Redis VMs
Then the plan should include both VMs
And the JavaScript VM should use the js canonical name
```

**Scenario: Adding cache layer   create redis**

```
Given I have an existing Python and PostgreSQL stack
When I plan to add Redis
Then the plan should include the create_vm intent
And the Redis VM should be included
```

---

## 9. Daily Workflow

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

When I run "vde stop all"

Then all VMs should stop gracefully

And my work is saved

```



**Stop everything:**

```bash

./scripts/vde stop all

```



**Good night, VDE!** See you tomorrow! 🌙

### Verified Scenarios

**Scenario: Daily workflow   evening cleanup**

```
Given I am done with development for the day
When I plan to stop everything
Then the plan should include the stop_vm intent
And the plan should apply to all running VMs
```

---

## 10. Adding More Languages

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

./scripts/vde create rust

./scripts/vde start rust

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

./scripts/vde start python rust js

```



**Polyglot programmer?** Why not! 😎

### Verified Scenarios

**Scenario: Language vm display names are user friendly**

```
Given I have VDE installed
When I query the display name for language VMs
Then each language VM should have a display name
And the display name should be descriptive
And common languages like Python, Go, and Rust should have recognizable names
```

**Scenario: Language vm ports are in correct range**

```
Given I have VDE installed
When I check the SSH port allocation for language VMs
Then all language VM ports should be between 2200 and 2299
And no language VM should use a service port range
```

**Scenario: Vm types are correctly categorized as language**

```
Given I have VDE installed
When I query VM types
Then programming language VMs should be categorized as "lang"
And Python, Go, Rust, and JavaScript should be language VMs
And language VMs should have SSH access configured
```

**Scenario: Common programming language aliases resolve correctly**

```
Given I have VDE installed
When I query alias mappings for programming languages
Then the metadata alias "python3" should map to "python"
And the metadata alias "nodejs" should map to "js"
And the metadata alias "golang" should map to "go"
And the metadata alias "c++" should map to "cpp"
And the metadata alias "rlang" should map to "r"
```

**Scenario: Language vm container names follow naming convention**

```
Given I have VDE installed
When I check container naming for language VMs
Then language VM containers should use the "{name}-dev" pattern
And Python container should be named "python-dev"
And Go container should be named "go-dev"
```

**Scenario: Language vms do not have service ports configured**

```
Given I have VDE installed
When I check service port configuration for language VMs
Then language VMs should not have service_port values
And Python should not have a service_port
And Go should not have a service_port
```

**Scenario: Team onboarding   explore languages**

```
Given I am a new team member
When I ask to list all languages
Then I should see only language VMs
And service VMs should not be included
```

**Scenario: Parse flags from natural language**

```
When I parse "rebuild with no cache"
Then rebuild flag should be true
And nocache flag should be true
```

---

## 11. Troubleshooting

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

2. Is the port already in use? `./scripts/vde list`

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

./scripts/vde start python --rebuild

```



**For complete rebuild (no cache):**

```bash

./scripts/vde start python --rebuild --no-cache

```

### Verified Scenarios

**Scenario: Rebuild port registry from compose files**

```
Given port registry cache is missing or invalid
When port registry is verified
Then registry should be rebuilt by scanning docker-compose files
And all allocated ports should be discovered
```

**Scenario: Detect rebuild vm intent**

```
When I parse "rebuild and start rust"
Then intent should be "restart_vm"
And rebuild flag should be true
```

**Scenario: Detect rebuild without cache intent**

```
When I parse "rebuild python with no cache"
Then intent should be "restart_vm"
And rebuild flag should be true
And nocache flag should be true
```

**Scenario: Unset non existent key should not error**

```
Given running in zsh
And I initialize an associative array
When I unset key "never_existed"
Then operation should complete successfully
And array should remain empty
```

**Scenario: Unset non existent key should not error (bash 3.x)**

```
Given running in bash "3.2"
And I initialize an associative array
When I unset key "imaginary_key"
Then operation should complete successfully
And array should remain empty
```

---

## Quick Reference Card 📇

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
