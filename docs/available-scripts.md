# Available Scripts
<!-- @shared-law (Sovereign Law) -->

Overview of all scripts included with VDE.

[← Back to README](../README.md)

---

## Core Scripts

### VDE Unified Command (Recommended)

The `vde` command is the canonical entry point for the **Sovereign Evolution (1.5.1)**. It wraps all infrastructure logic in the `vde_run` safety layer, ensuring Zsh purity and system integrity.

| Command | Purpose | Usage |
|---------|---------|-------|
| `vde init` | **The Initialization Ritual**: Hydrate infrastructure, SSH keys, networks, and build vde-base. | `vde init` |
| `vde create <vm>` | Create a new VM Spoke from the Beskar Registry. | `vde create python` |
| `vde path-of-the-foundling` | **The Path of the Foundling**: Interactive onboarding ritual for new students. | `vde path-of-the-foundling` |
| `vde rebuild <vm>` | Re-forge a Spoke's Docker image (defaults to no-cache). | `vde rebuild python` |
| `vde start <vm>` | Ignite a VM Spoke. Performs "System Breath" resource check. | `vde start python` |
| `vde stop <vm>` | Quench (stop) a running VM. | `vde stop postgres` |
| `vde restart <vm>` | Restart one or more active Spokes. | `vde restart rust` |
| `vde remove <vm>` | Dissolve (remove) a VM instance and its locks. (Aliases: `rm`, `delete`) | `vde remove rust` |
| `vde nuke` | **The Great Quench**: Remove all VDE artifacts (prompts for backup). | `vde nuke` |
| `vde exec <vm> <cmd>` | Execute a command inside a Spoke without a full login shell. | `vde exec go "go version"` |
| `vde enter <vm>` | The Sovereign Handshake: Enter a Spoke's login shell. (Alias: `ssh`) | `vde enter rust` |
| `vde add <name>` | Dynamic Expansion: Register a new Spoke type. | `vde add --pkgs "htop" myvm` |
| `vde uninstall <vm>` | Permanent Removal: Remove a Spoke type from the Registry. | `vde uninstall elixir` |
| `vde list` | Audit all predefined and custom Spokes. | `vde list` |
| `vde ps` | List all running VDE-managed containers. (Alias: `status`) | `vde ps` |
| `vde vision` | **The Archivist’s Vision**: Real-time Markdown-based status grid. | `vde vision` |
| `vde inspect <vm>` | Inspect container metadata and labels. | `vde inspect python` |
| `vde logs <vm>` | Tail the logs of a specific Spoke. | `vde logs redis` |
| `vde images` | List all VDE-managed Docker images. | `vde images` |
| `vde stats` | View real-time resource usage of active Spokes. | `vde stats` |
| `vde health` | Run the System Spine health check. | `vde health` |
| `vde cluster <cmd>` | Orchestrate multi-VM clusters (Tech Stacks). | `vde cluster start python-stack` |
| `vde ssh-setup` | Manage VDE SSH environment (keys, agent, config). | `vde ssh-setup init` |
| `vde ssh-sync` | Sync VDE SSH public keys to the build context. | `vde ssh-sync` |
| `vde networks` | Audit and manage the `vde-net` Docker bridges. | `vde networks` |
| `vde validate` | Verify the integrity of the Beskar Registry (JSON schemas). | `vde validate` |
| `vde prune` | **The Pruning Ritual**: Archive old plans/scripts and purge aged logs. | `vde prune` |
| `vde rebuild-cache` | Force a re-smelt of the internal VM cache. | `vde rebuild-cache` |
| `vde sync-version` | Synchronize versioning across the Hub and Spokes. | `vde sync-version` |
| `vde port <alias>` | Retrieve the assigned SSH port for a Spoke. | `vde port python` |
| `vde info` | Detailed system and environment diagnostic dump. | `vde info` |
| `vde dns-check` | **The Handshake Ritual**: Verify cross-Spoke DNS resolution. | `vde dns-check <src> <tgt> [port]` |
| `vde matrix-audit` | Exhaustive verification of every registered VM type (Serialized). | `vde matrix-audit` |
| `vde matrix-rebuild` | Comprehensive non-cached re-forging of the absolute Spoke matrix. | `vde matrix-rebuild` |
| `vde-enforce-uap.zsh` | **The Rule Spine**: Enforce Universal Agent Protocol compliance. | `bin/vde-enforce-uap.zsh` |
| `vde-spine-check.zsh` | **The Tetrad Check**: Verify Zsh, Git, Docker, and SSH pillars. | `bin/vde-spine-check.zsh` |
| `vde-gospel-audit.zsh` | **The Gospel Auditor**: Verify structural integrity of the Sovereign Artifact Set. | `bin/vde-gospel-audit.zsh` |
| `vde-heal-docs.zsh` | **The Self-Healer**: Autonomously synchronize Gospel documentation with the physical Forge. | `bin/vde-heal-docs.zsh` |

---

## Maintenance & Development Scripts

These scripts provide specialized maintenance, automation, and development support.

