# Implementation Plan: Enforcement of Chronicle Labeling

## Goal
Automate the synchronization of Conventional Commit types with GitHub labels and enforce compliant Pull Request titles to ensure absolute system-wide search and traceability.

## Implementation Steps

### 1. Create High-Impact Label
- **Action**: Create the `breaking-change` label on GitHub.
- **Command**: `gh label create breaking-change --description "High-impact or breaking changes" --color "b60205"`

### 2. Implement PR Title Validator (`.github/workflows/verify-pr-title.yml`)
- **Objective**: Reject any PR whose title does not conform to the Conventional Commits specification.
- **Trigger**: `pull_request` (opened, edited, synchronized).
- **Logic**: Use a regex check to verify the pattern `type(scope): description` or `type: description`.

### 3. Implement PR Auto-Labeler (`.github/workflows/auto-label-pr.yml`)
- **Objective**: Automatically apply the corresponding GitHub label based on the PR title prefix.
- **Logic**:
    - Parse title prefix (e.g., `feat`, `fix`, `chore`).
    - Apply matching label.
    - If title contains `!` before the colon (e.g., `feat!: rewrite core`), apply `breaking-change` label.

### 4. Update Sovereign Manuals
- **AGENTS.md**: Update Section 3, Phase 5 to mandate compliant PR titles.
- **PULL_REQUEST_TEMPLATE.md**: Add a reminder at the top regarding the mandatory title format.

## Verification
- Create a test PR with a non-compliant title; verify the validator fails.
- Create a test PR with a compliant title (e.g., `feat: test auto-labeling`); verify it passes and the `feat` label is applied automatically.
- Create a test PR with a breaking change (e.g., `fix!: critical breaking fix`); verify `fix` and `breaking-change` labels are applied.
