#!/usr/bin/env python3
# @forge (Governance Sentinel)
# VDE ARCHITECTURAL RECORD
"""
Step definitions for stable per-port USB names (Signet #528).

Real verification only, per the 100% Real Tests Mandate:
  - The map is produced by the canonical `vde usb-map` command, never by
    calling the in-Spoke script directly (Mandates 10 and 12).
  - Port paths are cross-checked against the Hub's own udev view, so a pass
    means the Spoke agrees with the host rather than merely being
    self-consistent.
  - No synthetic sysfs tree. Scenarios needing a board are tagged and skipped
    loudly by environment.py.
"""

import re
import subprocess

from behave import given, when, then

from config import get_vde_root
from shell_helpers import execute_in_container

# Helpers shared with the Signet #526 suite; importing keeps one definition of
# "which node is the board" rather than two that can drift.
from usb_serial_steps import (  # noqa: F401  (step registry side effects)
    _host_board_node,
    _host_board_nodes,
    _open_in_spoke,
)


def _run_vde(args, timeout=120):
    """Run the canonical entrypoint from the project root."""
    return subprocess.run(
        ["bin/vde", *args],
        cwd=str(get_vde_root()),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _parse_map(output):
    """
    Parse `vde usb-map` output into a list of dicts.

    Lines look like:
      node=/dev/ttyUSB1\tport=1-3.3\tname=/dev/vde/by-port/1-3.3\tvid:pid=10c4:ea60\tserial=0001
    """
    entries = []
    for line in output.splitlines():
        if not line.startswith("node="):
            continue
        fields = {}
        for chunk in line.split("\t"):
            if "=" in chunk:
                key, _, value = chunk.partition("=")
                fields[key.strip()] = value.strip()
        if "node" in fields and "port" in fields:
            entries.append(fields)
    return entries


def _host_port_path(node):
    """The Hub's own USB port path for a serial node, from sysfs."""
    target = subprocess.run(
        ["readlink", "-f", f"/sys/class/tty/{node.rsplit('/', 1)[-1]}"],
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()
    for part in target.split("/"):
        if re.fullmatch(r"\d+-\d+(\.\d+)*:\d+\.\d+", part):
            return part.split(":", 1)[0]
    return None


def _spoke_live_serial_nodes(spoke):
    """
    Serial nodes the Spoke can actually reach: present in sysfs AND backed by
    a /dev node inside the Spoke.

    /sys inside a container is the HOST's sysfs, so it also lists serial
    devices on minors outside this Spoke's declared slot range. Those have no
    /dev node and no cgroup grant, and `vde usb-map` rightly skips them, so
    comparing against sysfs alone would fail on a Hub with more serial devices
    than declared slots.
    """
    result = execute_in_container(
        f"vde-{spoke}",
        "for n in $(ls /sys/class/tty | grep -E '^tty(USB|ACM)[0-9]+$'); do "
        "test -e /dev/$n && echo $n; done || true",
        timeout=30,
    )
    return sorted(
        f"/dev/{name.strip()}" for name in result.stdout.splitlines() if name.strip()
    )


# ---------------------------------------------------------------------------
# Map directory presence
# ---------------------------------------------------------------------------


@then('Spoke "{spoke}" must carry the USB map resolver')
def step_resolver_present(context, spoke):
    """
    A Spoke still running from a pre-#528 image has no resolver and therefore
    no map directory. Assert the resolver first so that case reports an
    environment problem rather than looking like a code defect.
    """
    result = execute_in_container(
        f"vde-{spoke}",
        "test -x /usr/local/bin/vde-usb-map.zsh && echo PRESENT || echo ABSENT",
        timeout=30,
    )
    assert "PRESENT" in result.stdout, (
        f"Spoke '{spoke}' has no /usr/local/bin/vde-usb-map.zsh. It is running "
        f"from an image built before Signet #528, or was not recreated after "
        f"the rebuild. Run: vde rebuild --vm base && vde rebuild {spoke}, then "
        f"vde stop {spoke} && vde start {spoke}."
    )


@then('the directory "{path}" must exist in Spoke "{spoke}"')
def step_dir_exists(context, path, spoke):
    result = execute_in_container(
        f"vde-{spoke}", f"test -d {path} && echo PRESENT || echo ABSENT", timeout=30
    )
    assert "PRESENT" in result.stdout, (
        f"{path} does not exist in Spoke '{spoke}': {result.stdout!r}"
    )


@then('the directory "{path}" must not exist in Spoke "{spoke}"')
def step_dir_absent(context, path, spoke):
    result = execute_in_container(
        f"vde-{spoke}", f"test -d {path} && echo PRESENT || echo ABSENT", timeout=30
    )
    assert "ABSENT" in result.stdout, (
        f"{path} unexpectedly exists in Spoke '{spoke}', which has no USB "
        f"overlay: {result.stdout!r}"
    )


# ---------------------------------------------------------------------------
# Map content
# ---------------------------------------------------------------------------


@then("the map output must list exactly the Spoke's live serial nodes")
def step_map_matches_live(context):
    spoke = getattr(context, "usb_spoke", "python")
    reported = sorted(entry["node"] for entry in _parse_map(context.command_output))
    live = _spoke_live_serial_nodes(spoke)
    assert reported == live, (
        f"the map reported {reported} but the Spoke's live serial nodes are "
        f"{live}. The map must be neither stale nor inventive."
    )


@then("the map output must list no serial nodes")
def step_map_empty(context):
    entries = _parse_map(context.command_output)
    assert not entries, (
        f"the map listed {[e['node'] for e in entries]} with no board attached"
    )
    assert "No serial boards attached" in context.command_output, (
        f"the map did not say plainly that nothing is attached: "
        f"{context.command_output!r}"
    )


@then("the map output must report the attached board's node")
def step_map_reports_board(context):
    node = context.usb_board_node
    entries = _parse_map(context.command_output)
    nodes = [entry["node"] for entry in entries]
    assert node in nodes, (
        f"the attached board {node} is missing from the map; reported: {nodes}"
    )
    context.usb_map_entry = next(e for e in entries if e["node"] == node)


@then("the reported port path must match the Hub's own port path for that board")
def step_port_path_agrees(context):
    entry = context.usb_map_entry
    expected = _host_port_path(entry["node"])
    assert expected, (
        f"could not determine the Hub's port path for {entry['node']}"
    )
    assert entry["port"] == expected, (
        f"the Spoke reported port '{entry['port']}' but the Hub says "
        f"'{expected}'. The Spoke must agree with the host, not merely be "
        f"self-consistent."
    )


# ---------------------------------------------------------------------------
# Refresh and stable-name access
# ---------------------------------------------------------------------------


@given('the USB map has been refreshed for Spoke "{spoke}"')
def step_refresh_map(context, spoke):
    result = _run_vde(["usb-map", spoke])
    assert result.returncode == 0, (
        f"vde usb-map {spoke} failed: {result.stdout}\n{result.stderr}"
    )
    context.command_output = result.stdout + result.stderr
    context.usb_spoke = spoke

    entries = _parse_map(context.command_output)

    # Once a port has been recorded, match on the PORT from then on. After a
    # replug the board sits on a different node, so matching the pre-replug
    # node would make the whole point of this suite untestable.
    known_port = getattr(context, "usb_stable_port", None)
    if known_port:
        matching = [e for e in entries if e["port"] == known_port]
        assert matching, (
            f"port {known_port} is missing from the refreshed map; reported "
            f"ports: {[e['port'] for e in entries]}"
        )
        return

    node = getattr(context, "usb_board_node", None)
    if node:
        matching = [e for e in entries if e["node"] == node]
        assert matching, (
            f"the refreshed map does not contain the attached board {node}; "
            f"reported: {[e['node'] for e in entries]}"
        )
        context.usb_stable_name = matching[0]["name"]
        context.usb_stable_port = matching[0]["port"]
        context.usb_node_before = node


@when('the dev user opens the board\'s stable port name in Spoke "{spoke}"')
def step_open_stable(context, spoke):
    name = getattr(context, "usb_stable_name", None)
    assert name, "no stable port name was recorded"
    _open_in_spoke(context, spoke, name)


@then('the dev user must be able to open the board\'s stable port name in Spoke "{spoke}"')
def step_can_open_stable(context, spoke):
    name = getattr(context, "usb_stable_name", None)
    assert name, "no stable port name was recorded"
    assert _open_in_spoke(context, spoke, name), (
        f"could not open the stable name {name} in Spoke '{spoke}': errno "
        f"{context.usb_open_errno}"
    )


@then("the board's ttyUSB number must have changed")
def step_node_number_changed(context):
    before = context.usb_node_before
    entries = _parse_map(context.command_output)
    port = context.usb_stable_port
    matching = [e for e in entries if e["port"] == port]
    assert matching, (
        f"port {port} is missing from the refreshed map; reported ports: "
        f"{[e['port'] for e in entries]}"
    )
    after = matching[0]["node"]
    assert after != before, (
        f"the board is still on {before}, so this scenario cannot demonstrate "
        f"that a stable name survives a node change. The replug must be done "
        f"while the port is held open."
    )
    context.usb_node_after = after


@then("the board's stable port name must be unchanged")
def step_stable_name_unchanged(context):
    port = context.usb_stable_port
    entries = _parse_map(context.command_output)
    matching = [e for e in entries if e["port"] == port]
    assert matching, f"port {port} vanished from the map after the replug"
    assert matching[0]["name"] == context.usb_stable_name, (
        f"the stable name moved from {context.usb_stable_name} to "
        f"{matching[0]['name']}; it must be derived from the socket, not the node"
    )
    # And it must now point at the NEW node, which is the entire point.
    assert matching[0]["node"] == context.usb_node_after, (
        f"the stable name still refers to {matching[0]['node']} rather than "
        f"the board's new node {context.usb_node_after}"
    )
