#!/usr/bin/env zsh
# @armor (ZPTY Signal Injection Rig)
zmodload zsh/zpty
VDE_ROOT_DIR="${0:a:h:h:h}"

typeset signal_type="$1"
typeset command_str="$2"

# Start the command in a virtual PTY
zpty vde_test "${VDE_ROOT_DIR}/bin/vde" ${=command_str}

# Wait for process to appear
"${VDE_ROOT_DIR}/bin/vde-poll" --wait 3 "all" >/dev/null 2>&1

# Find the PID of the zpty child
typeset actual_pid=$(pgrep -P $$ | grep -v $$ | head -1)

# Fire signal
kill -s "${signal_type}" "${actual_pid}" 2>/dev/null

# Capture output from zpty
typeset output=""
typeset line=""
while zpty -r vde_test line; do
    output+="${line}\n"
done

# Cleanup zpty
zpty -d vde_test

# Output the captured log
echo -e "${output}"
