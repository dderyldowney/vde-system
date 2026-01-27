# MCP Architecture Overview

## System Architecture

```mermaid
graph TB
    subgraph "Kilo Code Application"
        KC[Kilo Code Core]
        CONFIG[mcp_settings.json]
    end
    
    subgraph "MCP Servers - Available"
        ST[sequential-thinking<br/>Complex Reasoning]
        GH[github<br/>Repository Operations]
        FT[fetch<br/>HTTP Requests]
        MEM[memory<br/>Knowledge Graph]
    end
    
    subgraph "MCP Servers - Investigation Needed"
        C7[context7<br/>Documentation Queries]
        V45[4.5v-mcp<br/>Image Analysis]
        WR[web_reader<br/>Web Scraping]
        CM[claude-mem<br/>Memory Observations]
    end
    
    subgraph "External Services"
        GITHUB[GitHub API]
        WEB[Web Resources]
        DOCS[Documentation Sites]
    end
    
    KC -->|reads| CONFIG
    CONFIG -->|configures| ST
    CONFIG -->|configures| GH
    CONFIG -->|configures| FT
    CONFIG -->|configures| MEM
    
    KC -.->|needs| C7
    KC -.->|needs| V45
    KC -.->|needs| WR
    KC -.->|needs| CM
    
    GH -->|queries| GITHUB
    FT -->|fetches| WEB
    C7 -.->|queries| DOCS
    WR -.->|scrapes| WEB
    
    style ST fill:#90EE90
    style GH fill:#90EE90
    style FT fill:#90EE90
    style MEM fill:#90EE90
    style C7 fill:#FFB6C1
    style V45 fill:#FFB6C1
    style WR fill:#FFB6C1
    style CM fill:#FFB6C1
```

**Legend:**
- 🟢 Green: Available and ready to configure
- 🔴 Pink: Needs investigation or custom implementation
- Solid lines: Confirmed connections
- Dotted lines: Potential connections

---

## MCP Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant KiloCode
    participant Config
    participant MCPServer
    participant ExternalAPI
    
    User->>KiloCode: Request task
    KiloCode->>Config: Load MCP settings
    Config-->>KiloCode: Server configurations
    KiloCode->>MCPServer: Start server process
    MCPServer-->>KiloCode: Ready
    KiloCode->>MCPServer: Send request
    MCPServer->>ExternalAPI: Query external service
    ExternalAPI-->>MCPServer: Response
    MCPServer-->>KiloCode: Formatted result
    KiloCode-->>User: Complete task
```

---

## Configuration Hierarchy

```mermaid
graph LR
    subgraph "Global Configuration"
        GC[~/.kilocode/cli/global/settings/mcp_settings.json]
    end
    
    subgraph "Workspace Configuration"
        WC[.kilocode/mcp_settings.json<br/>Optional Override]
    end
    
    subgraph "Environment Variables"
        ENV[GITHUB_TOKEN<br/>API_KEYS<br/>etc.]
    end
    
    GC -->|default| RUNTIME[Runtime Configuration]
    WC -->|overrides| RUNTIME
    ENV -->|provides| RUNTIME
    RUNTIME -->|launches| SERVERS[MCP Servers]
```

---

## Server Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Configured: Add to mcp_settings.json
    Configured --> Starting: Kilo Code launches
    Starting --> Running: Server ready
    Starting --> Failed: Error
    Running --> Idle: No requests
    Idle --> Processing: Request received
    Processing --> Idle: Request complete
    Running --> Stopped: Kilo Code exits
    Failed --> [*]
    Stopped --> [*]
```

---

## Data Flow: GitHub Operations Example

