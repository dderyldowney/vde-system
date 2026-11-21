#!/usr/bin/env python3
# @forge (Governance Sentinel)
# VDE ARCHITECTURAL RECORD
#
# Step definitions for the Configurable Projects Directory feature (Signet #543).
#
# These steps exercise REAL behaviour only:
#   - real `vde set-projects-dir` runs that move folders and rewrite .env
#   - real `bin/generate-all-configs --force` runs
#   - real `docker compose config` interpolation
#   - a real container recreate + `docker exec` round-trip proving the mount
#
# Isolation: every temporary Projects base lives OUTSIDE the repo under
# $HOME/.vde-test-projects-<pid>-<label>. The outer test harness snapshots and
# restores the repo .env, the generated configs, and the live vde-rust Spoke;
# these steps additionally clean up each temp base they create.

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from behave import given, when, then

from vm_common import VDE_ROOT


# ---------------------------------------------------------------------------
# Self-restoring snapshot / teardown
# ---------------------------------------------------------------------------

@given('the repo state is snapshotted for restoration')
def step_snapshot_repo(context):
    """Snapshot repo-root .env, configs/, and env-files/ and register an
    automatic teardown that restores them verbatim. Runs per-scenario (via the
    feature Background), so a run -- pass or fail -- leaves `git status`
    identical with no manual intervention."""
    _ensure_bases(context)

    env_file = VDE_ROOT / ".env"
    env_existed = env_file.exists()
    env_bytes = env_file.read_bytes() if env_existed else None

    snap_dir = Path(tempfile.mkdtemp(prefix="vde-repo-snap-"))
    for rel in ("configs", "env-files"):
        src = VDE_ROOT / rel
        if src.exists():
            shutil.copytree(src, snap_dir / rel, symlinks=True)

    def _restore():
        # .env
        if env_existed:
            env_file.write_bytes(env_bytes)
        elif env_file.exists():
            env_file.unlink()
        # tracked directories
        for rel in ("configs", "env-files"):
            saved = snap_dir / rel
            if not saved.exists():
                continue
            dst = VDE_ROOT / rel
            if dst.exists():
                shutil.rmtree(dst)
            shutil.move(str(saved), str(dst))
        shutil.rmtree(snap_dir, ignore_errors=True)
        # Remove any temp projects bases this scenario created.
        for p in Path.home().glob(f".vde-test-projects-{os.getpid()}-*"):
            shutil.rmtree(p, ignore_errors=True)

    context.add_cleanup(_restore)
    # Signals to step_unset_base that .env has a registered verbatim restore,
    # so it is safe for that step to edit .env.
    context.proj_repo_snapshotted = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _base_path(label):
    """Absolute path (realpath) for a named temporary Projects base."""
    p = Path.home() / f".vde-test-projects-{os.getpid()}-{label}"
    return Path(os.path.realpath(str(p)))


def _ensure_bases(context):
    if not hasattr(context, "proj_bases"):
        context.proj_bases = {}
    if not hasattr(context, "proj_env"):
        context.proj_env = ("unset", None)  # (mode, value)


def _subprocess_env(context, env_file_default=True):
    """Build the subprocess environment, honoring the exported-base intent."""
    env = os.environ.copy()
    env["VDE_ROOT_DIR"] = str(VDE_ROOT)
    env["VDE_TEST_MODE"] = "1"
    env["VDE_QUIET"] = "1"
    mode, value = getattr(context, "proj_env", ("unset", None))
    if mode == "set" and value:
        env["VDE_PROJECTS_DIR"] = value
    else:
        env.pop("VDE_PROJECTS_DIR", None)
    return env


def _run(cmd, context, timeout=400):
    env = _subprocess_env(context)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(VDE_ROOT),
        env=env,
    )
    context.proj_last = result
    return result


def _workspace_source_from_config(compose_file, env, env_file_null=False):
    """Run `docker compose config` and return the resolved host source for the
    /home/devuser/workspace bind mount."""
    cmd = ["docker", "compose", "-f", str(compose_file)]
    if env_file_null:
        cmd += ["--env-file", "/dev/null"]
    cmd += ["config"]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60, cwd=str(VDE_ROOT), env=env
    )
    assert result.returncode == 0, (
        f"docker compose config failed ({result.returncode}): {result.stderr}"
    )
    last_source = None
    for line in result.stdout.splitlines():
        s = line.strip()
        m = re.match(r"source:\s+(.*)$", s)
        if m:
            last_source = m.group(1).strip()
        if s == "target: /home/devuser/workspace":
            return last_source
    raise AssertionError("workspace bind mount not found in compose config output")


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------

