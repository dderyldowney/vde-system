# VDE INSTALLATION
<!-- @armor (Installation Ritual) -->
# The Installation Ritual (1.5.4)

Welcome, Foundling. To ignite your own Forge and walk the path of the VDE, you must first secure the **Unyielding Tetrad** on your host machine. This process establishes and certifies your **Sovereign Baseline 1.5.4**.

---

## 1. Prerequisites (The Unyielding Tetrad)

Before you begin, ensure these four pillars are active. Once you are in a Zsh terminal (native or WSL2), the VDE rituals are universal across Linux, macOS, and Windows.

| Pillar | Requirement | Purpose |
| :--- | :--- | :--- |
| **I. Zsh** | Version 5.0+ | The Voice of the Tribe. **ZSH ONLY.** |
| **II. Git** | Version 2.30+ | The Chronicler of your history. |
| **III. Docker** | Desktop / Engine | The World-Forge for your Spokes. |
| **IV. SSH** | Agent Active | The Transversal Bridge to your Spokes. |

### 🏁 Platform-Specific Setup

#### 🪟 Windows (The WSL2 Path)
For Windows users, the journey begins by creating a Linux sanctuary:
1.  **Enable WSL2**: Open PowerShell as Administrator and run `wsl --install`. Restart your computer.
2.  **Install Ubuntu**: If it didn't install automatically, find "Ubuntu" in the Microsoft Store and launch it.
3.  **Install Docker Desktop**: Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop). In Settings, ensure **"Use the WSL 2 based engine"** is enabled and your Ubuntu distribution is checked under **Resources > WSL Integration**.
4.  **Enter your Shell**: Open the "Ubuntu" terminal. You are now in a Linux environment.
5.  **Install Prereqs**:
    ```zsh
    sudo apt update && sudo apt install zsh git openssh-client -y
    ```

#### 🍎 macOS
1.  **Install Docker Desktop**: Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop).
2.  **Install Git**: Open Terminal and run `git --version` (macOS will prompt to install command line tools if missing).
3.  **Zsh**: macOS uses Zsh by default. Verify with `zsh --version`.
4.  **SSH**: OpenSSH is built into macOS. Verify with `ssh -V`.

#### 🐧 Linux
1.  **Install Docker**: Follow the [official engine installation](https://docs.docker.com/engine/install/) for your distro.
2.  **Install Prereqs**: Use your package manager to install `zsh`, `git`, and `openssh-client` (e.g., `sudo apt install zsh git openssh-client`).

---

## 2. Installation Sequence (The Fast Path)

Once your prerequisites are verified and you are in a **Zsh shell**, the journey is universal:

### Step 1: Clone the Baseline
```zsh
git clone -b stable https://github.com/dderyldowney/vde-system.git ~/VDE
cd ~/VDE
```

### Step 2: Take the Path of the Foundling (MANDATORY)
The `path-of-the-foundling` ritual is the **unique mechanism** for initial configuration and system certification. It will guide you through the hydration of your Forge, perform the `vde init` ritual automatically, and teach you the lifecycle of the Beskar.

```zsh
bin/vde path-of-the-foundling
```

**This ritual automates:**
1.  **Bootstrap**: Generating your `vde_student` SSH identity key.
2.  **Initialization (`init`)**: Hydrating core infrastructure, networks, and registries.
3.  **Certification**: Forging and entering your first development Spoke.
4.  **Sentinel Activation**: Installing the Git hooks that guard the Rule Spine.

---

## 3. Post-Installation

Add the VDE rituals to your shell's environment to ensure they are available from anywhere:

```zsh
echo 'export PATH="$HOME/vde/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**This is the Way.**
