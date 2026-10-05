#!/usr/bin/env python3
# @forge (Governance Sentinel)
# VDE ARCHITECTURAL RECORD
"""
Step definitions for USB serial board passthrough (Signet #526).

Real verification only, per the 100% Real Tests Mandate:
  - Config scenarios parse the rendered overlays and query the real
    compose-selection helper in lib/vm-common.
  - Runtime scenarios read live container config with `docker inspect` and
    exercise real open(2) calls inside the Spoke.
  - Hardware scenarios require a physically attached board. They are tagged
    @hardware and skipped loudly by environment.py when none is present;
    they never pass by simulating device state.
"""

import glob
import os
import re
import subprocess
import time

from behave import given, when, then

from config import get_vde_root
from shell_helpers import execute_in_container, verify_container_running

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SERIAL_GLOBS = ("/dev/ttyUSB*", "/dev/ttyACM*")


def _overlay_path(spoke):
    """Absolute path of a Spoke's USB overlay (may not exist)."""
    return os.path.join(
        str(get_vde_root()),
        "configs/docker/languages",
        spoke,
        "docker-compose.usb.yml",
    )


def _read_overlay(spoke):
    path = _overlay_path(spoke)
    assert os.path.isfile(path), f"USB overlay missing for '{spoke}': {path}"
    with open(path, encoding="utf-8") as handle:
        return handle.read()


# Drivers that back a real development-board serial bridge. Used to avoid
# mistaking an unrelated CDC-ACM device (an internal modem, another user's
# peripheral) for the board under test.
BOARD_DRIVERS = ("cp210x", "ch341", "ch34x", "ftdi_sio", "pl2303", "cdc_acm")


def _host_board_nodes():
    """Serial nodes physically present on the Hub right now."""
    found = []
    for pattern in SERIAL_GLOBS:
        found.extend(sorted(glob.glob(pattern)))
    return found