| Script | Purpose |
|--------|---------|
| `vde-bootstrap` | Initial Hub installation and dependency check. |
| `generate-all-configs` | Smelt all Spoke compose and SSH configurations. |
| `cleanup-ports` | Purge stale or orphaned entries from the port registry. |
| `vde-prune.zsh` | Archive old plans/scripts and purge aged logs. |
| `validate-schemas.zsh` | Verify Beskar Registry integrity against JSON schemas. |
| `vde-tactical-sweep.zsh` | Perform a project-wide cleanup of containers and locks. |
| `vde-poll` | Continuous health monitoring of the Spoke ecosystem. |
| `install-githooks` | Install the VDE Sentinel and Gatekeeper git hooks. |
| `check-zsh-shebang.zsh` | CI ritual to enforce the Zsh-only mandate. |
| `coverage.zsh` | Generate code coverage reports for the Forge. |
| `targeted-test.zsh` | Execute specific BDD or unit test suites. |
| `paired_update_enforcer` | Mandate L ritual to ensure PR/Remediation alignment. |
| `vde-rebuild-cache` | Force a re-smelt of the internal VM cache. |
| `vde-sync-version` | Synchronize versioning across the entire Forge. |
| `nuke-vde` | **The Great Quench**: Safe removal of all VDE artifacts. |
| `add-vm-type` | Low-level script to register a new VM type in the Beskar Registry. |
| `list-vms` | Low-level script to audit registered VM types. |
| `uninstall-vm-type` | Low-level script to permanently remove a VM type. |
| `ssh-setup` | Orchestrate local SSH key generation and configuration. |
| `ssh-agent-setup` | Secure initialization of the SSH agent for the Forge. |
| `ssh-sync` | Synchronize SSH public keys to the Docker build context. |
| `ssh-vm` | Primary bridge logic for connecting to Spoke SSH servers. |
| `vde-check-tetrad.zsh` | Fast technical gate for verifying core dependencies. |
| `vde-security-audit.zsh` | Execute deep security and privacy audits across the Forge. |
| `vde-matrix-audit.zsh` | Logic for exhaustive verification of the Spoke matrix. |
| `vde-matrix-rebuild.zsh` | Logic for comprehensive re-forging of all Spoke images. |
| `demo-schema-updates.zsh` | Ritual to demonstrate and verify registry schema evolution. |
| `generate_video` | Generate procedural video content for Forge documentation. |
| `remediate-installation-ambiguity.zsh` | Patch script to resolve installation path drift. |
| `remediate-phase24-sleep.zsh` | Tactical remediation for forbidden sleep calls. |

---

## Script Locations

The VDE repository follows a strict structural mandate. All binaries reside in `bin/` and rely on the libraries in `lib/`.

```
VDE_ROOT/
├── bin/
│   ├── vde                     # Unified Command Entry Point (THE WAY)
│   ├── vde-init                # Infrastructure Ritual Logic
│   ├── vde-rebuild             # Image Re-forging Logic
│   ├── vde-vision              # Observability Dashboard Logic
│   ├── vde-networks            # Bridge Management
│   ├── vde-ps / vde-logs       # Docker Proxy Tools
│   ├── vde-enforce-uap.zsh     # The Rule Spine (Compliance)
│   ├── install-githooks        # Activation Ritual for Forge Laws
│   └── ...                     # Specialized lifecycle scripts
├── githooks/
│   ├── pre-commit              # The Pre-Strike Sentinel (Purity Gate)
│   └── ...                     # Tracked Git hooks
├── lib/
```

---

## Undocumented Scripts (Pending Classification)

| Script | Purpose |
|--------|---------|
| `migrate-configs-to-categories.zsh` | Automatically discovered - documentation pending. |
| `vde-cluster` | Automatically discovered - documentation pending. |
| `vde-dns-check.zsh` | Automatically discovered - documentation pending. |
| `vde-exec` | Automatically discovered - documentation pending. |
| `vde-health` | Automatically discovered - documentation pending. |
| `vde-images` | Automatically discovered - documentation pending. |
| `vde-info` | Automatically discovered - documentation pending. |
| `vde-init` | Automatically discovered - documentation pending. |
| `vde-inspect` | Automatically discovered - documentation pending. |
| `vde-logs` | Automatically discovered - documentation pending. |
| `vde-networks` | Automatically discovered - documentation pending. |
| `vde-path-of-the-foundling` | Automatically discovered - documentation pending. |
| `vde-port` | Automatically discovered - documentation pending. |
| `vde-ps` | Automatically discovered - documentation pending. |
| `vde-rebuild` | Automatically discovered - documentation pending. |
| `vde-stats` | Automatically discovered - documentation pending. |
| `vde-vision` | Automatically discovered - documentation pending. |
| `vde-demo-intelligence.zsh` | Automatically discovered - documentation pending. |
| `vde-armor-heal.zsh` | Automatically discovered - documentation pending. |
| `temp-leak-test.zsh` | Automatically discovered - documentation pending. |
