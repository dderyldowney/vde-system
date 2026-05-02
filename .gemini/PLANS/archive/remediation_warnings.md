# Remediation Plan: ZSH-Native Compliance (Mandate 14)
<!-- @forge (Governance Sentinel) -->

The VDE Enforcer has identified 54 files with `UAP-WARN` flags, indicating potential Bash-isms or a lack of ZSH-native logic (specifically parameter expansion flags). Per Mandate 14, these warnings are treated as failures and must be remediated.

## Files Requiring Refactoring

### `bin/` Directory
1. `bin/build-and-start`: Lacks ZSH parameter expansion flags.
2. `bin/check-zsh-shebang.zsh`: Lacks ZSH parameter expansion flags.
3. `bin/cleanup-ports`: Lacks ZSH parameter expansion flags.
4. `bin/coverage.zsh`: Lacks ZSH parameter expansion flags.
5. `bin/create-and-start`: Lacks ZSH parameter expansion flags.
6. `bin/create-virtual-for`: Lacks ZSH parameter expansion flags.
7. `bin/delete-virtual`: Lacks ZSH parameter expansion flags.
8. `bin/demo-schema-updates.zsh`: Lacks ZSH parameter expansion flags.
9. `bin/generate_video`: Potential Bash-style brackets `[` and lacks ZSH parameter expansion flags.
10. `bin/install-githooks`: Lacks ZSH parameter expansion flags.
11. `bin/migrate-to-vde-ssh`: Potential Bash-style brackets `[` and lacks ZSH parameter expansion flags.
12. `bin/remediate-installation-ambiguity.zsh`: Lacks ZSH parameter expansion flags.
13. `bin/remediate-ssh-ambiguity.zsh`: Lacks ZSH parameter expansion flags.
14. `bin/remove-virtual`: Lacks ZSH parameter expansion flags.
15. `bin/restart-virtual`: Lacks ZSH parameter expansion flags.
16. `bin/shutdown-all`: Lacks ZSH parameter expansion flags.
17. `bin/ssh-agent-setup`: Lacks ZSH parameter expansion flags.
18. `bin/ssh-setup`: Lacks ZSH parameter expansion flags.
19. `bin/ssh-sync`: Lacks ZSH parameter expansion flags.
20. `bin/ssh-vm`: Lacks ZSH parameter expansion flags.
21. `bin/targeted-test.zsh`: Lacks ZSH parameter expansion flags.
22. `bin/validate-schemas.zsh`: Lacks ZSH parameter expansion flags.
23. `bin/vde`: Lacks ZSH parameter expansion flags.
24. `bin/vde-ask`: Lacks ZSH parameter expansion flags.
25. `bin/vde-cluster`: Lacks ZSH parameter expansion flags.
26. `bin/vde-exec`: Lacks ZSH parameter expansion flags.
27. `bin/vde-images`: Lacks ZSH parameter expansion flags.
28. `bin/vde-init`: Lacks ZSH parameter expansion flags.
29. `bin/vde-inspect`: Lacks ZSH parameter expansion flags.
30. `bin/vde-logs`: Lacks ZSH parameter expansion flags.
31. `bin/vde-networks`: Lacks ZSH parameter expansion flags.
32. `bin/vde-port`: Lacks ZSH parameter expansion flags.
33. `bin/vde-rebuild`: Lacks ZSH parameter expansion flags.
34. `bin/vde-rebuild-cache`: Lacks ZSH parameter expansion flags.
35. `bin/vde-stats`: Lacks ZSH parameter expansion flags.

### `lib/` Directory
36. `lib/vde-audit`: Lacks ZSH parameter expansion flags.
37. `lib/vde-cluster-utils`: Lacks ZSH parameter expansion flags.
38. `lib/vde-commands`: Potential Bash-style brackets `[` and lacks ZSH parameter expansion flags.
39. `lib/vde-constants`: Potential Bash-style brackets `[`.
40. `lib/vde-core`: Potential Bash-style brackets `[`.
41. `lib/vde-docker-state`: Potential Bash-style brackets `[` and lacks ZSH parameter expansion flags.
42. `lib/vde-errors`: Potential Bash-style brackets `[` and lacks ZSH parameter expansion flags.
43. `lib/vde-health`: Potential Bash-style brackets `[`.
44. `lib/vde-log`: Lacks ZSH parameter expansion flags.
45. `lib/vde-metrics`: Lacks ZSH parameter expansion flags.
46. `lib/vde-naming`: Lacks ZSH parameter expansion flags.
47. `lib/vde-progress`: Potential Bash-style brackets `[` and lacks ZSH parameter expansion flags.
48. `lib/vde-root-guard`: Lacks ZSH parameter expansion flags.
49. `lib/vde-security`: Lacks ZSH parameter expansion flags.
50. `lib/vde-ssh`: Lacks ZSH parameter expansion flags.

## Refactoring Strategy

1. **Bash Brackets**: Replace `[ ... ]` with ZSH-native `[[ ... ]]` for more robust conditional expressions.
2. **ZSH Parameter Expansion**: Ensure all scripts longer than 30 lines utilize ZSH-specific expansion flags (e.g., `${(f)...}`, `${(z)...}`) where appropriate to demonstrate native logic.
3. **1-Indexing**: Verify all array operations adhere to ZSH 1-indexing.
4. **Enforcer Verification**: After each refactor, run `bin/vde-enforce-uap.zsh` to ensure the file now satisfies all mandates.

## Execution
This task involves 50+ files and will be delegated to a sub-agent swarm for efficiency and to adhere to the Orchestrator mandate.
