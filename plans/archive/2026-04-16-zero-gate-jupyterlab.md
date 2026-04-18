# [CONSOLIDATED] - CONTENT MOVED TO plans/plan.md


# Zero-Gate JupyterLab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completely disable all authentication (token and password) and security blockades in JupyterLab to provide a seamless "Zero-Gate" experience for internal VDE use.

**Architecture:** 
1.  **Identity provider Hardening**: Target `c.IdentityProvider` for token/password suppression.
2.  **XSRF Suppression**: Disable XSRF checks to allow anonymous API requests (saving/executing).
3.  **Remote Access Authorization**: Explicitly allow remote access to bypass container hostname checks.

**Tech Stack:** JupyterLab 4.x, Jupyter Server 2.x, Zsh.

---

### Task 1: Update JupyterLab Hydration Script

**Files:**
- Modify: `scripts/setup/jupyterlab-init.zsh`

- [x] **Step 1: Apply Zero-Gate Configuration**
    - Update the cat block in section 5 of the hydration script.
    - Added: `c.ServerApp.allow_remote_access = True`
    - Added: `c.ServerApp.disable_check_xsrf = True`
    - Added: `c.IdentityProvider.token = ''`
    - Added: `c.IdentityProvider.password = ''`

```bash
# Section 5 of scripts/setup/jupyterlab-init.zsh should look like this:
sudo -u devuser zsh -c "cat <<EOF > ${_jupyter_config}
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = '/home/devuser/workspace'
c.ServerApp.allow_root = True
c.ServerApp.allow_remote_access = True
c.ServerApp.disable_check_xsrf = True
# Data Science Default: Zero-Gate Access for Internal Student Use
c.IdentityProvider.token = ''
c.IdentityProvider.password = ''
EOF"
```

- [x] **Step 2: Commit Changes**

```bash
git add scripts/setup/jupyterlab-init.zsh
git commit -m "feat(jupyter): implement zero-gate authentication for DS stack"
```

---

### Task 2: Rebuild and Verify

- [x] **Step 1: Rebuild JupyterLab Spoke**
    - Run: `bin/vde rebuild jupyterlab`
- [x] **Step 2: Verify Zero-Gate Access**
    - Start the cluster: `bin/vde start default`
    - Verify access via curl (checking for 200 OK without token):
    - Run: `curl -I http://localhost:$(bin/vde port jupyterlab 8888)`
    - Expected: `HTTP/1.1 200 OK` (or 302 redirect to /lab) without being prompted for a login.
- [x] **Step 3: Run Sovereign Audit**
    - Run: `bin/vde-enforce-uap.zsh`
