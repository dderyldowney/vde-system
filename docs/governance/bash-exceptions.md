# docs/governance/bash-exceptions.md
<!-- @forge (Mandate C vendor-installer exception allowlist) -->
# Mandate C Exceptions: Vendor Shell Installers

Mandate C (ZSH ONLY) forbids `bash`/`sh` in VDE. The only exceptions are the
third-party installers below. Each vendor ships a Bash or POSIX-sh script and no
zsh-native or binary alternative, so the script is the unavoidable path. This
file is the ONE list. `tests/unit/setup-bash-allowlist.test.zsh` fails on any
`bash`/`sh` invocation in `scripts/setup/*.zsh` that is not listed here, and on
any entry here that no longer matches a line (stale).

Each call site also carries a comment pointing back to this file.

Columns: script, a literal fragment of the invocation line (the match key), reason.

| Script | Match | Reason |
|--------|-------|--------|
| `kotlin-init.zsh` | `bash "${_sdkman_installer}"` | SDKMAN is Bash; its installer and generated sdkman-init.sh require Bash. Downloaded with `-fSL` and verified non-empty before running. |
| `csharp-init.zsh` | `bash /tmp/dotnet-install.sh` | Microsoft's dotnet-install.sh uses bashisms and pipefail; no native installer. |
| `embed-init.zsh` | `sh "${_installer}"` | probe-rs ships only a cargo-dist POSIX-sh installer; the alternative is a ~15-minute source build. |

Resolved, no longer exceptions: `js-init.zsh` (NodeSource) configures the signed
apt repository directly in zsh (Signet #594).

Adding an entry requires a Signet, a reason that no zsh-native path exists, and
a call-site comment referencing this file.
