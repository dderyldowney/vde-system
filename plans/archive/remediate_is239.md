
<!-- @shared-law (Forge Component) -->
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.


**Architecture:** We will systematically edit the headers of all core binaries and libraries to include the `@armor` architectural tag. We will refactor `bin/vde-poll` to strictly rely on ZSH's `zselect` for sub-second precision, failing fast if the module is unavailable. Finally, we will scan for and remove all documentation claiming `bash` compatibility, rewriting any lingering bashisms into native ZSH.

**Tech Stack:** ZSH

---

### Task 1: Tag Core `bin/` Scripts (@armor)

**Files:**
- Modify: `bin/vde-create`, `bin/vde-start`, `bin/vde-stop`, `bin/vde-rm`, `bin/vde-rebuild`, `bin/vde-exec`, `bin/vde-logs`, `bin/vde-ps`, `bin/vde-health`, `bin/vde-images`, `bin/vde-networks`, `bin/vde-port`, `bin/vde-stats`, `bin/vde-inspect`, `bin/ssh-setup`, `bin/ssh-sync`, `bin/ssh-agent-setup`, `bin/add-vm-type`, `bin/uninstall-vm-type`, `bin/cleanup-ports`, `bin/nuke-vde`

- [ ] **Step 1: Write the failing test**
Run `grep -L "@armor" bin/*` to verify these files are untagged.

- [ ] **Step 2: Write minimal implementation**
For each file listed above, insert `# @armor (<Specific Function>)` immediately after the `#!/usr/bin/env zsh` shebang.
Example for `bin/vde-create`:
```zsh
#!/usr/bin/env zsh
# @armor (Spoke Creation)
```
*(Agent Note: Due to Rule E, execute this systematically, either via a script or sequential subagent dispatches).*

- [ ] **Step 3: Run test to verify it passes**
Run `grep -l "@armor" bin/*` and verify all 21 files are now listed.

- [ ] **Step 4: Commit**
```bash
git add bin/
git commit -m "chore(armor): apply architectural tags to core binaries"
```

### Task 2: Tag Core `lib/` Libraries (@armor)

**Files:**
- Modify: `lib/vde-ssh`, `lib/vde-docker`, `lib/vde-naming`, `lib/vde-parser`, `lib/vde-path-utils`, `lib/vde-health`, `lib/vde-metrics`, `lib/vde-security`, `lib/vde-log`, `lib/vde-errors`, `lib/vde-templates`, `lib/vde-progress`, `lib/vm-lock`, `lib/vde-docker-state`

- [ ] **Step 1: Write the failing test**
Run `grep -L "@armor" lib/*` to verify these files are untagged.

- [ ] **Step 2: Write minimal implementation**
For each library listed above, insert `# @armor (<Specific Function>)` immediately after the `#!/usr/bin/env zsh` shebang.
Example for `lib/vde-docker`:
```zsh
#!/usr/bin/env zsh
# @armor (Docker Operations)
```

- [ ] **Step 3: Run test to verify it passes**
Run `grep -l "@armor" lib/*` and verify all 14 files are now listed.

- [ ] **Step 4: Commit**
```bash
git add lib/
git commit -m "chore(armor): apply architectural tags to core libraries"
```

### Task 3: Purify `bin/vde-poll` (Remove `sleep` Fallback)

**Files:**
- Modify: `bin/vde-poll`

- [ ] **Step 1: Write the failing test**
Run `grep "sleep" bin/vde-poll`. It should return the forbidden sleep fallback.

- [ ] **Step 2: Write minimal implementation**
Remove the `sleep` fallback and replace it with a hard failure.
Modify `bin/vde-poll` from:
```zsh
    zmodload zsh/zselect 2>/dev/null && zselect -t ${wait_ticks} || sleep ${opts[--wait]}
```
To:
```zsh
    if ! zmodload zsh/zselect 2>/dev/null; then
        echo "[ERROR] zsh/zselect module required but not found. Polling cannot continue safely." >&2
        return ${VDE_ERR_GENERAL}
    fi
    zselect -t ${wait_ticks}
```
*(Also remove any other instances of `sleep` in the file).*

- [ ] **Step 3: Run test to verify it passes**
Run `grep "sleep" bin/vde-poll`. It should return nothing.
Run `bin/vde-enforce-uap.zsh`. It should pass without flagging `vde-poll`.

- [ ] **Step 4: Commit**
```bash
git add bin/vde-poll
git commit -m "fix(armor): remove forbidden sleep fallback from vde-poll"
```

### Task 4: Remove Stale Bash Headers and Bashisms

**Files:**
- Modify: Files in `lib/` and `bin/` that contain references to "bash".

- [ ] **Step 1: Write the failing test**
Run `grep -il "bash" lib/* bin/*` to identify files with stale claims.

- [ ] **Step 2: Write minimal implementation**
For every file found:
1. Remove lines stating `# Shell Compatibility: POSIX-compliant (sh, bash, zsh)` or `- Supports zsh 5.0+, bash 4.0+, bash 3.x`.
2. Scan the file's code for actual bashisms (e.g., `[[ $BASH_VERSION ]]`, `shopt`, `type -t`). If found, rewrite to pure ZSH (e.g., `[[ -n $ZSH_VERSION ]]`, `setopt`, `whence -w`).

- [ ] **Step 3: Run test to verify it passes**
Run `grep -i "bash" lib/* bin/*`. It should return nothing (except for intentional tests checking FOR bash to reject it, if any).

- [ ] **Step 4: Commit**
```bash
git add lib/ bin/
git commit -m "refactor(armor): remove stale bash compatibility headers and ensure ZSH purity"
```