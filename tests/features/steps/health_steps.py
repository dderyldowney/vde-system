#!/usr/bin/env python3
# @forge (Governance Sentinel)
"""
Steps that make a host tool fail on demand, so a scenario can prove that
bin/vde-health reports a failed measurement as a failure instead of a pass.

A stub is a small zsh script placed first on PATH for the duration of the
scenario. The original PATH is restored (and the stub removed) by a behave
cleanup, even when the scenario fails.
"""

import os
import re
import shutil
import tempfile

from behave import given, then

_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _prepend_stub(context, tool, body):
    """Put a zsh stub named `tool` first on PATH until the scenario ends."""
    stub_dir = tempfile.mkdtemp(prefix="vde-stub-")
    stub_path = os.path.join(stub_dir, tool)
    with open(stub_path, "w") as stub:
        stub.write("#!/usr/bin/env zsh\n" + body + "\n")
    os.chmod(stub_path, 0o755)

    old_path = os.environ["PATH"]
    os.environ["PATH"] = stub_dir + os.pathsep + old_path

    def _restore():
        os.environ["PATH"] = old_path
        shutil.rmtree(stub_dir, ignore_errors=True)

    context.add_cleanup(_restore)


@then('the command output should not contain "{text}"')
def step_command_output_lacks(context, text):
    output = _ANSI.sub("", context.command_output)
    assert text not in output, f"Output contained forbidden text: {text!r}\n{output}"


@given('the "{tool}" command fails')
def step_tool_always_fails(context, tool):
    _prepend_stub(context, tool, "exit 1")


@given('the "{tool}" command fails when invoked with "{arg}"')
def step_tool_fails_for_argument(context, tool, arg):
    real = shutil.which(tool)
    assert real, f"'{tool}' is not installed, so it cannot be stubbed"
    body = (
        'for a in "$@"; do\n'
        f'    [[ "$a" == "{arg}" ]] && exit 1\n'
        "done\n"
        f'exec "{real}" "$@"'
    )
    _prepend_stub(context, tool, body)
