# VDE INSTALLATION
<!-- @armor (Installation Ritual) -->
# The Installation Ritual (1.5.6)

Welcome, Foundling. To ignite your own Forge and walk the path of the VDE, you must first secure the **Unyielding Tetrad** on your host machine. This process establishes and certifies your **Sovereign Baseline 1.5.6**.

---

## 1. One-Command Install (The Fast Path)

Run this in any terminal (bash or zsh):

```zsh
bash <(curl -sL https://raw.githubusercontent.com/dderyldowney/vde-system/stable/scripts/bootstrap.sh)
```

> **📂 Where should your code live? Decide now with `VDE_PROJECTS_DIR`.**
> `VDE_PROJECTS_DIR` is the **Projects base** — the directory under which VDE creates a per-VM subfolder (`<base>/<alias>`) that is mounted into each environment as your workspace. Set it and your code lives where **you** want (e.g. `~/Projects`, `~/GitHub`) instead of buried inside the VDE install; point it at an existing same-named folder and VDE adopts and coexists with it, never overwriting your work.
> **This installer is non-interactive — it never prompts.** If you don't pass `--projects-dir` (or pre-export `VDE_PROJECTS_DIR`), you silently get the default `<VDE>/projects`. Install is your one unattended chance to choose; otherwise change it later with `vde set-projects-dir <path>`.
>
> ```zsh
> # Pass it explicitly (the flag wins if both are set):
> bash <(curl -sL https://raw.githubusercontent.com/dderyldowney/vde-system/stable/scripts/bootstrap.sh) --projects-dir ~/Projects
>
> # Or pre-export it into the environment:
> VDE_PROJECTS_DIR=~/Projects bash <(curl -sL https://raw.githubusercontent.com/dderyldowney/vde-system/stable/scripts/bootstrap.sh)
> ```

This single command will:

1. **Check the 4 pillars** (Zsh, Git, Docker, SSH) and tell you exactly what to install if anything's missing.
2. **Clone VDE** from the `stable` branch.
3. **Launch the onboarding ritual** (`path-of-the-foundling`) which sets up SSH keys, builds the base image, and walks you through your first spoke.
4. **Add VDE to your PATH** automatically.

If anything is missing, the script prints the one command you need to fix it. Re-run the bootstrap command after installing.

---

## 2. Platform-Specific Prerequisites (If You Prefer Manual Setup)

The 4 pillars below are required. The bootstrap script checks for all of them automatically — but if you want to install them yourself first:

| Pillar | Requirement | Purpose |
| :--- | :--- | :--- |
| **I. Zsh** | Version 5.0+ | The Voice of the Tribe. **ZSH ONLY.** |
| **II. Git** | Version 2.30+ | The Chronicler of your history. |
| **III. Docker** | Desktop / Engine | The World-Forge for your Spokes. |
| **IV. SSH** | Agent Active | The Transversal Bridge to your Spokes. |

### 🪟 Windows (The WSL2 Path)

1. **Enable WSL2**: Open PowerShell as Administrator and run `wsl --install`. Restart your computer.
2. **Install Ubuntu**: If it didn't install automatically, find "Ubuntu" in the Microsoft Store and launch it.
3. **Install Docker Desktop**: Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop). In Settings, ensure **"Use the WSL 2 based engine"** is enabled and your Ubuntu distribution is checked under **Resources > WSL Integration**.
4. **Enter your Shell**: Open the "Ubuntu" terminal. You are now in a Linux environment.
5. **Install Prereqs**:

    ```zsh
    sudo apt update && sudo apt install zsh git openssh-client direnv -y
    ```

### 🍎 macOS

1. **Install Docker Desktop**: Download and install [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop).
2. **Install Git**: Open Terminal and run `git --version` (macOS will prompt to install command line tools if missing).
3. **Zsh**: macOS uses Zsh by default. Verify with `zsh --version`.
4. **SSH**: OpenSSH is built into macOS. Verify with `ssh -V`.

### 🐧 Linux

1. **Install Docker**: Follow the [official engine installation](https://docs.docker.com/engine/install/) for your distro.
2. **Install Prereqs**: Use your package manager to install `zsh`, `git`, and `openssh-client` (e.g., `sudo apt install zsh git openssh-client`).

---

## 3. Manual Installation

If you prefer to set everything up yourself:

```zsh
git clone -b stable https://github.com/dderyldowney/vde-system.git ~/VDE
cd ~/VDE
bin/vde path-of-the-foundling
```

The `path-of-the-foundling` ritual is the onboarding mechanism. It performs `vde init` automatically, sets up your `vde_student` SSH identity, builds the base image, and walks you through creating your first Python spoke.

### 📂 Choosing Your Projects Base

Your work lives under a single **Projects base**, and each Spoke's alias becomes its own subfolder beneath it (`<base>/<alias>`). That subfolder is mounted straight into the Spoke at `/home/devuser/workspace`, so what you write inside a Spoke lands in the base on your Hub.

**The prompt.** During onboarding, `path-of-the-foundling` (and `vde init`) pauses to ask where your Projects base should live. The default is `$VDE_ROOT/projects`, nestled inside the Forge. But you may name **any directory you control** — for example `$HOME/Projects` — even one that lives wholly outside the Forge. `~` and environment variables are expanded, the directory is created if it does not yet exist, and it must be writable by you.

**Non-interactive paths.** To skip the prompt — in scripts, in CI, or when you already know your mind — supply the base ahead of time:

```zsh
vde init --projects-dir <path>     # pass it explicitly
VDE_PROJECTS_DIR=<path> vde init   # or export it into the environment
```

Either way, the base is recorded as an absolute path in `.env` under the key `VDE_PROJECTS_DIR`.

**Your existing files are sacred.** VDE never overwrites what is already there. Point it at a folder that already holds your work and it simply adopts it, only ever adding its own `<base>/<alias>` subfolders alongside what you keep.

**Changed your mind later?** Re-point the base at any time with:

```zsh
vde set-projects-dir <new-path>
```

This safely moves your existing per-alias folders to the new base (skipping any name collisions, never overwriting or deleting), updates the `.env` record, and regenerates the Spoke configs. Your Spokes pick up the new location on their next start — no rebuild required.

## 4. Contributor Setup (The Forge)

Only needed for developing VDE itself (running the Proof of Life / `behave`), not for using it.

- **direnv** is required. It loads the project-local `.venv` automatically when you `cd` into the repo.
- One-time setup:

```zsh
sudo apt install direnv python3-venv   # Debian/Ubuntu
brew install direnv                    # macOS (venv ships with python3)
# then hook direnv into ~/.zshrc: eval "$(direnv hook zsh)"
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
direnv allow
```

---

**This is the Way.**
