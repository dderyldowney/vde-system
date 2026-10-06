#!/usr/bin/env python3
# @forge (Governance Sentinel)
# VDE ARCHITECTURAL RECORD
"""
Step definitions for canonical VM-type registration compliance (Signet #534).

Real verification only, per the 100% Real Tests Mandate:
  - Registration goes through `vde add`, the canonical entrypoint, never
    bin/add-vm-type directly (Mandates 10 and 12).
  - The Rule Spine assertion runs the actual Enforcer and checks its exit
    status, rather than inspecting files and inferring what it would say.
  - Every scenario is wrapped by the @vault-mutating guard in environment.py,
    which restores the Vault and purges generated artifacts afterwards.
"""

import json
import os
import re
import subprocess

from behave import then, when

from config import get_vde_root

CONF = "data/vm-types.conf"
PLACEHOLDER = "-"


def _ritual_path(name):
    return get_vde_root() / "scripts/setup" / f"{name}-init.zsh"


def _ritual_text(name):
    path = _ritual_path(name)
    assert path.is_file(), f"no hydration ritual at {path}"
    return path.read_text(encoding="utf-8")


def _conf_lines():
    return (get_vde_root() / CONF).read_text(encoding="utf-8").splitlines()


def _entry_line(name):
    for line in _conf_lines():
        if line.startswith(f"lang|vde-{name}|") or line.startswith(
            f"service|vde-{name}|"
        ):
            return line
    return None


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@when('I register the throwaway VM type "{name}" through the canonical entrypoint')
def step_register(context, name):
    # Record it first, so the environment guard purges the artifacts even if
    # the registration fails halfway through.
    if hasattr(context, "vault_throwaway"):
        context.vault_throwaway.add(name)

    result = subprocess.run(
        [
            "bin/vde",
            "add",
            name,
            "apt-get update -y && apt-get install -y hello",
        ],
        cwd=str(get_vde_root()),
        capture_output=True,
        text=True,
        timeout=300,
    )
    context.last_result = result
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode


# ---------------------------------------------------------------------------
# The forged hydration ritual
# ---------------------------------------------------------------------------


@then('a hydration ritual must exist for "{name}"')
def step_ritual_exists(context, name):
    path = _ritual_path(name)
    assert path.is_file(), (
        f"the canonical tool did not forge a hydration ritual at {path}. "
        f"Universal Script Parity requires every registry entry to point at "
        f"one. Output: {context.command_output!r}"
    )
    assert os.access(path, os.X_OK), f"{path} is not executable"


@then('the hydration ritual for "{name}" must carry an architectural tag on line 2 or 3')
def step_ritual_tagged(context, name):
    """
    The Positioning Law reserves line 1 for the shebang and requires the
    architectural tag on line 2 or 3. An untagged artifact is rejected by the
    Enforcer, which makes the canonical registration path a Protocol Blockade.
    """
    lines = _ritual_text(name).splitlines()
    assert len(lines) >= 3, f"ritual is only {len(lines)} lines"
    candidates = lines[1:3]
    tagged = any(
        re.search(r"#\s*@(armor|forge|shared-law)\b", line) for line in candidates
    )
    assert tagged, (
        "the forged ritual carries no architectural tag on line 2 or 3, so the "
        "Enforcer will reject it and the canonical registration path leaves the "
        "Forge in a Protocol Blockade. Lines 2-3 were:\n"
        + "\n".join(f"  {line!r}" for line in candidates)
    )


@then('the hydration ritual for "{name}" must declare "{text}"')
def step_ritual_declares(context, name, text):
    content = _ritual_text(name)
    assert text in content, f"the forged ritual does not declare {text!r}"


@then('the hydration ritual for "{name}" must purge apt ghosts')
def step_ritual_purges(context, name):
    content = _ritual_text(name)
    purges = "vde_purge_ghosts" in content or (
        "apt-get clean" in content and "rm -rf /var/lib/apt/lists/*" in content
    )
    assert purges, (
        "the forged ritual neither calls vde_purge_ghosts nor performs the "
        "literal apt cleanup required by Rule 12.5"
    )


