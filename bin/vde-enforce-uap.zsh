#!/usr/bin/env zsh
# @forge (Governance Sentinel)
#===============================================================================
# vde-enforce-uap.zsh - Universal Agent Protocol Enforcement (Hardened)
set -e
#
# Enforces the Strict Core Mandates from AGENTS.md:
# 1. Sovereign ZSH Purity (Shebang & Content)
# 2. Forbidden Patterns (No sleep, No bash-isms)
# 3. Structural Integrity (Mandatory Configs)
#===============================================================================
typeset _ZSH_PURE=${(%):-%x}

# Absolute on purpose (:A): a relative root such as "." would make every rule below depend on the caller's directory.
VDE_ROOT_DIR="${0:A:h:h}"

# 0. Technical Integrity Gate (Project 1 Dependency)
# The Forge cannot be lit without the Unyielding Tetrad.
if [[ -f "${VDE_ROOT_DIR}/bin/vde-check-tetrad.zsh" ]]; then
    "${VDE_ROOT_DIR}/bin/vde-check-tetrad.zsh" || exit 1
fi

# Parse flags
quiet=0
if [[ "${1}" == "--quiet" || "${1}" == "-q" ]]; then
    quiet=1
    shift
fi

# Counters for Verdict
errors=0
warnings=0

#===============================================================================
# GHOST ZONE CHECK (Zero-Tolerance)
#===============================================================================

