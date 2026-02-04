# MCP Server Implementation Plan

## Executive Summary

**Current State:** Empty MCP configuration file exists at [`~/.kilocode/cli/global/settings/mcp_settings.json`](~/.kilocode/cli/global/settings/mcp_settings.json)

**Goal:** Configure 8 MCP services as documented in [`.kilocode/rules/tools_mcp.md`](.kilocode/rules/tools_mcp.md)

**Status:** 4 of 8 services have official implementations available; 4 services need investigation or custom implementation

---

## Service Status Matrix

| Service | Status | Implementation | Priority | Action Required |
|---------|--------|----------------|----------|-----------------|
| sequential-thinking | ✅ Available | `@modelcontextprotocol/server-sequential-thinking` | **CRITICAL** | Configure |
| github | ✅ Available | `@modelcontextprotocol/server-github` | High | Configure + Token |
| fetch | ✅ Available | `@modelcontextprotocol/server-fetch` | High | Configure |
| memory | ✅ Available | `@modelcontextprotocol/server-memory` | Medium | Configure |
| web_reader | 🟡 Alternative | `@modelcontextprotocol/server-puppeteer` | Medium | Evaluate |
| context7 | ❌ Missing | Unknown | High | Investigate |
| 4.5v-mcp | ❌ Missing | Unknown | Medium | Investigate |
| claude-mem | ❌ Missing | Unknown | Medium | Investigate |

---

## Implementation Phases

### Phase 1: Core Setup (Immediate)
**Goal:** Get the 4 official MCP servers configured and working

#### Step 1.1: Verify Prerequisites
```bash
# Check Node.js version (requires 18+)
node --version

# Check npm
npm --version

# Test npx
npx --version
```

#### Step 1.2: Test Official Servers
Test each server individually before configuration:

```bash
# Test sequential-thinking
npx -y @modelcontextprotocol/server-sequential-thinking

# Test fetch
npx -y @modelcontextprotocol/server-fetch

# Test memory
npx -y @modelcontextprotocol/server-memory

# Test github (requires token - see Phase 1.3)
GITHUB_PERSONAL_ACCESS_TOKEN="test_token" npx -y @modelcontextprotocol/server-github
```

#### Step 1.3: Setup GitHub Token
1. Generate GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Create token with scopes: `repo`, `read:org`, `read:user`
2. Store securely (choose one):
   - **Option A:** Environment variable in `~/.zshrc`
   - **Option B:** Directly in config (less secure)
   - **Option C:** Use Kilo Code's secrets management

#### Step 1.4: Create Minimal Configuration
Update [`~/.kilocode/cli/global/settings/mcp_settings.json`](~/.kilocode/cli/global/settings/mcp_settings.json):

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

#### Step 1.5: Test Configuration
1. Restart Kilo Code or reload configuration
2. Verify servers are accessible
3. Test basic functionality of each service
4. Check logs for any errors

**Success Criteria:**
- ✅ All 4 servers start without errors
- ✅ Kilo Code can communicate with servers
- ✅ Basic operations work (thinking, fetch, memory, GitHub)

---

### Phase 2: Investigation (Research Required)
**Goal:** Determine the nature and availability of missing services

#### Step 2.1: Investigate context7
**Questions to Answer:**
- Is this an internal Kilo Code service?
- Is it a third-party MCP server?
- Is it a custom implementation?
- What is its exact purpose? (Library/API docs)

**Possible Actions:**
1. Check Kilo Code documentation
2. Search for `context7` in Kilo Code codebase
3. Contact Kilo Code support/community
4. Check MCP registry for similar services

**Alternatives if not found:**
- Use `fetch` server to query documentation sites
- Implement custom documentation query service
- Use web search APIs

#### Step 2.2: Investigate 4.5v-mcp
**Questions to Answer:**
- Is this Claude 4.5 Vision integration?
- Is it built into Kilo Code?
- Does it need separate configuration?

**Possible Actions:**
1. Check if Kilo Code has built-in vision capabilities
2. Review Kilo Code's Claude API integration
3. Determine if this is automatic or needs configuration