def _node_driver(node):
    """The USB driver backing a serial node, via udevadm. None if unknown."""
    result = subprocess.run(
        ["udevadm", "info", "-q", "property", "-n", node],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("ID_USB_DRIVER="):
            return line.split("=", 1)[1].strip()
    return None


def _host_board_node():
    """
    The single serial node backed by a recognised board driver.

    Fails loudly when the Hub is ambiguous rather than guessing, so a passing
    hardware scenario always means the board under test was exercised.
    """
    candidates = [
        node for node in _host_board_nodes() if _node_driver(node) in BOARD_DRIVERS
    ]
    assert candidates, (
        "LOUD FAILURE: no serial node on the Hub is backed by a recognised "
        f"board driver {BOARD_DRIVERS}. Attached: {_host_board_nodes()}"
    )
    assert len(candidates) == 1, (
        f"LOUD FAILURE: the Hub has several board serial nodes {candidates}. "
        "Leave exactly one attached so the scenario proves which device it "
        "actually exercised."
    )
    return candidates[0]


def _node_identity(spoke, node):
    """(inode, change-time) of a node inside the Spoke, or None if absent."""
    result = execute_in_container(
        f"vde-{spoke}", f"stat -c '%i %Z' {node} 2>/dev/null", timeout=30
    )
    parts = result.stdout.strip().split()
    return tuple(parts) if len(parts) == 2 else None


def _compose_files(spoke):
    """Ask the real helper in lib/vm-common for the ordered compose list."""
    root = str(get_vde_root())
    script = (
        f"VDE_ROOT_DIR={root}; cd {root} || exit 1; "
        "source ./lib/vde-shell-compat; source ./lib/vde-constants; "
        "source ./lib/vde-log; source ./lib/vde-naming; source ./lib/vm-common; "
        "load_vm_types >/dev/null 2>&1; "
        f"get_vm_compose_files {spoke}"
    )
    result = subprocess.run(
        ["zsh", "-c", script], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, (
        f"get_vm_compose_files failed for '{spoke}': {result.stderr}"
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _inspect(container, go_template):
    result = subprocess.run(
        ["docker", "inspect", "-f", go_template, container],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"docker inspect failed: {result.stderr}"
    return result.stdout.strip()


def _open_in_spoke(context, spoke, node):
    """
    Attempt a real open(2) of `node` inside the Spoke as devuser.

    Records errno and elapsed wall time on the context so later steps can
    assert both the failure mode and that it did not block.
    """
    container = f"vde-{spoke}"
    program = (
        "import os,sys\n"
        f"node={node!r}\n"
        "try:\n"
        "    fd=os.open(node, os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)\n"
        "    os.close(fd)\n"
        "    print('OPEN_OK')\n"
        "except OSError as e:\n"
        "    print(f'OPEN_FAIL errno={e.errno}')\n"
    )
    encoded = program.encode("utf-8").hex()
    command = (
        "python3 -c \"import binascii,sys;"
        f"exec(binascii.unhexlify('{encoded}').decode())\""
    )
    started = time.monotonic()
    result = execute_in_container(container, command, timeout=30)
    context.usb_open_elapsed = time.monotonic() - started
    context.usb_open_output = f"{result.stdout}\n{result.stderr}"
    context.usb_open_node = node

    match = re.search(r"OPEN_FAIL errno=(\d+)", context.usb_open_output)
    context.usb_open_errno = int(match.group(1)) if match else None
    context.usb_open_ok = "OPEN_OK" in context.usb_open_output
    return context.usb_open_ok


# ---------------------------------------------------------------------------
# Config scenarios (no Docker, no hardware)
# ---------------------------------------------------------------------------


@then('a USB overlay must exist for the Spoke "{spoke}"')
def step_overlay_exists(context, spoke):
    path = _overlay_path(spoke)
    assert os.path.isfile(path), f"expected USB overlay for '{spoke}' at {path}"


@then('no USB overlay must exist for the Spoke "{spoke}"')
def step_overlay_absent(context, spoke):
    path = _overlay_path(spoke)
    assert not os.path.exists(path), (
        f"'{spoke}' is not opted in but has an overlay at {path}"
    )


@then('the USB overlay for "{spoke}" must declare the service "{service}"')
def step_overlay_service(context, spoke, service):
    content = _read_overlay(spoke)
    assert re.search(rf"^\s+{re.escape(service)}:\s*$", content, re.MULTILINE), (
        f"overlay for '{spoke}' does not declare service '{service}'"
    )


@then('the USB overlay for "{spoke}" must grant the device cgroup rule "{rule}"')
def step_overlay_rule(context, spoke, rule):
    content = _read_overlay(spoke)
    assert f'"{rule}"' in content, (
        f"overlay for '{spoke}' is missing cgroup rule '{rule}'"
    )


@then('the USB overlay for "{spoke}" must not grant any wildcard device rule')
def step_overlay_no_wildcard(context, spoke):
    """
    A wildcard major would grant every minor of that class. The entrypoint
    only ever creates the declared nodes, so the grant must enumerate exactly
    those and nothing spare.
    """
    content = _read_overlay(spoke)
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or "rmw" not in stripped:
            continue
        assert ":*" not in stripped, (
            f"overlay for '{spoke}' grants a wildcard rule, which is wider "
            f"than the declared nodes: {line!r}"
        )


@then('the USB overlay for "{spoke}" must grant exactly one rule per declared node')
def step_overlay_rule_per_node(context, spoke):
    """
    The rule list and VDE_USB_TTY_NODES are derived from the same spec and
    must not drift: a node with no rule is unopenable, and a rule with no node
    is an unused grant.
    """
    content = _read_overlay(spoke)

    spec_match = re.search(r"VDE_USB_TTY_NODES=([^\n]+)", content)
    assert spec_match, f"overlay for '{spoke}' declares no VDE_USB_TTY_NODES"

    expected = set()
    for entry in spec_match.group(1).split():
        name, major, count = entry.split(":")
        for index in range(int(count)):
            expected.add((major, str(index)))

    granted = set()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        rule = re.search(r'"c (\d+):(\d+) rmw"', stripped)
        if rule:
            granted.add((rule.group(1), rule.group(2)))

    assert granted == expected, (
        f"overlay for '{spoke}' has drifted: declared nodes "
        f"{sorted(expected)} but granted rules {sorted(granted)}. "
        f"Missing: {sorted(expected - granted)}. Extra: {sorted(granted - expected)}"
    )


@then('the USB overlay for "{spoke}" must not grant any rule for USB bus major 189')
def step_overlay_no_bus(context, spoke):
    content = _read_overlay(spoke)
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert "189" not in stripped, (
            f"overlay for '{spoke}' references major 189 in an active line: {line!r}"
        )


@then('the USB overlay for "{spoke}" must not enable privileged mode')
def step_overlay_no_privileged(context, spoke):
    content = _read_overlay(spoke)
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert not stripped.startswith("privileged:"), (
            f"overlay for '{spoke}' enables privileged mode: {line!r}"
        )


@then('the USB overlay for "{spoke}" must not declare any "devices:" mapping')
def step_overlay_no_devices(context, spoke):
    content = _read_overlay(spoke)
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert not stripped.startswith("devices:"), (
            f"overlay for '{spoke}' declares a devices: mapping, which makes the "
            f"Spoke fail to start when the host node is absent: {line!r}"
        )


@then('the USB overlay for "{spoke}" must declare the node spec "{spec}"')
def step_overlay_node_spec(context, spoke, spec):
    content = _read_overlay(spoke)
    assert f"VDE_USB_TTY_NODES={spec}" in content, (
        f"overlay for '{spoke}' does not declare node spec '{spec}'"
    )


@then('the compose file list for "{spoke}" must include the base compose file')
def step_list_has_base(context, spoke):
    files = _compose_files(spoke)
    expected = f"configs/docker/languages/{spoke}/docker-compose.yml"
    assert expected in files, f"base compose file missing from {files}"


@then('the compose file list for "{spoke}" must include the USB overlay')
def step_list_has_overlay(context, spoke):
    files = _compose_files(spoke)
    expected = f"configs/docker/languages/{spoke}/docker-compose.usb.yml"
    assert expected in files, f"USB overlay missing from {files}"


@then('the base compose file must come first in the compose file list for "{spoke}"')
def step_list_base_first(context, spoke):
    files = _compose_files(spoke)
    assert files, f"no compose files returned for '{spoke}'"
    assert files[0].endswith("docker-compose.yml"), (
        f"base compose file must be first so compose resolves relative paths "
        f"against it, got {files}"
    )


@then('the compose file list for "{spoke}" must contain only the base compose file')
def step_list_base_only(context, spoke):
    files = _compose_files(spoke)
    assert len(files) == 1, (
        f"'{spoke}' is not opted in and must yield exactly one compose file, "
        f"got {files}"
    )


# ---------------------------------------------------------------------------
# Runtime scenarios (require Docker, require NO hardware)
# ---------------------------------------------------------------------------


@given("no USB serial board is attached to the Hub")
def step_no_board(context):
    # Scenarios needing an empty Hub carry @no-board and are skipped by
    # environment.py before they reach this step. Reaching it with a board
    # attached means the gate was bypassed, which must fail loudly.
    attached = _host_board_nodes()
    assert not attached, (
        f"LOUD FAILURE: this scenario requires NO serial board attached, but "
        f"the Hub has {attached}. The @no-board gate should have skipped it."
    )


@given('the node "{node}" in Spoke "{spoke}" has no board behind it')
def step_slot_empty(context, spoke, node):
    """
    Assert a specific slot is genuinely unoccupied, by checking the Hub rather
    than assuming. A high spare slot is empty whenever fewer boards than slots
    are attached, which lets the empty-slot scenario run with a board present.
    """
    host_node = node  # Spoke node names mirror the Hub's.
    assert host_node not in _host_board_nodes(), (
        f"LOUD FAILURE: {host_node} is occupied on the Hub, so it cannot prove "
        f"empty-slot behaviour. Attached: {_host_board_nodes()}"
    )
    context.usb_spoke = spoke


@given('the Spoke "{spoke}" is running')
def step_spoke_running_given(context, spoke):
    container = f"vde-{spoke}"
    # Ensure, do not assume: a scenario must not depend on a previous one
    # having started the Spoke, because the gates can skip that scenario.
    state = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if state.stdout.strip() != "true":
        start = subprocess.run(
            ["bin/vde", "start", spoke],
            cwd=str(get_vde_root()),
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert start.returncode == 0, (
            f"could not start Spoke '{spoke}': {start.stdout}\n{start.stderr}"
        )
    verify_container_running(container)
    context.usb_spoke = spoke

    # Baseline the pre-created nodes so a later step can prove a node was NOT
    # destroyed and re-made across a replug.
    context.usb_node_baseline = {}
    for index in range(8):
        node = f"/dev/ttyUSB{index}"
        identity = _node_identity(spoke, node)
        if identity:
            context.usb_node_baseline[node] = identity


@then('the Spoke "{spoke}" should be running')
def step_spoke_running_then(context, spoke):
    container = f"vde-{spoke}"
    state = _inspect(container, "{{.State.Running}}")
    assert state == "true", f"Spoke '{spoke}' is not running (State.Running={state})"


@then('the Spoke "{spoke}" must report device cgroup rule "{rule}"')
def step_spoke_has_rule(context, spoke, rule):
    rules = _inspect(f"vde-{spoke}", "{{json .HostConfig.DeviceCgroupRules}}")
    assert rule in rules, (
        f"Spoke '{spoke}' does not carry cgroup rule '{rule}'; reported: {rules}"
    )


@then('the Spoke "{spoke}" must not report any wildcard device cgroup rule')
def step_spoke_no_wildcard(context, spoke):
    """
    The live container must carry only enumerated minors. A wildcard here
    would mean the running Spoke has a wider grant than the overlay declares.
    """
    rules = _inspect(f"vde-{spoke}", "{{json .HostConfig.DeviceCgroupRules}}")
    assert ":*" not in rules, (
        f"Spoke '{spoke}' carries a wildcard device rule, which is wider than "
        f"its declared nodes: {rules}"
    )


@then('the Spoke "{spoke}" must not be privileged')
def step_spoke_not_privileged(context, spoke):
    privileged = _inspect(f"vde-{spoke}", "{{.HostConfig.Privileged}}")
    assert privileged == "false", (
        f"Spoke '{spoke}' is privileged, which this design forbids"
    )


@then('the Spoke "{spoke}" must report no device cgroup rule for major {major:d}')
def step_spoke_no_rule_for_major(context, spoke, major):
    rules = _inspect(f"vde-{spoke}", "{{json .HostConfig.DeviceCgroupRules}}")
    assert f"c {major}:" not in rules, (
        f"Spoke '{spoke}' unexpectedly carries a rule for major {major}: {rules}"
    )


@then('the node "{node}" in Spoke "{spoke}" must have major "{major}" and minor "{minor}"')
def step_node_majmin(context, node, spoke, major, minor):
    result = execute_in_container(
        f"vde-{spoke}", f"stat -c '%t %T' {node}", timeout=30
    )
    output = result.stdout.strip().split()
    assert len(output) == 2, (
        f"could not stat {node} in Spoke '{spoke}': "
        f"stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    # stat prints device major/minor in hex.
    actual_major, actual_minor = int(output[0], 16), int(output[1], 16)
    assert actual_major == int(major), (
        f"{node} major is {actual_major}, expected {major}"
    )
    assert actual_minor == int(minor), (
        f"{node} minor is {actual_minor}, expected {minor}"
    )


@then('the node "{node}" in Spoke "{spoke}" must be group "{group}" with mode "{mode}"')
def step_node_group_mode(context, node, spoke, group, mode):
    result = execute_in_container(
        f"vde-{spoke}", f"stat -c '%G %a' {node}", timeout=30
    )
    output = result.stdout.strip().split()
    assert len(output) == 2, (
        f"could not stat {node} in Spoke '{spoke}': stdout={result.stdout!r}"
    )
    assert output[0] == group, f"{node} group is {output[0]}, expected {group}"
    assert output[1] == mode, f"{node} mode is {output[1]}, expected {mode}"


@then('the node "{node}" must not exist in Spoke "{spoke}"')
def step_node_absent(context, node, spoke):
    result = execute_in_container(
        f"vde-{spoke}", f"test -e {node} && echo PRESENT || echo ABSENT", timeout=30
    )
    assert "ABSENT" in result.stdout, (
        f"{node} unexpectedly exists in Spoke '{spoke}': {result.stdout!r}"
    )


@when('the dev user opens "{node}" in Spoke "{spoke}"')
def step_open_node(context, node, spoke):
    _open_in_spoke(context, spoke, node)


@when('the dev user opens a fabricated node for major {major:d} in Spoke "{spoke}"')
def step_open_fabricated(context, major, spoke):
    container = f"vde-{spoke}"
    # Fabricate a node for a device the Spoke was NOT granted. mknod itself is
    # permitted by CAP_MKNOD; the device cgroup rule is what must refuse open().
    probe = "/tmp/vde-usb-bus-probe"
    setup = execute_in_container(
        container,
        f"sudo rm -f {probe} && sudo mknod -m 0666 {probe} c {major} 301 "
        f"&& test -e {probe} && echo MKNOD_OK",
        timeout=30,
        user="devuser",
    )
    # Without this, a failed mknod leaves no node and the probe reports ENOENT
    # (2), which would read as "the cgroup grant is wrong" instead of "the
    # test setup broke".
    assert "MKNOD_OK" in setup.stdout, (
        f"could not fabricate the probe node in Spoke '{spoke}'; the security "
        f"scenario cannot draw a conclusion. stdout={setup.stdout!r} "
        f"stderr={setup.stderr!r}"
    )
    _open_in_spoke(context, spoke, probe)
    execute_in_container(container, f"sudo rm -f {probe}", timeout=30)


@then("the open must fail with errno {errno:d} for {label}")
def step_open_failed_errno(context, errno, label):
    assert not context.usb_open_ok, (
        f"open of {context.usb_open_node} unexpectedly succeeded; "
        f"expected errno {errno} ({label})"
    )
    assert context.usb_open_errno == errno, (
        f"open of {context.usb_open_node} failed with errno "
        f"{context.usb_open_errno}, expected {errno} ({label}). "
        f"Raw: {context.usb_open_output!r}"
    )


@then("the open must not block for longer than {seconds:d} seconds")
def step_open_not_blocking(context, seconds):
    assert context.usb_open_elapsed is not None, "no open was attempted"
    assert context.usb_open_elapsed < seconds, (
        f"open of {context.usb_open_node} took "
        f"{context.usb_open_elapsed:.2f}s, which exceeds {seconds}s; a Spoke "
        f"must never block on an absent board"
    )


# ---------------------------------------------------------------------------
# Hardware-in-the-loop scenarios (require a real board)
# ---------------------------------------------------------------------------


@given("a USB serial board is attached to the Hub")
def step_board_attached(context):
    # Driver-verified, and loud when ambiguous: a pass must mean the board
    # under test was exercised, not whatever happened to be first.
    context.usb_board_node = _host_board_node()


@given("a USB serial board has been unplugged and replugged")
def step_board_replugged(context):
    context.usb_board_node = _host_board_node()


@given('the dev user is holding the board node open in Spoke "{spoke}"')
def step_hold_open(context, spoke):
    node = _host_board_node()
    container = f"vde-{spoke}"
    # signal.pause() blocks until a signal is handled: no timer, no polling
    # loop, so the descriptor stays open without a forbidden sleep call.
    # It is signal.pause(), NOT os.pause() -- os has no such attribute, and
    # getting it wrong kills the holder instantly with AttributeError AFTER
    # the pid file is written, which looks exactly like a holder that died on
    # unplug. SIGHUP is ignored as well, so a hangup from the device going
    # away cannot terminate the holder while the scenario still needs the old
    # minor pinned; with SIG_IGN installed, pause() simply keeps blocking.
    holder = (
        f"nohup python3 -c \"import os,signal;"
        f"signal.signal(signal.SIGHUP, signal.SIG_IGN);"
        f"fd=os.open('{node}', os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK);"
        f"open('/tmp/vde-usb-holder.pid','w').write(str(os.getpid()));"
        f"[signal.pause() for _ in iter(int, 1)]\" >/dev/null 2>&1 &"
    )
    execute_in_container(container, holder, timeout=30)
    context.usb_held_node = node
    context.usb_spoke = spoke


@when("a USB serial board is plugged into the Hub")
def step_board_plugged_now(context):
    assert _host_board_nodes(), (
        "LOUD FAILURE: no board appeared. This scenario requires the Clan "
        "Leader to physically plug a board in when prompted."
    )
    context.usb_board_node = _host_board_node()


@when("the board is unplugged from the Hub")
def step_board_unplugged_now(context):
    attached = _host_board_nodes()
    assert not attached, (
        f"LOUD FAILURE: board still present at {attached}; this scenario "
        f"requires it to be physically unplugged."
    )
    node = getattr(context, "usb_board_node", "/dev/ttyUSB0")
    _open_in_spoke(context, getattr(context, "usb_spoke", "python"), node)


@when("the board is unplugged and replugged while the port is held")
def step_replug_while_held(context):
    attached = _host_board_nodes()
    assert attached, "LOUD FAILURE: no board present after the replug."
    context.usb_board_nodes_after = attached


@when('the dev user opens the attached board node in Spoke "{spoke}"')
def step_open_attached(context, spoke):
    node = getattr(context, "usb_board_node", None)
    assert node, "no attached board node recorded"
    _open_in_spoke(context, spoke, node)


@then("the open must succeed")
def step_open_succeeded(context):
    assert context.usb_open_ok, (
        f"open of {context.usb_open_node} failed with errno "
        f"{context.usb_open_errno}. Raw: {context.usb_open_output!r}"
    )


@then("the open must fail with a device-absent errno")
def step_open_failed_absent(context):
    # ENXIO (6) when the slot never had a device; ENODEV (19) when a stale
    # port is still pinned open by an existing descriptor. Both are correct.
    assert not context.usb_open_ok, (
        f"open of {context.usb_open_node} succeeded despite the board being absent"
    )
    assert context.usb_open_errno in (6, 19), (
        f"expected ENXIO (6) or ENODEV (19), got {context.usb_open_errno}. "
        f"Raw: {context.usb_open_output!r}"
    )


@then("the serial driver must answer a termios query")
def step_termios(context):
    spoke = getattr(context, "usb_spoke", "python")
    node = context.usb_board_node
    program = (
        "import os,termios\n"
        f"fd=os.open({node!r}, os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)\n"
        "termios.tcgetattr(fd)\n"
        "os.close(fd)\n"
        "print('TERMIOS_OK')\n"
    )
    encoded = program.encode("utf-8").hex()
    command = (
        "python3 -c \"import binascii;"
        f"exec(binascii.unhexlify('{encoded}').decode())\""
    )
    result = execute_in_container(f"vde-{spoke}", command, timeout=30)
    assert "TERMIOS_OK" in result.stdout, (
        f"termios query failed on {node}: stdout={result.stdout!r} "
        f"stderr={result.stderr!r}"
    )


@then('the dev user must be able to open the attached board node in Spoke "{spoke}"')
def step_can_open_attached(context, spoke):
    node = getattr(context, "usb_board_node", None)
    assert node, "no attached board node recorded"
    assert _open_in_spoke(context, spoke, node), (
        f"could not open {node} in Spoke '{spoke}': errno "
        f"{context.usb_open_errno}"
    )


@then('the Spoke "{spoke}" must not have been restarted')
def step_not_restarted(context, spoke):
    restarts = _inspect(f"vde-{spoke}", "{{.RestartCount}}")
    assert restarts == "0", (
        f"Spoke '{spoke}' has RestartCount={restarts}; a replug must not "
        f"require a restart"
    )


@then("the node must not have been recreated")
def step_node_not_recreated(context):
    spoke = getattr(context, "usb_spoke", "python")
    node = context.usb_board_node
    baseline = getattr(context, "usb_node_baseline", {}).get(node)
    assert baseline, (
        f"no baseline identity was captured for {node}, so 'not recreated' "
        f"cannot be proven. Baselined nodes: "
        f"{sorted(getattr(context, 'usb_node_baseline', {}))}"
    )
    current = _node_identity(spoke, node)
    assert current, f"{node} is absent in Spoke '{spoke}' after the replug"
    # Same inode and same change time means the entrypoint did not re-make it:
    # the original node carried the board across the replug.
    assert current == baseline, (
        f"{node} was recreated across the replug: inode/ctime moved from "
        f"{baseline} to {current}. The design requires the ORIGINAL node to "
        f"keep working without recreation."
    )


@then("the board must surface on the next minor")
def step_next_minor(context):
    before = context.usb_held_node
    after = context.usb_board_nodes_after
    assert after, "no board node present after the replug"

    # Match on the same device family as the held node, so an unrelated
    # ttyACM device cannot be mistaken for the replugged board.
    prefix = re.match(r"(/dev/tty[A-Za-z]+)", before)
    assert prefix, f"could not parse a device family from {before}"
    family = prefix.group(1)

    moved = [
        node
        for node in after
        if node != before and node.startswith(family)
    ]
    assert moved, (
        f"expected the board to reappear on a different {family}* minor while "
        f"{before} was held open, but the Hub reports {after}. Without a move "
        f"this scenario cannot prove the spare slots are needed."
    )
    context.usb_spare_node = sorted(moved)[0]


@then('the dev user must be able to open that spare node in Spoke "{spoke}"')
def step_open_spare(context, spoke):
    node = context.usb_spare_node
    assert _open_in_spoke(context, spoke, node), (
        f"could not open spare node {node} in Spoke '{spoke}': errno "
        f"{context.usb_open_errno}"
    )
