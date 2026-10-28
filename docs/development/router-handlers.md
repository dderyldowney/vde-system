# The `vde` Router and Its Action Handlers
<!-- @shared-law (Sovereign Law) -->

How `bin/vde` dispatches commands, where the multi-line command bodies live (`lib/vde-actions`), what its
exit statuses mean, and how changes to it are verified.

[← Back to README](../../README.md)

---

## 1. Shape of `bin/vde`

`bin/vde` is a router. It runs with `set -e` and does, in order:

1. Loads libraries and the isolated SSH agent environment, sets the `SIGINT`/`SIGTERM` trap.
2. Takes the first word as `ACTION` (`vde <ACTION> ...`). If there is none, it prints usage and exits 2
   (see section 4).
3. Sources `lib/vde-actions` (the handler functions, section 2).
4. Handles `function-trace <command>` by re-parsing the real command, and installs the trace wrappers later,
   after target resolution, so the trace starts clean at dispatch.
5. Parses flags: `-f/--force` and `-q/--quiet` are consumed by the router; every other word goes into
   `input_targets` (for `exec`, `enter`, `ssh` only the first word is a target and the rest is `ACTION_ARGS`).
6. Resolves `input_targets` into `targets`: `default` becomes `jupyterlab postgres`, a saved cluster name
   expands to its members, `all` expands to every registered VM, anything else passes through unchanged.
7. Dispatches through `case ${ACTION}`. Most commands delegate to a script in `bin/` through `vde_run`,
   passing either `input_targets` (as typed) or `targets` (resolved). `-f` is re-added as `--force` only for
   `ssh-setup`, `ssh-sync` and `ssh-agent-setup`.

The router has no trailing `exit`: the handlers in `lib/vde-actions` `exit` with their own status, and
delegated commands leave their status as the script's status.

## 2. `lib/vde-actions`

The eight commands whose bodies were long enough to live inline in the `case` (`start`, `stop`, `restart`,
`remove`, `exec`, `enter`, `port`, `help`) are functions in `lib/vde-actions`:

| Command | Function |
|---------|----------|
| `start` | `vde_action_start` |
| `stop` | `vde_action_stop` |
| `restart` | `vde_action_restart` |
| `remove` / `delete` / `rm` | `vde_action_remove` |
| `exec` | `vde_action_exec` |
| `enter` / `ssh` | `vde_action_enter` |
| `port` | `vde_action_port` |
| `help` / `-h` / `--help` | `vde_action_help` |

The `case` arm for each is a one-line call, for example `start) vde_action_start ;;`.

**Contract.** The functions take no positional parameters. They read the router's globals directly
(`ACTION`, `ACTION_ARGS`, `input_targets`, `targets`, `force`, `_vde_help_status`) and, like the inline arms
they replaced, finish by calling `exit`. They are only valid when called from `bin/vde` after step 6 above.
The library has a load guard (`_VDE_ACTIONS_LOADED`).

**Why extract.** The bodies can be read, traced and tested as named units, and they are the natural
execution targets for a parser that turns a typed command or a natural-language request into a plan.

## 3. How the handlers report status

`vde_action_start` accumulates a status (`GLOBAL_RC`); `vde_action_stop`, `vde_action_restart` and
`vde_action_remove` accumulate `action_rc`. Each ends with an explicit `exit`:

```zsh
exit ${action_rc}
```

`action_rc` starts at 0 and is set to 1 when a target alias is unknown, or when the docker operation for a
target fails (`docker stop`, `docker rm -f`, or the `vde start` that `restart` runs). A target that is already
in the desired state (stopped for `stop`, no container for `remove`) is not a failure.

Why an explicit `exit` and not a trailing `[[ -n "${last_stopped}" ]] && vde_print_next_steps ...`: under
`set -e`, a false `[[ ]] &&` list as the last command of a **function** makes the function return 1, and the
errexit-enabled caller then exits 1 without any failure having happened. At top level the same line would fall
through with status 0, which is why moving the arm bodies into functions changed the status until the handlers
were given an explicit one. The next-steps hint is therefore wrapped in an `if`, and the handler's status comes
from `action_rc` alone. If you add a handler, end it with an explicit `exit`, and never let its status be the
result of a `&&` list.

A related rule: inside a function called as `f || x` or `if f`, errexit is disabled in the function body. Do not
rely on it.

## 4. Exit status of `vde`

