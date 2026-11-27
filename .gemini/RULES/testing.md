# Testing Rules (Binding)
<!-- @forge (Governance Sentinel) -->

These rules bind every agent (main agent and sub-agents) that writes or changes a test, or any gate or test tooling. The full policy is [`docs/development/testing.md`](../../docs/development/testing.md), section `Testing Policy (binding)`. That section is the single source of truth: this file states obligations only and restates no rule value. Breaking one of these obligations is a violation: stop, report it to the User, and remediate before continuing.

- **Read the policy first.** Before writing or changing a test, or any gate or test tooling, read the section `Testing Policy (binding)` in full. Rules, test sizes, budgets and numbers come from that section, never from memory or from this file.
- **Show every test fail, then pass.** Each test change is shown failing (RED) before the change and passing (GREEN) after it. Paste the literal output into the pull request evidence section. A test that has never failed is not evidence.
- **Never write a fake test.** Follow [`.gemini/RULES/fake_tests.md`](fake_tests.md). The rule applies to every test, including one written under deadline pressure.
- **Follow the determinism rules** stated in the policy. A test that depends on timing, locale, execution order, shared host state or the network is fixed before it merges.
- **State the timing and flake facts in the pull request.** Give the duration of each suite the change touches, any budget it approaches or exceeds, the container counts the policy measures, and whether any run flaked. Write "no flakes observed" only when the runs show it.
- **Report a flaky or slow test.** Never hide a flake by rerunning it silently or by weakening its assertion. Report it to the User and in the pull request, and fix it on sight until the policy's flake procedure is in the tooling.
- **Run the independent review before a commit.** Follow [`.gemini/RULES/review.md`](review.md). The review must pass, and the User must approve, before any commit. The review covers the test evidence above.
- **Do not hand-run the full suite before a push.** The pre-push gate certifies the full suite and the Proof of Life on the pushed tip. During work, run only the focused tests for the change.
- **Begin code-work sub-agent prompts with the security preamble, then the testing preamble.** Every sub-agent prompt for code work starts with [`.gemini/RULES/security-preamble.md`](security-preamble.md), followed by [`.gemini/RULES/testing-preamble.md`](testing-preamble.md). Sub-agents skip the startup reading, so the prompt is their only source of these rules.
- **The policy wins over a shortcut.** When the policy and a convenient shortcut conflict, the policy wins. Tell the User which shortcut was refused and why.