# Rule 3 Enforcement: plans/ Subdirectory Lock (REPORT-ONLY, Signet #643)
# The audit fails (zero tolerance) and names every offending directory, but it
# NEVER deletes anything: an untracked file under an offender has no way back.
# Hidden directories (plans/.<name>/) count: the (D) glob qualifier matches them.
# The rule reads plans/ under the absolute VDE_ROOT_DIR, so it audits the repository the
# enforcer lives in whatever the caller's working directory is.
typeset plans_dir="${VDE_ROOT_DIR}/plans"
if [[ -d "${plans_dir}" ]]; then
    typeset -a ghost_zones=()
    for item in "${plans_dir}"/*(DN/); do
        local sub_name="${item:t}"
        if [[ "${sub_name}" != "scripts" && "${sub_name}" != "archive" ]]; then
            ghost_zones+=("${sub_name}")
        fi
    done
    if (( ${#ghost_zones} > 0 )); then
        for sub_name in "${ghost_zones[@]}"; do
            echo "\033[1;31m[CRITICAL FAILURE]\033[0m Ghost Zone 'plans/${sub_name}/' detected."
            echo "Protocol Violation: Rule 3 (Ghost Zone Prohibition)."
            echo "Nothing was deleted. Move 'plans/${sub_name}/' under plans/archive/ or remove it deliberately, then re-run the audit."
        done
        exit 1
    fi
fi

# Mandatory config files (Mandate 0 & 14 integration; the security policy, rule and process: Signet #736)
MANDATORY_FILES=("AGENTS.md" "GEMINI.md" ".gemini/STATE/MEMORY.md" "SECURITY.md" ".gemini/RULES/security.md" ".gemini/RULES/security-preamble.md" "docs/governance/security-process.md" "docs/security/advisories.md")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check for mandatory config files [Mandate 0]
[[ $quiet -eq 0 ]] && echo -e "${GREEN}[UAP-START]${NC} Verifying mandatory configurations..."
for file in "${MANDATORY_FILES[@]}"; do
    # -f and -s: a regular file AND non-empty (an emptied policy file, or a directory put in its place, is as bad as a missing one).
    if [[ ! -f "${VDE_ROOT_DIR}/${file}" || ! -s "${VDE_ROOT_DIR}/${file}" ]]; then
        echo -e "${RED}[UAP-ERROR]${NC} Mandatory file missing or empty: ${file}"
        errors=$((errors + 1))
    fi
done

# 1b. The private security directory (Signet #737): the Forge creates it, never assumes it.
# FORGE ONLY: nothing on the student (@armor) install or upgrade path calls this. The path
# is not printed, so a public CI log never shows where it is.
if [[ ! -f "${VDE_ROOT_DIR}/lib/vde-security-dir" ]]; then
    echo -e "${RED}[UAP-ERROR]${NC} lib/vde-security-dir missing; cannot create the private security directory."
    errors=$((errors + 1))
else
    source "${VDE_ROOT_DIR}/lib/vde-security-dir"
    if ! typeset -f vde_security_dir_ensure >/dev/null; then
        echo -e "${RED}[UAP-ERROR]${NC} lib/vde-security-dir did not define vde_security_dir_ensure; the private security directory cannot be created."
        errors=$((errors + 1))
    elif ! vde_security_dir_ensure "${VDE_ROOT_DIR}" >/dev/null; then
        echo -e "${RED}[UAP-ERROR]${NC} The private security directory is unavailable (see the [SECURITY-DIR] line above); security work needs it."
        errors=$((errors + 1))
    fi
fi

# 2. The Audit Function (Deep Content Inspection)
audit_file_content() {
    local file=$1
    local first_line
    
    # Skip backup files explicitly
    if [[ "$file" == *.bak ]]; then
        return
    fi
    
    # Skip binary files
    if ! (file "$file" | grep -qE "text|JSON|XML|source"); then
        return
    fi
    
    # Mandate 24: Absolute Tagging Rule (Line 2 or 3)
    # Architectural tags can NEVER be on the first line.
    if head -n 1 "$file" | grep -qE "@armor|@forge|@shared-law"; then
        echo -e "${RED}[UAP-ERROR]${NC} Architectural tag found on line 1 of ${file#${VDE_ROOT_DIR}/}. Move to line 2 or 3."
        errors=$((errors + 1))
    fi

    # Support # (Shell/Python/INI), <!-- --> (XML/Markdown), " (JSON), // (JS/C), -- (SQL)
    # ZSH-native pattern matching for tag extraction
    local tag_found=$(sed -n '2,3p' "$file" | grep -E "^[[:space:]]*(#|<!--|//|\"|--|;)[[:space:]]*@(armor|forge|shared-law).*")
    if [[ -z "${tag_found}" ]]; then
        echo -e "${RED}[UAP-ERROR]${NC} Missing or invalid architectural tag in lines 2-3 of ${file#${VDE_ROOT_DIR}/}."
        echo "Expected Pattern: @armor|@forge|@shared-law (Functional Effect)"
        errors=$((errors + 1))
    fi

    # Only audit ZSH logic for scripts (skip data and documentation)
    if [[ "$file" == *.zsh || ( "$file" != *.* && $(file "$file" 2>/dev/null) == *"shell script"* ) ]]; then
        # Mandate 1: Sovereign Shebang Check (ZSH ONLY)
        read -r first_line < "$file"
        if [[ "${first_line}" != "#!/usr/bin/env zsh" && "${first_line}" != "#!/bin/zsh" ]]; then
            echo -e "${RED}[UAP-ERROR]${NC} Non-canonical ZSH shebang in ${file#${VDE_ROOT_DIR}/}. Expected #!/usr/bin/env zsh"
            errors=$((errors + 1))
        fi

        # Forbidden Pattern: Sleep Calls [CRITICAL FORBIDDEN PATTERNS]
        if grep -qE "\bsleep [0-9]+" "$file"; then
            echo -e "${RED}[UAP-ERROR]${NC} Forbidden 'sleep' found in ${file#${VDE_ROOT_DIR}/}. Use polling."
            errors=$((errors + 1))
        fi

        # Bash-ism: Single Brackets [CRITICAL FORBIDDEN PATTERNS]
        if grep -q " \[ " "$file" && ! grep -q " \[\[ " "$file"; then
             echo -e "${YELLOW}[UAP-WARN]${NC} Potential Bash-style '[' in ${file#${VDE_ROOT_DIR}/}. Use ZSH '[[ ]]'"
             warnings=$((warnings + 1))
        fi

        # Mandate 1: 0-indexed Arrays (Shibboleth) - ZSH ONLY
        if grep -q "\[0\]" "$file"; then
            echo -e "${RED}[UAP-ERROR]${NC} 0-indexed array found in ${file#${VDE_ROOT_DIR}/}. ZSH is 1-indexed."
            errors=$((errors + 1))
        fi

        # Mandate 1: "Fake ZSH" Detection (Checks for lack of expansion flags)
        if [[ $(wc -l < "$file") -gt 30 ]] && ! grep -q "\${(" "$file"; then
            echo -e "${YELLOW}[UAP-WARN]${NC} ${file#${VDE_ROOT_DIR}/} lacks ZSH parameter flags. Verify ZSH-native logic."
            warnings=$((warnings + 1))
        fi
    elif [[ "$file" == *.py ]]; then
        # Python Shebang Check
        read -r first_line < "$file"
        if [[ "${first_line}" != "#!/usr/bin/env python3" ]]; then
            echo -e "${RED}[UAP-ERROR]${NC} Non-canonical Python shebang in ${file#${VDE_ROOT_DIR}/}. Expected #!/usr/bin/env python3"
            errors=$((errors + 1))
        fi
        
        # Forbidden Pattern: Sleep Calls in Python (still applies to governance logic)
        if grep -qE "time\.sleep\(" "$file"; then
            echo -e "${RED}[UAP-ERROR]${NC} Forbidden 'sleep' found in Python script ${file#${VDE_ROOT_DIR}/}. Use polling."
            errors=$((errors + 1))
        fi
    fi
}

# 3. Directory Traversal Logic
check_dir() {
    local dir=$1
    if [[ ! -d "$dir" ]]; then return; fi
    
    # Skip archive directory
    if [[ "${dir}" == *"bin/archive" ]]; then
        return
    fi

    [[ $quiet -eq 0 ]] && echo -e "${GREEN}[UAP-CHECK]${NC} Auditing directory: ${dir#${VDE_ROOT_DIR}/}"
    # Use recursive glob (**) to audit all files in subdirectories
    for file in "${dir}"/**/*(N.); do
        # Skip files in archive subdirectories
        if [[ "$file" == *"bin/archive/"* ]]; then
            continue
        fi

        # Audit all files in these directories
        if [[ -f "$file" ]]; then
            audit_file_content "$file"
        fi
    done
}

