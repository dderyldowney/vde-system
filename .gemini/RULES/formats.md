# REQUIRED OUTPUT FORMATS
<!-- @forge (Agent Logic) -->
## Git Commit Format
```zsh
git commit -m "<type>: <description>

- Detail 1
- Detail 2


```
**Types:** `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
## Batching Rules
**User-facing tasks:** Complete ONE user-requested task → Ask what's next. DO NOT batch user tasks without explicit user confirmation.
**Internal swarm (autonomous):** Internal sub-agent swarms spawned per `subagent_mcp_mandate.md` run in parallel autonomously — no user confirmation required. This rule governs user-visible task sequencing only.