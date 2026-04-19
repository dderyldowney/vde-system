# VDE Installation & Configuration Guide

Welcome, Foundling! This guide will walk you through the **Installation Ritual** for the Virtualized Development Environment (VDE). Follow these steps to forge your sovereign development ecosystem.

---

## 1. Prerequisites (The Warrior's Rights)

Before you ignite the Forge, you must have the following four pillars installed on your host machine.

### Pillar I: Docker Desktop (The World-Forge)
Docker is the engine that runs your isolated development Spokes.
- **macOS:** [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop).
- **Windows:** [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) (Requires WSL 2 and integration enabled).
- **Linux:** [Install Docker Engine](https://docs.docker.com/engine/install/).

### Pillar II: Git (The Chronicler)
Git is required to pull the VDE Intel from the repository.
- **macOS:** Comes pre-installed. Update via `brew install git`.
- **Windows:** Install inside WSL distribution: `sudo apt install git`.
- **Linux:** `sudo apt install git`.

### Pillar III: Zsh 5.0+ (The Voice of the Tribe)
VDE is forged strictly in Zsh. **Bash is prohibited.**
- **macOS:** Default shell since Catalina. Check with `zsh --version`.
- **Windows/Linux/WSL:** `sudo apt install zsh && chsh -s $(which zsh)` (Windows users: Must install inside WSL).

### Pillar IV: SSH (The Transversal Bridge)
The VDE Hub uses the **Sovereign Baseline** to connect you to your Spokes.
- **Requirement:** An active SSH client and agent on your host machine.
- **Windows Users:** Ensure `ssh-agent` is running inside WSL (add `eval $(ssh-agent -s)` to `~/.zshrc`).

---

## 2. Installation Ritual (Step-by-Step)

### Step 1: Clone the Beskar Hub
**🛡️ The Sovereign Record:** The default branch for this repository is `develop` (The Anvil). For the stable, certified **Sovereign Baseline** (Production), ensure you clone the `main` branch.

Open your terminal (Zsh) and clone the VDE repository.

```zsh
# Clone the stable Production branch (Sovereign Baseline)
git clone https://github.com/dderyldowney/vde-system.git ~/vde
cd ~/vde
```

### Step 2: Add VDE to your PATH
To call `vde` from anywhere, add the `bin` directory to your `.zshrc`.

```zsh
echo 'export PATH="$HOME/vde/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Sovereign Bootstrap (The Passport Ritual)
Execute the bootstrap ritual to generate your VDE SSH identity and prepare the Hub's credentials.

```zsh
vde-bootstrap
```

### Step 4: Ignite the Forge (The One True Way)
Run the `init` command. This single ritual hydrates your entire infrastructure (directories, networks, and internal caches).

```zsh
vde init
```

### Step 5: Install the Sentinels (Git Hooks)
Install the project git hooks to ensure every commit and push remains compliant with the Rule Spine.

```zsh
install-githooks
```

---

## 3. Configuration (Your First Spoke)

### Step 1: Forge a Spoke
Create a new VM for your preferred language (e.g., Python).

```zsh
vde create python
```

### Step 2: Start the Spoke
This builds the Docker image and starts the container.

```zsh
vde start python
```

### Step 3: Enter the Jail
Connect via **The Sovereign Baseline**.

```zsh
vde enter python
```

---

## 4. Verification (Proof of Life)

Verify your workspace is mounted correctly:

```zsh
# Inside the VM
ls ~/workspace
```

---

## 5. Troubleshooting (Protocol Blockades)

| Blockade | Resolution |
| :--- | :--- |
| **Docker Denied** | Ensure Docker Desktop is running. |
| **Zsh Missing** | Ensure `zsh --version` returns 5.0+. |
| **Handshake Fail** | Run `vde init` again to repair SSH configurations. |

**This is the Way.**