@then('the hydration ritual for "{name}" must carry the Forged in Beskar header')
def step_ritual_header(context, name):
    content = _ritual_text(name)
    assert "Forged in Beskar" in content, (
        "the forged ritual lacks the standardised 'Forged in Beskar' header "
        "that the USP validation scenario requires of every setup script"
    )


# ---------------------------------------------------------------------------
# The Rule Spine
# ---------------------------------------------------------------------------


@then("the Sovereign Audit must return PASS")
def step_enforcer_passes(context):
    """
    Run the real Enforcer. Inspecting files and inferring the verdict would let
    a future change to the Enforcer's own rules escape this test.
    """
    result = subprocess.run(
        ["bin/vde-enforce-uap.zsh"],
        cwd=str(get_vde_root()),
        capture_output=True,
        text=True,
        timeout=600,
    )
    clean = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr)
    assert result.returncode == 0, (
        f"the Enforcer rejected the Forge after a canonical registration "
        f"(exit {result.returncode}). Under Mandate 15 this is a Protocol "
        f"Blockade caused by the documented tool doing its job.\n"
        + "\n".join(
            line for line in clean.splitlines() if "UAP-ERROR" in line or "UAP-FAILURE" in line
        )
    )


# ---------------------------------------------------------------------------
# The Beskar Vault entry
# ---------------------------------------------------------------------------


@then('the registry entry for "{name}" must carry exactly 8 fields')
def step_entry_eight_fields(context, name):
    line = _entry_line(name)
    assert line, f"no registry entry found for {name} in {CONF}"
    count = len(line.split("|"))
    assert count == 8, (
        f"the forged entry carries {count} fields, violating the 8-Field "
        f"Standard: {line!r}"
    )


@then('the registry entry for "{name}" must use the placeholder for every empty field')
def step_entry_placeholders(context, name):
    """
    Siblings use "-" for empty pkgs and service_ports. A blank field makes the
    entry structurally unlike the other 24 and changes what the renderer emits:
    a non-empty value trips the Dockerfile's apt branch.
    """
    line = _entry_line(name)
    assert line, f"no registry entry found for {name}"
    fields = line.split("|")
    offenders = [
        (index, value)
        for index, value in enumerate(fields)
        if value == ""
    ]
    assert not offenders, (
        f"the forged entry leaves field(s) blank where siblings use "
        f"{PLACEHOLDER!r}: {offenders}. Entry: {line!r}"
    )


@then('the registry entry for "{name}" must list "{alias}" among its aliases')
def step_entry_alias(context, name, alias):
    line = _entry_line(name)
    assert line, f"no registry entry found for {name}"
    aliases = [a.strip() for a in line.split("|")[2].split(",") if a.strip()]
    assert alias in aliases, (
        f"the forged entry lists aliases {aliases}, which omits the primary "
        f"name {alias!r}; resolution then depends on name derivation rather "
        f"than the Vault recording it"
    )


@then('the registry entry for "{name}" must sit inside the language block')
def step_entry_in_language_block(context, name):
    """
    The conf is grouped and the header documents the layout. An entry appended
    after the service block means a reader scanning 'Language VMs' will not
    see it.
    """
    lines = _conf_lines()
    target = f"lang|vde-{name}|"
    index = next((i for i, l in enumerate(lines) if l.startswith(target)), None)
    assert index is not None, f"no language entry found for {name}"

    preceding_services = [
        i for i, l in enumerate(lines) if l.startswith("service|") and i < index
    ]
    assert not preceding_services, (
        f"the forged entry sits at line {index + 1}, after the service block "
        f"(first service entry at line {preceding_services[0] + 1}), so it "
        f"falls outside the documented language section"
    )


# ---------------------------------------------------------------------------
# Reversibility across both SSH configs
# ---------------------------------------------------------------------------

SSH_CONFIGS = ("configs/ssh/config", "configs/ssh/config.spoke")


