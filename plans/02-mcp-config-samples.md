# MCP Configuration Samples

## Configuration File Location
**Primary:** `~/.kilocode/cli/global/settings/mcp_settings.json`

## Sample Configurations

### Option 1: Minimal Configuration (Official Servers Only)

This configuration includes only the 4 confirmed official MCP servers that are available.

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
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
```

**Pros:**
- ✅ All servers are official and maintained
- ✅ No custom implementation needed
- ✅ Easy to set up and test

**Cons:**
- ❌ Missing 4 services: context7, 4.5v-mcp, web_reader, claude-mem
- ❌ May not meet all requirements from tools_mcp.md

---

### Option 2: Extended Configuration (With Puppeteer for Web Reading)

This adds the puppeteer server for web scraping capabilities.

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
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
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

**Pros:**
- ✅ Adds web scraping capabilities
- ✅ Still using official servers

**Cons:**
- ❌ Still missing 3 services: context7, 4.5v-mcp, claude-mem
- ⚠️ Puppeteer may be heavier (requires Chrome/Chromium)

---

### Option 3: Global Installation (Faster Startup)

If you prefer global installation for faster startup times:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "mcp-server-sequential-thinking"
    },
    "github": {
      "command": "mcp-server-github",
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    },
    "fetch": {
      "command": "mcp-server-fetch"
    },
    "memory": {
      "command": "mcp-server-memory"
    }
  }
}
```

**Installation Commands:**
```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-memory
```

**Pros:**
- ✅ Faster startup (no npx overhead)
- ✅ Works offline after installation

**Cons:**
- ❌ Requires manual updates
- ❌ Global namespace pollution

---

### Option 4: Placeholder Configuration (All Services)

This configuration includes placeholders for ALL 8 required services. Services marked with `PLACEHOLDER` need to be replaced with actual implementations.

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
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
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
    },
    "context7": {
      "command": "PLACEHOLDER",
      "args": ["NEEDS_IMPLEMENTATION"],
      "disabled": true
    },
    "4.5v-mcp": {
      "command": "PLACEHOLDER",
      "args": ["NEEDS_IMPLEMENTATION"],
      "disabled": true
    },
    "claude-mem": {
      "command": "PLACEHOLDER",
      "args": ["NEEDS_IMPLEMENTATION"],
      "disabled": true
    }
  }
}
```

**Note:** The `disabled` flag (if supported) prevents these from being loaded until implemented.

---

## Configuration with Environment Variables

For better security, use environment variables for sensitive data:

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
    }
  }
}
```

Then set in your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export GITHUB_TOKEN="your_github_token_here"
```

---

## Testing Configuration

After configuring, test each server individually:

### Test sequential-thinking
```bash
npx -y @modelcontextprotocol/server-sequential-thinking
```

### Test github (requires token)
```bash
GITHUB_PERSONAL_ACCESS_TOKEN="your_token" npx -y @modelcontextprotocol/server-github
```

### Test fetch
```bash
npx -y @modelcontextprotocol/server-fetch
```

### Test memory
```bash
npx -y @modelcontextprotocol/server-memory
```

---

## Troubleshooting

### Server Won't Start
1. Check Node.js version: `node --version` (requires Node.js 18+)
2. Check npm version: `npm --version`
3. Clear npm cache: `npm cache clean --force`
4. Try running server directly to see error messages

### GitHub Server Authentication Issues
1. Verify token has correct permissions (repo, read:org)
2. Check token is not expired
3. Ensure token is properly set in environment

### NPX Slow Startup
1. Consider global installation for frequently used servers
2. Check internet connection
3. Use `--prefer-offline` flag if packages are cached

### Memory Server Data Location
Default location: `~/.mcp-memory/`
- Can be changed with environment variable
- Ensure directory has write permissions

---

## Recommended Next Steps

1. **Start with Option 1 (Minimal):**
   - Get the 4 official servers working first
   - Verify Kilo Code can communicate with them
   - Test basic functionality

2. **Investigate Missing Services:**
   - Contact Kilo Code support about context7, 4.5v-mcp, claude-mem
   - Check if they're internal services or need custom implementation
   - Determine if alternatives are acceptable

3. **Add Web Reader (Optional):**
   - If web scraping is needed, add puppeteer server
   - Test with sample websites
   - Consider resource usage

4. **Document Your Configuration:**
   - Keep notes on what works
   - Document any custom implementations
   - Share findings with team

---

## GitHub Token Setup

To use the GitHub server, you need a Personal Access Token:

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name (e.g., "MCP Server")
4. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org and team membership)
   - `read:user` (Read user profile data)
5. Generate and copy the token
6. Add to configuration or environment variable

**Security Note:** Never commit tokens to version control. Use environment variables or secure secret management.
