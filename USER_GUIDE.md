<p align="center"><img src="docs/imgs/vde-system-logo.png" alt="Virtualized Development Environment System Logo"></p>

# VDE User Guide: The Student's Path

Welcome to the **Virtualized Development Environment (VDE)**. This guide is your map to forging a sovereign development ecosystem where you can learn, build, and experiment without cluttering your host computer.

**Every workflow in this guide is an Executable Specification.** That means we don't just "hope" these steps work; we mathematically prove they work using our automated testing suite. Look for the **Verified Scenario** boxes to see the storyline that drives our development.

---

## Table of Contents

*💡 **Tip:** Click the ▶ triangle next to any section title below to expand or collapse that section.*

1. [1. Installation & Prerequisites](#1.-installation)
2. [2. Your First VM: The Initial Strike](#2.-your-first-vm)
3. [3. Connecting & Coding](#3.-connecting-to-your-vm)
4. [4. Understanding the Workspace](#4.-understanding-your-workspace)
5. [5. The Daily Rhythm: Start, Code, Stop](#5.-daily-rhythm)
6. [6. Exploring New Languages](#6.-exploring-languages)
7. [7. Working with Databases](#7.-databases)
8. [8. Troubleshooting](#8.-troubleshooting)
9. [9. Reference: Available Commands & VMs](#9.-reference)

---

<details id="1.-installation" data-section="1. Installation & Prerequisites">
<summary><h2>1. Installation & Prerequisites</h2></summary>

Before you can ignite the Forge, you need four core pillars installed on your machine.

### The Four Pillars (The Tetrad)

| Pillar | Requirement | Purpose |
| :--- | :--- | :--- |
| **I. Docker Desktop** | Latest Version | The engine that runs your isolated environments. |
| **II. Git** | Latest Version | Downloads the VDE system and tracks your code. |
| **III. Zsh** | Version 5.0+ | The mandatory shell for all VDE operations. |
| **IV. SSH** | Agent Active | The bridge that connects your host to the VMs. |

---

### 🍎 For macOS Users

1.  **Zsh:** You're already set! macOS has used Zsh by default since Catalina.
2.  **Homebrew (Recommended):** Open **Terminal** and run:
    `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
3.  **Git:** Run `brew install git`.
4.  **Docker Desktop:** [Download for Mac](https://www.docker.com/products/docker-desktop). Choose "Apple Chip" for M1/M2/M3 or "Intel Chip" for older Macs.

### 🪟 The Windows Frontier (WSL 2)

To walk the Way on Windows, you must build a sanctuary that speaks the **Language of the Tribe**.

1.  **WSL 2 (Mandatory):** Open **PowerShell as Administrator** and run `wsl --install`. Restart your machine to temper the changes.
2.  **The Language (Zsh):** Inside your WSL terminal, install Zsh and Git:
    `sudo apt update && sudo apt install zsh git curl -y`
    Set Zsh as default: `chsh -s $(which zsh)`.
3.  **The World-Forge (Docker):** [Download Docker Desktop](https://www.docker.com/products/docker-desktop). In Settings > Resources > WSL Integration, enable integration for your specific WSL distribution.
4.  **The Bridge (SSH):** Add `eval $(ssh-agent -s) > /dev/null` to your `~/.zshrc` inside WSL to ensure the agent is ignited.
5.  **Path Sovereignty:** **CRITICAL:** Clone VDE into the Linux filesystem (e.g., `~/vde`). Storing it on the Windows filesystem (`/mnt/c/...`) will cause severe performance degradation and break SSH key permissions.

### 🐧 For Linux Users

1.  **Zsh:** Run `sudo apt install zsh` (Debian/Ubuntu) or your distro's equivalent.
2.  **Git:** Run `sudo apt install git`.
3.  **Docker:** Follow the [Official Docker Engine Install Guide](https://docs.docker.com/engine/install/).

---

### Final Step: Clone & Init

**🛡️ The Sovereign Record:** The default branch for this repository is `develop` (**The Anvil**). For the stable, certified **Sovereign Baseline** (**Production**), ensure you clone using the `-b stable` flag as shown below.

Once the pillars are active, open your **Zsh** terminal and run:

```zsh
# Clone the repository
git clone -b stable https://github.com/dderyldowney/vde-system.git ~/vde
cd ~/vde

# Add VDE to your PATH
echo 'export PATH="$HOME/vde/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Take the Path of the Foundling (Interactive Onboarding)
vde path-of-the-foundling
```

</details>

<details id="2.-your-first-vm" data-section="2. Your First VM">
<summary><h2>2. Your First VM: The Initial Strike</h2></summary>

Now that the Forge is ignited, let's create your first development jail. We'll start with Python.

### Verified Scenario: Spoke Creation
> **Scenario:** Lifecycle Step 2 - Spoke Creation and Ignition
> **Given** I have a valid VM definition for "python"
> **When** I execute `vde create python`
> **Then** the Docker image "vde-python" should exist on the Hub

**Try it yourself:**
```zsh
vde create python
```
This command builds a clean, isolated Python environment. It might take a few minutes the first time as it downloads the base OS.

</details>

<details id="3.-connecting-to-your-vm" data-section="3. Connecting & Coding">
<summary><h2>3. Connecting & Coding</h2></summary>

Once a VM is created, you need to start it and step inside.

### Verified Scenario: Connecting
> **Scenario:** Lifecycle Step 2 (Continued)
> **When** I execute `vde start python`
> **Then** a container named "vde-python" should be running
> **And** the SSH bridge to "python" should be established

**Execution:**
```zsh
vde start python
vde enter python
```
You are now "inside" the VM. Your prompt will change, and you'll have access to a clean workspace at `~/workspace`.

**To Leave:** Type `exit` or press `Ctrl+D`.

</details>

<details id="4.-understanding-your-workspace" data-section="4. Understanding the Workspace">
<summary><h2>4. Understanding the Workspace</h2></summary>

VDE keeps everything organized in your `~/vde` directory:

| Directory | Purpose |
| :--- | :--- |
| `projects/` | **YOUR CODE GOES HERE.** This folder is shared with your VMs. |
| `data/` | Database data (Postgres, Redis, etc.). It survives even if you delete the VM. |
| `configs/` | The internal blueprints for your environments. |
| `bin/` | The `vde` commands you use every day. |

**Important:** Always save your code in `projects/<vm-name>/`. If you save it anywhere else inside the VM, it might be lost if the VM is rebuilt.

</details>

<details id="5.-daily-rhythm" data-section="5. The Daily Rhythm">
<summary><h2>5. The Daily Rhythm: Start, Code, Stop</h2></summary>

### Verified Scenario: A Typical Study Session
> **Scenario:** A Typical Study Session
> **When** I execute `vde start python`
> **Then** I can `vde enter python` and run `python3 --version`
> **When** I am done, I execute `vde stop python`

**Daily Workflow:**
1.  **Open Terminal** (Zsh).
2.  **Start your lab:** `vde start python`
3.  **Code:** `vde enter python`
4.  **Cleanup:** `vde stop python` (or `vde stop all` if you have many running).

</details>

<details id="6.-exploring-languages" data-section="6. Exploring New Languages">
<summary><h2>6. Exploring New Languages</h2></summary>

One of the best things about VDE is how easy it is to try something new.

### Verified Scenario: Exploring Go
> **Scenario:** Exploring a New Language
> **When** I execute `vde create go`
> **Then** I can `vde start go` and run `go version`
> **When** I am done, I can `vde rm go` to clean up

**Try a new language:**
```zsh
vde create rust
vde start rust
vde enter rust
```

</details>

<details id="7.-databases" data-section="7. Working with Databases">
<summary><h2>7. Working with Databases</h2></summary>

VDE isn't just for languages; it's for infrastructure too.

**Start a database cluster:**
```zsh
vde start python postgres redis
```
Your Python VM can now talk to the Postgres and Redis VMs automatically. The connection details are stored in your environment files at `env-files/`.

</details>

<details id="8.-troubleshooting" data-section="8. Troubleshooting">
<summary><h2>8. Troubleshooting</h2></summary>

| Issue | Resolution |
| :--- | :--- |
| **"Cannot connect to Docker"** | Ensure Docker Desktop is running and the whale icon is solid. |
| **"Port already allocated"** | VDE will try to rotate ports automatically. If it fails, run `vde stop all`. |
| **"Command not found: vde"** | Ensure you added VDE to your PATH (Step 2 of Installation). |
| **"Permission Denied"** | Run `vde init` to refresh your SSH identities. |

</details>

<details id="9.-reference" data-section="9. Reference">
<summary><h2>9. Reference: Available Commands & VMs</h2></summary>

### Essential Commands

| Command | Action |
| :--- | :--- |
| `vde path-of-the-foundling` | The recommended interactive onboarding ritual for new students. |
| `vde init` | Initialize or repair the VDE infrastructure. |
| `vde list` | Show all registered and running VMs. |
| `vde create <alias>` | Build a new VM image. |
| `vde start <alias>` | Start a VM container. |
| `vde enter <alias>` | Connect to a running VM (alias: `vde ssh`). |
| `vde stop <alias>` | Stop a running VM (use `all` for everything). |
| `vde remove <alias>` | Delete a VM container (alias: `vde rm`). |
| `vde rebuild <alias>` | Force a fresh build of a VM. |

### Active VM Types

| Languages | Services |
| :--- | :--- |
| `python`, `js`, `go`, `rust`, `cpp`, `c`, `java` | `postgres`, `redis`, `mongodb`, `mysql` |
| `elixir`, `flutter`, `haskell`, `kotlin`, `lua` | `nginx`, `rabbitmq`, `couchdb`, `jupyterlab` |
| `php`, `ruby`, `scala`, `swift`, `asm` | |

</details>

<script>
// Collapsible sections with TOC navigation
(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const STORAGE_KEY = 'vde-user-guide-last-section';
        function expandSection(sectionId) {
            const targetSection = document.querySelector(`details[id="${sectionId}"]`);
            if (targetSection) {
                targetSection.setAttribute('open', '');
                localStorage.setItem(STORAGE_KEY, sectionId);
                history.replaceState(null, null, '#' + sectionId);
                const allSections = document.querySelectorAll('details');
                allSections.forEach(function(section) {
                    if (section !== targetSection) {
                        section.removeAttribute('open');
                    }
                });
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
        let targetSectionId = window.location.hash.substring(1);
        if (!targetSectionId) {
            targetSectionId = localStorage.getItem(STORAGE_KEY) || '';
        }
        if (targetSectionId) {
            setTimeout(function() {
                expandSection(targetSectionId);
            }, 100);
        }
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
