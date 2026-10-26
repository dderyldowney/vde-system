# LIFECYCLE OF A SPOKE
<!-- @armor (Container Orchestration) -->
**The Lifecycle of a Spoke in the VDE Sovereign Baseline (1.5.6)** is governed by the **Proof of Life Contract**, a non-negotiable functional sequence that ensures system integrity from initial hydration to final decommissioning.

### **At a Glance: The Spoke Lifecycle**

The lifecycle follows a strictly enforced path: **Init → Create → Start → Enter → Stop → Remove**.

---

### **1. Ignition: Initialization and Creation**

*   **The Initialization Ritual (`vde init`)**: This pre-flight phase hydrates the Hub's infrastructure. It forges the `vde_student` SSH identity keys, establishes the `vde-net` bridge, and builds the foundational `vde-base` image.
*   **Spoke Creation (`vde create <alias>`)**: A new Spoke image is smelted from the Beskar Registry definition. This process uses **Universal Script Parity (USP)** to hydrate the environment at build-time, ensuring the Spoke is **Born Ready (BTO)** with no runtime network dependencies.
*   **Dynamic Registration (`vde add`)**: New Spoke types can be registered dynamically, enforcing the 8-field standard registry structure.

### **2. Active Service**

*   **Spoke Ignition (`vde start <alias>`)**: The container process is ignited. This includes a "System Breath" resource check and a **Physical Handshake** to verify port availability.
*   **The Sovereign Handshake (`vde enter <alias>`)**: The user enters the Spoke's login shell as the `devuser` account via the secure SSH transversal bridge. This bridge utilizes a `socat` proxy to forward the host's SSH agent into the Spoke.
*   **Workspace Persistence**: Inside the Spoke, the user operates at `$HOME/workspace/`. This directory is **persistently synced** to `<projects-base>/<alias>` on the Hub. Work saved here survives image rebuilds and container dissolution.
*   **The Projects Base (Sovereign Origin)**: The `<projects-base>` is a **configurable** anchor, not a fixed path. It defaults to `${VDE_ROOT_DIR}/projects` and is chosen at onboarding (`vde init` / `vde path-of-the-foundling`). The student may override it with `vde init --projects-dir <path>` or an exported `VDE_PROJECTS_DIR`. The effective base is persisted as the absolute `.env` key `VDE_PROJECTS_DIR` and resolved at runtime by the `vde_projects_dir()` helper in `lib/vde-path-utils`. The base may live anywhere the student controls — inside or outside the repo (e.g. `$HOME/Projects`). For each Spoke, `<projects-base>/<alias>` is mounted at `/home/devuser/workspace`. Creation **never overwrites** existing content: a same-named folder already present is adopted intact.

### **3. Maintenance and Re-Forging**

*   **Re-smelting (`vde rebuild <alias>`)**: If a Spoke requires updates or becomes unstable, it is re-forged. This rebuilds the Spoke's Docker image (reusing Docker's cache by default; pass `--no-cache` for a from-scratch rebuild) to restore the factory baseline while preserving the `$HOME/workspace/` data.
*   **Re-anchoring the Base (`vde set-projects-dir <new-path>`)**: The projects base can be relocated after onboarding without a rebuild. This ritual safely **MOVES** existing alias folders to the new base (skipping collisions, never overwriting or deleting), updates the `VDE_PROJECTS_DIR` key in `.env`, and regenerates the Spoke configs. The new base takes effect on the next Spoke start.

### **4. Decommissioning: The Quench and Dissolution**

*   **The Quench (`vde stop <alias>`)**: The running Spoke process is stopped, releasing Hub memory and CPU while keeping the instance registered.
*   **Dissolution (`vde rm <alias>`)**: The Spoke instance and its associated atomic file locks are dissolved from the Hub.
*   **Permanent Removal (`vde uninstall <alias>`)**: The Spoke type is permanently removed from the Beskar Registry.
*   **The Great Quench (`vde nuke`)**: A comprehensive cleanup ritual that dissolves VDE's own operational state while **guarding the student's sovereign data**. It **preserves** the projects base (`projects/` or an external `VDE_PROJECTS_DIR`) and the service database `data/` directory — in-tree or external — and **offers to move** both to a safe location before proceeding. It **removes** VDE's operational state: all Spokes, Spoke images, the Docker `vde-net` network and volumes, the SSH config and keys at `$HOME/.ssh/vde`, and the `logs/`, `env-files/`, caches, and atomic file locks. The ritual does **not** delete the VDE program itself; the VDE folder is removed afterward by manual deletion, once the preserved projects and data have been secured.

---

**This is the Way.**