@given('a clean temporary projects base "{label}"')
def step_clean_base(context, label):
    _ensure_bases(context)
    p = _base_path(label)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)
    context.proj_bases[label] = p


@given('a non-existent temporary projects base "{label}"')
def step_absent_base(context, label):
    _ensure_bases(context)
    p = _base_path(label)
    if p.exists():
        shutil.rmtree(p)
    context.proj_bases[label] = p
    assert not p.exists(), f"base {p} should not exist yet"


@given('the projects base "{label}" has an alias folder "{alias}" with a marker file')
def step_base_alias_marker(context, label, alias):
    base = context.proj_bases[label]
    alias_dir = base / alias
    alias_dir.mkdir(parents=True, exist_ok=True)
    marker = alias_dir / f"MARKER_{alias}_{os.getpid()}"
    marker.write_text("moved-with-the-folder\n")
    context.proj_marker_names = getattr(context, "proj_marker_names", {})
    context.proj_marker_names[(label, alias)] = marker.name


@given('the projects base "{label}" already has an alias folder "{alias}" containing the sentinel "{content}"')
def step_base_alias_sentinel(context, label, alias, content):
    base = context.proj_bases[label]
    alias_dir = base / alias
    alias_dir.mkdir(parents=True, exist_ok=True)
    sentinel = alias_dir / "SENTINEL"
    sentinel.write_text(content + "\n")
    context.proj_sentinel = sentinel


@given('VDE_PROJECTS_DIR is exported to base "{label}"')
def step_export_base(context, label):
    _ensure_bases(context)
    context.proj_env = ("set", str(context.proj_bases[label]))


def _strip_projects_dir_lines(env_file):
    """Drop every `VDE_PROJECTS_DIR=` line from .env, keeping all other bytes
    and the file mode. No write happens when no such line exists."""
    if not env_file.exists():
        return
    lines = env_file.read_bytes().splitlines(keepends=True)
    kept = [ln for ln in lines if not ln.startswith(b"VDE_PROJECTS_DIR=")]
    if len(kept) != len(lines):
        env_file.write_bytes(b"".join(kept))


@given('VDE_PROJECTS_DIR is unset')
def step_unset_base(context):
    _ensure_bases(context)
    # A repo .env VDE_PROJECTS_DIR= line would leak into the helper's fallback,
    # so remove it. Only safe once the Background snapshot has registered a
    # verbatim restore of .env; refuse to mutate it otherwise.
    assert getattr(context, "proj_repo_snapshotted", False), (
        "refusing to edit repo .env: 'the repo state is snapshotted for "
        "restoration' (Background) must run first to register its restore"
    )
    _strip_projects_dir_lines(VDE_ROOT / ".env")
    context.proj_env = ("unset", None)


@given('all configs are regenerated')
@when('I regenerate all configs')
def step_regen_configs(context):
    result = _run(["zsh", "bin/generate-all-configs", "--force"], context, timeout=120)
    assert result.returncode == 0, (
        f"generate-all-configs failed ({result.returncode}): "
        f"{result.stdout}\n{result.stderr}"
    )
    compose = VDE_ROOT / "configs/docker/languages/rust/docker-compose.yml"
    text = compose.read_text()
    assert "${VDE_PROJECTS_DIR:-" in text, (
        "regenerated rust compose is missing the VDE_PROJECTS_DIR interpolation"
    )


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------

@when('I run "vde set-projects-dir" targeting base "{label}"')
def step_run_set_projects_dir(context, label):
    target = str(context.proj_bases[label])
    _run(["zsh", "bin/vde", "set-projects-dir", target], context, timeout=120)


@when('I render the resolved compose for "{vm}"')
def step_render_compose(context, vm):
    compose = VDE_ROOT / f"configs/docker/languages/{vm}/docker-compose.yml"
    env = _subprocess_env(context)
    mode, _ = getattr(context, "proj_env", ("unset", None))
    # Pass --env-file /dev/null so the repo .env (possibly mutated by an
    # earlier scenario) cannot leak in; interpolation uses the shell env, which
    # we control, and otherwise falls back to the compose default.
    context.proj_resolved_source = _workspace_source_from_config(
        compose, env, env_file_null=True
    )


