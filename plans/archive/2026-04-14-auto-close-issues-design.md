# Design Spec: Automated Issue Closure on Non-Default Branch

**Date:** 2026-04-14
**Status:** Approved
**Target:** Sovereign Baseline 1.3.1 (GitHub Automation)

## 1. Goal
Automate the closing of GitHub issues when a Pull Request is merged into the `develop` branch (or any non-default branch), replicating the native behavior that only works for `main`.

## 2. Technical Strategy
Implement a dedicated GitHub Action workflow triggered by the `pull_request` event when closed on the `develop` branch. This workflow will parse the PR body for closing keywords (e.g., `Closes #123`, `Fixes #123`) using a regular expression and use the GitHub REST API to manually close those issues.

## 3. Implementation Details
**Workflow Structure:**
*   **File:** `.github/workflows/close-linked-issues.yml`
*   **Trigger:** `pull_request` types `[closed]` on branches `[develop]`.
*   **Condition:** Only run if `github.event.pull_request.merged == true` (ignore PRs closed without merging).
*   **Action:** A `github-script` step to regex-match the PR body and execute the `github.rest.issues.update` API call.
*   **Permissions:** Requires `issues: write` permission to close the issues.

**Example Action Logic (JavaScript):**
```javascript
const body = context.payload.pull_request.body;
const issueRegex = /(?:close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)\s+#(\d+)/gi;
let match;
while ((match = issueRegex.exec(body)) !== null) {
  const issueNumber = match[1];
  await github.rest.issues.update({
    owner: context.repo.owner,
    repo: context.repo.repo,
    issue_number: issueNumber,
    state: 'closed'
  });
  console.log(`Closed issue #${issueNumber}`);
}
```

## 4. Verification Plan
1.  Create the workflow file `.github/workflows/close-linked-issues.yml`.
2.  Commit the changes to a new feature branch `feat/auto-close-issues`.
3.  Open a test issue.
4.  Open a PR that references the test issue (e.g., `Closes #XYZ`).
5.  Merge the PR into `develop`.
6.  Verify that the GitHub Action runs successfully and closes the linked issue.

## 5. Compliance
- **Rule P (Sovereign Branching)**: Supports the mandatory workflow of merging feature branches into `develop`.
- **Automation**: Resolves the "Ghost Persistence" of open issues that should have been closed.
- **Security**: Relies on native GitHub Actions (`actions/github-script`) and explicit permissions.