def _ssh_has_host(rel, name):
    """
    Exact, line-anchored match. A bare substring test matches prefixes, so
    "roundtrip" would report present when only "Host vde-roundtrip2" exists --
    a false pass on the positive assertion and a false failure on the negative
    one. bin/uninstall-vm-type's own parser anchors the same way.
    """
    path = get_vde_root() / rel
    if not path.is_file():
        return False
    target = f"Host vde-{name}"
    return any(
        line.strip() == target
        for line in path.read_text(encoding="utf-8").splitlines()
    )


@when('I remove the throwaway VM type "{name}" through the canonical entrypoint')
def step_remove(context, name):
    result = subprocess.run(
        ["bin/vde", "uninstall", name, "--skip-confirm"],
        cwd=str(get_vde_root()),
        capture_output=True,
        text=True,
        timeout=300,
    )
    context.last_result = result
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode


@then('both SSH configs must carry a host block for "{name}"')
def step_both_ssh_present(context, name):
    missing = [rel for rel in SSH_CONFIGS if not _ssh_has_host(rel, name)]
    assert not missing, (
        f"registration did not write a host block for vde-{name} into "
        f"{missing}. Both files are generated from the registry, so both must "
        f"gain the Spoke."
    )


@then('neither SSH config must carry a host block for "{name}"')
def step_neither_ssh_present(context, name):
    """
    The asymmetry this guards: configs/ssh/config was edited surgically on
    uninstall while configs/ssh/config.spoke, written by generate-all-configs,
    was never rebuilt -- so an uninstalled Spoke kept a live host block there.
    """
    lingering = [rel for rel in SSH_CONFIGS if _ssh_has_host(rel, name)]
    assert not lingering, (
        f"uninstall left a host block for vde-{name} behind in {lingering}. "
        f"Registration must be fully reversible, or every removed Spoke "
        f"accumulates a stale entry."
    )


@then('the registry must no longer contain "{name}"')
def step_registry_absent(context, name):
    line = _entry_line(name)
    assert line is None, f"the registry still holds an entry for {name}: {line!r}"

    json_path = get_vde_root() / "data/vm-types.json"
    assert f'"vde-{name}"' not in json_path.read_text(encoding="utf-8"), (
        f"the re-smelted JSON Vault still holds vde-{name}"
    )


# ---------------------------------------------------------------------------
# Port ranges (Signet #534, folded scope)
# ---------------------------------------------------------------------------