@when('I recreate the "{vm}" Spoke from this repo')
def step_recreate_spoke(context, vm):
    # Pre-create the alias dir in the chosen base (vde start would too).
    mode, value = context.proj_env
    assert mode == "set", "round-trip requires an exported base"
    (Path(value) / vm).mkdir(parents=True, exist_ok=True)
    context.proj_marker_file = f"PROOF_{os.getpid()}"

    container = f"vde-{vm}"
    # Capture the ORIGINAL owning install (compose working dir) so teardown can
    # recreate the Spoke exactly as found -- the live container may belong to a
    # DIFFERENT VDE install on this host and mount real student data.
    owner_dir = None
    insp = subprocess.run(
        ["docker", "inspect", "-f",
         '{{index .Config.Labels "com.docker.compose.project.working_dir"}}',
         container],
        capture_output=True, text=True,
    )
    if insp.returncode == 0:
        wd = insp.stdout.strip()
        if wd:
            # working_dir is .../configs/docker/languages/<vm>; the install root
            # is four levels up.
            owner_dir = str(Path(wd).parents[3])

    def _restore_spoke():
        clean_env = os.environ.copy()
        clean_env.pop("VDE_PROJECTS_DIR", None)
        clean_env.pop("VDE_ROOT_DIR", None)
        if owner_dir and (Path(owner_dir) / "bin" / "vde").exists():
            subprocess.run(["zsh", f"{owner_dir}/bin/vde", "start", "-f", vm],
                           capture_output=True, text=True, timeout=400,
                           cwd=owner_dir, env=clean_env)
        else:
            # No prior owner: recreate from this repo with the default base.
            subprocess.run(["zsh", "bin/vde", "start", "-f", vm],
                           capture_output=True, text=True, timeout=400,
                           cwd=str(VDE_ROOT), env=clean_env)

    context.add_cleanup(_restore_spoke)
    _run(["zsh", "bin/vde", "start", "-f", vm], context, timeout=400)