```mermaid
graph LR
    subgraph "User Request"
        UR[Search GitHub repos]
    end
    
    subgraph "Kilo Code Processing"
        KC[Kilo Code Core]
        ROUTER[MCP Router]
    end
    
    subgraph "MCP GitHub Server"
        GHS[GitHub Server]
        AUTH[Token Auth]
        API[GitHub API Client]
    end
    
    subgraph "GitHub"
        GHAPI[GitHub REST API]
        REPOS[Repositories]
    end
    
    UR --> KC
    KC --> ROUTER
    ROUTER --> GHS
    GHS --> AUTH
    AUTH --> API
    API --> GHAPI
    GHAPI --> REPOS
    REPOS --> GHAPI
    GHAPI --> API
    API --> GHS
    GHS --> ROUTER
    ROUTER --> KC
    KC --> RESULT[Results to User]
```

---

## Installation Options Comparison

```mermaid
graph TB
    subgraph "NPX Method"
        NPX1[npx -y @package/name]
        NPX2[Downloads on first use]
        NPX3[Always latest version]
        NPX4[Slower startup]
    end
    
    subgraph "Global Install Method"
        GLB1[npm install -g @package/name]
        GLB2[Installed once]
        GLB3[Manual updates needed]
        GLB4[Faster startup]
    end
    
    subgraph "Local Install Method"
        LOC1[npm install @package/name]
        LOC2[Project-specific]
        LOC3[Version controlled]
        LOC4[Isolated dependencies]
    end
    
    CHOICE{Choose Method}
    CHOICE -->|Development| NPX1
    CHOICE -->|Production| GLB1
    CHOICE -->|Custom| LOC1
```

---

## Security Model

```mermaid
graph TB
    subgraph "Sensitive Data"
        TOKEN[GitHub Token]
        APIKEY[API Keys]
        SECRETS[Other Secrets]
    end
    
    subgraph "Storage Options"
        ENV[Environment Variables<br/>Recommended]
        CONFIG[Config File<br/>Less Secure]
        VAULT[Secrets Manager<br/>Most Secure]
    end
    
    subgraph "MCP Server"
        SERVER[Server Process]
        RUNTIME[Runtime Environment]
    end
    
    TOKEN -.->|avoid| CONFIG
    TOKEN -->|preferred| ENV
    TOKEN -->|best| VAULT
    
    APIKEY -.->|avoid| CONFIG
    APIKEY -->|preferred| ENV
    APIKEY -->|best| VAULT
    
    ENV --> RUNTIME
    VAULT --> RUNTIME
    CONFIG --> RUNTIME
    RUNTIME --> SERVER
    
    style CONFIG fill:#FFB6C1
    style ENV fill:#90EE90
    style VAULT fill:#87CEEB
```

---

## Troubleshooting Decision Tree

```mermaid
graph TD
    START[MCP Server Issue]
    START --> Q1{Server starts?}
    Q1 -->|No| Q2{Node.js installed?}
    Q1 -->|Yes| Q3{Responds to requests?}
    
    Q2 -->|No| FIX1[Install Node.js 18+]
    Q2 -->|Yes| Q4{NPX works?}
    
    Q4 -->|No| FIX2[Fix npm/npx installation]
    Q4 -->|Yes| Q5{Config correct?}
    
    Q5 -->|No| FIX3[Fix mcp_settings.json]
    Q5 -->|Yes| Q6{Network access?}
    
    Q6 -->|No| FIX4[Check firewall/proxy]
    Q6 -->|Yes| FIX5[Check server logs]
    
    Q3 -->|No| Q7{Authentication issue?}
    Q3 -->|Yes| SUCCESS[Working correctly]
    
    Q7 -->|Yes| FIX6[Check tokens/API keys]
    Q7 -->|No| Q8{Timeout?}
    
    Q8 -->|Yes| FIX7[Increase timeout/check network]
    Q8 -->|No| FIX8[Review server logs]
    
    style SUCCESS fill:#90EE90
    style FIX1 fill:#FFB6C1
    style FIX2 fill:#FFB6C1
    style FIX3 fill:#FFB6C1
    style FIX4 fill:#FFB6C1
    style FIX5 fill:#FFB6C1
    style FIX6 fill:#FFB6C1
    style FIX7 fill:#FFB6C1
    style FIX8 fill:#FFB6C1
```

---

## Implementation Phases Timeline

