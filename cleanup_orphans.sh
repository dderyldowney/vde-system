#!/usr/bin/env zsh
# Kill stray ssh‑agents
pkill -u $USER ssh-agent
# Remove stale sockets
rm -f /tmp/ssh-*/agent.*
# Flush loaded keys
ssh-add -D
# List any remaining background jobs and kill them
for job in $(jobs -p); do
    kill $job
done
echo "Orphaned processes cleaned up."

