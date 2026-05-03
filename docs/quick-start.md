# QUICK-START
<!-- @shared-law (Sovereign Law) -->
# Quick Start (Sovereign Baseline 1.5.2)

Get up and running with VDE in minutes.

[← Back to README](../README.md)

---

## First-Time Setup

1. **Verify Prereqs**: Ensure the **Unyielding Tetrad** (Zsh 5.0+, Git, Docker, and SSH) is installed. 
   - *Windows Users*: You MUST use **WSL2** (run `wsl --install` in PowerShell) to create your Linux sanctuary first.
2. **Clone the Baseline**:
   ```zsh
   git clone https://github.com/dderyldowney/vde-system.git ~/vde
   cd ~/vde
   ```
3. **Take the Path of the Foundling**:
   ```zsh
   bin/vde path-of-the-foundling
   ```

---

## What Just Happened?

When you ran `bin/vde path-of-the-foundling`:
1. **Interactive Induction**: A step-by-step ritual guided you through initial configuration.
2. **Infrastructure Smelting**: `vde init` was executed automatically, creating networks and enforcing permissions.
3. **Identity Forgery**: Your unique `vde_student` SSH identity key was generated and primed.
4. **Foundation Building**: The foundational `vde-base` image was built and baked with your identity.
5. **Certification**: Your first Spoke was created and ignited to certify the Transversal Bridge.

## Daily Workflow

1. **Ignite & Enter**: 
   ```zsh
   vde start python && vde enter python
   ```
2. **Code**: You are now the `devuser`. Work in `$HOME/workspace/`. This directory is **persistently synced** to `projects/python` on your Hub (host machine).
3. **Persist**: Anything saved in `$HOME/workspace/` survives even if you `vde rebuild` the Spoke.
4. **Quench**: 
   ```zsh
   vde stop python
   ```

---

## Next Steps

- **User Guide**: Read the full [USER_GUIDE.md](../USER_GUIDE.md) for advanced rituals.
- **Foundling Guide**: Read [docs/FOUNDLING_GUIDE.md](./FOUNDLING_GUIDE.md) for a simplified manual.
- **Reference**: See [Command Reference](./command-reference.md) for all rituals.

---

[← Back to README](../README.md)

*[Home](../README.md) | [Quick Start](./quick-start.md) | [Documentation](./)*
