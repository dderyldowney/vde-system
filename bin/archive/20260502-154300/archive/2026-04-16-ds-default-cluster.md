# Data Science Default Cluster Implementation Plan (Refined 2026)
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a hardened Data Science default cluster (`default`) with 2026-standard libraries, password-less access, and Postgres integration.

**Architecture:** 
1.  **Hydration Hardening**: Update `jupyterlab-init.zsh` with the 2026 library alloy (Polars, PyTorch, LangGraph, etc.) and zero-gate access.
2.  **Infrastructure Bridge**: Install system-level Postgres clients for driver stability.
3.  **Cluster Formalization**: Use `vde cluster` to anchor the `default` stack.

**Tech Stack:** JupyterLab (Jupyter Server 2.x), Postgres, Polars, PyTorch, LangGraph, Zsh.

---

### Task 1: Harden JupyterLab for 2026 DS/AI

**Files:**
- Modify: `scripts/setup/jupyterlab-init.zsh`

- [x] **Step 1: Update System Alloys**
    - Add `libpq-dev` and `postgresql-client` to `apt-get install`.
- [x] **Step 2: Install 2026 Library Alloy**
    - Install `polars`, `torch`, `langgraph`, `fastapi`, `streamlit`.
    - Install Postgres bridges: `psycopg[binary]`, `sqlalchemy`, `jupysql`.
    - Retain foundations: `numpy`, `pandas`, `matplotlib`.
- [x] **Step 3: Enable Zero-Gate Access**
    - Configure `jupyter_server_config.py` with empty token/password.

---

### Task 2: Formalize the 'default' Cluster

**Files:**
- Modify: `bin/vde-init`

- [x] **Step 1: Ensure Cluster Persistence**
    - Add ritual to `bin/vde-init` to save `default` cluster.
- [x] **Step 2: Create Cluster**
    - Command: `bin/vde cluster save default jupyterlab postgres`

---

### Task 3: Final Verification

- [x] **Step 1: Run Sovereign Audit**
- [ ] **Step 2: Verify 'vde start default'**
- [ ] **Step 3: Request Code Review (Mandate 19)**
- [ ] **Step 4: Commit and Link**
