#!/usr/bin/env zsh
# @forge (Governance Sentinel)
#===============================================================================
# vde-security-audit.zsh - Continuous CodeQL & Privacy Monitoring
#===============================================================================
typeset _zsh_pure=${(%):-%x}

# 1. Dynamic Repo Discovery (Rule 4 Alignment)
typeset _repo=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
if [[ -z "${_repo}" ]]; then
    echo "[SECURITY] Warning: Could not determine repository name. Skipping CodeQL audit."
else
    # 2. CodeQL Monitoring
    echo "[SECURITY] Auditing CodeQL Alerts for ${_repo}..."
    local _alerts=$(gh api "repos/${_repo}/code-scanning/alerts" --params 'state=open' -q '.[] | select(.rule.security_severity_level == "high" or .rule.security_severity_level == "critical") | .html_url' 2>/dev/null)

    if [[ -n "${_alerts}" ]]; then
        echo -e "\033[0;31m[CRITICAL] Unremediated High/Critical CodeQL Alerts Found:\033[0m"
        echo "${_alerts}"
        exit 1
    fi
    echo "[SECURITY] CodeQL High/Critical Audit: PASS"
fi

# 3. Privacy Leak Guard (Absolute Path Detection)
echo "[SECURITY] Scanning for Absolute Path Leaks..."
# Purge matches for the literal pattern in this script and exclude common non-text dirs
# Using grep -r to find absolute /Users/ paths while excluding self and known artifacts
# We explicitly exclude .tmp.driveupload/download as they contain ephemeral artifacts with absolute paths
typeset _leaks=$(grep -r "/Users/" . \
    --exclude-dir=.git \
    --exclude-dir=.cache \
    --exclude-dir=.tmp.driveupload \
    --exclude-dir=.tmp.drivedownload \
    --exclude-dir=logs \
    --exclude-dir=node_modules \
    --exclude-dir=__pycache__ \
    --exclude-dir=SKILLS \
    --exclude="*.pdf" \
    --exclude="vde-security-audit.zsh" \
    --exclude="vde-root-guard" \
    --exclude="README.md" | wc -l)

if [[ ${_leaks} -gt 0 ]]; then
    echo -e "\033[0;31m[CRITICAL] Absolute Path Leaks Detected in Workspace!\033[0m"
    grep -r "/Users/" . \
        --exclude-dir={.git,.cache,.tmp.driveupload,.tmp.drivedownload,logs,node_modules,__pycache__,SKILLS} \
        --exclude={"*.pdf","vde-security-audit.zsh","vde-root-guard","README.md"} | head -n 5
    exit 1
fi
echo "[SECURITY] Privacy Leak Audit: PASS"

exit 0