# Run Audits on core directories
check_dir "${VDE_ROOT_DIR}/bin"
check_dir "${VDE_ROOT_DIR}/lib"
check_dir "${VDE_ROOT_DIR}/.gemini"
check_dir "${VDE_ROOT_DIR}/env-files"
check_dir "${VDE_ROOT_DIR}/scripts"
check_dir "${VDE_ROOT_DIR}/data"
check_dir "${VDE_ROOT_DIR}/docs"
check_dir "${VDE_ROOT_DIR}/templates"
check_dir "${VDE_ROOT_DIR}/tests"
check_dir "${VDE_ROOT_DIR}/githooks"
check_dir "${VDE_ROOT_DIR}/.github"
check_dir "${VDE_ROOT_DIR}/.gemini_security"

# Prints one shibboleth error line; `print -r` keeps backslashes in file names raw.
shib_error() { printf '%b' "${RED}[UAP-ERROR]${NC} "; print -r -- "$*"; }

# 3b. Shibboleth sweep (Mandate C, Signet #626): every tracked zsh file must carry the literal line; shrink-only baseline.
if [[ ! -f "${VDE_ROOT_DIR}/lib/vde-shibboleth" ]]; then
    echo -e "${RED}[UAP-ERROR]${NC} lib/vde-shibboleth missing; cannot enforce the shibboleth (Mandate C)."
    errors=$((errors + 1))
