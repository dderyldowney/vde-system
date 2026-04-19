#!/usr/bin/env zsh
# VDE Repro: Tilde Expansion Bug
# Verifies that quoted tilde doesn't expand in local assignment.

local dev_home_quoted="~root"
local dev_home_unquoted=~root

echo "Quoted: ${dev_home_quoted}"
echo "Unquoted: ${dev_home_unquoted}"

if [[ "${dev_home_quoted}" == "~root" ]]; then
  echo "BUG PROVEN: Quoted tilde failed to expand."
fi

if [[ "${dev_home_unquoted}" != "~root" ]]; then
  echo "SUCCESS: Unquoted tilde expanded to ${dev_home_unquoted}."
fi
