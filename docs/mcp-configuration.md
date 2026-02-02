# MCP Configuration Documentation

## Overview

This document describes the MCP (Model Context Protocol) server configuration for the VDE project. MCP servers extend the capabilities of Kilo Code by providing specialized tools for various tasks.

## Configuration Location

The MCP configuration is located at:
```
~/.kilocode/cli/global/settings/mcp_settings.json
```

## Configured Services

| Service | Purpose | Status |
|---------|---------|--------|
| `sequential-thinking` | Complex reasoning, debugging, planning | ✅ Configured |
| `github` | PRs, issues, file operations, code review | ✅ Configured |
| `fetch` | Web requests (HTML/JSON/Markdown/TXT) | ✅ Configured |
| `memory` | Knowledge graph (entities, relations) | ✅ Configured |
| `web_reader` | Web-to-Markdown conversion with image handling | ✅ Configured |

## Configuration File

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "web_reader": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

## Setup Instructions

### 1. GitHub Token Setup

The GitHub MCP server requires a personal access token:

1. Generate a GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Create token with scopes: `repo`, `read:org`, `read:user`

2. Set the environment variable:
   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```
   Add this to `~/.zshrc` for persistence.

### 2. Restart Kilo Code

After configuring MCP servers, restart Kilo Code to load the new configuration.

## Service Details

### sequential-thinking
- **Package:** `@modelcontextprotocol/server-sequential-thinking`
- **Purpose:** Dynamic and reflective problem-solving through structured thinking
- **Usage:** Complex reasoning, debugging, planning

### github
- **Package:** `@modelcontextprotocol/server-github`
- **Purpose:** GitHub integration for PRs, issues, file operations
- **Requires:** `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable

### fetch
- **Package:** `@modelcontextprotocol/server-fetch`
- **Purpose:** Web requests for HTML, JSON, Markdown, and text content

### memory
- **Package:** `@modelcontextprotocol/server-memory`
- **Purpose:** Knowledge graph for persistent context across sessions

### web_reader
- **Package:** `@modelcontextprotocol/server-puppeteer`
- **Purpose:** Web-to-Markdown conversion with JavaScript rendering

## Not Configured (Investigation Required)

| Service | Reason |
|---------|--------|
| `context7` | Documentation/API lookup - requires investigation |
| `4.5v-mcp` | Image analysis - may be built into Kilo Code |
| `claude-mem` | May overlap with `memory` server |

## Troubleshooting

### Check Configuration
```bash
cat ~/.kilocode/cli/global/settings/mcp_settings.json | jq .
```

### Test Individual Server
```bash
npx -y @modelcontextprotocol/server-[name]
```

### Clear NPX Cache (if issues)
```bash
npm cache clean --force
```

## References

- [MCP Implementation Plan](../mcp-implementation-plan.md)
- [Kilo Code MCP Rules](../.kilocode/rules/tools_mcp.md)
