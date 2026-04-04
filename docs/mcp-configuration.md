# MCP Configuration Documentation

## Overview

This document describes the MCP (Model Context Protocol) server configuration for the VDE project. MCP servers extend the capabilities of the Gemini CLI by providing specialized tools for various tasks.

> **MANDATE**: All agents MUST utilize these connected MCP servers as their primary interface for system interaction. Documentation updates and technical queries MUST utilize `context7` and `gemini-docs-mcp`.

## Configuration Location

The project-specific MCP configuration is located at:
```
.gemini/settings.json
```

Global configuration can be found at:
```
~/.gemini/settings.json
```

## Configured Services

| Service | Purpose | Status |
|---------|---------|--------|
| `context7` | Up-to-date documentation and code examples | ✅ Configured |
| `gemini-docs-mcp` | Gemini API and CLI documentation | ✅ Configured |
| `redis-mcp-server` | Natural language interface for Redis | ✅ Configured |
| `github` | PRs, issues, file operations, code review | ✅ Configured |
| `sequential-thinking` | Complex reasoning, debugging, planning | ✅ Configured |
| `MCP_DOCKER` | Docker operations and gateway | ✅ Configured |

## Configuration File (.gemini/settings.json)

```json
{
  "mcp": {
    "allowed": [
      "context7",
      "gemini-docs-mcp",
      "MCP_DOCKER",
      "github",
      "redis",
      "firebase",
      "google-workspace"
    ]
  },
  "mcpServers": {
    "context7": {
      "timeout": 60000,
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"]
    },
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"]
    }
  }
}
```

## Setup Instructions

### 1. Context7 Setup

Context7 provides up-to-date documentation. It is configured to run via `npx`. Ensure you have an internet connection for the first run.

### 2. Redis MCP Server

The Redis MCP server can be configured via `uvx` or `docker`. For VDE, we prefer the Docker-based approach for isolation:

```bash
gemini mcp add redis docker run --rm --name redis-mcp-server -i -e REDIS_URL=redis://localhost:6379/0 mcp-redis
```

### 3. GitHub Token Setup

The GitHub MCP server requires a personal access token:

1. Generate a GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Create token with scopes: `repo`, `read:org`, `read:user`

2. Set the environment variable:
   ```bash
   export GITHUB_TOKEN="your_token_here"
   ```

## Service Details

### context7
- **Package:** `@upstash/context7-mcp`
- **Purpose:** Prevents outdated or hallucinated API responses by providing real-time documentation.
- **Usage:** "Researcher, use context7 to find the latest Next.js routing patterns."

### gemini-docs-mcp
- **Purpose:** Specialized documentation for Gemini API and CLI features.
- **Usage:** Must be used before any Gemini API integration.

### redis-mcp-server
- **Package:** `mcp-redis`
- **Purpose:** Natural language interface for managing and searching data in Redis.
- **Usage:** "Database Admin, check the user session cache in Redis."

### MCP_DOCKER
- **Purpose:** Bridge between the CLI and Docker runtime for VM management.

## Troubleshooting

### Check Configuration
```bash
cat .gemini/settings.json | jq .
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
- [Kilo Code MCP Rules](../.gemini/RULES/tools_mcp.md)
