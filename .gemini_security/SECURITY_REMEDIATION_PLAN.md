# Security Remediation Plan

## Findings
1. **CRITICAL - Command Injection Vulnerability (eval):** The `bin/vde-ps` command builds a filter parameter string and uses `eval` to execute the resulting `docker ps` command. If a malicious user supplies an unsanitized string (e.g. via `--filter`), it allows for arbitrary host command execution.
2. **MEDIUM - Dangerous String Evaluation:** The `bin/vde-rebuild` command builds a docker string command and executes it using `eval`. While user input is mostly restricted here, it's an anti-pattern that can lead to command injection if `canonical_name` or paths are manipulated.

## Remediation Steps
- [x] Refactored `bin/vde-ps` to use an array for building the `docker ps` command and execute it directly, completely eliminating `eval`.
- [x] Refactored `bin/vde-rebuild` to use arrays `build_cmd=(...)` instead of string evaluation `eval "${build_cmd}"`, mitigating command injection vectors.

## Status
- Both Code Review and Security Audit report nothing left to be done. All identified issues have been remediated.