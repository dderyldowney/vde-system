# Security Preamble (binding for every agent)
<!-- @forge (Governance Sentinel) -->

**NO AID TO THE ENEMY.** This repository is public, open source and free. Any public information about the inner workings and failings of unfixed code harms the project's credibility and helps those who would attack it. This preamble binds every agent however it is activated: a main agent, a sub-agent, a skill, a command or another tool.

1. Before any public action (an issue, a pull request, a commit message, a code comment, a test name, a review reply, a state file, a chat message posted anywhere public), ask: would this help someone attack an unpatched install, or tell them where to look? If yes, or if unsure, keep it private.
2. A new finding is never filed publicly first. Record it in the private ledger, which lives outside the repository (`~/.vde-security/`, or the path in `VDE_SECURITY_DIR`), and tell the User. A public issue is created only when the User approves, neutral from the start, and titled `fix: <version> security hardening, item NN`.
3. Every security-item branch is named `fix/sec-item-NN` (NN is the item number in the neutral issue title).
4. Never commit, paste or quote the private ledger or an advisory draft into the repository.
5. Every sub-agent prompt begins with this preamble, because sub-agents skip the startup reading.

The full rules are in `.gemini/RULES/security.md`; the full process is in `docs/governance/security-process.md`.
