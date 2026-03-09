# Test Suite Remediation Plan — 2026-03-09

## Test Run Summary

| Suite | Result |
|-------|--------|
| `make test-e2e` (Zsh integration) | **79/79 passing** |
| `python3 -m behave` (Behave) | **222/240 passing — 18 failing** |

---

## Failure Inventory

### P1 — FIXED: Missing env files (14 failures)

**Feature:** `docker-operations.feature` (lines 16, 23, 29, 35, 40, 46, 59, 66, 72, 77, 83, 87, 93, 99)

**Root cause:** `vde-postgres.env`, `vde-js.env`, and `vde-zig.env` were accidentally deleted
and not restored. Docker Compose refuses to start any VM that references a missing `env_file`,
causing all 14 docker-operations scenarios to fail with:

```
env file /Users/dderyldowney/dev/env-files/vde-postgres.env not found
```

**Status: FIXED** — Files restored from git history (`69e0247^`) in commit `d969bd2`.

---

### P2 — FIXED: Python compose uses `restart: always` (2 failures)

**Feature:** `critical-path.feature:22`, `critical-path.feature:73`

**Root cause:** `configs/docker/python/docker-compose.yml` had `restart: always` instead of
`restart: unless-stopped` (the template default). This caused two cascading failures:

1. `critical-path:22` — direct assertion: `Expected 'restart: unless-stopped' in docker-compose.yml`
2. `critical-path:73` — `vde stop` appeared to fail: Docker restarted the container immediately
   after `docker stop` because `restart: always` ignores manual stops.

**Status: FIXED** — Changed to `restart: unless-stopped` in commit `d969bd2`.

---

### P3 — OPEN: SSH config bloat — 475 duplicate entries (1 failure)

**Feature:** `ssh-configuration.feature:151` — "Merge does not duplicate existing VDE entries"

**Error:** `Should have exactly one 'Host vde-python' entry, found 475`

**Root cause:** Bug in `merge_ssh_config_entry()` in `lib/vde-ssh` (lines 314–325).
The function attempts to remove the existing Host block before appending a new one, but the
removal logic is broken:

- Line 316: `grep -v "^Host $host_alias$"` only removes the `Host vde-python` header line —
  it does NOT remove the block body (HostName, Port, User, etc.).
- Line 319: A `sed` command runs on `$temp_file` (already incorrect), not `$ssh_config`.
- Line 324: An `awk` expression overwrites `$temp_file` again with another flawed removal
  that still only targets the header line, not the full block.

Result: Every `merge_ssh_config_entry` call appends a full Host block without removing the
previous block's body. After hundreds of test runs, `~/.ssh/vde/config` has grown to 140,286
lines.

**Fix required:**
1. Rewrite `merge_ssh_config_entry()` to correctly remove the entire Host block (all lines
   from `^Host alias$` up to the next `^Host ` or EOF) before appending the new entry.
   Correct awk pattern:
   ```
   awk '/^Host vde-python$/{skip=1} skip && /^Host / && !/^Host vde-python$/{skip=0} !skip' config
   ```
2. Truncate/rebuild `~/.ssh/vde/config` — run `vde ssh-setup generate` after the fix.

**Blast radius:** Every call to `create-virtual-for`, `start-virtual --update-ssh`, and
`vde ssh-setup generate` invokes this function. Config will re-bloat until fixed.

---

### P4 — OPEN: Wrong network name in test (1 failure)

**Feature:** `installation-setup.feature:78` — "Create Docker network"

**Error:** `vde-testing Docker network does not exist`

**Root cause:** Test assertion in `post_install_verification_steps.py:457` checks for a
Docker network named `vde-testing`, but the actual VDE network is `vde-net`. This is a
test bug — the network was renamed at some point but the test was not updated.

**Fix required:**
- Update `post_install_verification_steps.py:457` (and all references to `vde-testing` in
  that file and `vm_docker_network_steps.py`) to use `vde-net`.
- Files to update:
  - `tests/features/steps/post_install_verification_steps.py` (lines 454–465)
  - `tests/features/steps/deferred/vm_docker_network_steps.py` (lines 27, 45, 58, 69–95)

---

## Priority Order

| # | Issue | Scenarios | Status | Effort |
|---|-------|-----------|--------|--------|
| 1 | Missing env files (postgres, js, zig) | 14 | **FIXED** | — |
| 2 | Python `restart: always` → `unless-stopped` | 2 | **FIXED** | — |
| 3 | SSH config merge duplicates entries | 1 | **OPEN** | Medium |
| 4 | Test checks wrong network name (`vde-testing` vs `vde-net`) | 1 | **OPEN** | Low |

---

## Remaining Open Work (P3 + P4)

After fixing P3 and P4, expected result: **240/240 passing**.

### P3: Fix `merge_ssh_config_entry` (lib/vde-ssh:299–350)

```zsh
# Replace the removal block (lines 314–325) with a single correct awk pass:
if [[ -f "$ssh_config" ]]; then
    awk -v host="$host_alias" '
        /^Host / { skip = ($0 == "Host " host) }
        !skip { print }
    ' "$ssh_config" > "$temp_file" 2>/dev/null || cp "$ssh_config" "$temp_file"
fi
```

Then regenerate the SSH config:
```zsh
# Clean the bloated config first:
vde ssh-setup generate
# or manually truncate and regenerate:
> ~/.ssh/vde/config && vde ssh-setup generate
```

### P4: Update network name in test steps

In `post_install_verification_steps.py` and `vm_docker_network_steps.py`, replace all
occurrences of `vde-testing` with `vde-net`.

---

## Verification

After P3 + P4 fixes:
```zsh
/usr/local/bin/python3 -m behave
# Expected: 240 scenarios passed, 0 failed
```

Note: use `/usr/local/bin/python3` (3.13) — system `python3` is 3.9 and fails on `int | None`
union type syntax used in step files.
