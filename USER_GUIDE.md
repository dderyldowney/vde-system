
---

<details id="12.-trial-of-the-gauntlet" data-section="12. Trial of the Gauntlet">

<summary><h2>12. Trial of the Gauntlet (TDD Mandate)</h2></summary>

### ⚔️ The Law of the Red-Green-Refactor

The VDE Hub is a hardened ecosystem. To ensure absolute stability and security, all new features or bug fixes MUST pass through the **Trial of the Gauntlet**. This is not a suggestion; it is the Way.

**The Three Strikes of the Forge:**

1.  **Strike One: The Red Gauntlet (The Mark)**
    - Before writing any implementation code, you MUST create a physical test file (e.g., `tests/unit/test_feature.zsh`).
    - You MUST execute this test and demonstrate a **RED** failure. This proves the target is marked.

2.  **Strike Two: The Green Victory (The Strike)**
    - Write the **minimal** code required to make the test pass.
    - Execute the test again to achieve a **GREEN** result.

3.  **Strike Three: The Refiner's Fire (The Refactor)**
    - With the test Green, clean up your code. Improve readability and ensure ZSH 5.0+ purity.
    - The test MUST remain Green. If it turns Red, you have failed the trial.

**Why we do this:**
- ✅ **Empirical Proof**: We don't "hope" it works; we prove it.
- ✅ **Anti-Regression**: Your tests protect your work from future changes.
- ✅ **Security**: The Gauntlet forces you to think about edge cases before they become vulnerabilities.

**Every workflow in the Hub is verified. Your contribution must be too.**

</details>