```mermaid
gantt
    title MCP Server Implementation Timeline
    dateFormat YYYY-MM-DD
    section Phase 1: Core Setup
    Verify Prerequisites           :p1a, 2026-01-27, 1h
    Test Official Servers          :p1b, after p1a, 2h
    Setup GitHub Token             :p1c, after p1a, 1h
    Create Minimal Config          :p1d, after p1b, 1h
    Test Configuration             :p1e, after p1d, 2h
    
    section Phase 2: Investigation
    Investigate context7           :p2a, after p1e, 2d
    Investigate 4.5v-mcp          :p2b, after p1e, 2d
    Investigate web_reader         :p2c, after p1e, 1d
    Investigate claude-mem         :p2d, after p1e, 1d
    
    section Phase 3: Extended Config
    Add Available Services         :p3a, after p2d, 2h
    Test Extended Config           :p3b, after p3a, 2h
    
    section Phase 4: Optimization
    Consider Global Install        :p4a, after p3b, 1h
    Setup Monitoring              :p4b, after p4a, 1h
    
    section Phase 5: Documentation
    Create Config Guide           :p5a, after p4b, 2h
    Update Project Docs           :p5b, after p5a, 1h
```

---

## Service Priority Matrix

```mermaid
quadrantChart
    title MCP Service Priority vs Availability
    x-axis Low Availability --> High Availability
    y-axis Low Priority --> High Priority
    quadrant-1 Quick Wins
    quadrant-2 Strategic
    quadrant-3 Low Priority
    quadrant-4 Fill Gaps
    sequential-thinking: [0.9, 0.95]
    github: [0.9, 0.85]
    fetch: [0.9, 0.8]
    memory: [0.9, 0.6]
    web_reader: [0.5, 0.6]
    context7: [0.2, 0.8]
    4.5v-mcp: [0.3, 0.6]
    claude-mem: [0.2, 0.6]
```

**Interpretation:**
- **Quadrant 1 (Quick Wins):** High priority, high availability - implement first
- **Quadrant 2 (Strategic):** High priority, low availability - needs investigation
- **Quadrant 3 (Low Priority):** Low priority, low availability - defer
- **Quadrant 4 (Fill Gaps):** Low priority, high availability - nice to have

---

## Configuration File Structure

```
~/.kilocode/
├── cli/
│   ├── config.json
│   ├── history.json
│   ├── logs/
│   │   └── cli.txt
│   └── global/
│       ├── global-state.json
│       ├── secrets.json
│       ├── cache/
│       │   └── [model caches]
│       ├── settings/
│       │   ├── custom_modes.yaml
│       │   └── mcp_settings.json  ← TARGET FILE
│       └── tasks/
│           └── [task data]
```

---

## Recommended Configuration (Phase 1)

This is the minimal working configuration to start with:

```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "description": "Complex reasoning and planning"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      },
      "description": "GitHub repository operations"
    },
    "fetch": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch"],
      "description": "HTTP/HTTPS requests"
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"],
      "description": "Knowledge graph and persistent memory"
    }
  }
}
```

**Note:** The `description` field is optional but helpful for documentation.

---

## Next Steps Summary

1. ✅ **Completed:** Analysis and planning
2. 🔄 **Ready:** Phase 1 implementation (4 official servers)
3. ⏳ **Pending:** Investigation of 4 missing services
4. ⏳ **Future:** Extended configuration and optimization

---

## Key Findings

### Available Now (4/8 services)
- ✅ sequential-thinking - CRITICAL for Phase 0
- ✅ github - High priority
- ✅ fetch - High priority  
- ✅ memory - Medium priority

### Needs Investigation (4/8 services)
- ❓ context7 - Documentation queries
- ❓ 4.5v-mcp - Image analysis (may be built-in)
- ❓ web_reader - Web scraping (puppeteer alternative exists)
- ❓ claude-mem - Memory observations (may be built-in)

### Critical Questions
1. Are the missing services internal to Kilo Code?
2. Should we proceed with partial implementation?
3. What are acceptable alternatives for missing services?
