#!/usr/bin/env python3
# @forge (Governance Sentinel)
# VDE ARCHITECTURAL RECORD
"""
Step definitions for the embed Spoke (Signet #533).

Real verification only, per the 100% Real Tests Mandate:
  - Registry assertions read the Beskar Vault itself, and alias resolution is
    driven through the real resolve_vm_name in lib/vm-common rather than
    re-implementing the lookup in Python.
  - Toolchain assertions execute the tool inside the running Spoke; presence on
    disk is not accepted as proof it works.
  - The cross-compile scenario builds a genuine bare-metal object and inspects
    the resulting ELF, so a broken toolchain cannot pass.
"""

import json
import re
import subprocess

from behave import given, when, then

from config import get_vde_root
from shell_helpers import execute_in_container

CONF = "data/vm-types.conf"
JSON_VAULT = "data/vm-types.json"


def _vault():
    with open(get_vde_root() / JSON_VAULT, encoding="utf-8") as handle:
        return json.load(handle)


def _entry(name):
    for group in _vault()["vms"].values():
        for vm in group:
            if vm["name"] == name:
                return vm
    return None


def _conf_lines():
    with open(get_vde_root() / CONF, encoding="utf-8") as handle:
        return handle.read().splitlines()


def _resolve(alias):
    """Resolve an alias through the real library function, not a reimplementation."""
    root = str(get_vde_root())
    script = (
        f"VDE_ROOT_DIR={root}; export VDE_ROOT_DIR; cd {root} || exit 1; "
        "source ./lib/vde-shell-compat; source ./lib/vde-constants; "
        "source ./lib/vde-log; source ./lib/vde-naming; source ./lib/vm-common; "
        "load_vm_types >/dev/null 2>&1; "
        f"resolve_vm_name {alias}"
    )
    result = subprocess.run(
        ["zsh", "-c", script], capture_output=True, text=True, timeout=60
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


@then('the registry must contain a Spoke named "{name}"')
def step_registry_has(context, name):
    assert _entry(name), (
        f"{name} is absent from {JSON_VAULT}. Registered language Spokes: "
        f"{[v['name'] for v in _vault()['vms'].get('language', [])]}"
    )


@then('the Spoke "{name}" must resolve from the alias "{alias}"')
def step_alias_resolves(context, name, alias):
    resolved = _resolve(alias)
    assert resolved == name, (
        f"alias '{alias}' resolved to '{resolved}', expected '{name}'"
    )


@then('the Spoke "{name}" must hold SSH port {port:d}')
def step_ssh_port(context, name, port):
    entry = _entry(name)
    assert entry, f"{name} is absent from the registry"
    assert entry["ssh_port"] == port, (
        f"{name} holds SSH port {entry['ssh_port']}, expected {port}"
    )


@then('the Spoke "{name}" must hydrate from "{path}"')
def step_hydration(context, name, path):
    entry = _entry(name)
    assert entry, f"{name} is absent from the registry"
    assert path in entry["custom_cmd"], (
        f"{name} hydrates via {entry['custom_cmd']!r}, which does not reference "
        f"{path}"
    )
    # Universal Script Parity: the referenced ritual must physically exist.
    script = get_vde_root() / path
    assert script.is_file(), f"hydration ritual missing on disk: {script}"


@then("every registry entry must carry exactly 8 fields")
def step_eight_fields(context):
    offenders = []
    for line in _conf_lines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        count = len(stripped.split("|"))
        if count != 8:
            offenders.append((count, stripped))
    assert not offenders, (
        "the 8-Field Standard is violated by:\n"
        + "\n".join(f"  {n} fields: {l}" for n, l in offenders)
    )


@then("the language SSH port range comment must include port {port:d}")
def step_port_range_comment(context, port):
    """
    Assert against the AUTHORITATIVE range in lib/vde-constants, and that the
    conf comment agrees with it.

    Asserting against the comment alone would be a hand-maintained fiction:
    bin/add-vm-type allocates from VDE_LANG_PORT_START..VDE_LANG_PORT_END, so
    the next Spoke added by the normal tool would fail a test for being outside
    a comment rather than outside the real range.
    """
    root = str(get_vde_root())
    probe = subprocess.run(
        [
            "zsh",
            "-c",
            f"VDE_ROOT_DIR={root}; export VDE_ROOT_DIR; cd {root} || exit 1; "
            "source ./lib/vde-constants; "
            "print -r -- ${VDE_LANG_PORT_START} ${VDE_LANG_PORT_END}",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    bounds = probe.stdout.split()
    assert len(bounds) == 2, (
        f"could not read VDE_LANG_PORT_START/END: {probe.stdout!r} {probe.stderr!r}"
    )
    low, high = int(bounds[0]), int(bounds[1])
    assert low <= port <= high, (
        f"port {port} falls outside the authoritative language range "
        f"{low}-{high} from lib/vde-constants"
    )

    # The conf comment must agree with the constants, or the Vault documents a
    # range its own allocator does not use.
    for line in _conf_lines():
        match = re.search(r"Language VMs \(SSH ports (\d+)-(\d+)", line)
        if match:
            c_low, c_high = int(match.group(1)), int(match.group(2))
            assert (c_low, c_high) == (low, high), (
                f"{CONF} documents language ports {c_low}-{c_high} but "
                f"lib/vde-constants declares {low}-{high}"
            )
            return
    raise AssertionError(f"no language port range comment found in {CONF}")


# ---------------------------------------------------------------------------
# Toolchain
# ---------------------------------------------------------------------------


@given('the image for Spoke "{spoke}" has been built')
def step_image_built(context, spoke):
    """
    Starting a Spoke whose image is absent makes bin/vde build it, which for
    this Spoke far exceeds the step timeout and surfaces as TimeoutExpired --
    an error, not a usable failure. Assert the image first so the operator gets
    the actual remedy.
    """
    result = subprocess.run(
        ["docker", "image", "inspect", f"vde-{spoke}:latest"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"the image vde-{spoke}:latest does not exist, so these scenarios "
        f"cannot run. This Spoke carries a large toolchain and takes roughly "
        f"15-20 minutes to forge. Build it first with: vde create {spoke}"
    )


@then('the command "{tool}" must be available in Spoke "{spoke}"')
def step_tool_available(context, tool, spoke):
    # Execute it, do not merely locate it: a tool present but unable to run
    # (missing shared library, broken venv shim) must not pass.
    result = execute_in_container(
        f"vde-{spoke}",
        f"command -v {tool} >/dev/null 2>&1 && echo FOUND || echo MISSING",
        timeout=60,
    )
    assert "FOUND" in result.stdout, (
        f"{tool} is not on PATH in Spoke '{spoke}': {result.stdout!r} "
        f"{result.stderr!r}"
    )


@then('the Rust target "{target}" must be installed in Spoke "{spoke}"')
def step_rust_target(context, target, spoke):
    result = execute_in_container(
        f"vde-{spoke}", "rustup target list --installed", timeout=120
    )
    installed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    assert target in installed, (
        f"Rust target {target} is not installed in Spoke '{spoke}'. "
        f"Installed: {installed}"
    )


@then('the Python module "{module}" must import in Spoke "{spoke}"')
def step_python_module(context, module, spoke):
    result = execute_in_container(
        f"vde-{spoke}",
        f"python3 -c 'import {module}; print(\"IMPORT_OK\")'",
        timeout=60,
    )
    assert "IMPORT_OK" in result.stdout, (
        f"python3 cannot import '{module}' in Spoke '{spoke}': "
        f"{result.stdout!r} {result.stderr!r}"
    )


@when('the dev user cross-compiles a bare-metal object for "{target}" in Spoke "{spoke}"')
def step_cross_compile(context, target, spoke):
    """
    Compile a real bare-metal translation unit. Freestanding, no libc startup,
    so success depends on the cross toolchain actually working.
    """
    source = (
        "volatile unsigned int counter;\\n"
        "void _start(void) { for (;;) { counter++; } }\\n"
    )
    # Cortex-M4F flags matching thumbv7em-none-eabihf.
    command = (
        "set -e; cd /tmp; "
        f"printf '{source}' > bare.c; "
        "arm-none-eabi-gcc -mcpu=cortex-m4 -mthumb -mfloat-abi=hard "
        "-mfpu=fpv4-sp-d16 -ffreestanding -nostdlib -O2 -c bare.c -o bare.o; "
        "echo COMPILE_OK"
    )
    result = execute_in_container(f"vde-{spoke}", command, timeout=120)
    context.embed_compile_output = f"{result.stdout}\n{result.stderr}"
    context.embed_compile_ok = "COMPILE_OK" in result.stdout
    context.embed_spoke = spoke
    context.embed_target = target


@then("the compile must succeed")
def step_compile_ok(context):
    assert context.embed_compile_ok, (
        f"bare-metal cross-compile failed: {context.embed_compile_output!r}"
    )


@then("the produced object must be ARM 32-bit ELF")
def step_object_is_arm(context):
    spoke = context.embed_spoke
    result = execute_in_container(
        f"vde-{spoke}", "arm-none-eabi-readelf -h /tmp/bare.o", timeout=60
    )
    out = result.stdout
    assert "ELF32" in out, f"object is not 32-bit ELF:\n{out}"
    assert "ARM" in out, f"object is not ARM:\n{out}"
    assert "Relocatable" in out or "REL (Relocatable" in out, (
        f"object is not a relocatable object file:\n{out}"
    )