else
    source "${VDE_ROOT_DIR}/lib/vde-shibboleth"
    if ! typeset -f vde_shib_sweep >/dev/null || ! typeset -f vde_shib_sweep_snapshot >/dev/null || ! typeset -f vde_shib_baseline_growth >/dev/null || ! typeset -f vde_shib_ensure_base_ref >/dev/null; then
        echo -e "${RED}[UAP-ERROR]${NC} lib/vde-shibboleth did not define its functions; the shibboleth cannot be enforced (Mandate C)."
        errors=$((errors + 1))
    else
    # `|| shib_rc=$?`: this script runs under `set -e`, and a bare assignment from a
    # failing command substitution would end the audit silently with no report.
    typeset -A shib_missing_set=()
    shib_rc=0
    shib_out="$(vde_shib_sweep "${VDE_ROOT_DIR}")" || shib_rc=$?
    if [[ $shib_rc -ne 0 ]]; then
        while IFS= read -r shib_line; do
            [[ -z "${shib_line}" ]] && continue
            case "${shib_line}" in
                MISSING\ *)
                    shib_rel="${shib_line#MISSING }"
                    shib_error "Shibboleth MISSING in ${shib_rel}: add '${VDE_SHIBBOLETH_LITERAL}' as its own line within the first 20 lines (Mandate C)."
                    shib_missing_set[${shib_rel}]=1
                    ;;
                UNREADABLE\ *)
                    shib_rel="${shib_line#UNREADABLE }"
                    shib_error "Shibboleth UNREADABLE ${shib_rel}: the file cannot be read, so the shibboleth cannot be verified (fix its permissions)."
                    ;;
                STALE\ *)
                    # Contract: `STALE <rel> :: <reason>`; split on the first ` :: ` (rel may contain spaces).
                    shib_rest="${shib_line#STALE }"
                    if [[ "${shib_rest}" == *" :: "* ]]; then
                        shib_rel="${shib_rest%% :: *}"
                        shib_reason="${shib_rest#* :: }"
                    else
                        shib_rel="${shib_rest}"
                        shib_reason="unspecified"
                    fi
                    shib_error "Shibboleth baseline entry ${shib_rel} is stale (${shib_reason}); remove it from docs/governance/shibboleth-baseline.txt."
                    ;;
                *)
                    shib_error "${shib_line}"
                    ;;
            esac
            errors=$((errors + 1))
        done <<< "${shib_out}"
    fi
    # Signet #645: the sweep above judges the WORKING copy, but the bytes a push carries are the
    # COMMITTED ones. A file the working-copy sweep already reported is not reported twice.
    shib_snap_rc=0
    shib_snap_out="$(vde_shib_sweep_snapshot "${VDE_ROOT_DIR}" head)" || shib_snap_rc=$?
    shib_snap_errors=0
    if [[ $shib_snap_rc -ne 0 ]]; then
        while IFS= read -r shib_line; do
            [[ -z "${shib_line}" ]] && continue
            case "${shib_line}" in
                COMMITTED\ *)
                    shib_rel="${shib_line#COMMITTED }"
                    [[ -n "${shib_missing_set[${shib_rel}]:-}" ]] && continue
                    shib_error "Shibboleth MISSING in the COMMITTED version of ${shib_rel}: HEAD has no shibboleth line in that file (a working-copy fix does not count until it is committed); add '${VDE_SHIBBOLETH_LITERAL}' as its own line within the first 20 lines and commit it (Mandate C)."
                    ;;
                *)
                    shib_error "${shib_line}"
                    ;;
            esac
            errors=$((errors + 1))
            shib_snap_errors=$((shib_snap_errors + 1))
        done <<< "${shib_snap_out}"
    fi
    # Fail closed: rc 2 (git could not answer) with no message must still fail the audit.
    if [[ $shib_snap_rc -ge 2 && $shib_snap_errors -eq 0 ]]; then
        shib_error "Shibboleth committed-content check failed (rc ${shib_snap_rc}) without a message; the bytes a push carries were not verified."
        errors=$((errors + 1))
        shib_snap_errors=$((shib_snap_errors + 1))
    fi
    if [[ $shib_rc -eq 0 && $shib_snap_errors -eq 0 ]]; then
        [[ $quiet -eq 0 ]] && echo -e "${GREEN}[UAP-CHECK]${NC} Shibboleth sweep clean"
    fi

    # Shrink-only growth check: baseline entries absent from the base ref are errors.
    shib_base="${VDE_SHIB_BASE_REF:-origin/${VDE_ANVIL_BRANCH:-develop}}"
    # Best-effort, at most one fetch (never truncates history); a failed fetch is judged below.
    vde_shib_ensure_base_ref "${VDE_ROOT_DIR}" "${shib_base}" || true
    shib_grow_rc=0
    shib_growth="$(vde_shib_baseline_growth "${VDE_ROOT_DIR}" "${shib_base}")" || shib_grow_rc=$?
    case $shib_grow_rc in
        0) ;;
        1)
            while IFS= read -r shib_grow_line; do
                [[ -z "${shib_grow_line}" ]] && continue
                if [[ "${shib_grow_line}" == "baseline file deleted"* ]]; then
                    # The library already says what happened and what to do; "GREW" would mislead.
                    shib_error "Shibboleth ${shib_grow_line}."
                else
                    shib_error "Shibboleth baseline GREW versus ${shib_base}: ${shib_grow_line}. The baseline is shrink-only: add the shibboleth to that file instead of listing it."
                fi
                errors=$((errors + 1))
            done <<< "${shib_growth}"
            ;;
        2)
            # rc 2: the library's own read/parse error text is the first line of its output.
            shib_grow_first="${shib_growth%%$'\n'*}"
            shib_error "Shibboleth baseline growth could not be checked: ${shib_grow_first}"
            errors=$((errors + 1))
            ;;
        *)
            # Fail closed: rc 3 (base ref unresolvable) or anything unexpected.
            shib_error "Shibboleth baseline growth could not be checked: base ref '${shib_base}' is unavailable (fetch it, or set VDE_SHIB_BASE_REF)."
            errors=$((errors + 1))
            ;;
    esac
    # The growth above reads the WORKING-TREE baseline. An exemption a commit added and an uncommitted edit
    # then removed would hide from it, yet the push carries the commit: judge the COMMITTED baseline too, and
    # report an entry once (Signet #646). Only when the base resolved (rc 0 or 1 above).
    if [[ $shib_grow_rc -le 1 ]]; then
        shib_head_rc=0
        shib_head_growth="$(vde_shib_baseline_growth "${VDE_ROOT_DIR}" "${shib_base}" "" head)" || shib_head_rc=$?
        shib_seen_lines=("${(@f)shib_growth}")
        case $shib_head_rc in
            0) ;;
            1)
                while IFS= read -r shib_grow_line; do
                    [[ -z "${shib_grow_line}" ]] && continue
                    # already reported by the working-copy view
                    (( ${shib_seen_lines[(Ie)${shib_grow_line}]} )) && continue
                    if [[ "${shib_grow_line}" == "baseline file deleted"* ]]; then
                        shib_error "Shibboleth ${shib_grow_line}."
                    else
                        shib_error "Shibboleth baseline GREW in the COMMITTED baseline versus ${shib_base}: ${shib_grow_line}. The baseline is shrink-only: add the shibboleth to that file instead of listing it."
                    fi
                    errors=$((errors + 1))
                done <<< "${shib_head_growth}"
                ;;
            *)
                shib_error "Shibboleth committed baseline growth could not be checked (rc ${shib_head_rc}): ${shib_head_growth%%$'\n'*}"
                errors=$((errors + 1))
                ;;
        esac
    fi
    fi