def _port_bounds(kind):
    """The authoritative range for a type, read from lib/vde-constants."""
    root = str(get_vde_root())
    var = "SVC" if kind == "service" else "LANG"
    result = subprocess.run(
        [
            "zsh",
            "-c",
            f"VDE_ROOT_DIR={root}; export VDE_ROOT_DIR; cd {root} || exit 1; "
            f"source ./lib/vde-constants; "
            f"print -r -- ${{VDE_{var}_PORT_START}} ${{VDE_{var}_PORT_END}}",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    parts = result.stdout.split()
    assert len(parts) == 2, f"could not read {var} port bounds: {result.stdout!r}"
    return int(parts[0]), int(parts[1])


@when('I register the throwaway service type "{name}" on service port {svc_port:d}')
def step_register_service(context, name, svc_port):
    if hasattr(context, "vault_throwaway"):
        context.vault_throwaway.add(name)
    result = subprocess.run(
        [
            "bin/vde", "add", "--type", "service", "--svc-port", str(svc_port),
            name, "apt-get update -y",
        ],
        cwd=str(get_vde_root()),
        capture_output=True,
        text=True,
        timeout=300,
    )
    context.last_result = result
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode


@when('I try to register the service type "{name}" on SSH port {ssh_port:d}')
def step_register_service_bad_port(context, name, ssh_port):
    if hasattr(context, "vault_throwaway"):
        context.vault_throwaway.add(name)
    result = subprocess.run(
        [
            "bin/vde", "add", "--type", "service", "--svc-port", "9997",
            "--ssh-port", str(ssh_port), name, "apt-get update -y",
        ],
        cwd=str(get_vde_root()),
        capture_output=True,
        text=True,
        timeout=300,
    )
    context.last_result = result
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode


@then("the command should fail")
def step_command_failed(context):
    assert context.command_exit_code != 0, (
        f"the command succeeded when it should have been refused. "
        f"Output: {context.command_output!r}"
    )


@then('the registry entry for "{name}" must hold an SSH port inside the service range')
def step_entry_service_port(context, name):
    line = _entry_line(name)
    assert line, f"no registry entry found for {name}"
    fields = line.split("|")
    assert fields[0] == "service", f"{name} was registered as {fields[0]!r}"
    port = int(fields[7])
    low, high = _port_bounds("service")
    assert low <= port <= high, (
        f"{name} holds SSH port {port}, outside the service range {low}-{high}. "
        f"data/vm-types.schema.json rejects it, which leaves the registry "
        f"invalid and makes uninstall refuse to run."
    )


@then("the registry must satisfy its own schema")
def step_schema_valid(context):
    """
    Read the bounds out of the schema itself and check every entry. An invalid
    Vault is not a cosmetic problem: uninstall validates on load, so it stops
    being removable.
    """
    root = get_vde_root()
    schema = json.loads((root / "data/vm-types.schema.json").read_text(encoding="utf-8"))
    vault = json.loads((root / "data/vm-types.json").read_text(encoding="utf-8"))

    defs = schema.get("definitions", {})
    bounds = {}
    for kind, key in (("language", "languageVM"), ("service", "serviceVM")):
        props = defs.get(key, {}).get("properties", {}).get("ssh_port", {})
        if "minimum" in props and "maximum" in props:
            bounds[kind] = (props["minimum"], props["maximum"])

    # Fail loudly if the shape is not what we expect. Iterating absent
    # collections would yield an empty offenders list and PASS, so a change to
    # the JSON shape would silently disable this check entirely.
    assert bounds, (
        "could not read ssh_port bounds for languageVM/serviceVM from "
        "data/vm-types.schema.json; the schema shape changed and this check "
        "would otherwise pass without verifying anything"
    )
    vms = vault.get("vms")
    assert isinstance(vms, dict), f"vms is {type(vms).__name__}, expected a mapping"

    offenders = []
    checked = 0
    for kind, (low, high) in bounds.items():
        collection = vms.get(kind)
        assert isinstance(collection, list) and collection, (
            f"vms.{kind} is missing or empty in the Vault; this check would "
            f"otherwise verify nothing for {kind} entries"
        )
        for vm in collection:
            port = vm.get("ssh_port")
            checked += 1
            if not isinstance(port, int) or not low <= port <= high:
                offenders.append((vm.get("name"), port, f"{low}-{high}"))

    assert checked, "no VM entries were examined; the check verified nothing"
    assert not offenders, (
        "the registry violates its own schema: "
        + "; ".join(f"{n} has ssh_port {p}, expected {r}" for n, p, r in offenders)
    )


# ---------------------------------------------------------------------------
# SSH port reclamation (Signet #534, folded scope)
# ---------------------------------------------------------------------------

PORT_REGISTRY = ".cache/port-registry"


def _port_record(name):
    """The recorded port for a Spoke, or None. vde_normalize_name strips the
    vde- prefix, so the record is '<name>.port'; both spellings are checked so
    a change to that normalisation surfaces as a failure, not a silent pass."""
    for candidate in (f"{name}.port", f"vde-{name}.port"):
        path = get_vde_root() / PORT_REGISTRY / candidate
        if path.is_file():
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
    return None


@then('an SSH port must be recorded for "{name}"')
def step_port_recorded(context, name):
    port = _port_record(name)
    assert port, (
        f"no port record found for {name} under {PORT_REGISTRY}; the "
        f"reclamation assertion that follows would then pass vacuously"
    )
    context.usb_recorded_port = port

    lock = get_vde_root() / PORT_REGISTRY / f"port-{port}.lock"
    assert lock.is_dir(), f"port lock {lock} was not created for {name}"


@then('no SSH port may remain recorded for "{name}"')
def step_port_released(context, name):
    port = _port_record(name)
    assert port is None, (
        f"uninstall left a port record for {name} holding port {port}. "
        f"find_available_ssh_port then skips a port nothing holds, and the "
        f"range is finite."
    )


@then('the port lock for "{name}" must have been released')
def step_port_lock_released(context, name):
    port = getattr(context, "usb_recorded_port", None)
    assert port, "no port was recorded earlier, so release cannot be asserted"
    lock = get_vde_root() / PORT_REGISTRY / f"port-{port}.lock"
    assert not lock.exists(), (
        f"the port lock {lock} survived uninstall, so port {port} stays "
        f"claimed by a Spoke that no longer exists"
    )


# ---------------------------------------------------------------------------
# The forged ritual must RUN, not merely exist (Signet #534)
# ---------------------------------------------------------------------------
#
# The Proof of Life asserts only that the setup script for a dynamically added
# Spoke EXISTS. Nothing in the heartbeat ever builds such a Spoke, so a ritual
# that parses but dies at run time went unnoticed: a Spoke name is not a shell
# identifier, and "typeset vde_dynamic-vm_pkgs" fails with "not valid in this
# context", which under the ritual's own set -e aborts it before the work
# section. These steps close that gap at the layer the defect lives in, rather
# than adding a multi-minute image build to the heartbeat.


@when('I register the throwaway VM type "{name}" with install command "{install_cmd}"')
def step_register_with_cmd(context, name, install_cmd):
    if hasattr(context, "vault_throwaway"):
        context.vault_throwaway.add(name)
    result = subprocess.run(
        ["bin/vde", "add", name, install_cmd],
        cwd=str(get_vde_root()),
        capture_output=True,
        text=True,
        timeout=300,
    )
    context.last_result = result
    context.command_output = result.stdout + result.stderr
    context.command_exit_code = result.returncode
    context.forge_marker = install_cmd.split()[-1] if install_cmd else ""


@then('the hydration ritual for "{name}" must declare only valid shell identifiers')
def step_ritual_identifiers(context, name):
    """
    A variable name may hold only [A-Za-z0-9_] and may not begin with a digit.
    Interpolating a Spoke name into one is the defect: hyphens are legal in
    Spoke names and illegal in identifiers.
    """
    offenders = []
    for line in _ritual_text(name).splitlines():
        stripped = line.strip()
        if not stripped.startswith("typeset "):
            continue
        decl = stripped[len("typeset ") :].lstrip()
        ident = re.split(r"[=\s]", decl, maxsplit=1)[0]
        # ${...} forms are computed at run time and are not literal identifiers.
        if ident.startswith("${"):
            continue
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", ident):
            offenders.append((ident, stripped))

    assert not offenders, (
        "the forged ritual declares variable name(s) that zsh will reject at "
        "run time, aborting the ritual before its work section:\n"
        + "\n".join(f"  {i!r} in {l!r}" for i, l in offenders)
    )


@then('the hydration ritual for "{name}" must execute and reach its work section')
def step_ritual_executes(context, name):
    """
    Run the real ritual in a throwaway container, the way the image build does
    (the registry's custom_cmd is `zsh /vde/scripts/setup/<name>-init.zsh`),
    and assert it reaches the install command. Parsing is not enough: the
    hyphen defect passes `zsh -n` and fails only when executed.
    """
    marker = getattr(context, "forge_marker", "")
    assert marker, "no marker recorded from the install command"

    root = str(get_vde_root())
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{root}:/vde",
            "--entrypoint", "zsh",
            "vde-base:latest",
            f"/vde/scripts/setup/{name}-init.zsh",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )
    combined = result.stdout + result.stderr
    assert "not valid in this context" not in combined, (
        f"the forged ritual died on an invalid variable name before its work "
        f"section:\n{combined}"
    )
    assert marker in combined, (
        f"the forged ritual never reached its work section: the marker "
        f"{marker!r} was not emitted. Exit {result.returncode}.\n{combined}"
    )
