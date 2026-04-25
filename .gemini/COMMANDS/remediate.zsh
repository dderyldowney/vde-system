#!/usr/bin/env zsh
# @forge (Governance Sentinel)
# .gemini/COMMANDS/remediate.zsh

# 1. Capture the failure log from the Enforcer
LOG_FILE="logs/uap_failure_$(date +%Y%m%d_%H%M%S).log"
bin/vde-enforce-uap.zsh > "$LOG_FILE" 2>&1

# 2. Instruct the Agent to ingest the log and create a plan
echo "MANDATE VIOLATIONS DETECTED. Log saved to $LOG_FILE."
echo "ACTION: Read $LOG_FILE. Identify every file and line violation."
echo "PLAN: Create a new plan in plans/remediation_$(date +%s).md."
echo "The plan must prioritize: 1. ZSH Purity, 2. Sleep removal, 3. Bash-ism refactoring."
