# TROUBLESHOOTING
<!-- @shared-law (Sovereign Law) -->
# Troubleshooting (1.5.6)

Common issues and solutions for VDE in the **Sovereign Baseline (1.5.6)**.

[← Back to README](../../README.md)

---

## SSH Authentication Fails: "Permission denied (publickey)"

**Problem:** You try to connect but get "Permission denied (publickey)".

### Solution 1: Use the `vde` command (Recommended)

```zsh
# The canonical way to enter a Spoke:
vde enter go
```

### Solution 2: Verify the Identity Key is Loaded

VDE uses the `vde_student` key. Ensure it is in your host's SSH agent:

```zsh
ssh-add -l | grep vde_student
```
If not found, run:
```zsh
vde init
```

### Why this happens

Your Hub has a username (like `alex`). VDE Spokes use `devuser` as the internal account. When you run `ssh localhost`, SSH tries to log in as **your** Hub username. The `vde enter` command automatically handles the `devuser@` mapping and port resolution.

---

## Port Conflicts

**Problem:** A port is already in use, preventing Spoke ignition.

```zsh
# See what is using the port (e.g., 2203)
lsof -i :2203

# Stop the conflicting Spoke
vde stop python

# Or use the Tactical Sweep to clear all locks
vde-tactical-sweep.zsh
```

---

## SSH Agent Forwarding Issues

**Problem:** You cannot use Git or SSH between Spokes.

```zsh
# 1. Check if the agent is running on the Hub
echo $SSH_AUTH_SOCK

# 2. Verify the vde_student key is loaded
ssh-add -l

# 3. Run the Handshake Ritual to verify the bridge
vde dns-check python postgres
```

---

## Spoke Won't Start

**Problem:** A Spoke fails to ignite or crashes immediately.

```zsh
# 1. Check the logs
vde logs python

# 2. Re-smelt the image to factory baseline
vde rebuild python

# 3. Verify the Tetrad health
vde health
```

---

## VSCode Remote-SSH Connection Failures

**Problem:** VSCode cannot connect to a Spoke.

```zsh
# 1. Verify you can connect from the terminal
vde enter go

# 2. Ensure your Hub's SSH config includes the VDE vault:
# Your ~/.ssh/config should contain: Include ~/.ssh/vde/config

# 3. Open the correct folder in VSCode:
$HOME/workspace/
```

---

## Data Persistence

**Problem:** Your code disappeared after a rebuild.

**Solution:** Ensure you are saving work in `$HOME/workspace/`. Files saved outside this directory (e.g., in `/tmp` or `/etc`) are ephemeral and will be purged during a `vde rebuild`.

---

## `git checkout` Fails: "this operation must be run in a work tree"

**Problem:** `core.bare` in `.git/config` was flipped to `true` by something other than you.

**Immediate fix:**

```zsh
git config core.bare false
```

**Find out what did it (Linux audit watch, needs `sudo`):** a file watcher shows *when* the file changed, but only the kernel audit subsystem records *which process* wrote it. Run these from the repository root.

```zsh
# 1. Install the audit daemon (Debian/Ubuntu)
sudo apt install -y auditd

# 2. Watch writes and attribute changes to .git/config (lasts until reboot)
sudo auditctl -w "$(git rev-parse --absolute-git-dir)/config" -p wa -k vde-git-config

# 3. Make the rule survive reboots
print -r -- "-w $(git rev-parse --absolute-git-dir)/config -p wa -k vde-git-config" | sudo tee /etc/audit/rules.d/vde-git-config.rules
sudo augenrules --load

# 4. Confirm exactly one vde-git-config rule is loaded
sudo auditctl -l
```

After the next flip, read the record:

```zsh
sudo ausearch -k vde-git-config -i --start today
```

Each event names the writer in its `SYSCALL` line (`comm=`, `exe=`, `pid=`, `ppid=`, `auid=`), and the `PROCTITLE` line shows the full command line. `git config` rewrites the file through `config.lock` and a `rename`; the watch follows that, so every write is caught. The `ppid` points at the parent process (for example a Git GUI or an editor integration), which `ps` can no longer tell you once it exits.

Note: if `ausearch` prints events for `git config` only, the flip came from a `git` command. A process that edits the file directly will appear under its own `comm=`/`exe=`.

---

## Complete Reset (The Great Quench)

If the Forge is hopelessly fractured and you need a clean start:

```zsh
# 1. Backup your projects/ and data/ directories.
# 2. Execute the Great Quench
vde nuke
```
This removes all VDE containers, images, and networks, allowing you to run `vde path-of-the-foundling` from a blank slate.

---

[← Back to README](../../README.md)
**This is the Way.**