fi

# 4. Continuous Security & Privacy Audit
if [[ -f "${VDE_ROOT_DIR}/bin/vde-security-audit.zsh" ]]; then
    zsh "${VDE_ROOT_DIR}/bin/vde-security-audit.zsh" || errors=$((errors + 1))
fi

# 5. Final Verdict [REWRITTEN]
if [[ $errors -gt 0 ]] || [[ $warnings -gt 0 ]]; then
    echo -e "\n${RED}[UAP-FAILURE]${NC} $errors violations and $warnings warnings detected."
    echo -e "${YELLOW}[MANDATE 14 ACTIVE]${NC} Agent must halt current phase and generate a remediation plan."
    exit 1
else
    [[ $quiet -eq 0 ]] && echo -e "\n${GREEN}[UAP-SUCCESS]${NC} All core mandates satisfied. Agent is cleared for action."
    # Support wrapping commands for Mandatory Enforcer Supervision (Mandate 3)
    # Only execute if the script is NOT being sourced (detecting via ZSH_EVAL_CONTEXT)
    if [[ $# -gt 0 && "${ZSH_EVAL_CONTEXT}" != *"toplevel"* ]]; then
        # If the only argument is --quiet, don't try to exec it
        if [[ "$1" != "--quiet" ]]; then
            [[ $quiet -eq 0 ]] && echo -e "${GREEN}[UAP-EXEC]${NC} Executing supervised command: $@"
            exec "$@"
        fi
    fi
    exit 0
fi
