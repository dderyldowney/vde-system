# Testing Preamble (binding for every agent that writes or changes code)
<!-- @forge (Governance Sentinel) -->

1. Read the Testing Policy first: section `Testing Policy (binding)` in `docs/development/testing.md`, and `.gemini/RULES/testing.md`.
2. Follow the RED-before-GREEN rule in `docs/development/testing.md` and show the literal failing output before the fix and the literal passing output after it.
3. Write no fake tests, as defined in `.gemini/RULES/fake_tests.md` and `docs/development/testing.md`.
4. Keep every test deterministic by following the determinism rules in `docs/development/testing.md`.
5. Do not run the full suite; run only the tests you were told to run, and report their literal output.
6. Report any flaky, slow or skipped test to the main agent instead of hiding it, as `docs/development/testing.md` requires.

Every sub-agent prompt for code work begins with .gemini/RULES/security-preamble.md and then this preamble, because sub-agents skip the startup reading.