**Alternatives if not found:**
- May already be integrated into Kilo Code
- Could use Claude API directly
- May not need separate MCP server

#### Step 2.3: Investigate web_reader
**Questions to Answer:**
- Is puppeteer server sufficient?
- Are there specific requirements?
- What content types need to be read?

**Possible Actions:**
1. Test `@modelcontextprotocol/server-puppeteer`
2. Evaluate if it meets requirements
3. Consider lighter alternatives if puppeteer is too heavy

**Alternatives:**
- `@modelcontextprotocol/server-puppeteer` (official)
- Custom implementation with cheerio/jsdom
- Use `fetch` server for simple HTML

#### Step 2.4: Investigate claude-mem
**Questions to Answer:**
- Is this different from `memory` server?
- Is it Claude-specific memory features?
- Is it built into Kilo Code?

**Possible Actions:**
1. Compare with `memory` server functionality
2. Check if Kilo Code has built-in memory features
3. Determine if separate implementation is needed

**Alternatives if not found:**
- Use `memory` server as replacement
- May be built into Kilo Code's context management
- Could be Claude API feature

**Success Criteria:**
- ✅ Clear understanding of each missing service
- ✅ Identified whether internal or external
- ✅ Documented alternatives or implementation paths

---

### Phase 3: Extended Configuration (Conditional)
**Goal:** Add additional services based on Phase 2 findings

#### Scenario A: Services are Internal to Kilo Code
**Action:** Document that no additional configuration needed
**Update:** Add notes to configuration documentation

#### Scenario B: Services are Third-Party MCP Servers
**Action:** Add to configuration like Phase 1 servers
**Example:**
```json
{
  "mcpServers": {
    // ... existing servers ...
    "context7": {
      "command": "npx",
      "args": ["-y", "@package/context7-server"]
    }
  }
}
```

#### Scenario C: Services Need Custom Implementation
**Action:** Create custom MCP servers
**Steps:**
1. Design server interface
2. Implement server logic
3. Package as npm module or local script
4. Add to configuration
5. Test integration

#### Scenario D: Services Have Acceptable Alternatives
**Action:** Use alternative implementations
**Example:** Use puppeteer for web_reader:
```json
{
  "mcpServers": {
    // ... existing servers ...
    "web_reader": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    }
  }
}
```

**Success Criteria:**
- ✅ All required services either configured or documented as internal
- ✅ No missing functionality
- ✅ All services tested and working

---

### Phase 4: Optimization (Optional)
**Goal:** Improve performance and reliability

#### Step 4.1: Consider Global Installation
For frequently used servers, global installation reduces startup time:

```bash
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-github
npm install -g @modelcontextprotocol/server-fetch
npm install -g @modelcontextprotocol/server-memory
```

Update configuration to use global commands:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "mcp-server-sequential-thinking"
    }
    // ... etc
  }
}
```

#### Step 4.2: Setup Monitoring
- Monitor server startup times
- Track error rates
- Log usage patterns
- Identify performance bottlenecks

#### Step 4.3: Create Backup Configuration
Keep a backup of working configuration:
```bash
cp ~/.kilocode/cli/global/settings/mcp_settings.json \
   ~/.kilocode/cli/global/settings/mcp_settings.json.backup
