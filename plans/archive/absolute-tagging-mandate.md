# Absolute Tagging Mandate Implementation Plan
<!-- @shared-law (Forge Component) -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Codify the Mandatory Labeling Rule into the Sovereign Law and achieve 100% project-wide compliance by tagging every file in the repository.

**Architecture:** We will first update the Supreme Law (`GEMINI.md`) and the UAP Sentinel (`bin/vde-enforce-uap.zsh`) to enforce the new tagging standard. Then, we will perform a repository-wide sweep to ensure every file is tagged in its first 3 lines.

**Tech Stack:** ZSH, Markdown, Python

---

### Task 1: Codify the Mandatory Labeling Rule (@shared-law)

**Files:**
- Modify: `GEMINI.md`

- [ ] **Step 1: Insert the Mandatory Labeling Rule**
Add the detailed "MANDATORY LABELING RULE FOR dderyldowney/vde-system REPOSITORY" text provided by the Clan Leader into the Mandate 24 section of `GEMINI.md`.

- [ ] **Step 2: Update the 'Sovereign Execution' section**
Ensure the agent is explicitly mandated to stop any commit if tags are missing or incorrect.

- [ ] **Step 3: Commit**
```bash
git add GEMINI.md
git commit -m "chore(shared-law): codify mandatory labeling rule in sovereign law"
```

### Task 2: Harden UAP Enforcement (@forge)

**Files:**
- Modify: `bin/vde-enforce-uap.zsh`

- [ ] **Step 1: Implement First 3 Lines Check**
Update the `audit_file_content` function to specifically check for the architectural tag pattern within the first 3 lines of the file.

```zsh
# Mandate 24: Absolute Tagging Rule (First 3 Lines)
local tag_found=$(head -n 3 "$file" | grep -E "^#? ?@(armor|forge|shared-law) \(.+\)")
if [[ -z "${tag_found}" ]]; then
    echo -e "${RED}[UAP-ERROR]${NC} Missing or invalid architectural tag in first 3 lines of ${file#${VDE_ROOT_DIR}/}."
    echo "Expected Pattern: @armor|@forge|@shared-law (Functional Effect)"
    errors=$((errors + 1))
fi
```

- [ ] **Step 2: Verify Enforcement**
Run the enforcer against a known tagged file and a file with a tag moved to line 4. Ensure it fails for the latter.

- [ ] **Step 3: Commit**
```bash
git add bin/vde-enforce-uap.zsh
git commit -m "feat(forge): harden UAP enforcer for absolute tagging compliance"
```

### Task 3: 100% Project-Scope Tagging Sweep (@forge)

- [ ] **Step 1: Identify All Untagged/Mis-tagged Files**
Run a sweep across the entire repo (excluding `.git`, `node_modules`, etc.).
```bash
for f in $(git ls-files); do
    head -n 3 "$f" | grep -qE "@armor|@forge|@shared-law" || echo "NON-COMPLIANT: $f"
done
```

- [ ] **Step 2: Remediate Non-Compliant Files**
For every file found:
1. Analyze its purpose.
2. Insert the appropriate tag in the first 3 lines.
*(Agent Note: Use Rule E sequential edits via subagent swarm).*

- [ ] **Step 3: Commit**
```bash
git add .
git commit -m "chore(core): ensure 100% project-scope tagging of repository files"
```

### Task 4: Create Signet & Chronicle (@forge)

- [ ] **Step 1: Create Issue**
`gh issue create --title "Ensuring 100% project-scope tagging of Project files" --body "..."`

- [ ] **Step 2: Create PR**
`gh pr create --title "chore(core): 100% absolute tagging compliance" --body "..."`
