# VDE Installation & Configuration Guide (v1.2.2)

Welcome, Foundling! This guide will walk you through the **Installation Ritual** for the Virtualized Development Environment (VDE). Follow these steps to forge your sovereign development ecosystem.

---

## 1. Prerequisites (The Warrior's Rights)

Before you ignite the Forge, you must have the following three pillars installed on your host machine.

### Pillar I: Docker Desktop (The World-Forge)
Docker is the engine that runs your isolated development Spokes.
- **macOS:** [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop) (Select Apple Chip or Intel Chip).
- **Windows:** [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) (Requires WSL 2).
- **Linux:** [Install Docker Engine](https://docs.docker.com/engine/install/) and [Post-install steps](https://docs.docker.com/engine/install/linux-postinstall/) (Add user to `docker` group).

### Pillar II: Git (The Chronicler)
Git is required to pull the VDE Intel (code) from the repository.
- **macOS:** Comes pre-installed. Update via `brew install git` if using [Homebrew](https://brew.sh/).
- **Windows:** [Download Git for Windows](https://git-scm.com/download/win).
- **Linux:** `sudo apt install git` (Debian/Ubuntu) or `sudo dnf install git` (Fedora).

### Pillar III: Zsh 5.0+ (The Voice of the Tribe)
VDE is forged strictly in Zsh. **Bash is prohibited.**
- **macOS:** Default shell since Catalina. Check with `zsh --version`.
- **Windows:** Install via [WSL 2](https://learn.microsoft.com/en-us/windows/wsl/install) (e.g., `sudo apt install zsh`).
- **Linux:** `sudo apt install zsh` (Debian/Ubuntu) or `sudo dnf install zsh` (Fedora).

---

## 2. Installation Ritual (Step-by-Step)

### Step 1: Clone the Beskar Hub
Open your terminal (Zsh) and clone the VDE repository into your preferred development directory.

```zsh
# Create a development directory if it doesn't exist
mkdir -p ~/dev && cd ~/dev

# Clone the VDE system
git clone https://github.com/dderyldowney/vde-system.git vde
cd vde
```

### Step 2: Add VDE to your PATH
To call `vde` from anywhere in your system, add the `bin` directory to your `.zshrc`.

```zsh
# Add to .zshrc
echo 'export PATH="$HOME/dev/vde/bin:$PATH"' >> ~/.zshrc

# Reload your configuration
source ~/.zshrc
```

### Step 3: Initial Handshake (Bootstrap)
Run the `list` command to initialize the internal cache and verify the **Unyielding Tetrad** (Zsh, Git, Docker, SSH).

```zsh
vde list
```

---

## 3. Configuration (Your First Spoke)

VDE is "Born Ready" (BTO). Configuration happens automatically when you create your first environment.

### Step 1: Forge a Language Spoke
Create a new VM for your preferred language (e.g., Python). VDE will automatically allocate a unique SSH port and generate an isolated SSH identity at `~/.ssh/vde/`.

```zsh
vde create python
```

### Step 2: Ignite the Spoke
This ritual builds the Docker image and starts the container.

```zsh
vde start python
```

### Step 3: Enter the Jail
Connect to your new environment via the **Sovereign Handshake**.

```zsh
vde enter python
```

---

## 4. Verification (Proof of Life)

Once inside the Spoke, verify your workspace is mounted correctly:

```zsh
# Inside the VM
ls ~/workspace
```

Any files you place in `~/dev/vde/projects/python/` on your host will appear here.

---

## 5. Troubleshooting (Protocol Blockades)

| Blockade | Resolution |
| :--- | :--- |
| **Docker Denied** | Ensure Docker Desktop is running and your user is in the `docker` group. |
| **SSH Port Conflict** | VDE automatically rotates ports. If a conflict persists, run `vde port rotate [alias]`. |
| **Zsh Missing** | Ensure `zsh --version` returns 5.0 or higher. |

**This is the Way.**