```

**Success Criteria:**
- ✅ Optimal performance
- ✅ Reliable operation
- ✅ Easy to maintain

---

### Phase 5: Documentation (Final)
**Goal:** Document the complete setup for future reference

#### Step 5.1: Create Configuration Guide
Document in [`plans/mcp-configuration-guide.md`](plans/mcp-configuration-guide.md):
- Final configuration
- Installation steps
- Testing procedures
- Troubleshooting tips

#### Step 5.2: Update Project Documentation
Add MCP configuration to:
- Project README
- Developer setup guide
- Architecture documentation

#### Step 5.3: Create Troubleshooting Guide
Document common issues and solutions:
- Server won't start
- Authentication failures
- Performance issues
- Network problems

**Success Criteria:**
- ✅ Complete documentation
- ✅ Easy for others to replicate
- ✅ Troubleshooting guide available

---

## Decision Points

### Decision 1: Installation Method
**Options:**
- **A. NPX (Recommended):** Always latest, no global install
- **B. Global NPM:** Faster startup, manual updates
- **C. Mixed:** NPX for testing, global for production

**Recommendation:** Start with NPX (Option A), move to global (Option B) if performance is critical

### Decision 2: Missing Services
**Options:**
- **A. Wait for Investigation:** Don't configure until all services identified
- **B. Partial Deployment:** Configure available services now, add others later
- **C. Alternative Solutions:** Use alternatives for missing services

**Recommendation:** Partial Deployment (Option B) - get working services configured now

### Decision 3: GitHub Token Storage
**Options:**
- **A. Environment Variable:** Most secure, requires shell config
- **B. Config File:** Convenient, less secure
- **C. Secrets Manager:** Most secure, may require additional setup

**Recommendation:** Environment Variable (Option A) for security

### Decision 4: Web Reader Implementation
**Options:**
- **A. Puppeteer:** Full browser, heavy but powerful
- **B. Lightweight Parser:** Fast but limited
- **C. Fetch Only:** Simplest, no JavaScript support

**Recommendation:** Depends on requirements - start with Fetch (Option C), upgrade if needed

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Missing services are internal | Low | High | Document as internal, no action needed |
| NPX slow startup | Medium | Medium | Use global installation |
| GitHub token exposure | High | Low | Use environment variables |
| Server compatibility issues | Medium | Low | Test thoroughly before deployment |
| Network dependency | Medium | Medium | Consider offline fallbacks |

---

## Timeline Estimate

**Phase 1 (Core Setup):** 1-2 hours
- Prerequisites: 15 minutes
- Testing: 30 minutes
- Configuration: 30 minutes
- Verification: 30 minutes

**Phase 2 (Investigation):** Variable (1-5 days)
- Depends on service availability
- May require support contact
- Research and testing time

**Phase 3 (Extended Config):** 1-4 hours
- Depends on Phase 2 findings
- Simple if services exist
- Complex if custom implementation needed

**Phase 4 (Optimization):** 1-2 hours (optional)
**Phase 5 (Documentation):** 1-2 hours

**Total:** 4-8 hours active work + investigation time

---

## Success Metrics

1. **Functionality:** All required MCP services available and working
2. **Performance:** Server startup < 2 seconds per service
3. **Reliability:** < 1% error rate in normal operation
4. **Maintainability:** Clear documentation, easy to update
5. **Security:** No exposed credentials, secure token management

---

## Next Steps

1. **Immediate:** Execute Phase 1 (Core Setup)
2. **Short-term:** Begin Phase 2 (Investigation)
3. **Medium-term:** Complete Phase 3 (Extended Configuration)
4. **Long-term:** Optimize and document (Phases 4-5)

---

## Questions for User

Before proceeding with implementation, please clarify:

1. **Priority:** Should we implement Phase 1 immediately, or wait until all services are identified?
2. **Missing Services:** Do you have information about context7, 4.5v-mcp, web_reader, and claude-mem?
3. **GitHub Token:** Do you have a GitHub token ready, or should we create one?
4. **Installation Method:** Prefer NPX (always latest) or global installation (faster)?
5. **Testing:** Can we test the configuration in your environment, or should we provide test scripts?

---

## Appendix: Useful Commands

### Check Current Configuration
```bash
cat ~/.kilocode/cli/global/settings/mcp_settings.json | jq
```

### Test Individual Server
```bash
npx -y @modelcontextprotocol/server-[name]
```

### View Server Logs
```bash
# Location depends on Kilo Code's logging setup
tail -f ~/.kilocode/cli/logs/cli.txt
```

### Update All Global Servers
```bash
npm update -g @modelcontextprotocol/server-*
```

### Clear NPX Cache
```bash
npm cache clean --force
```
