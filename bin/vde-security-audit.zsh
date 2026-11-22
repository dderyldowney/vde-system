#!/usr/bin/env zsh
# @forge (Governance Sentinel)
#===============================================================================
# vde-security-audit.zsh - Continuous CodeQL & Privacy Monitoring
#===============================================================================
typeset _zsh_pure=${(%):-%x}

# Anchor every scan to the repo root (this script's grandparent dir), not the
# caller's cwd, so the guards cannot fail open when run from elsewhere.
typeset _audit_root="${0:A:h:h}"

# 1. Dynamic Repo Discovery (Rule 4 Alignment)
typeset _repo=""
if command -v gh >/dev/null 2>&1; then
    _repo=$(cd "${_audit_root}" && gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null)
    if [[ -z "${_repo}" ]]; then
        if ! gh auth status >/dev/null 2>&1 && [[ -z "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ]]; then
            echo "[SECURITY] Warning: gh is not authenticated. Skipping the CodeQL audit here (the CI \"Security & Privacy Audit\" job runs it with a token)."
        else
            echo -e "\033[0;31m[CRITICAL] gh is installed but the repository could not be determined (not logged in, offline or not a GitHub repository) -- the CodeQL audit cannot run, treating as unsafe.\033[0m"
            exit 1
        fi
    fi
    # 2. CodeQL Monitoring (skipped when gh is unauthenticated, _repo stays empty)
    if [[ -n "${_repo}" ]]; then
    echo "[SECURITY] Auditing CodeQL Alerts for ${_repo}..."
    typeset _alerts _api_rc _err_file
    _err_file="$(mktemp)"
    _alerts="$(gh api --paginate -X GET "repos/${_repo}/code-scanning/alerts" -f state=open -q '.[] | select(.rule.security_severity_level == "high" or .rule.security_severity_level == "critical") | .html_url' 2>"${_err_file}")"; _api_rc=$?
    if (( _api_rc != 0 )); then
        echo -e "\033[0;31m[CRITICAL] Could not read CodeQL alerts (gh api exit ${_api_rc}) -- treating as unsafe.\033[0m"
        head -n 3 -- "${_err_file}"
        rm -f -- "${_err_file}"
        exit 1
    fi
    rm -f -- "${_err_file}"

    if [[ -n "${_alerts}" ]]; then
        echo -e "\033[0;31m[CRITICAL] Unremediated High/Critical CodeQL Alerts Found:\033[0m"
        echo "${_alerts}"
        exit 1
    fi
    echo "[SECURITY] CodeQL High/Critical Audit: PASS"
    fi
else
    echo "[SECURITY] Warning: gh is not installed. Skipping CodeQL audit."
fi

# 3. Privacy Leak Guard (Absolute Path Detection)
echo "[SECURITY] Scanning for Absolute Path Leaks..."
# Exclude dirs and files shared by both the counting and display grep passes
typeset -a _scan_exclude_dirs=(.git .cache .claude .venv .tmp.driveupload .tmp.drivedownload logs node_modules __pycache__ SKILLS output projects)
typeset -a _scan_exclude_files=(vde-security-audit.zsh vde-root-guard README.md)
typeset -a _grep_excludes=()
for _d in "${_scan_exclude_dirs[@]}"; do _grep_excludes+=(--exclude-dir="${_d}"); done
for _f in "${_scan_exclude_files[@]}"; do _grep_excludes+=(--exclude="${_f}"); done
_grep_excludes+=(--exclude="*.pdf")

typeset _leak_hits _leak_rc
_leak_hits=$(grep -rn "${_grep_excludes[@]}" -- "/Users/" "${_audit_root}")
_leak_rc=$?
if (( _leak_rc == 0 )); then
    echo -e "\033[0;31m[CRITICAL] Absolute Path Leaks Detected in Workspace!\033[0m"
    echo "${_leak_hits}" | head -n 5
    exit 1
elif (( _leak_rc >= 2 )); then
    echo -e "\033[0;31m[CRITICAL] Privacy leak scan failed (grep error ${_leak_rc}) -- treating as unsafe.\033[0m"
    exit 1
fi
echo "[SECURITY] Privacy Leak Audit: PASS"

# 4. Build-Arg Secret Guard (Issue #560): a secret passed as a Docker build arg
#    bakes into image layers (Docker Scout violation). Secrets belong in
#    env_file at runtime, never in build.args. Scan compose templates and
#    generated compose files for the known offender appearing as a build-arg key.
echo "[SECURITY] Scanning for secrets in Docker build args..."
typeset -a _buildarg_scan=("${_audit_root}/templates" "${_audit_root}/configs/docker")
# A missing scan root means nothing was actually scanned -- fail rather than
# silently report clean (Sourcery #562).
typeset _p
for _p in "${_buildarg_scan[@]}"; do
    if [[ ! -d "${_p}" ]]; then
        echo -e "\033[0;31m[CRITICAL] Build-arg scan path missing: ${_p} -- incomplete scan, treating as unsafe.\033[0m"
        exit 1
    fi
done
# Distinguish grep's no-match status (1 = clean) from a read/scan error (>=2);
# only a clean no-match is a pass, a scan error fails the audit.
typeset _hits _grep_rc
_hits=$(grep -rnE '^[[:space:]]*POSTGRES_DEV_PASSWORD:' "${_buildarg_scan[@]}")
_grep_rc=$?
if (( _grep_rc == 0 )); then
    echo -e "\033[0;31m[CRITICAL] POSTGRES_DEV_PASSWORD present as a Docker build arg (secret baked into image layers)!\033[0m"
    echo "${_hits}" | head -n 5
    echo "Secrets belong in env_file at runtime, not build.args. See Issue #560."
    exit 1
elif (( _grep_rc >= 2 )); then
    echo -e "\033[0;31m[CRITICAL] Build-arg secret scan failed (grep error ${_grep_rc}) -- treating as unsafe.\033[0m"
    exit 1
fi
echo "[SECURITY] Build-Arg Secret Audit: PASS"

exit 0