@when('I create a marker file in the "{vm}" Spoke workspace')
def step_create_marker(context, vm):
    container = f"vde-{vm}"
    marker = context.proj_marker_file
    # Real exec into the VDE-managed container (scoped to vde.managed=true).
    result = subprocess.run(
        ["docker", "exec", "--user", "devuser", container, "zsh", "-c",
         f"touch /home/devuser/workspace/{marker} && echo OK"],
        capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 0 and "OK" in result.stdout, (
        f"docker exec touch failed: rc={result.returncode} "
        f"out={result.stdout} err={result.stderr}"
    )


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------

@then('the projects command should succeed')
def step_cmd_succeed(context):
    r = context.proj_last
    assert r.returncode == 0, (
        f"command failed ({r.returncode}):\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


@then('the repo .env should contain the VDE_PROJECTS_DIR key pointing at base "{label}"')
def step_env_contains(context, label):
    expected = str(context.proj_bases[label])
    env_file = VDE_ROOT / ".env"
    assert env_file.exists(), ".env not found"
    lines = env_file.read_text().splitlines()
    want = f"VDE_PROJECTS_DIR={expected}"
    assert want in lines, (
        f"expected '{want}' in .env; VDE_PROJECTS_DIR lines present: "
        f"{[l for l in lines if l.startswith('VDE_PROJECTS_DIR=')]}"
    )


@then('the projects base "{label}" should exist on disk')
def step_base_exists(context, label):
    p = context.proj_bases[label]
    assert p.is_dir(), f"projects base {p} does not exist"


@then('the projects base "{label}" should be outside the repository')
def step_base_outside_repo(context, label):
    p = context.proj_bases[label]
    repo = Path(os.path.realpath(str(VDE_ROOT)))
    assert repo not in p.parents and p != repo, f"{p} is inside the repo {repo}"


@then('the resolved rust workspace source should be base "{label}" alias "{alias}"')
def step_resolved_source_is_base(context, label, alias):
    expected = str(context.proj_bases[label] / alias)
    got = context.proj_resolved_source
    assert got == expected, f"workspace source expected '{expected}', got '{got}'"


@then('the resolved rust workspace source should be the in-tree default alias "{alias}"')
def step_resolved_source_default(context, alias):
    expected = str(Path(os.path.realpath(str(VDE_ROOT))) / "projects" / alias)
    got = os.path.realpath(context.proj_resolved_source)
    assert got == expected, f"default workspace source expected '{expected}', got '{got}'"


@then('the "{vm}" Spoke should be running')
def step_spoke_running(context, vm):
    container = f"vde-{vm}"
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0 and result.stdout.strip() == "true", (
        f"{container} is not running: rc={result.returncode} "
        f"out={result.stdout} err={result.stderr}\n"
        f"start output:\n{context.proj_last.stdout}\n{context.proj_last.stderr}"
    )


@then('the marker should appear on the host at base "{label}" alias "{vm}"')
def step_marker_on_host(context, label, vm):
    host_path = context.proj_bases[label] / vm / context.proj_marker_file
    assert host_path.exists(), (
        f"marker {host_path} did not appear on the host -- the Spoke is NOT "
        f"mounting the chosen external base"
    )


@then('the alias folder "{alias}" and its marker should have moved from base "{a}" to base "{b}"')
def step_alias_moved(context, alias, a, b):
    src = context.proj_bases[a] / alias
    dst = context.proj_bases[b] / alias
    marker_name = context.proj_marker_names[(a, alias)]
    assert not src.exists(), f"source alias folder {src} should be gone after move"
    assert dst.is_dir(), f"destination alias folder {dst} should exist after move"
    assert (dst / marker_name).exists(), (
        f"marker {marker_name} should have moved into {dst}"
    )


@then('the colliding alias "{alias}" should remain in base "{a}"')
def step_collision_remains(context, alias, a):
    src = context.proj_bases[a] / alias
    assert src.is_dir(), (
        f"colliding alias {src} should be LEFT in place (skipped, not moved)"
    )


@then('the sentinel file in base "{b}" alias "{alias}" should still read "{content}"')
def step_sentinel_intact(context, b, alias, content):
    sentinel = context.proj_bases[b] / alias / "SENTINEL"
    assert sentinel.exists(), f"sentinel {sentinel} should be untouched"
    actual = sentinel.read_text().strip()
    assert actual == content, (
        f"sentinel was overwritten: expected '{content}', got '{actual}'"
    )


@then('the projects helper should resolve to the in-tree default')
def step_helper_default(context):
    env = _subprocess_env(context)
    result = subprocess.run(
        ["zsh", "-c",
         'source "${VDE_ROOT_DIR}/lib/vde-path-utils"; vde_projects_dir'],
        capture_output=True, text=True, timeout=30, cwd=str(VDE_ROOT), env=env,
    )
    assert result.returncode == 0, f"helper failed: {result.stderr}"
    got = result.stdout.strip()
    expected = str(VDE_ROOT / "projects")
    assert got == expected, f"helper expected '{expected}', got '{got}'"


# ---------------------------------------------------------------------------
# B6: Adoption / non-destruction
# ---------------------------------------------------------------------------

@given('the projects base "{label}" is pre-populated with the student\'s own work')
def step_prepopulate(context, label):
    base = context.proj_bases[label]
    (base / "my_novel").mkdir(parents=True, exist_ok=True)
    (base / "my_novel" / "chapter1.txt").write_text("Chapter One. It was a dark night.\n")
    (base / "notes.txt").write_text("remember: feed the cat\n")
    # A folder whose name collides with a VDE alias, holding the student's file.
    (base / "rust").mkdir(parents=True, exist_ok=True)
    (base / "rust" / "student_main.rs").write_text("fn main() { /* mine */ }\n")
    context.adopt_fp = {
        "novel": (base / "my_novel" / "chapter1.txt").read_bytes(),
        "notes": (base / "notes.txt").read_bytes(),
        "rust": (base / "rust" / "student_main.rs").read_bytes(),
    }


@when('VDE ensures the per-alias directories for "{aliases}" under that base')
def step_ensure_alias_dirs(context, aliases):
    # Runs the REAL production helper ensure_vm_directories (lib/vm-common),
    # which `vde start` uses. For each alias it creates the external
    # $(vde_projects_dir)/<alias> (the adoption path under test: an existing
    # folder is left untouched) plus repo-local configs/docker/<category>/<alias>
    # and logs/<alias>. configs/ is restored by the Background snapshot; logs/
    # is not, so the logs dirs this step creates are recorded here and removed
    # by a registered cleanup. Nothing else in the repo is touched.
    env = _subprocess_env(context)
    parts = [a.strip() for a in aliases.split(",") if a.strip()]

    logs_dir = VDE_ROOT / "logs"
    logs_existed = logs_dir.exists()
    created_logs = [logs_dir / a for a in parts if not (logs_dir / a).exists()]

    def _cleanup_logs():
        for d in created_logs:
            if d.exists():
                shutil.rmtree(d, ignore_errors=True)
        if not logs_existed and logs_dir.is_dir() and not any(logs_dir.iterdir()):
            logs_dir.rmdir()

    context.add_cleanup(_cleanup_logs)

    # Libraries are sourced in the same order bin/nuke-vde uses. Aliases go in
    # as positional args ($@), so no alias text is ever spliced into the script.
    script = (
        'source "${VDE_ROOT_DIR}/lib/vde-shell-compat"; '
        'source "${VDE_ROOT_DIR}/lib/vde-constants"; '
        'source "${VDE_ROOT_DIR}/lib/vde-errors"; '
        'source "${VDE_ROOT_DIR}/lib/vde-log"; '
        'source "${VDE_ROOT_DIR}/lib/vde-naming"; '
        'source "${VDE_ROOT_DIR}/lib/vde-core"; '
        'source "${VDE_ROOT_DIR}/lib/vm-common"; '
        'for a in "$@"; do ensure_vm_directories "$a" lang || exit 1; done'
    )
    result = subprocess.run(
        ["zsh", "-c", script, "zsh", *parts], capture_output=True, text=True,
        timeout=60, cwd=str(VDE_ROOT), env=env,
    )
    context.proj_last = result


@then('the student\'s pre-existing work in base "{label}" is byte-for-byte intact')
def step_adopt_intact(context, label):
    base = context.proj_bases[label]
    fp = context.adopt_fp
    assert (base / "my_novel" / "chapter1.txt").read_bytes() == fp["novel"], \
        "my_novel/chapter1.txt was altered"
    assert (base / "notes.txt").read_bytes() == fp["notes"], \
        "notes.txt was altered"
    assert (base / "rust" / "student_main.rs").read_bytes() == fp["rust"], \
        "student's rust/student_main.rs was altered"


@then('VDE\'s new alias folder "{alias}" coexists in base "{label}"')
def step_new_alias_coexists(context, alias, label):
    base = context.proj_bases[label]
    assert (base / alias).is_dir(), f"VDE did not create {base/alias}"
    # Unrelated work is still present alongside.
    assert (base / "my_novel").is_dir(), "unrelated my_novel/ disappeared"
    assert (base / "notes.txt").exists(), "unrelated notes.txt disappeared"


@then('the adopted alias folder "{alias}" still holds the student\'s own file')
def step_adopted_alias_intact(context, alias, ):
    # The colliding alias folder was adopted (mkdir -p no-op), not recreated.
    # Resolve against whichever base was pre-populated.
    for label, base in context.proj_bases.items():
        cand = base / alias / "student_main.rs"
        if cand.exists():
            assert cand.read_bytes() == context.adopt_fp["rust"], \
                "adopted alias file was altered"
            return
    raise AssertionError(f"adopted alias '{alias}' student file not found")


# ---------------------------------------------------------------------------
# B7: Nuke data integrity (dry-run only)
# ---------------------------------------------------------------------------

@when('I run nuke in dry-run mode')
def step_nuke_dry_run(context):
    result = subprocess.run(
        ["zsh", "bin/nuke-vde", "--dry-run", "--skip-confirm"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120,
        cwd=str(VDE_ROOT), env=_subprocess_env(context),
    )
    context.nuke_out = result.stdout + result.stderr
    context.proj_last = result


@then('the dry-run output marks projects and data as KEPT')
def step_nuke_kept(context):
    out = context.nuke_out
    assert "KEPT" in out, "no KEPT section in dry-run output"
    # The KEPT block names both projects and data.
    kept_region = out.split("KEPT", 1)[1]
    assert re.search(r"projects", kept_region, re.I), "projects not named as KEPT"
    assert re.search(r"data", kept_region, re.I), "data not named as KEPT"


@then('the dry-run output does not list projects or data for removal')
def step_nuke_not_removed(context):
    out = context.nuke_out
    offenders = []
    for line in out.splitlines():
        action = re.search(r"would remove|removing:|removed ", line, re.I)
        if action and re.search(r"\b(projects|data)\b", line, re.I):
            offenders.append(line.strip())
    assert not offenders, (
        "nuke dry-run lists student dir(s) for removal:\n" + "\n".join(offenders)
    )
