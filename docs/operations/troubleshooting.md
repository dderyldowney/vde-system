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

## "Address already in use" on `agent.sock` / Pillar IV Fails

**Problem:** `vde ssh-setup start` or the Spine Check fails, and `ssh-agent` says:

```text
unix_listener: cannot bind to path /home/<you>/.ssh/vde/agent.sock: Address already in use
```

**Cause:** `~/.ssh/vde/agent.sock` is a *directory*, not a socket. Docker creates a missing bind-mount source as an empty directory owned by root. That happened because a Spoke started while the VDE agent was not running. Nothing is listening there; the path is simply taken.

```zsh
# Confirm: the first character must be "s" (a socket), not "d" (a directory)
ls -ld ~/.ssh/vde/agent.sock
```

**Fix:** the Spine Check, `vde ssh-setup start` and `vde start` now remove the directory themselves when it is empty (`rmdir` cannot remove anything that has contents). It works even though root owns the directory, because you own the folder it sits in (`~/.ssh/vde`). If VDE cannot remove it, it prints the exact command:

```zsh
rmdir ~/.ssh/vde/agent.sock        # add sudo only if the line above is refused
vde ssh-setup start                # start the agent and load vde_student
```

If the directory has contents, or the path is a file or symlink, VDE leaves it alone and says so: move or remove it yourself. This is a failure in every mode, including `VDE_CI_MODE=1`, because the agent cannot bind while anything other than a socket sits on that path. `git commit` runs the Spine Check and shows its message when it fails.

**Prevention:** `vde start` now starts the VDE agent before it runs Docker, and refuses to start the Spoke if the agent cannot be started, so Docker is never handed a socket path that does not exist.

---

## "No Space Left on Device" During a Build

**Problem:** a `vde rebuild`, `vde create` or `vde start` fails, or `df -h /` shows the disk nearly full. The usual cause is Docker's *build cache*: a `--no-cache` rebuild of a few Spokes can leave tens of gigabytes behind.

```zsh
vde clean --dry-run    # shows how much build cache there is; changes nothing
vde clean              # frees it
```

`vde clean` removes only the build cache. It never removes images, containers or volumes, so your Spokes are untouched; the only cost is that the next build is slower once. VDE already cleans the cache after every successful rebuild, so you normally meet this only after an interrupted build, a failed build, or a rebuild with `--keep-cache`. When a build fails with the disk nearly full, VDE says so and names this command.

If space is still short afterwards, look at what else Docker holds (`docker system df`) and at your own files. Do **not** run `vde prune` for this: it is the Forge's housekeeping for old logs and plans, not a disk-space tool. On Docker Desktop or WSL2, freed space stays inside Docker's disk file until that file is compacted, so the host's free space may not rise at once.

---

## Spoke Won't Start

**Problem:** A Spoke fails to ignite or crashes immediately.

```zsh
# 1. Check the logs
vde logs python

# 2. Re-smelt the Spoke image. A normal rebuild (reusing cache) often clears
#    transient breakage cheaply:
vde rebuild python
# If the image itself is suspect, force a clean, cache-free rebuild (slower —
# recompiles from source):
vde rebuild --no-cache python

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

## My Projects Aren't Where I Expected / I Want to Move Them

**Problem:** Your code is landing somewhere you didn't intend, or you've decided your **Projects base** belongs in a different folder.

**Solution:** Re-point the base at any location you control:

```zsh
vde set-projects-dir <new-path>
```

This safely moves your existing per-alias folders to the new base — it skips any name collisions and never overwrites or deletes what is already there — updates the `.env` record (`VDE_PROJECTS_DIR`), and regenerates the Spoke configs. The new location takes effect on each Spoke's next start; no rebuild is required. Each alias continues to appear at `$HOME/workspace/` inside its Spoke, now backed by `<new-path>/<alias>` on your Hub.

To see where your base currently points, check `VDE_PROJECTS_DIR` in your `.env`.

---

## Will `vde nuke` Delete My Code or Databases?

**Problem:** You want to reset the Forge but fear losing your work.

**Solution:** No — the Great Quench **preserves both your `projects/` and your database `data/`**, whether they live in-tree or at an external base like `$HOME/Projects`. `vde nuke` tears down only VDE's own state: Spokes, images, networks and volumes, the SSH config and keys at `$HOME/.ssh/vde`, and the `logs/`, `env-files/`, caches, and locks.

Before it removes anything, `vde nuke` offers to **move your `projects/` and `data/` to safety first** (or lets you continue as-is), and it warns you if either still lives inside the VDE folder. Even after the Quench, the program itself remains until you manually delete the VDE folder — so your code and databases are never swept away by the reset.

---

## `git checkout` Fails: "this operation must be run in a work tree"

**Problem:** `core.bare` in `.git/config` was flipped to `true` by something other than you.

**Known cause (fixed in Signet #493):** the spine check's Pillar II probe ran `git init` with the `GIT_DIR` that git exports to a hook launched from a linked worktree, so it re-initialised the worktree's gitdir and wrote `core.bare = true` into the shared config. The probe now scrubs git's repository-selecting environment. If you still see the flip on a build that has this fix, use the audit watch below to find the real writer.

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

# 4. Confirm exactly one vde-git-config rule is loaded (exits non-zero otherwise)
test "$(sudo auditctl -l | grep -F -c -- '-k vde-git-config')" -eq 1
```

Step 3 does not work if the repository path contains whitespace: a rules-file entry with a space in the path did not load, quoted or unquoted (`auditctl -R` exited 1 and no rule was loaded). The shell-quoted `auditctl -w` command in step 2 does work with spaces, so in that case use step 2 only and re-run it after each reboot.

Persistence was checked without rebooting: `sudo augenrules --check` reports `No change`, and after deleting the live rules (`sudo auditctl -D`) and restarting `auditd` (its unit runs `augenrules --load`) the rule came back from the rules file and still recorded writes. An actual reboot was not tested.

After the next flip, read the record:

```zsh
sudo ausearch -k vde-git-config -i --start today
```

Each event names the writer in its `SYSCALL` line (`comm=`, `exe=`, `pid=`, `ppid=`, `auid=`), and the `PROCTITLE` line shows the full command line. `git` rewrites the file through `config.lock` and a `rename`; the watch follows that, so every write is caught. The `ppid` points at the parent process (for example a Git GUI or an editor integration), which `ps` can no longer tell you once it exits.

Expect a noisy log: every `git` command that rewrites `.git/config` is recorded, not only `git config`. In practice that included `git push -u ...` (two events each, when it sets the upstream), `git branch -d ...` (removing a branch's config section) and `git config ...`, plus `auditctl` itself whenever rules are loaded. So `comm=git` alone does not identify a culprit. Match the event time to when `git checkout` started failing, then read `proctitle=` and `ppid=`: a writer that is not one of your own commands (a Git GUI, an editor integration or an agent tool) is the lead. To list every command that wrote the file:

```zsh
sudo ausearch -k vde-git-config -i --start today | grep -E 'proctitle=' | sed -E 's/.*proctitle=//' | sort | uniq -c | sort -rn
```

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