| Situation | Output | Exit |
|-----------|--------|------|
| Command succeeds | command output | 0 |
| `vde help`, `vde -h`, `vde --help` | usage text | 0 |
| `vde` with no command (also `vde function-trace` alone) | the same usage text | 2 (`VDE_ERR_INVALID_INPUT`) |
| Unknown command, e.g. `vde frobnicate` | `Unknown command 'frobnicate'. Run 'vde help' for usage.` on **stderr** | 2 |
| `vde -q start` (a flag before the command) | treated as an unknown command `-q` | 2 |
| `vde dns-check` with missing arguments | `Usage: vde dns-check <source_vm> <target_vm> [port]` | 2 |
| `vde stop` / `restart` / `remove` with no target | usage error | 1 |
| `vde stop` / `restart` / `remove`, every target handled or already stopped/absent | | 0 |
| `vde stop` / `restart` / `remove` with any unknown alias, or a failed `docker stop` / `rm -f` | warning or failure message | 1 |
| `vde start` of an unknown VM | "Unknown VM type or alias" message | 0 |

Flags go **after** the command: `vde start -q python`, not `vde -q start python`.

A mixed run (some targets fine, one unknown) still processes every target and then exits 1. `vde start` does
not follow this rule: an unknown alias is reported but does not affect its status.

## 5. Typed arguments reach the delegates

The words typed after the command are passed on to the delegate script:

- `dns-check` gets `<source_vm> <target_vm> [port]`; the optional port defaults to 22.
- `audit`, `check-tetrad`/`spine-check` and `heal` get the typed words. None of the three scripts reads
  arguments today, so this has no visible effect yet.

## 6. Tests

| File | Covers |
|------|--------|
| `tests/unit/vde-actions.test.zsh` | 33 cases. Runs the real router and `lib/vde-actions` in a sandbox with a stub `docker` that logs its argv and stub exec/ssh delegates, so no daemon is needed. Covers start/stop/restart/remove/exec/enter/port/help: usage errors, unknown aliases, present and absent containers, failing `docker stop`/`rm -f`, mixed targets, and flag handling. Also checks that every `vde_action_*` handler is defined, that `function-trace` does not show `vde_action_*` frames, and that no `_VDE_ACTION_RC` handover remains. |
| `tests/unit/vde-router-exit-status.test.zsh` | Unknown command exits 2 with the message on stderr; bare `vde` and bare `function-trace` print usage and exit 2; `vde help` exits 0. |
| `tests/unit/vde-router-delegate-args.test.zsh` | A copy of `bin/vde` against stub delegates that echo their argv: typed arguments reach `audit`, `check-tetrad`/`spine-check`, `heal` and `dns-check`. |

All three are registered in `tests/run-sovereign-tests.zsh`.

## 7. Function trace and the handlers

`vde_trace_install` (`lib/vde-function-trace`) wraps every function defined in the repository, except the trace
machinery itself and `vde_action_*`. The handlers are left unwrapped on purpose: they are transparent, so the
functions they call keep the call depth they had when these bodies were inline `case` arms, and a trace shows
no extra `vde_action_*` level. This is a skip in the install loop, not an entry in `_VDE_TRACE_HIDE`.

## 8. Verifying a change to the router

The extraction was verified with characterization tests rather than by reading the diff. The approach is
reusable:

1. **Record a baseline** from the commit before the change: run a matrix of commands (every command, with no
   arguments, an alias, a cluster, `default`, `all`, `-f`, a leading option, and each lifecycle command against
   empty / images-present / running / cluster host states) against a **fake `docker`** that records every call
   and answers from a scripted state. Per case, store: exit code, normalized stdout/stderr (timestamps, ANSI
   codes, spinner glyphs, ssh fingerprints and zsh error line numbers masked), every `docker` argv, and file
   changes. Delegate scripts are replaced by recorders in the routing cases, so what is pinned is which script
   is called with which arguments.
2. **Re-run after the change** and compare case by case. Every difference must be one you intended.
3. **Compare `function-trace` output** between the old and new tree for the handler commands. Because the
   handlers are not wrapped (section 7), the trace should be identical.
4. **Run the repo's own suites**: the `function-trace` behave feature (`tests/features/governance/`) and
   `tests/unit/*.test.zsh`.
5. **Mutation-check the tests**: deliberately break the code (for example `docker stop` to `docker kill`, `rm -f`
   to `rm`, dispatch `restart` to the stop handler, delete the `source` line, drop an `exit ${action_rc}`) and
   confirm a test fails for each.
6. Run each run in a **throwaway copy** of the tree. Leftover state such as `.cache/` or `.docker-state/` makes
   results depend on history.

## 9. Direction (not implemented)

The router is being prepared to run through `lib/vde-parser`: a strict argv-to-plan front door (deterministic,
no natural language), then the same handlers executing the plan, with natural-language input as a separate,
confirmation-gated entry. Open points before that can happen: the parser's two intent detectors (`detect_intent`
and the inline `case` in `generate_plan`) have drifted and must be unified; its plan format needs to carry
flags and resolved targets; `heal` needs degraded-mode startup before `vm-common` loads, so it must bypass the
parser; and `function-trace`, the signal trap, `set -e` and the exit codes above must be preserved. Today
`lib/vde-parser` is not called by `bin/vde` or any script (only a unit-test list and a comment mention it).
