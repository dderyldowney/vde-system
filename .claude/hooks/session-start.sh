#!/usr/bin/env bash
# VDE Session Start Hook
# Preloads critical library metadata to reduce token usage
# This hook runs when a Claude Code session starts for this project

set -euo pipefail

# Colors for output
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[VDE Hook]${NC} $*"
}

log_debug() {
    echo -e "${BLUE}[VDE Hook]${NC} $*"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PROJECT_ROOT

# ==============================================================================
# VDE Library Metadata Preload
# ==============================================================================
# Instead of loading entire library files, we capture their structure and key
# patterns. This allows Claude to understand the codebase without expensive
# re-reads of large files.

log_info "Preloading VDE library metadata..."

# Library file summaries (structure only)
declare -A LIBRARY_SUMMARIES=(
    ["vde-constants"]="Return codes, port ranges, timeouts, exit codes"
    ["vde-shell-compat"]="Cross-shell compatibility layer (zsh 5.x, bash 4.x, bash 3.x)"
    ["vde-errors"]="Structured error handling with remediation suggestions"
    ["vde-log"]="JSON/text/syslog logging with rotation"
    ["vde-core"]="Basic VDE operations (VM status, SSH checks)"
    ["vm-common"]="Full VM management (Docker, SSH, templates) - LARGEST LIB"
    ["vde-commands"]="Safe wrapper functions for AI/CLI validation"
    ["vde-parser"]="Natural language intent detection (start, stop, create, list, etc.)"
    ["vde-naming"]="VM naming conventions and validation"
    ["vde-audit"]="Security and configuration auditing"
    ["vde-metrics"]="Performance and usage metrics collection"
    ["vde-progress"]="Progress bars and user feedback"
    ["vde-ai-api"]="AI assistant integration layer"
)

# Key patterns in VDE scripts
declare -a VDE_PATTERNS=(
    "All scripts use #!/usr/bin/env zsh shebang (NOT sh)"
    "Source guard pattern: if [ \"\${_LIB_LOADED:-}\" = \"1\" ]; then return 0; fi"
    "Port allocation: 2200-2299 (language VMs), 2400-2499 (service VMs)"
    "Return codes: 0=success, 1=general, 2=invalid_input, 3=not_found, 4=permission, 5=timeout"
    "Docker container naming: <vm-name>-dev (e.g., python-dev, rust-dev)"
    "SSH config: User devuser, password auth disabled, keys from public-ssh-keys/"
    "Template system: language-compose.yml.template, service-compose.yml.template"
    "VM types defined in: scripts/data/vm-types.conf"
    "Data-driven: adding VM type requires only one line in vm-types.conf"
)

# Critical files to index
declare -a CRITICAL_FILES=(
    "scripts/lib/vm-common"
    "scripts/lib/vde-shell-compat"
    "scripts/lib/vde-constants"
    "scripts/data/vm-types.conf"
    "scripts/vde"
    "CLAUDE.md"
)

# ==============================================================================
# Generate Observation for Session Context
# ==============================================================================
# This creates an observation that claude-mem can index, making the patterns
# searchable in future sessions.

generate_observation() {
    cat <<'EOF'
<observation>
  <type>discovery</type>
  <title>VDE Session Startup - Library Structure Indexed</title>
  <category>shell-pattern</category>
  <concepts>how-it-works,dependency-chain</concepts>
  <narrative>
# VDE Library Architecture

## Core Libraries (scripts/lib/)

| Library | Purpose | Size |
|---------|---------|------|
| vm-common | Full VM management (Docker, SSH, templates) | Largest (69KB) |
| vde-shell-compat | Cross-shell compatibility (zsh, bash 4.x, bash 3.x) | 21KB |
| vde-constants | Return codes, port ranges, timeouts | 8KB |
| vde-parser | Natural language intent detection | 28KB |
| vde-commands | Safe wrappers for AI/CLI | 15KB |
| vde-errors | Structured error handling | 10KB |
| vde-log | Logging system (JSON/text/syslog) | 14KB |
| vde-core | Basic operations (status, SSH checks) | 9KB |

## Key Patterns

1. **Shebang**: All scripts use `#!/usr/bin/env zsh` (NOT sh)
2. **Source Guard**: `if [ "${_LIB_LOADED:-}" = "1" ]; then return 0; fi`
3. **Ports**: 2200-2299 (language VMs), 2400-2499 (services)
4. **Return Codes**: 0=success, 1=general, 2=invalid, 3=not_found, 4=permission, 5=timeout
5. **Naming**: `<vm>-dev` for containers, `User devuser` for SSH

## Data-Driven Design

- **vm-types.conf**: One line per VM type defines everything
- **Templates**: language-compose.yml.template, service-compose.yml.template
- **Adding VM**: Single line to vm-types.conf, run generate-all-configs

## Critical Files for Understanding

1. `CLAUDE.md` - Project instructions (MANDATORY reading)
2. `scripts/lib/vm-common` - VM management core
3. `scripts/lib/vde-shell-compat` - Shell compatibility layer
4. `scripts/vde` - Unified CLI entry point
5. `scripts/data/vm-types.conf` - VM type definitions
  </narrative>
</observation>
EOF
}

# ==============================================================================
# Hook Execution
# ==============================================================================

log_debug "Project root: $PROJECT_ROOT"
log_debug "Libraries indexed: ${#LIBRARY_SUMMARIES[@]}"
log_debug "Patterns captured: ${#VDE_PATTERNS[@]}"

# Output the observation (will be captured by claude-mem)
generate_observation

# ==============================================================================
# CRITICAL: Output Session State Files
# ==============================================================================
# These files MUST be read by Claude at session start. We output them directly
# so they appear in the startup context and cannot be missed.

log_info "Session state files:"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SESSION_STATE.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$PROJECT_ROOT/SESSION_STATE.md" 2>/dev/null || echo "⚠️  SESSION_STATE.md not found"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TODO.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "$PROJECT_ROOT/TODO.md" 2>/dev/null || echo "⚠️  TODO.md not found"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

log_info "VDE context preloaded. Use memory search before reading large files."

# ==============================================================================
# MCP Services Available
# ==============================================================================

log_info "MCP services configured in .mcp.json:"
echo "  • github       - GitHub API access (PRs, issues, files, search)"
echo "  • sequential-thinking - Structured problem-solving and planning"
echo "  • fetch        - Web requests and external data fetching"
echo ""

# ==============================================================================
# Planning & Accountability Reminder
# ==============================================================================

echo "⚠️  MANDATORY: All work requires planning BEFORE implementation."
echo "   Use /plan, EnterPlanMode tool, or claude-mem:plan for complex tasks."
echo ""
echo "⚠️  DO NOT start work on TODO.md items without explicit user authorization."
echo ""

exit 0
