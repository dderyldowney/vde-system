# VDE Installation & Configuration Guide

Welcome, Foundling! This guide will walk you through the **Installation Ritual** for the Virtualized Development Environment (VDE). Follow these steps to forge your sovereign development ecosystem.

---

## 1. Prerequisites (The Warrior's Rights)

Before you ignite the Forge, you must have the following four pillars installed on your host machine.

### Pillar I: Docker Desktop (The World-Forge)
Docker is the engine that runs your isolated development Spokes.
- **macOS:** [Download Docker Desktop for Mac](https://www.docker.com/products/docker-desktop).
- **Windows:** [Download Docker Desktop for Windows](https://www.docker.com/products/docker-desktop) (Requires WSL 2).
- **Linux:** [Install Docker Engine](https://docs.docker.com/engine/install/).

### Pillar II: Git (The Chronicler)
Git is required to pull the VDE Intel from the repository.
- **macOS:** Comes pre-installed. Update via `brew install git`.
- **Windows:** [Download Git for Windows](https://git-scm.com/download/win).
- **Linux:** `sudo apt install git`.

### Pillar III: Zsh 5.0+ (The Voice of the Tribe)
VDE is forged strictly in Zsh. **Bash is prohibited.**
- **macOS:** Default shell since Catalina. Check with `zsh --version`.
- **Linux/WSL:** `sudo apt install zsh`.

### Pillar IV: SSH (The Transversal Bridge)
The VDE Hub uses the **Sovereign Baseline** to connect you to your Spokes.
- **Requirement:** An active SSH client and agent on your host machine.

---

## 2. Installation Ritual (Step-by-Step)

### Step 1: Clone the Beskar Hub
Open your terminal (Zsh) and clone the VDE repository.

```zsh
git clone https://github.com/dderyldowney/vde-system.git ~/vde
cd ~/vde
```

### Step 2: Add VDE to your PATH
To call `vde` from anywhere, add the `bin` directory to your `.zshrc`.

```zsh
echo 'export PATH="$HOME/vde/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Ignite the Forge (The One True Way)
Run the `init` command. This single ritual hydrates your entire infrastructure (directories, networks, and SSH identities).

```zsh
vde init
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
