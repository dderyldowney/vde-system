# VDE Beskar Record: 1.5.0 (The Sovereign Evolution)
<!-- @shared-law (Forge Component) -->

## SOVEREIGN STATE
- **Baseline**: 1.5.0 (Certified 2026-04-26)
- **Status**: 100% GREEN (PEAK INTEGRITY)
- **Heartbeat**: Certified via Mandate L; automated via pre-push and CI.

## CORE MEMORIES
- **Locking Storm Remediation**: Fixed infinite recursion in `vde-poll` by moving ecosystem sourcing below the `--wait` block. Implemented `VDE_NO_LOCK` bypass and 10s "Stale Lock Buster" in `lib/vm-lock`.
- **Registry Restoration**: Re-added missing entries (`certified-ghost`, `lamp`, `lua`, `mean`) to Beskar Registry and ensured all hydration commands use absolute `/vde/` paths for in-container reliability.
- **Project Portability**: Standardized `VDE_ROOT_DIR` calculation using zsh-native absolute detection. Documented "Absolute Path Exemption" for container-internal filesystem paths.
- **Path Purification**: Purged absolute host-path leaks in `.tmp.driveupload` and updated `vde-security-audit.zsh` to exclude ephemeral artifacts.
- **Phase 31 (DNS & Bridge) [CERTIFIED]**: Verified Spoke-to-Spoke and Hub-to-Spoke resolution.
- **Phase 32 (Forge Intelligence) [CERTIFIED]**: Validated auto-remediation and registry healing rituals.

**This is the Way.**
