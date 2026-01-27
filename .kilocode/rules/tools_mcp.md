# TOOLS & AGENTS REFERENCE
- PRIMARY: Use MCP services (sequential-thinking, github, context7, fetch) before local tools | Explore Agent: Codebase exploration | yume-implementer: Fixing guardian issues | yume-guardian: Reviewing for fake testing patterns | code-reviewer: Security and logic audits
## Sub-Agents (Task Tool)
| Agent | Purpose | Phase |
|-------|---------|-------|
| Explore | Codebase exploration, finding files, understanding architecture | Before Phase 1 |
| Plan | Designing implementation strategies | Phase 1 |
| yume-implementer | Fixing specific issues identified by yume-guardian | Phase 3 |
| yume-guardian | Review for fake testing patterns | Phase 3, Phase 5 |
| code-reviewer | Review for bugs, security, style | Phase 4 |
| general-purpose | Multi-step tasks, complex research, cross-file search | Any |
## MCP Services (PRIMARY - Use First)
| MCP Service | Purpose | When to Use |
|-------------|---------|-------------|
| `sequential-thinking` | Complex reasoning, debugging, planning | **ALL multi-step thinking** (Phase 0 requirement) |
| `github` | PRs, issues, file operations, search, code review | Any GitHub interaction |
| `context7` | Library/API docs, code examples from official sources | Documentation queries |
| `fetch` | Web requests, fetch HTML/JSON/Markdown/TXT | URL-based queries |
| `4.5v-mcp` | Image analysis | Image file inputs |
| `memory` | Knowledge graph - create entities, relations, observations | Cross-session context |
| `web_reader` | Web-to-Markdown conversion with image handling | Reading web content |
| `claude-mem` | Search/timeline memory observations | Retrieving session context |
## File Command Priority Order
**1. MCP File Services (PRIMARY)** - Use for: GitHub search, fetch, web_reader - When available: ALWAYS use first | **2. Local Toolsets (SECONDARY)** - Use when: MCP file services are unavailable - Tools: `jq`, `grep`, `find`, `cat`, `head`, `tail`, `sed`, `awk` | **3. Internal Toolsets (FALLBACK)** - Use when: Both MCP and local tools are unavailable - Tools: Read tool, Grep tool, Glob tool, Edit tool
