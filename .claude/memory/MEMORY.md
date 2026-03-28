# Memory Index

- [VDE startup must be fully automatic](feedback_startup_auto_execute.md) — 7-step checklist must run before user can type anything; implemented via ~/.zshrc wrapper + /new command override
- [Git push in batches](feedback_git_push_policy.md) — never push after individual commits; user batches pushes manually at session end
- [VDE BDD fast-suite baseline](project_bdd_baseline.md) — 268 passed / 0 failed / 187 skipped; `--tags="not @integration"` ~2.5 min; 187 @integration Docker scenarios separate
- [VDE Docker feature stack plan](project_docker_stack.md) — All 8 features complete (O-8 done 2026-03-28); run ./tests/run-full-test-suite.zsh for final verification
- [O-1 through O-8 audit findings](project_audit_findings.md) — ALL HIGH/MEDIUM items fixed & committed (23914c3, 4dfbaf9); remaining LOW systemic items (FAKE-3/4, DRY-2/3/6/7, timeouts) are non-blockers
- [Swarm+MCP mandatory for multi-step batches](feedback_swarm_mcp_mandate.md) — >1 step fix batches must use parallel sub-agent swarm + sequential-thinking MCP; main agent synthesizes only
- [No direct docker calls in step files](feedback_no_direct_docker_calls.md) — use bin/vde CLI only; vde ps -q, vde stop, vde remove, vde networks
- [Refresh language docs via context7 at session start](feedback_context7_language_refresh.md) — fetch Python, behave, PyYAML, Docker, docker-compose, Zsh, SSH docs in parallel on every resume
