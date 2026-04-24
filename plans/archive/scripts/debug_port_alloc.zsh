#!/usr/bin/env zsh
# @shared-law (Forge Component)
source lib/vm-common
echo "Testing find_available_port 2200 2210"
res=$(find_available_port 2200 2210)
echo "Result: '$res'"
echo "Exit code: $?"
