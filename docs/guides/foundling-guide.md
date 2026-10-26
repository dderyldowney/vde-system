# FOUNDLING GUIDE
<!-- @shared-law (Sovereign Law) -->
# Path of the Foundling: A Student's Guide to VDE (1.5.6)

Welcome, Foundling. You have entered the Forge. This guide explains the "Rituals" (commands) and "Creed" (rules) you will follow to learn the ways of engineering within the **Sovereign Baseline (1.5.6)**.

---

## 1. Why the Forge?
The VDE (Virtual Development Environment) provides you with "Spokes" (isolated containers). This means:
- Your computer stays clean. No installing Python, Node, or Postgres directly.
- Everything is disposable. If you break a Spoke, you just "Re-forge" (rebuild) it.
- You learn professional tools (Docker, Zsh, SSH) from day one.

## 2. The Onboarding Ritual (The First Strike)

**One command sets up everything:**

```zsh
bash <(curl -sL https://raw.githubusercontent.com/dderyldowney/vde-system/stable/scripts/bootstrap.sh)
```

This checks your system, clones VDE, and launches the onboarding. If anything's missing, it tells you exactly what to install.

**What this ritual does:**
- **Ignition**: Performs the `vde init` ritual automatically, setting up your `vde_student` SSH keys and creating the networks.
- **Spine Check**: Verifies that your Hub is ready (Zsh, Git, Docker, and SSH).
- **First Spoke**: Guides you through forging and entering your very first Python workspace.

## 3. Core Rituals (The Commands)

### Creating a Spoke (The Forge)
To create a workspace for a specific language or service:
```zsh
vde create <alias>
```

### Starting and Entering (The Handshake)
To start your Spoke and step inside as the `devuser`:
```zsh
vde start <alias>
vde enter <alias>
```
Once inside, you operate at `$HOME/workspace/`. This directory is **persistently synced** to `projects/<alias>` on your host computer, ensuring your work survives if you rebuild the Spoke image.

> **Where your projects live:** During onboarding (`vde path-of-the-foundling` / `vde init`), the Forge asks you to choose a **Projects base** — the folder that every Spoke's workspace syncs beneath. Press Enter to accept the default, `projects/` inside the Forge, or type a path of your own.
>
> The base can live **anywhere you control**, inside or outside the Forge — `$HOME/Projects`, `~/code/vde`, or a directory where you already keep your work. The Forge expands `~` and environment variables, creates the folder if it does not exist, and asks only that it be writable. Each Spoke alias then gets its own subfolder beneath it: `<base>/python`, `<base>/rust`, and so on, mounted inside the Spoke at `$HOME/workspace/`.
>
> **The Forge never harms what is already there.** It only *adds* its own `<base>/<alias>` subfolders. If a folder of that name already exists, the Forge **adopts** it — uses it exactly as it stands — and never overwrites or deletes your files. So you may safely point the Forge at a directory that already holds your projects.
>
> Prefer not to answer the prompt? Set it non-interactively with `vde init --projects-dir <path>` or by exporting `VDE_PROJECTS_DIR`. The Forge stores your choice as an absolute path in the `VDE_PROJECTS_DIR` key of your `.env`. To move the base later, run `vde set-projects-dir <path>`: your existing alias folders move with it (name collisions are skipped, never clobbered) and Spokes use the new spot on their next start — no rebuild. And when you eventually run `vde nuke`, your Projects base and your `data/` are never deleted; the Forge even offers to relocate them to safety first.

### Closing the Spoke (The Quench)
When your study session is done:
```zsh
vde stop <alias>
```

## 4. The Beskar Rules (Your Creed)
1. **Never use Bash**: We speak ZSH. All your scripts must start with `#!/usr/bin/env zsh`.
2. **Born Ready**: Your Spokes should have everything they need when they are created. 
3. **The Proof of Life**: We don't believe a system works; we prove it. The Forge is certified by the Heartbeat.

This is the Way.
