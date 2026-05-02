# Security Remediation: Deep Purification Plan - The Reclamation Strike (1.4.0)
<!-- @shared-law (Forge Component) -->

## Objective
To eliminate exposed secrets and resolve absolute git repository corruption by re-initializing the VDE repository from the certified 1.4.0 Sovereign Baseline.

## 1. Background & Motivation
Real API keys were leaked in `rebuild_debug.log`. Subsequent diagnostics (`git fsck`) revealed over 300 failed commit parses and systemic tree fractures. The repository is no longer a reliable chronicler of our history. We must reclaim the Forge through a total re-forge.

## 2. Scope & Impact
- **Impacted Secrets**: `CONTEXT7_API_KEY`, `GOOGLE_API_KEY`, `GEMINI_API_KEY`, `NEWSAPI_ORG_API_KEY`, `OPENROUTER_API_KEY`.
- **Impacted Record**: The entire corrupted git history of `vde-system`.
- **Sovereign Level**: Class-A Protocol Violation. Total Reclamation required.

## 3. Proposed Solution: The Three-Strike Strike

### Strike I: Immediate Key Rotation (External)
**The Clan Leader (User) MUST manually perform the following:**
1. Revoke the existing keys for Context7, Google Cloud, NewsAPI, and OpenRouter.
2. Generate new keys for each service.
3. Update local `.env` files (ensuring they remain UNTRACKED).

### Strike II: Local Reclamation (The Re-Forge)
**The Alor (Agent) will execute the following surgical strikes:**
1. **Evacuation**: Ensure the current 1.4.0 state (files) is stable.
2. **The Purge**: Delete the corrupted `.git` directory.
3. **Initialization**: Initialize a fresh git repository (`git init`).
4. **Branching Law**: Establish the `develop` (default), `main`, and `stable` branches.
5. **Base Commit**: Create an initial commit with the 1.4.0 Sovereign Baseline.

### Strike III: Origin Reset (Remote Synchronization)
**Once local history is purified:**
1. **Remote Re-Link**: Re-add the remote origin.
2. **The Overwrite**: Force-push the fresh `main`, `develop`, and `stable` branches to the remote.
3. **The Mirror**: Synchronize the `stable` branch to the 1.4.0 commit.

## 4. Implementation Steps

1. **Step 1: Backup Verification**: Confirm all 1.4.0 SAS members and core scripts are present.
2. **Step 2: Destruction**: `rm -rf .git` to destroy the corrupted history.
3. **Step 3: Creation**: `git init` and `git checkout -b develop`.
4. **Step 4: Staging**: `git add .` (ensuring `.gitignore` and `rebuild_debug.log` removal).
5. **Step 5: Initial Chronicle**: `git commit -m "feat(core): initial 1.4.0 Sovereign Baseline (Reclamation Strike)"`.
6. **Step 6: Remote Strike**: `git remote add origin ...` and force-push all branches.

## 5. Verification
- `git fsck --full` returns 0 errors.
- `git log` shows only the clean 1.4.0 start.
- `grep` scan across the repository confirms zero matches for old keys.
- Proof of Life Heartbeat remains 100% Green.

**This is the Way.**
