# FOUNDLING GUIDE
<!-- @shared-law (Sovereign Law) -->
# Path of the Foundling: A Student's Guide to VDE

Welcome, Foundling. You have entered the Forge. This guide explains the "Rituals" (commands) and "Creed" (rules) you will follow to learn the ways of engineering.

---

## 1. Why the Forge?
The VDE (Virtual Development Environment) provides you with "Spokes" (isolated containers). This means:
- Your computer stays clean. No installing Python, Node, or Postgres directly.
- Everything is disposable. If you break a Spoke, you just "Re-forge" (rebuild) it.
- You learn professional tools (Docker, Zsh, SSH) from day one.

## 2. Core Rituals (The Commands)

### The Path of the Foundling (Interactive Induction)
When you first clone this repository, you must begin your journey:
```zsh
vde path-of-the-foundling
```
This interactive script will guide you through:
- **Ignition**: Setting up your SSH keys and creating the networks.
- **Spine Check**: Verifying that your Hub is ready (Zsh, Git, Docker, and SSH).
- **First Spoke**: Creating your very first Python workspace automatically.

### Creating a Spoke (The Forge)
If you followed the Path above, your Python Spoke was already created. To create a workspace for another specific language:
```zsh
vde create <alias>
```

### Starting and Entering (The Handshake)
To start your Spoke and step inside:
```zsh
vde start python
vde enter python
```
Once inside, you are in a pure Linux environment, ready to code.

### Closing the Spoke (The Quench)
When your study session is done:
```zsh
vde stop python
```

## 3. The Beskar Rules (Your Creed)
1. **Never use Bash**: We speak ZSH. All your scripts must start with `#!/usr/bin/env zsh`.
2. **Born Ready**: Your Spokes should have everything they need when they are created. 
3. **The Proof of Life**: We don't believe a system works; we prove it. Run the tests frequently.

## 4. Next Steps
- Follow the `USER_GUIDE.md` for more advanced rituals.
- Use `vde help` to see all available commands.

This is the Way.
